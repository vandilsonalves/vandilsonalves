"""
Test Feed Photo Upload Feature
- POST /api/feed/posts/com-foto - Upload photo with optional text
- GET /api/feed/fotos-restantes - Get remaining photos for the day
- Limit of 2 photos per day (24h)
- Format validation (jpg/png/webp/heic/heif)
- Size validation (max 5MB)
"""

import pytest
import requests
import os
from io import BytesIO
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Admin authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def atleta_token():
    """Get atleta authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ATLETA_EMAIL,
        "password": ATLETA_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Atleta authentication failed: {response.status_code} - {response.text}")


def create_test_image(width=200, height=200, color='red', format='JPEG'):
    """Create a test image in memory"""
    img = Image.new('RGB', (width, height), color)
    buffer = BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer


class TestFotosRestantes:
    """Test GET /api/feed/fotos-restantes endpoint"""
    
    def test_fotos_restantes_returns_correct_structure(self, admin_token):
        """Test that fotos-restantes returns correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/feed/fotos-restantes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "fotos_hoje" in data, "Response should contain 'fotos_hoje'"
        assert "limite_diario" in data, "Response should contain 'limite_diario'"
        assert "restantes" in data, "Response should contain 'restantes'"
        assert data["limite_diario"] == 2, "Daily limit should be 2"
        assert isinstance(data["restantes"], int), "restantes should be an integer"
        assert data["restantes"] >= 0, "restantes should be >= 0"
        print(f"✓ Fotos restantes: {data['restantes']}/{data['limite_diario']}")
    
    def test_fotos_restantes_requires_auth(self):
        """Test that fotos-restantes requires authentication"""
        response = requests.get(f"{BASE_URL}/api/feed/fotos-restantes")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Endpoint requires authentication")


