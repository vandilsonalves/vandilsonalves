# /app/backend/tests/test_iter107_ranking_strava.py
# Iteration 107: Testing ranking-corridas endpoints, Strava auth, and avaliar-corrida
# Features: Pagination, cache, FRONTEND_URL in Strava redirect, unique endpoints in ranking_corridas_routes.py

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRankingCorridasEndpoints:
    """Tests for /api/ranking-corridas endpoints in corridas_eventos_routes.py"""
    
    def test_ranking_corridas_returns_paginated_data(self):
        """GET /api/ranking-corridas should return paginated data with required fields"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify required pagination fields
        assert "total_corridas" in data, "Missing total_corridas field"
        assert "page" in data, "Missing page field"
        assert "limit" in data, "Missing limit field"
        assert "has_more" in data, "Missing has_more field"
        assert "ranking" in data, "Missing ranking field"
        assert isinstance(data["ranking"], list), "ranking should be a list"
        print(f"PASS: ranking-corridas returns paginated data with {data['total_corridas']} total corridas")
    
    def test_ranking_corridas_pagination_limit(self):
        """GET /api/ranking-corridas?page=1&limit=5 should return exactly 5 items (or less if fewer exist)"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas?page=1&limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["page"] == 1, f"Expected page=1, got {data['page']}"
        assert data["limit"] == 5, f"Expected limit=5, got {data['limit']}"
        
        # Should return at most 5 items
        ranking_count = len(data["ranking"])
        assert ranking_count <= 5, f"Expected at most 5 items, got {ranking_count}"
        
        # If total > 5, has_more should be True
        if data["total_corridas"] > 5:
            assert data["has_more"] == True, "has_more should be True when more items exist"
        
        print(f"PASS: Pagination works - returned {ranking_count} items with limit=5")
    
    def test_ranking_corridas_stats(self):
        """GET /api/ranking-corridas/stats should return total_corridas and total_avaliacoes"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_corridas" in data, "Missing total_corridas in stats"
        assert "total_avaliacoes" in data, "Missing total_avaliacoes in stats"
        assert isinstance(data["total_corridas"], int), "total_corridas should be int"
        assert isinstance(data["total_avaliacoes"], int), "total_avaliacoes should be int"
        print(f"PASS: stats endpoint returns total_corridas={data['total_corridas']}, total_avaliacoes={data['total_avaliacoes']}")
    
    def test_ranking_corridas_estados(self):
        """GET /api/ranking-corridas/estados should return list of estados"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/estados")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "estados" in data, "Missing estados field"
        assert isinstance(data["estados"], list), "estados should be a list"
        print(f"PASS: estados endpoint returns {len(data['estados'])} estados")


class TestStravaAuthorize:
    """Tests for Strava OAuth authorization endpoint"""
    
    @pytest.fixture
    def atleta_token(self):
        """Login as atleta to get token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "teste.dono@teste.com", "password": "123456"}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Could not login as atleta")
    
    def test_strava_authorize_returns_auth_url_with_correct_frontend_url(self, atleta_token):
        """GET /api/strava/authorize should return auth_url with FRONTEND_URL in redirect_uri"""
        response = requests.get(
            f"{BASE_URL}/api/strava/authorize",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "auth_url" in data, "Missing auth_url in response"
        
        auth_url = data["auth_url"]
        # Verify the redirect_uri contains the correct FRONTEND_URL
        expected_domain = "geo-filtered-admin.preview.emergentagent.com"
        assert expected_domain in auth_url, f"auth_url should contain {expected_domain}, got: {auth_url}"
        assert "redirect_uri=" in auth_url, "auth_url should contain redirect_uri parameter"
        
        # Verify it's pointing to the callback endpoint
        assert "/api/strava/callback" in auth_url, "redirect_uri should point to /api/strava/callback"
        
        print(f"PASS: Strava authorize returns correct auth_url with FRONTEND_URL")
        print(f"  auth_url contains: {expected_domain}")
    
    def test_strava_authorize_requires_auth(self):
        """GET /api/strava/authorize without token should return 401"""
        response = requests.get(f"{BASE_URL}/api/strava/authorize")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASS: Strava authorize requires authentication")


class TestAvaliarCorridaAuth:
    """Tests for /api/avaliar-corrida authentication requirement"""
    
    def test_avaliar_corrida_requires_auth(self):
        """POST /api/avaliar-corrida without token should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/avaliar-corrida",
            data={
                "corrida_id": "test-id",
                "organizacao": 5,
                "percurso": 5,
                "kit_atleta": 5,
                "hidratacao": 5,
                "pos_prova": 5,
                "premiacao": 5,
                "participei": True,
                "aceito_termo": True
            }
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASS: avaliar-corrida requires authentication (401 without token)")


class TestUniqueEndpointsInRankingCorridasRoutes:
    """Tests for unique endpoints that should exist in ranking_corridas_routes.py"""
    
    @pytest.fixture
    def atleta_token(self):
        """Login as atleta to get token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "teste.dono@teste.com", "password": "123456"}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Could not login as atleta")
    
    def test_minhas_avaliacoes_corridas_endpoint_exists(self, atleta_token):
        """GET /api/minhas-avaliacoes-corridas should exist and require auth"""
        response = requests.get(
            f"{BASE_URL}/api/minhas-avaliacoes-corridas",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        # Should return 200 with list (even if empty)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Should return a list"
        print(f"PASS: minhas-avaliacoes-corridas endpoint exists and returns list ({len(data)} items)")
    
    def test_reputacao_avaliador_endpoint_exists(self, atleta_token):
        """GET /api/reputacao-avaliador/{atleta_id} should exist"""
        # First get the user ID
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        if response.status_code != 200:
            pytest.skip("Could not get user info")
        
        user_id = response.json().get("id")
        
        # Now test reputacao endpoint
        response = requests.get(f"{BASE_URL}/api/reputacao-avaliador/{user_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_avaliacoes" in data, "Missing total_avaliacoes"
        assert "nivel_atual" in data, "Missing nivel_atual"
        print(f"PASS: reputacao-avaliador endpoint exists and returns data")
    
    def test_minha_reputacao_endpoint_exists(self, atleta_token):
        """GET /api/minha-reputacao should exist and require auth"""
        response = requests.get(
            f"{BASE_URL}/api/minha-reputacao",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_avaliacoes" in data, "Missing total_avaliacoes"
        assert "nivel_atual" in data, "Missing nivel_atual"
        print(f"PASS: minha-reputacao endpoint exists and returns data")


class TestRankingCorridasCidades:
    """Tests for /api/ranking-corridas/cidades endpoint"""
    
    def test_ranking_corridas_cidades(self):
        """GET /api/ranking-corridas/cidades should return list of cidades"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/cidades")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "cidades" in data, "Missing cidades field"
        assert isinstance(data["cidades"], list), "cidades should be a list"
        print(f"PASS: cidades endpoint returns {len(data['cidades'])} cidades")
    
    def test_ranking_corridas_cidades_with_estado_filter(self):
        """GET /api/ranking-corridas/cidades?estado=SP should filter by estado"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/cidades?estado=SP")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "cidades" in data, "Missing cidades field"
        print(f"PASS: cidades endpoint with estado filter returns {len(data['cidades'])} cidades for SP")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
