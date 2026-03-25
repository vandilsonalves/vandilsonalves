"""
Test Stories Feature - Iteration 76
Tests for the Stories (temporary 24h photos) feature in the Feed

Endpoints tested:
- POST /api/feed/stories - Create story with photo and text
- GET /api/feed/stories - List active stories (24h) grouped by author
- POST /api/feed/stories/{id}/visualizar - Mark story as viewed
- POST /api/feed/stories/{id}/reagir - React to story with emoji
- GET /api/feed/stories/restantes - Return daily limit
- 429 limit enforcement (1 story/day)
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


class TestStoriesFeature:
    """Stories feature tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def get_auth_token(self, email, password):
        """Get authentication token"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json().get("token"), response.json().get("user", {}).get("id")
        return None, None
    
    def test_01_get_stories_list(self):
        """Test GET /api/feed/stories - List active stories"""
        token, user_id = self.get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token is not None, "Failed to get admin token"
        
        response = self.session.get(
            f"{BASE_URL}/api/feed/stories",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert "autores" in data, "Response should have 'autores' field"
        assert "total" in data, "Response should have 'total' field"
        assert isinstance(data["autores"], list), "'autores' should be a list"
        
        # Verify author structure if there are stories
        if len(data["autores"]) > 0:
            autor = data["autores"][0]
            assert "autor_id" in autor, "Author should have 'autor_id'"
            assert "autor_nome" in autor, "Author should have 'autor_nome'"
            assert "stories" in autor, "Author should have 'stories'"
            assert "tem_nao_visto" in autor, "Author should have 'tem_nao_visto'"
            
            # Verify story structure
            if len(autor["stories"]) > 0:
                story = autor["stories"][0]
                assert "id" in story, "Story should have 'id'"
                assert "imagem_url" in story, "Story should have 'imagem_url'"
                assert "texto" in story, "Story should have 'texto'"
                assert "data_criacao" in story, "Story should have 'data_criacao'"
                assert "visualizacoes" in story, "Story should have 'visualizacoes'"
                assert "reacoes" in story, "Story should have 'reacoes'"
                assert "visto" in story, "Story should have 'visto'"
        
        print(f"✓ Stories list returned {data['total']} stories from {len(data['autores'])} authors")
    
    def test_02_get_stories_restantes_admin(self):
        """Test GET /api/feed/stories/restantes - Check daily limit for admin"""
        token, user_id = self.get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token is not None, "Failed to get admin token"
        
        response = self.session.get(
            f"{BASE_URL}/api/feed/stories/restantes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert "stories_hoje" in data, "Response should have 'stories_hoje'"
        assert "limite_diario" in data, "Response should have 'limite_diario'"
        assert "restantes" in data, "Response should have 'restantes'"
        
        # Verify limit is 1
        assert data["limite_diario"] == 1, f"Daily limit should be 1, got {data['limite_diario']}"
        
        # Verify restantes calculation
        expected_restantes = max(0, data["limite_diario"] - data["stories_hoje"])
        assert data["restantes"] == expected_restantes, f"Restantes calculation incorrect"
        
        print(f"✓ Admin has {data['restantes']} stories remaining today (posted {data['stories_hoje']}/{data['limite_diario']})")
    
    def test_03_get_stories_restantes_atleta(self):
        """Test GET /api/feed/stories/restantes - Check daily limit for atleta"""
        token, user_id = self.get_auth_token(ATLETA_EMAIL, ATLETA_PASSWORD)
        assert token is not None, "Failed to get atleta token"
        
        response = self.session.get(
            f"{BASE_URL}/api/feed/stories/restantes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Atleta already posted 1 story, should have 0 remaining
        assert data["limite_diario"] == 1, f"Daily limit should be 1"
        
        print(f"✓ Atleta has {data['restantes']} stories remaining today (posted {data['stories_hoje']}/{data['limite_diario']})")
    
    def test_04_create_story_limit_enforcement(self):
        """Test POST /api/feed/stories - Verify 429 when limit reached"""
        token, user_id = self.get_auth_token(ATLETA_EMAIL, ATLETA_PASSWORD)
        assert token is not None, "Failed to get atleta token"
        
        # Create a test image
        from PIL import Image
        import io
        img = Image.new("RGB", (400, 700), "blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Atleta already posted 1 story, second attempt should fail with 429
        response = requests.post(
            f"{BASE_URL}/api/feed/stories",
            headers={"Authorization": f"Bearer {token}"},
            files={"foto": ("test.jpg", img_bytes, "image/jpeg")},
            data={"texto": "Segunda tentativa"}
        )
        
        assert response.status_code == 429, f"Expected 429 (limit reached), got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Response should have error detail"
        assert "amanhã" in data["detail"].lower() or "hoje" in data["detail"].lower(), "Error should mention daily limit"
        
        print(f"✓ 429 limit enforcement working: {data['detail']}")
    
    def test_05_visualizar_story(self):
        """Test POST /api/feed/stories/{id}/visualizar - Mark story as viewed"""
        # Get admin token to find a story
        admin_token, admin_id = self.get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert admin_token is not None, "Failed to get admin token"
        
        # Get stories list
        response = self.session.get(
            f"{BASE_URL}/api/feed/stories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find a story to view
        story_id = None
        for autor in data["autores"]:
            if len(autor["stories"]) > 0:
                story_id = autor["stories"][0]["id"]
                break
        
        if story_id is None:
            pytest.skip("No stories available to test visualization")
        
        # Get atleta token to view the story
        atleta_token, atleta_id = self.get_auth_token(ATLETA_EMAIL, ATLETA_PASSWORD)
        assert atleta_token is not None, "Failed to get atleta token"
        
        # Mark story as viewed
        response = self.session.post(
            f"{BASE_URL}/api/feed/stories/{story_id}/visualizar",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=true"
        
        print(f"✓ Story {story_id} marked as viewed")
    
    def test_06_reagir_story(self):
        """Test POST /api/feed/stories/{id}/reagir - React to story with emoji"""
        # Get admin token to find a story
        admin_token, admin_id = self.get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert admin_token is not None, "Failed to get admin token"
        
        # Get stories list
        response = self.session.get(
            f"{BASE_URL}/api/feed/stories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find a story to react to
        story_id = None
        for autor in data["autores"]:
            if len(autor["stories"]) > 0:
                story_id = autor["stories"][0]["id"]
                break
        
        if story_id is None:
            pytest.skip("No stories available to test reaction")
        
        # Get atleta token to react
        atleta_token, atleta_id = self.get_auth_token(ATLETA_EMAIL, ATLETA_PASSWORD)
        assert atleta_token is not None, "Failed to get atleta token"
        
        # React with fogo emoji
        response = self.session.post(
            f"{BASE_URL}/api/feed/stories/{story_id}/reagir",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={"tipo_reacao": "fogo"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("ok") == True, "Response should have ok=true"
        assert "emoji" in data, "Response should have emoji"
        assert data["emoji"] == "🔥", f"Expected 🔥 emoji, got {data['emoji']}"
        
        print(f"✓ Reacted to story {story_id} with 🔥")
    
    def test_07_reagir_story_invalid_reaction(self):
        """Test POST /api/feed/stories/{id}/reagir - Invalid reaction type"""
        admin_token, admin_id = self.get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert admin_token is not None, "Failed to get admin token"
        
        # Get stories list
        response = self.session.get(
            f"{BASE_URL}/api/feed/stories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find a story
        story_id = None
        for autor in data["autores"]:
            if len(autor["stories"]) > 0:
                story_id = autor["stories"][0]["id"]
                break
        
        if story_id is None:
            pytest.skip("No stories available to test")
        
        # Try invalid reaction
        response = self.session.post(
            f"{BASE_URL}/api/feed/stories/{story_id}/reagir",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"tipo_reacao": "invalid_reaction"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid reaction, got {response.status_code}"
        
        print(f"✓ Invalid reaction correctly rejected with 400")
    
    def test_08_visualizar_nonexistent_story(self):
        """Test POST /api/feed/stories/{id}/visualizar - Non-existent story"""
        token, user_id = self.get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token is not None, "Failed to get token"
        
        response = self.session.post(
            f"{BASE_URL}/api/feed/stories/nonexistent-story-id/visualizar",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404, f"Expected 404 for non-existent story, got {response.status_code}"
        
        print(f"✓ Non-existent story correctly returns 404")
    
    def test_09_stories_grouped_by_author(self):
        """Test that stories are correctly grouped by author"""
        token, user_id = self.get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token is not None, "Failed to get token"
        
        response = self.session.get(
            f"{BASE_URL}/api/feed/stories",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify each author has unique autor_id
        autor_ids = [a["autor_id"] for a in data["autores"]]
        assert len(autor_ids) == len(set(autor_ids)), "Author IDs should be unique (stories grouped by author)"
        
        # Verify each author's stories belong to that author
        for autor in data["autores"]:
            for story in autor["stories"]:
                assert story["autor_id"] == autor["autor_id"], f"Story autor_id should match author's autor_id"
        
        print(f"✓ Stories correctly grouped by {len(autor_ids)} unique authors")
    
    def test_10_stories_sorted_unseen_first(self):
        """Test that unseen stories appear before seen stories"""
        token, user_id = self.get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token is not None, "Failed to get token"
        
        response = self.session.get(
            f"{BASE_URL}/api/feed/stories",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check ordering: tem_nao_visto=True should come before tem_nao_visto=False
        seen_unseen = False
        for autor in data["autores"]:
            if not autor["tem_nao_visto"]:
                seen_unseen = True
            elif seen_unseen:
                # If we've seen a "seen" author and now see an "unseen" one, ordering is wrong
                pytest.fail("Unseen stories should appear before seen stories")
        
        print(f"✓ Stories correctly sorted (unseen first)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