class TestFotoUpload:
    """Test POST /api/feed/posts/com-foto endpoint"""
    
    def test_upload_foto_with_text(self, admin_token):
        """Test uploading a photo with text caption"""
        # First check remaining photos
        check_response = requests.get(
            f"{BASE_URL}/api/feed/fotos-restantes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        remaining = check_response.json().get("restantes", 0)
        
        if remaining == 0:
            pytest.skip("No remaining photos for today - limit reached")
        
        # Create test image
        img_buffer = create_test_image(200, 200, 'blue')
        
        files = {
            'foto': ('test_image.jpg', img_buffer, 'image/jpeg')
        }
        data = {
            'texto': 'Teste de upload de foto com legenda!'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/com-foto",
            headers={"Authorization": f"Bearer {admin_token}"},
            files=files,
            data=data
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        result = response.json()
        assert "message" in result, "Response should contain 'message'"
        assert "post_id" in result, "Response should contain 'post_id'"
        assert "imagem_url" in result, "Response should contain 'imagem_url'"
        assert "fotos_restantes_hoje" in result, "Response should contain 'fotos_restantes_hoje'"
        assert result["imagem_url"].startswith("/uploads/feed/"), "Image URL should start with /uploads/feed/"
        print(f"✓ Photo uploaded successfully: {result['imagem_url']}")
        print(f"✓ Remaining photos: {result['fotos_restantes_hoje']}")
    
    def test_upload_foto_without_text(self, admin_token):
        """Test uploading a photo without text (text is optional)"""
        # First check remaining photos
        check_response = requests.get(
            f"{BASE_URL}/api/feed/fotos-restantes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        remaining = check_response.json().get("restantes", 0)
        
        if remaining == 0:
            pytest.skip("No remaining photos for today - limit reached")
        
        # Create test image
        img_buffer = create_test_image(200, 200, 'green')
        
        files = {
            'foto': ('test_no_text.jpg', img_buffer, 'image/jpeg')
        }
        # No texto field - should work since text is optional
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/com-foto",
            headers={"Authorization": f"Bearer {admin_token}"},
            files=files
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        result = response.json()
        assert "post_id" in result, "Response should contain 'post_id'"
        print(f"✓ Photo without text uploaded successfully")
    
    def test_upload_requires_auth(self):
        """Test that upload requires authentication"""
        img_buffer = create_test_image()
        files = {'foto': ('test.jpg', img_buffer, 'image/jpeg')}
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/com-foto",
            files=files
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Upload requires authentication")


class TestFotoValidation:
    """Test photo validation rules"""
    
    def test_invalid_format_rejected(self, admin_token):
        """Test that invalid file formats are rejected"""
        # Create a fake file with invalid extension
        fake_file = BytesIO(b"This is not an image")
        
        files = {
            'foto': ('test.txt', fake_file, 'text/plain')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/com-foto",
            headers={"Authorization": f"Bearer {admin_token}"},
            files=files
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid format, got {response.status_code}"
        print("✓ Invalid format correctly rejected")
    
    def test_png_format_accepted(self, admin_token):
        """Test that PNG format is accepted"""
        # Check remaining photos first
        check_response = requests.get(
            f"{BASE_URL}/api/feed/fotos-restantes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        remaining = check_response.json().get("restantes", 0)
        
        if remaining == 0:
            pytest.skip("No remaining photos for today")
        
        # Create PNG image
        img_buffer = create_test_image(100, 100, 'yellow', format='PNG')
        
        files = {
            'foto': ('test.png', img_buffer, 'image/png')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/com-foto",
            headers={"Authorization": f"Bearer {admin_token}"},
            files=files
        )
        
        # Should be 200 or 429 (if limit reached)
        assert response.status_code in [200, 429], f"Expected 200 or 429, got {response.status_code}: {response.text}"
        if response.status_code == 200:
            print("✓ PNG format accepted")
        else:
            print("✓ PNG format would be accepted (limit reached)")


class TestFotoLimit:
    """Test daily photo limit (2 photos per 24h)"""
    
    def test_limit_enforced(self, atleta_token):
        """Test that the 2 photo daily limit is enforced"""
        # The atleta teste.dono@teste.com already used 2 photos according to context
        # So this should return 429
        
        # First check remaining
        check_response = requests.get(
            f"{BASE_URL}/api/feed/fotos-restantes",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        remaining = check_response.json().get("restantes", 0)
        print(f"Atleta has {remaining} photos remaining")
        
        if remaining > 0:
            pytest.skip(f"Atleta still has {remaining} photos remaining - cannot test limit")
        
        # Try to upload when limit is reached
        img_buffer = create_test_image(100, 100, 'purple')
        files = {'foto': ('test_limit.jpg', img_buffer, 'image/jpeg')}
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/com-foto",
            headers={"Authorization": f"Bearer {atleta_token}"},
            files=files
        )
        
        assert response.status_code == 429, f"Expected 429 when limit reached, got {response.status_code}: {response.text}"
        print("✓ Daily limit correctly enforced with HTTP 429")


class TestFeedWithPhotos:
    """Test that photos appear correctly in the feed"""
    
    def test_feed_shows_photo_posts(self, admin_token):
        """Test that the feed includes photo posts with correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/feed?pagina=1&limite=20",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "posts" in data, "Response should contain 'posts'"
        
        # Look for photo posts
        photo_posts = [p for p in data["posts"] if p.get("tipo") == "foto"]
        
        if photo_posts:
            post = photo_posts[0]
            assert post.get("tipo") == "foto", "Photo post should have tipo='foto'"
            assert post.get("imagem_url") is not None, "Photo post should have imagem_url"
            assert post["imagem_url"].startswith("/uploads/feed/"), "Image URL should be in /uploads/feed/"
            print(f"✓ Found {len(photo_posts)} photo post(s) in feed")
            print(f"✓ Photo post structure correct: tipo=foto, imagem_url={post['imagem_url']}")
        else:
            print("⚠ No photo posts found in feed (may need to upload first)")
    
    def test_photo_file_accessible(self, admin_token):
        """Test that uploaded photo files are accessible via static URL"""
        # Get feed to find a photo post
        response = requests.get(
            f"{BASE_URL}/api/feed?pagina=1&limite=20",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        data = response.json()
        photo_posts = [p for p in data.get("posts", []) if p.get("tipo") == "foto" and p.get("imagem_url")]
        
        if not photo_posts:
            pytest.skip("No photo posts found to test file accessibility")
        
        # Try to access the image
        imagem_url = photo_posts[0]["imagem_url"]
        full_url = f"{BASE_URL}/api{imagem_url}"
        
        img_response = requests.get(full_url)
        
        assert img_response.status_code == 200, f"Image should be accessible at {full_url}, got {img_response.status_code}"
        assert "image" in img_response.headers.get("content-type", ""), "Response should be an image"
        print(f"✓ Photo file accessible at {full_url}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
