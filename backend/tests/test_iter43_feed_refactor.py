# /app/backend/tests/test_iter43_feed_refactor.py
# Testing Feed Social (only likes, no comments), Liga Assessorias and Ranking Corridas routes
# Iteration 43: Verify comments functionality removed, new modules refactored

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable is required")

# Test credentials
TEST_USER_EMAIL = "admin@runpro.com"
TEST_USER_PASSWORD = "admin123"


class TestAuthentication:
    """Test authentication for getting token"""
    
    def test_login_success(self):
        """Verify login works with test credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # API returns 'token' not 'access_token'
        assert "token" in data, "Missing token in response"
        return data["token"]


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for authenticated tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get auth headers with bearer token"""
    return {"Authorization": f"Bearer {auth_token}"}


# ============================================================
# FEED SOCIAL TESTS - Only Likes, No Comments
# ============================================================

class TestFeedSocial:
    """Test Feed Social endpoints (comments removed, only likes)"""
    
    def test_get_feed_requires_auth(self):
        """GET /api/feed requires authentication"""
        response = requests.get(f"{BASE_URL}/api/feed")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_get_feed_with_auth(self, auth_headers):
        """GET /api/feed returns feed posts when authenticated"""
        response = requests.get(f"{BASE_URL}/api/feed", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "posts" in data, "Missing 'posts' in response"
        assert "pagina" in data, "Missing 'pagina' in response"
        assert "total" in data, "Missing 'total' in response"
        assert isinstance(data["posts"], list), "Posts should be a list"
    
    def test_create_post_requires_auth(self):
        """POST /api/feed/posts requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": "Test post", "tipo": "texto"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_create_post_with_auth(self, auth_headers):
        """POST /api/feed/posts creates a new post"""
        unique_text = f"Test post from pytest - {uuid.uuid4()}"
        response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": unique_text, "tipo": "texto"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "post_id" in data, "Missing 'post_id' in response"
        assert data.get("message") == "Post criado com sucesso!", f"Wrong message: {data.get('message')}"
        return data["post_id"]
    
    def test_create_post_empty_text_fails(self, auth_headers):
        """POST /api/feed/posts with empty text should fail"""
        response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": "   ", "tipo": "texto"},
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_like_post(self, auth_headers):
        """POST /api/feed/posts/{post_id}/curtir toggles like"""
        # First create a post
        unique_text = f"Test post for like - {uuid.uuid4()}"
        create_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": unique_text, "tipo": "texto"},
            headers=auth_headers
        )
        assert create_response.status_code == 200
        post_id = create_response.json()["post_id"]
        
        # Like the post
        like_response = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/curtir",
            headers=auth_headers
        )
        assert like_response.status_code == 200, f"Like failed: {like_response.text}"
        like_data = like_response.json()
        assert "curtido" in like_data, "Missing 'curtido' in response"
        assert like_data["curtido"] == True, "Expected curtido=True after first like"
        
        # Unlike the post (toggle)
        unlike_response = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/curtir",
            headers=auth_headers
        )
        assert unlike_response.status_code == 200, f"Unlike failed: {unlike_response.text}"
        unlike_data = unlike_response.json()
        assert unlike_data["curtido"] == False, "Expected curtido=False after toggle"
    
    def test_like_nonexistent_post_fails(self, auth_headers):
        """POST /api/feed/posts/{post_id}/curtir with nonexistent post should fail"""
        fake_id = str(uuid.uuid4())
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{fake_id}/curtir",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_get_trending(self, auth_headers):
        """GET /api/feed/trending returns trending posts"""
        response = requests.get(f"{BASE_URL}/api/feed/trending", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "trending" in data, "Missing 'trending' in response"
        assert isinstance(data["trending"], list), "Trending should be a list"
    
    def test_get_trending_with_limit(self, auth_headers):
        """GET /api/feed/trending?limite=5 respects limit parameter"""
        response = requests.get(f"{BASE_URL}/api/feed/trending?limite=5", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert len(data.get("trending", [])) <= 5, "Should return at most 5 posts"
    
    def test_comments_endpoint_not_exist(self, auth_headers):
        """Verify comment endpoints do NOT exist (comments removed)"""
        # Create a post first
        create_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"Test comment removal - {uuid.uuid4()}", "tipo": "texto"},
            headers=auth_headers
        )
        post_id = create_response.json().get("post_id", "test-id")
        
        # Try to create a comment - should NOT exist
        comment_response = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/comentarios",
            json={"texto": "Test comment"},
            headers=auth_headers
        )
        # Endpoint should not exist (404) or method not allowed (405)
        assert comment_response.status_code in [404, 405, 422], \
            f"Comment endpoint should not exist. Got {comment_response.status_code}: {comment_response.text}"
    
    def test_get_comments_endpoint_not_exist(self, auth_headers):
        """Verify GET comments endpoint does NOT exist"""
        response = requests.get(
            f"{BASE_URL}/api/feed/posts/test-id/comentarios",
            headers=auth_headers
        )
        assert response.status_code in [404, 405, 422], \
            f"GET comments endpoint should not exist. Got {response.status_code}"


# ============================================================
# LIGA ASSESSORIAS TESTS - Refactored Module
# ============================================================

class TestLigaAssessorias:
    """Test Liga Assessorias endpoints (refactored module)"""
    
    def test_get_estados_com_assessorias(self):
        """GET /api/liga-assessorias/estados returns list of states"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/estados")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Should return a list of states"
        # States should be strings
        for estado in data:
            assert isinstance(estado, str), f"State should be string, got {type(estado)}"
    
    def test_get_cidades_com_assessorias(self):
        """GET /api/liga-assessorias/cidades returns list of cities"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/cidades")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Should return a list of cities"
    
    def test_get_cidades_with_estado_filter(self):
        """GET /api/liga-assessorias/cidades?estado=SP filters by state"""
        # First get available states
        states_response = requests.get(f"{BASE_URL}/api/liga-assessorias/estados")
        if states_response.status_code == 200 and states_response.json():
            first_state = states_response.json()[0]
            response = requests.get(f"{BASE_URL}/api/liga-assessorias/cidades?estado={first_state}")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            # Should still be a list
            data = response.json()
            assert isinstance(data, list), "Should return a list"
        else:
            pytest.skip("No states available for filtering test")


# ============================================================
# RANKING CORRIDAS TESTS - Refactored Module
# ============================================================

class TestRankingCorridas:
    """Test Ranking Corridas endpoints (refactored module)"""
    
    def test_get_ranking_corridas(self):
        """GET /api/ranking-corridas returns ranking data"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "tipo" in data, "Missing 'tipo' in response"
        assert "total_corridas" in data, "Missing 'total_corridas' in response"
        assert "ranking" in data, "Missing 'ranking' in response"
        assert isinstance(data["ranking"], list), "Ranking should be a list"
    
    def test_get_ranking_corridas_nacional(self):
        """GET /api/ranking-corridas?tipo=nacional returns national ranking"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas?tipo=nacional")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("tipo") == "nacional", f"Expected tipo=nacional, got {data.get('tipo')}"
    
    def test_get_ranking_corridas_estadual(self):
        """GET /api/ranking-corridas?tipo=estadual&estado=SP filters by state"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas?tipo=estadual&estado=SP")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("tipo") == "estadual", f"Expected tipo=estadual, got {data.get('tipo')}"
    
    def test_get_ranking_corridas_stats(self):
        """GET /api/ranking-corridas/stats returns statistics"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Check for expected fields - API might use different field names
        assert "total_avaliacoes" in data, "Missing 'total_avaliacoes' in response"
        # Check for corridas count - might be total_corridas or similar
        has_corrida_stats = "total_corridas" in data or "total_avaliadores" in data or "melhor_avaliada" in data
        assert has_corrida_stats, f"Missing corrida stats in response: {data.keys()}"
    
    def test_get_estados_com_corridas(self):
        """GET /api/ranking-corridas/estados returns states with races"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/estados")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "estados" in data, "Missing 'estados' in response"
        assert isinstance(data["estados"], list), "Estados should be a list"
    
    def test_get_cidades_com_corridas(self):
        """GET /api/ranking-corridas/cidades returns cities with races"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/cidades")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "cidades" in data, "Missing 'cidades' in response"
        assert isinstance(data["cidades"], list), "Cidades should be a list"
    
    def test_get_cidades_with_estado_filter(self):
        """GET /api/ranking-corridas/cidades?estado=SP filters by state"""
        # First get available states
        states_response = requests.get(f"{BASE_URL}/api/ranking-corridas/estados")
        if states_response.status_code == 200:
            data = states_response.json()
            if data.get("estados"):
                first_state = data["estados"][0]
                response = requests.get(f"{BASE_URL}/api/ranking-corridas/cidades?estado={first_state}")
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            else:
                pytest.skip("No states available for filtering test")
        else:
            pytest.skip("Could not get states list")


# ============================================================
# CODE REVIEW VERIFICATION - Feed without Comments
# ============================================================

class TestFeedCodeReview:
    """Verify feed implementation doesn't have comment references"""
    
    def test_feed_posts_have_likes_count(self, auth_headers):
        """Verify feed posts include total_curtidas field"""
        response = requests.get(f"{BASE_URL}/api/feed", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            for post in data.get("posts", [])[:3]:  # Check first 3 posts
                assert "total_curtidas" in post, f"Post missing 'total_curtidas': {post.keys()}"
                assert "curtido" in post, f"Post missing 'curtido': {post.keys()}"
    
    def test_trending_posts_have_likes_count(self, auth_headers):
        """Verify trending posts include engagement metrics (only likes)"""
        response = requests.get(f"{BASE_URL}/api/feed/trending", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            for post in data.get("trending", [])[:3]:  # Check first 3 posts
                assert "total_curtidas" in post, f"Trending post missing 'total_curtidas'"
                assert "engajamento" in post, f"Trending post missing 'engajamento'"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
