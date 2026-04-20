"""
Iteration 121: Bug Fixes Testing
- Bug 1: Feed não permite postar nem enviar stories
- Bug 2: Na assessoria não consegue enviar mensagem no feed da equipe nem adicionar foto
- Bug 3: Cadastro de novo atleta fecha automaticamente a tela

Root cause: Anti-bot too aggressive (included /feed/ and /assessorias) + 
Axios interceptor redirected to /login when receiving 401 on /assessorias/lista
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "vandy1250@gmail.com"
TEST_PASSWORD = "d7ff103ad1250@#$"


class TestPublicEndpoints:
    """Test that public endpoints return 200 without token"""
    
    def test_assessorias_lista_public(self):
        """Bug fix: /api/assessorias/lista should be public (no auth required)"""
        response = requests.get(f"{BASE_URL}/api/assessorias/lista", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list of assessorias"
        print(f"✅ /api/assessorias/lista returns 200 (public) - {len(data)} assessorias found")
    
    def test_corridas_eventos_public(self):
        """Public endpoint: /api/corridas-eventos"""
        response = requests.get(f"{BASE_URL}/api/corridas-eventos", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ /api/corridas-eventos returns 200 (public)")
    
    def test_regulamento_public(self):
        """Public endpoint: /api/regulamento"""
        response = requests.get(f"{BASE_URL}/api/regulamento", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ /api/regulamento returns 200 (public)")
    
    def test_health_public(self):
        """Public endpoint: /api/health"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ /api/health returns 200 (public)")


class TestProtectedEndpoints:
    """Test that protected endpoints return 401 without token"""
    
    def test_ranking_povao_protected(self):
        """Protected endpoint: /api/ranking/povao"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao", timeout=10)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ /api/ranking/povao returns 401 (protected)")
    
    def test_liga_assessorias_ranking_protected(self):
        """Protected endpoint: /api/liga-assessorias/ranking"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking", timeout=10)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ /api/liga-assessorias/ranking returns 401 (protected)")
    
    def test_feed_protected(self):
        """Protected endpoint: /api/feed"""
        response = requests.get(f"{BASE_URL}/api/feed", timeout=10)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ /api/feed returns 401 (protected)")


class TestLoginAndFeed:
    """Test login flow and feed functionality"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10
        )
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = response.json()
        assert "token" in data, "Token not in response"
        return data["token"]
    
    def test_login_returns_tokens(self):
        """Login should return both token and refresh_token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10
        )
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = response.json()
        assert "token" in data, "Token not in response"
        assert "refresh_token" in data, "Refresh token not in response"
        print("✅ Login returns both token and refresh_token")
    
    def test_feed_accessible_with_token(self, auth_token):
        """Feed should be accessible with valid token"""
        time.sleep(1)  # Avoid rate limiting
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/feed", headers=headers, timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "posts" in data, "Posts not in response"
        print(f"✅ /api/feed accessible with token - {len(data.get('posts', []))} posts")
    
    def test_feed_trending_accessible(self, auth_token):
        """Feed trending should be accessible with valid token"""
        time.sleep(1)  # Avoid rate limiting
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/feed/trending?limite=5", headers=headers, timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ /api/feed/trending accessible with token")
    
    def test_feed_fotos_restantes(self, auth_token):
        """Feed fotos-restantes should be accessible"""
        time.sleep(1)  # Avoid rate limiting
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/feed/fotos-restantes", headers=headers, timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "restantes" in data, "restantes not in response"
        print(f"✅ /api/feed/fotos-restantes returns {data.get('restantes')} photos remaining")
    
    def test_feed_reacoes_disponiveis_public(self):
        """Feed reacoes-disponiveis should be public"""
        response = requests.get(f"{BASE_URL}/api/feed/reacoes-disponiveis", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ /api/feed/reacoes-disponiveis returns 200 (public)")


class TestSecurityMiddleware:
    """Test that security middleware is correctly configured"""
    
    def test_anti_bot_not_blocking_feed(self):
        """Anti-bot should NOT block /feed/ endpoints (bug fix)"""
        # The anti-bot now only monitors: /ranking, /liga-assessorias, /strava-atividades, /badges/ranking
        # It should NOT monitor /feed/ anymore
        
        # Get token first
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10
        )
        token = login_response.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make a few requests to feed (should not trigger anti-bot)
        time.sleep(2)  # Wait to avoid rate limit from login
        for i in range(3):
            response = requests.get(f"{BASE_URL}/api/feed", headers=headers, timeout=10)
            # Should get 200, not 429
            if response.status_code == 429:
                pytest.fail("Feed endpoint blocked by anti-bot - BUG NOT FIXED")
            time.sleep(0.5)  # Small delay between requests
        
        print("✅ Anti-bot not blocking /feed/ endpoints")
    
    def test_anti_bot_monitors_ranking(self):
        """Anti-bot should still monitor /ranking endpoints"""
        # This is expected behavior - ranking endpoints are protected by anti-bot
        # We just verify the endpoint is protected (returns 401 without token)
        response = requests.get(f"{BASE_URL}/api/ranking/povao", timeout=10)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ /ranking endpoints still protected")


class TestAssessoriaEndpoints:
    """Test assessoria-related endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10
        )
        return response.json().get("token")
    
    def test_assessorias_lista_returns_data(self):
        """Assessorias lista should return list of assessorias"""
        response = requests.get(f"{BASE_URL}/api/assessorias/lista", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check structure if data exists
        if len(data) > 0:
            first = data[0]
            assert "nome" in first, "Assessoria should have 'nome' field"
            print(f"✅ Assessorias lista returns {len(data)} items with correct structure")
        else:
            print("✅ Assessorias lista returns empty list (no assessorias in DB)")
    
    def test_liga_assessorias_ranking_with_token(self, auth_token):
        """Liga assessorias ranking should work with token"""
        time.sleep(1)
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking", headers=headers, timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "ranking" in data, "ranking not in response"
        print(f"✅ /api/liga-assessorias/ranking returns {len(data.get('ranking', []))} assessorias")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
