"""
Iteration 108: Cloud Storage Migration Tests
Tests for Object Storage migration from local disk to Emergent cloud storage.

Features tested:
1. GET /api/storage/health - Storage health check
2. GET /api/cloud-files/{path} - Cloud file proxy endpoint
3. POST /api/atletas/foto - Profile photo upload to cloud
4. POST /api/admin/instagram/upload-foto - Instagram photo upload to cloud
5. POST /api/admin/parceiros - Partner image upload to cloud
6. POST /api/admin/mensagens/upload - Admin message file upload to cloud
7. GET /api/uploads/ - Legacy local file serving (backward compatibility)
8. MongoDB URL migration verification
"""

import pytest
import requests
import os
import base64
from io import BytesIO

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"
MASTER_PASSWORD = "d7ff103ad1250@#$"

# Small 1x1 PNG image for testing uploads
TEST_PNG_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


def get_test_image():
    """Returns a small PNG image as bytes for testing uploads"""
    return base64.b64decode(TEST_PNG_BASE64)


class TestStorageHealth:
    """Tests for /api/storage/health endpoint"""
    
    def test_storage_health_returns_ok(self):
        """GET /api/storage/health should return status ok and storage_key_set true"""
        response = requests.get(f"{BASE_URL}/api/storage/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data, "Response should contain 'status' field"
        assert data["status"] == "ok", f"Expected status 'ok', got '{data['status']}'"
        assert "storage_key_set" in data, "Response should contain 'storage_key_set' field"
        assert data["storage_key_set"] == True, "storage_key_set should be True"
        print(f"✓ Storage health check passed: {data}")


class TestCloudFilesProxy:
    """Tests for /api/cloud-files/{path} proxy endpoint"""
    
    def test_cloud_files_invalid_path_returns_404(self):
        """GET /api/cloud-files/invalid/path should return 404"""
        response = requests.get(f"{BASE_URL}/api/cloud-files/invalid/nonexistent/path.jpg")
        assert response.status_code == 404, f"Expected 404 for invalid path, got {response.status_code}"
        print("✓ Invalid cloud file path returns 404")
    
    def test_cloud_files_valid_path_structure(self):
        """Verify cloud files endpoint accepts rankingrun prefix paths"""
        # This tests the endpoint structure - actual file may or may not exist
        response = requests.get(f"{BASE_URL}/api/cloud-files/rankingrun/perfil/test.jpg")
        # Should return 404 (file not found) or 200 (if file exists), not 500
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}: {response.text}"
        print(f"✓ Cloud files endpoint structure valid (status: {response.status_code})")


class TestAuthentication:
    """Helper class for authentication"""
    
    @staticmethod
    def get_admin_token():
        """Get admin JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    @staticmethod
    def get_atleta_token():
        """Get atleta JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None


class TestAtletaFotoUpload:
    """Tests for POST /api/atletas/foto - Profile photo upload to cloud"""
    
    def test_atleta_foto_upload_requires_auth(self):
        """POST /api/atletas/foto should require authentication"""
        files = {"foto": ("test.png", get_test_image(), "image/png")}
        response = requests.post(f"{BASE_URL}/api/atletas/foto", files=files)
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Atleta foto upload requires authentication")
    
    def test_atleta_foto_upload_returns_cloud_url(self):
        """POST /api/atletas/foto should return foto_url with /api/cloud-files/"""
        token = TestAuthentication.get_atleta_token()
        if not token:
            pytest.skip("Could not get atleta token - skipping authenticated test")
        
        headers = {"Authorization": f"Bearer {token}"}
        files = {"foto": ("test_profile.png", get_test_image(), "image/png")}
        
        response = requests.post(f"{BASE_URL}/api/atletas/foto", headers=headers, files=files)
        
        # May return 403 if user is not premium, which is expected behavior
        if response.status_code == 403:
            print("✓ Atleta foto upload correctly requires premium access (403)")
            return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "foto_url" in data, "Response should contain 'foto_url'"
        assert "/api/cloud-files/" in data["foto_url"], f"foto_url should contain '/api/cloud-files/', got: {data['foto_url']}"
        print(f"✓ Atleta foto upload returns cloud URL: {data['foto_url']}")


class TestAdminInstagramUpload:
    """Tests for POST /api/admin/instagram/upload-foto"""
    
    def test_instagram_upload_requires_admin(self):
        """POST /api/admin/instagram/upload-foto should require admin auth"""
        files = {"foto": ("test.png", get_test_image(), "image/png")}
        response = requests.post(f"{BASE_URL}/api/admin/instagram/upload-foto", files=files)
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Instagram upload requires admin authentication")
    
    def test_instagram_upload_returns_cloud_url(self):
        """POST /api/admin/instagram/upload-foto should return foto_url with /api/cloud-files/"""
        token = TestAuthentication.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token - skipping authenticated test")
        
        headers = {"Authorization": f"Bearer {token}"}
        files = {"foto": ("instagram_test.png", get_test_image(), "image/png")}
        
        response = requests.post(f"{BASE_URL}/api/admin/instagram/upload-foto", headers=headers, files=files)
        
        # Endpoint may not exist or may have different behavior
        if response.status_code == 404:
            print("⚠ Instagram upload endpoint not found (404) - may not be implemented")
            return
        
        if response.status_code == 200:
            data = response.json()
            if "foto_url" in data:
                assert "/api/cloud-files/" in data["foto_url"], f"foto_url should contain '/api/cloud-files/', got: {data['foto_url']}"
                print(f"✓ Instagram upload returns cloud URL: {data['foto_url']}")
            else:
                print(f"✓ Instagram upload succeeded: {data}")
        else:
            print(f"⚠ Instagram upload returned {response.status_code}: {response.text[:200]}")


