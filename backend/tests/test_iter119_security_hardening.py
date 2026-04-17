# /app/backend/tests/test_iter119_security_hardening.py
# Security Hardening Tests - Anti-scraping, JWT protection, parameter validation
# Iteration 119: Testing security middleware and protected routes

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
SUPER_ADMIN_EMAIL = "vandy1250@gmail.com"
SUPER_ADMIN_PASSWORD = "d7ff103ad1250@#$"


class TestAuthentication:
    """Test login and token generation"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for protected routes"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    
    def test_login_success(self):
        """Test login with valid credentials returns 200 and token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Response should contain 'token'"
        assert "user" in data, "Response should contain 'user'"
        assert len(data["token"]) > 0, "Token should not be empty"


class TestProtectedRoutesWithoutToken:
    """Test that protected routes return 401 without token"""
    
    def test_ranking_corridas_requires_auth(self):
        """GET /api/ranking-corridas should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    def test_ranking_avaliadores_requires_auth(self):
        """GET /api/ranking-avaliadores should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/ranking-avaliadores")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    def test_ranking_povao_requires_auth(self):
        """GET /api/ranking/povao should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    def test_corrida_avaliacoes_requires_auth(self):
        """GET /api/corrida-avaliacoes/{id} should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/corrida-avaliacoes/test-id-123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


class TestProtectedRoutesWithToken:
    """Test that protected routes return 200 with valid token"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for protected routes"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    def test_ranking_corridas_with_token(self, auth_token):
        """GET /api/ranking-corridas should return 200 with valid token"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ranking-corridas", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "ranking" in data or "total_corridas" in data, "Response should contain ranking data"
    
    def test_ranking_avaliadores_with_token(self, auth_token):
        """GET /api/ranking-avaliadores should return 200 with valid token"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ranking-avaliadores", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "ranking" in data, "Response should contain 'ranking'"
    
    def test_ranking_povao_with_token(self, auth_token):
        """GET /api/ranking/povao should return 200 with valid token"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ranking/povao", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "ranking" in data, "Response should contain 'ranking'"


class TestPublicRoutes:
    """Test that public routes return 200 without token"""
    
    def test_ranking_corridas_stats_public(self):
        """GET /api/ranking-corridas/stats should be public (200 without token)"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total_corridas" in data or "total_avaliacoes" in data, "Response should contain stats"
    
    def test_ranking_corridas_estados_public(self):
        """GET /api/ranking-corridas/estados should be public (200 without token)"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/estados")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "estados" in data, "Response should contain 'estados'"
    
    def test_corridas_eventos_public(self):
        """GET /api/corridas-eventos should be public (200 without token)"""
        response = requests.get(f"{BASE_URL}/api/corridas-eventos")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        # Response is a list of corridas
        assert isinstance(response.json(), list), "Response should be a list"
    
    def test_temporadas_historico_public(self):
        """GET /api/temporadas/historico should be public (200 without token)"""
        response = requests.get(f"{BASE_URL}/api/temporadas/historico")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_financeiro_config_precos_publico(self):
        """GET /api/financeiro/config-precos-publico should be public (200 without token)"""
        response = requests.get(f"{BASE_URL}/api/financeiro/config-precos-publico")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_auth_login_public(self):
        """POST /api/auth/login should be public (accepts requests without token)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@test.com", "password": "wrong"}
        )
        # Should return 401 for invalid credentials, not 403 for missing token
        assert response.status_code in [401, 400], f"Expected 401/400 for invalid creds, got {response.status_code}"


class TestParameterValidation:
    """Test parameter validation and capping"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for protected routes"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    def test_ranking_povao_page_capped_at_100(self, auth_token):
        """GET /api/ranking/povao?page=999 should cap page at 100"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/ranking/povao?page=999&limit=20",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Page should be capped at 100
        assert data.get("page", 0) <= 100, f"Page should be capped at 100, got {data.get('page')}"
    
    def test_ranking_povao_limit_capped_at_20(self, auth_token):
        """GET /api/ranking/povao?limit=999 should cap limit at 20"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/ranking/povao?page=1&limit=999",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Limit should be capped at 20
        assert data.get("limit", 0) <= 20, f"Limit should be capped at 20, got {data.get('limit')}"
    
    def test_ranking_corridas_page_capped_at_100(self, auth_token):
        """GET /api/ranking-corridas?page=500 should cap page at 100"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/ranking-corridas?page=500&limit=50",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Page should be capped at 100
        assert data.get("page", 0) <= 100, f"Page should be capped at 100, got {data.get('page')}"
    
    def test_ranking_corridas_limit_capped_at_50(self, auth_token):
        """GET /api/ranking-corridas?limit=100 should cap limit at 50"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/ranking-corridas?page=1&limit=100",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Limit should be capped at 50
        assert data.get("limit", 0) <= 50, f"Limit should be capped at 50, got {data.get('limit')}"


class TestSecurityHeaders:
    """Test that security headers are present in responses"""
    
    def test_security_headers_on_api_response(self):
        """API responses should include security headers"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        
        # Check X-Content-Type-Options
        assert "X-Content-Type-Options" in response.headers, "Missing X-Content-Type-Options header"
        assert response.headers["X-Content-Type-Options"] == "nosniff", "X-Content-Type-Options should be 'nosniff'"
        
        # Check X-Frame-Options
        assert "X-Frame-Options" in response.headers, "Missing X-Frame-Options header"
        assert response.headers["X-Frame-Options"] == "DENY", "X-Frame-Options should be 'DENY'"
        
        # Check X-XSS-Protection
        assert "X-XSS-Protection" in response.headers, "Missing X-XSS-Protection header"
        
        # Check Strict-Transport-Security (HSTS)
        assert "Strict-Transport-Security" in response.headers, "Missing Strict-Transport-Security header"
    
    def test_security_headers_on_protected_route(self):
        """Protected routes should also include security headers"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        # Even 401 responses should have security headers
        
        assert "X-Content-Type-Options" in response.headers, "Missing X-Content-Type-Options header on 401"
        assert "X-Frame-Options" in response.headers, "Missing X-Frame-Options header on 401"


class TestRateLimiting:
    """Test that rate limiting doesn't block normal usage"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for protected routes"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    def test_normal_usage_not_blocked(self, auth_token):
        """Normal usage (< 120 req/min) should not be blocked"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Make 10 requests - should all succeed
        success_count = 0
        for i in range(10):
            response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats", headers=headers)
            if response.status_code == 200:
                success_count += 1
        
        assert success_count >= 8, f"At least 8/10 requests should succeed, got {success_count}"
    
    def test_public_endpoint_rate_limit(self):
        """Public endpoints should allow reasonable traffic"""
        # Make 5 requests to public endpoint
        success_count = 0
        for i in range(5):
            response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
            if response.status_code == 200:
                success_count += 1
        
        assert success_count >= 4, f"At least 4/5 requests should succeed, got {success_count}"


class TestHealthEndpoint:
    """Test health endpoint is accessible"""
    
    def test_health_endpoint(self):
        """GET /api/health should return 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
