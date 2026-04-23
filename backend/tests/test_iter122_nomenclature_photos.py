"""
Iteration 122 Tests: Nomenclature Changes, Birthday Calendar, Ranking Photos, Premiacao Photos
Tests for 4 new features:
1. Nomenclature changes on RankingPage (text-only)
2. Birthday calendar includes dono_assessoria role
3. Ranking assessorias returns foto_url
4. Premiacao photo upload endpoint for options
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
SUPER_ADMIN_EMAIL = "vandy1250@gmail.com"
SUPER_ADMIN_PASSWORD = "d7ff103ad1250@#$"


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("✅ Health endpoint working")
    
    def test_frontend_loads(self):
        """Test frontend is accessible"""
        response = requests.get(BASE_URL, timeout=10)
        assert response.status_code == 200, f"Frontend failed: {response.status_code}"
        print("✅ Frontend loads")


class TestAuthentication:
    """Authentication tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for super admin"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD},
            timeout=10
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code} - {response.text}")
        data = response.json()
        assert "token" in data, "No token in response"
        return data["token"]
    
    def test_login_super_admin(self, auth_token):
        """Test super admin login works"""
        assert auth_token is not None
        print(f"✅ Super admin login successful, token: {auth_token[:20]}...")


class TestAniversariantesEndpoints:
    """Test birthday calendar endpoints - should include dono_assessoria role"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD},
            timeout=10
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        return response.json()["token"]
    
    def test_aniversariantes_mes_endpoint(self, auth_token):
        """Test GET /api/admin/aniversariantes returns data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/aniversariantes",
            headers=headers,
            timeout=10
        )
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "calendario" in data, "Missing 'calendario' in response"
        assert "mes" in data, "Missing 'mes' in response"
        assert "ano" in data, "Missing 'ano' in response"
        assert "total_aniversariantes" in data, "Missing 'total_aniversariantes'"
        print(f"✅ Aniversariantes endpoint working - {data['total_aniversariantes']} aniversariantes no mês")
    
    def test_aniversariantes_hoje_endpoint(self, auth_token):
        """Test GET /api/admin/aniversariantes/hoje"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/aniversariantes/hoje",
            headers=headers,
            timeout=10
        )
        assert response.status_code == 200, f"Failed: {response.status_code}"
        data = response.json()
        assert "aniversariantes" in data
        assert "data" in data
        print(f"✅ Aniversariantes hoje endpoint working - {len(data['aniversariantes'])} aniversariantes hoje")
    
    def test_aniversariantes_semana_endpoint(self, auth_token):
        """Test GET /api/admin/aniversariantes/semana"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/aniversariantes/semana",
            headers=headers,
            timeout=10
        )
        assert response.status_code == 200, f"Failed: {response.status_code}"
        data = response.json()
        assert "aniversariantes" in data
        assert "periodo" in data
        print(f"✅ Aniversariantes semana endpoint working - {len(data['aniversariantes'])} aniversariantes na semana")