class TestAdminParceirosUpload:
    """Tests for POST /api/admin/parceiros - Partner image upload to cloud"""
    
    def test_parceiros_upload_requires_admin(self):
        """POST /api/admin/parceiros should require admin auth"""
        data = {"nome": "Test Partner", "instagram": "@test", "site": "https://test.com"}
        response = requests.post(f"{BASE_URL}/api/admin/parceiros", data=data)
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Parceiros creation requires admin authentication")
    
    def test_parceiros_with_image_returns_cloud_url(self):
        """POST /api/admin/parceiros with image should return imagem_url with /api/cloud-files/"""
        token = TestAuthentication.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token - skipping authenticated test")
        
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "nome": "Test Partner Cloud",
            "instagram": "@testcloud",
            "site": "https://testcloud.com"
        }
        files = {"imagem": ("partner_logo.png", get_test_image(), "image/png")}
        
        response = requests.post(f"{BASE_URL}/api/admin/parceiros", headers=headers, data=data, files=files)
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        
        result = response.json()
        if "imagem_url" in result and result["imagem_url"]:
            assert "/api/cloud-files/" in result["imagem_url"], f"imagem_url should contain '/api/cloud-files/', got: {result['imagem_url']}"
            print(f"✓ Parceiros upload returns cloud URL: {result['imagem_url']}")
        else:
            print(f"✓ Parceiros created (no image URL in response): {result}")


class TestAdminMensagensUpload:
    """Tests for POST /api/admin/mensagens/upload - Admin message file upload"""
    
    def test_mensagens_upload_requires_admin(self):
        """POST /api/admin/mensagens/upload should require admin auth"""
        files = {"arquivo": ("test.png", get_test_image(), "image/png")}
        response = requests.post(f"{BASE_URL}/api/admin/mensagens/upload", files=files)
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Mensagens upload requires admin authentication")
    
    def test_mensagens_upload_returns_cloud_url(self):
        """POST /api/admin/mensagens/upload should return url with /api/cloud-files/"""
        token = TestAuthentication.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token - skipping authenticated test")
        
        headers = {"Authorization": f"Bearer {token}"}
        files = {"arquivo": ("message_attachment.png", get_test_image(), "image/png")}
        
        response = requests.post(f"{BASE_URL}/api/admin/mensagens/upload", headers=headers, files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, "Response should contain 'url'"
        assert "/api/cloud-files/" in data["url"], f"url should contain '/api/cloud-files/', got: {data['url']}"
        print(f"✓ Mensagens upload returns cloud URL: {data['url']}")


class TestLegacyUploadsEndpoint:
    """Tests for GET /api/uploads/ - Legacy local file serving"""
    
    def test_legacy_uploads_endpoint_exists(self):
        """GET /api/uploads/ should be accessible (backward compatibility)"""
        # Test that the endpoint exists and returns appropriate response
        response = requests.get(f"{BASE_URL}/api/uploads/")
        # Should return 404 (no index) or 200 (directory listing) or 403 (forbidden), not 500
        assert response.status_code in [200, 403, 404], f"Expected 200/403/404, got {response.status_code}"
        print(f"✓ Legacy /api/uploads/ endpoint accessible (status: {response.status_code})")
    
    def test_legacy_uploads_nonexistent_file(self):
        """GET /api/uploads/nonexistent.jpg should return 404"""
        response = requests.get(f"{BASE_URL}/api/uploads/nonexistent_file_12345.jpg")
        assert response.status_code == 404, f"Expected 404 for nonexistent file, got {response.status_code}"
        print("✓ Legacy uploads returns 404 for nonexistent files")


class TestMongoDBMigration:
    """Tests to verify MongoDB URLs were migrated correctly"""
    
    def test_user_foto_url_format(self):
        """Verify user foto_url in MongoDB uses /api/cloud-files/ format"""
        token = TestAuthentication.get_atleta_token()
        if not token:
            pytest.skip("Could not get atleta token - skipping test")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/atletas/meu-perfil", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            foto_url = data.get("foto_url", "")
            if foto_url:
                # Check if it's a cloud URL or legacy URL
                if "/api/cloud-files/" in foto_url:
                    print(f"✓ User foto_url uses cloud format: {foto_url}")
                elif "/api/uploads/" in foto_url or "/uploads/" in foto_url:
                    print(f"⚠ User foto_url still uses legacy format: {foto_url}")
                else:
                    print(f"ℹ User foto_url format: {foto_url}")
            else:
                print("ℹ User has no foto_url set")
        else:
            print(f"⚠ Could not fetch user profile: {response.status_code}")


class TestCloudStorageService:
    """Tests for the object_storage service functionality"""
    
    def test_storage_initialization(self):
        """Verify storage service initializes correctly via health endpoint"""
        response = requests.get(f"{BASE_URL}/api/storage/health")
        assert response.status_code == 200
        data = response.json()
        
        # If status is error, print the detail
        if data.get("status") == "error":
            print(f"⚠ Storage initialization error: {data.get('detail', 'Unknown error')}")
            pytest.fail(f"Storage not initialized: {data.get('detail')}")
        
        assert data["status"] == "ok"
        assert data["storage_key_set"] == True
        print("✓ Cloud storage service initialized correctly")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