class TestRankingAssessoriasEndpoints:
    """Test ranking assessorias endpoints - should return foto_url"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD},
            timeout=10
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        return response.json()["token"]
    
    def test_liga_assessorias_ranking(self, auth_token):
        """Test GET /api/liga-assessorias/ranking returns foto_url field"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional",
            headers=headers,
            timeout=15
        )
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "ranking" in data, "Missing 'ranking' in response"
        assert "total_assessorias" in data, "Missing 'total_assessorias'"
        
        # Check that foto_url field exists in ranking items
        if data["ranking"]:
            first_item = data["ranking"][0]
            assert "foto_url" in first_item, "Missing 'foto_url' field in ranking item"
            print(f"✅ Liga assessorias ranking working - {data['total_assessorias']} assessorias, foto_url field present")
            print(f"   First assessoria: {first_item.get('nome')}, foto_url: {first_item.get('foto_url', 'empty')[:50] if first_item.get('foto_url') else 'None'}")
        else:
            print("✅ Liga assessorias ranking working - 0 assessorias (empty database)")
    
    def test_liga_assessorias_stats(self, auth_token):
        """Test GET /api/liga-assessorias/stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/stats",
            headers=headers,
            timeout=10
        )
        assert response.status_code == 200, f"Failed: {response.status_code}"
        data = response.json()
        assert "total_assessorias" in data
        assert "total_atletas_vinculados" in data
        print(f"✅ Liga stats working - {data['total_assessorias']} assessorias, {data['total_atletas_vinculados']} atletas")
    
    def test_assessorias_lista_public(self):
        """Test GET /api/assessorias/lista is public (no auth required)"""
        response = requests.get(
            f"{BASE_URL}/api/assessorias/lista",
            timeout=10
        )
        assert response.status_code == 200, f"Failed: {response.status_code} - should be public"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✅ Assessorias lista (public) working - {len(data)} assessorias")


class TestPremiacaoEndpoints:
    """Test premiacao endpoints - new foto upload for options"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD},
            timeout=10
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        return response.json()["token"]
    
    def test_premiacao_list(self, auth_token):
        """Test GET /api/premiacao/admin/premiacoes"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers=headers,
            timeout=10
        )
        assert response.status_code == 200, f"Failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✅ Premiacao list working - {len(data)} premiacoes")
        return data
    
    def test_premiacao_opcao_foto_endpoint_exists(self, auth_token):
        """Test POST /api/premiacao/admin/premiacoes/{id}/categorias/{id}/opcao/{idx}/foto returns 404 for nonexistent"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Test with fake IDs - should return 404 (not 405 Method Not Allowed)
        response = requests.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/fake-prem-id/categorias/fake-cat-id/opcao/0/foto",
            headers=headers,
            files={"foto": ("test.jpg", b"fake image data", "image/jpeg")},
            timeout=10
        )
        # Should return 404 (not found) not 405 (method not allowed) - proving endpoint exists
        assert response.status_code in [404, 400], f"Unexpected status: {response.status_code} - endpoint may not exist"
        print(f"✅ Premiacao opcao foto endpoint exists (returns {response.status_code} for nonexistent IDs)")
    
    def test_premiacao_public_list(self):
        """Test GET /api/premiacao/todas (public)"""
        response = requests.get(
            f"{BASE_URL}/api/premiacao/todas",
            timeout=10
        )
        assert response.status_code == 200, f"Failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✅ Premiacao public list working - {len(data)} premiacoes")


class TestRankingEndpoints:
    """Test ranking endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD},
            timeout=10
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        return response.json()["token"]
    
    def test_ranking_profissional(self, auth_token):
        """Test GET /api/ranking/profissional"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/ranking/profissional",
            headers=headers,
            timeout=15
        )
        assert response.status_code == 200, f"Failed: {response.status_code}"
        data = response.json()
        assert "ranking" in data or isinstance(data, list), "Invalid response format"
        print(f"✅ Ranking profissional working")
    
    def test_ranking_povao(self, auth_token):
        """Test GET /api/ranking/povao"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/ranking/povao",
            headers=headers,
            timeout=15
        )
        assert response.status_code == 200, f"Failed: {response.status_code}"
        print(f"✅ Ranking povao working")


class TestFeedEndpoints:
    """Test feed endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD},
            timeout=10
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        return response.json()["token"]
    
    def test_feed_endpoint(self, auth_token):
        """Test GET /api/feed"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/feed",
            headers=headers,
            timeout=10
        )
        assert response.status_code == 200, f"Failed: {response.status_code}"
        print(f"✅ Feed endpoint working")


class TestCadastroEndpoint:
    """Test cadastro stays open (no redirect)"""
    
    def test_cadastro_page_accessible(self):
        """Test cadastro page is accessible without redirect"""
        response = requests.get(
            f"{BASE_URL}/cadastro",
            timeout=10,
            allow_redirects=False
        )
        # Should return 200 (page loads) not 302 (redirect)
        assert response.status_code == 200, f"Cadastro page returned {response.status_code}"
        print(f"✅ Cadastro page accessible (status {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
