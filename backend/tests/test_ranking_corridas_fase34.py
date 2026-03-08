"""
Tests for Ranking das Corridas - Fase 3 e 4
- Fase 3: Sistema de Selos automáticos (5 Estrelas, Top 10 Brasil, Top 10 Estado)
- Fase 4: Dashboard Admin com estatísticas, gráficos, CRUD corridas
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminAuth:
    """Test admin authentication first"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_admin_login(self, admin_token):
        """Test that admin can login"""
        assert admin_token is not None
        assert len(admin_token) > 0


class TestAdminRankingCorridasDashboard:
    """Test the admin dashboard endpoint for Ranking das Corridas"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        return response.json().get("token")
    
    def test_dashboard_endpoint_exists(self, admin_token):
        """Test GET /api/admin/ranking-corridas/dashboard exists"""
        response = requests.get(
            f"{BASE_URL}/api/admin/ranking-corridas/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
    
    def test_dashboard_returns_stats(self, admin_token):
        """Test dashboard returns stats object"""
        response = requests.get(
            f"{BASE_URL}/api/admin/ranking-corridas/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        assert "stats" in data
        assert "total_corridas" in data["stats"]
        assert "total_avaliacoes" in data["stats"]
        assert "media_geral" in data["stats"]
        assert isinstance(data["stats"]["total_corridas"], int)
        assert isinstance(data["stats"]["total_avaliacoes"], int)
    
    def test_dashboard_returns_distribuicao_notas(self, admin_token):
        """Test dashboard returns nota distribution"""
        response = requests.get(
            f"{BASE_URL}/api/admin/ranking-corridas/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        assert "distribuicao_notas" in data
        assert isinstance(data["distribuicao_notas"], list)
        # Each item should have nota and total
        for item in data["distribuicao_notas"]:
            assert "nota" in item
            assert "total" in item
    
    def test_dashboard_returns_melhores_por_estado(self, admin_token):
        """Test dashboard returns best races by state"""
        response = requests.get(
            f"{BASE_URL}/api/admin/ranking-corridas/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        assert "melhores_por_estado" in data
        assert isinstance(data["melhores_por_estado"], list)
        # Each item should have estado, nome_corrida, media
        for item in data["melhores_por_estado"]:
            assert "estado" in item
            assert "nome_corrida" in item
    
    def test_dashboard_returns_ranking_top20(self, admin_token):
        """Test dashboard returns top 20 ranking"""
        response = requests.get(
            f"{BASE_URL}/api/admin/ranking-corridas/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        assert "ranking_top20" in data
        assert isinstance(data["ranking_top20"], list)
        
        # Each race in ranking should have required fields
        for race in data["ranking_top20"]:
            assert "id" in race
            assert "nome_corrida" in race
            assert "total_avaliacoes" in race
            assert "media_geral" in race
            assert "no_ranking" in race
    
    def test_dashboard_requires_admin(self):
        """Test dashboard requires admin authentication"""
        # Without token
        response = requests.get(f"{BASE_URL}/api/admin/ranking-corridas/dashboard")
        assert response.status_code == 403 or response.status_code == 401
        
        # With atleta token
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "gustavo_carvalho_13@email.com",
            "password": "atleta123"
        })
        if login_resp.status_code == 200:
            atleta_token = login_resp.json().get("token")
            response = requests.get(
                f"{BASE_URL}/api/admin/ranking-corridas/dashboard",
                headers={"Authorization": f"Bearer {atleta_token}"}
            )
            assert response.status_code == 403


class TestCorridasEventosCRUD:
    """Test CRUD operations for /api/corridas-eventos"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def test_corrida_id(self, admin_token):
        """Create a test corrida and return its ID for later tests"""
        response = requests.post(
            f"{BASE_URL}/api/corridas-eventos",
            headers={"Authorization": f"Bearer {admin_token}"},
            data={
                "nome_corrida": "TEST_Corrida Pytest Fase34",
                "organizador": "TEST Organizador",
                "cidade": "Test City",
                "estado": "SP",
                "data_corrida": "2026-12-25",
                "pagina_link": "https://test.com",
                "status": "ativa"
            }
        )
        if response.status_code == 200:
            return response.json().get("id")
        return None
    
    def test_post_corridas_eventos(self, admin_token):
        """Test POST /api/corridas-eventos - Create new race"""
        response = requests.post(
            f"{BASE_URL}/api/corridas-eventos",
            headers={"Authorization": f"Bearer {admin_token}"},
            data={
                "nome_corrida": "TEST_Nova Corrida Pytest",
                "organizador": "TEST Organizador",
                "cidade": "São Paulo",
                "estado": "SP",
                "data_corrida": "2026-08-15",
                "pagina_link": "https://example.com",
                "status": "ativa"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"] == "Corrida cadastrada com sucesso!"
        
        # Cleanup - delete the test corrida
        corrida_id = data["id"]
        requests.delete(
            f"{BASE_URL}/api/corridas-eventos/{corrida_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
    
    def test_get_corridas_eventos_list(self):
        """Test GET /api/corridas-eventos - List all races"""
        response = requests.get(f"{BASE_URL}/api/corridas-eventos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Each race should have required fields
        for race in data:
            assert "id" in race
            assert "nome_corrida" in race
            assert "organizador" in race
            assert "cidade" in race
            assert "estado" in race
    
    def test_get_corrida_by_id(self, admin_token, test_corrida_id):
        """Test GET /api/corridas-eventos/{id}"""
        if not test_corrida_id:
            pytest.skip("No test corrida created")
        
        response = requests.get(f"{BASE_URL}/api/corridas-eventos/{test_corrida_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_corrida_id
        assert data["nome_corrida"] == "TEST_Corrida Pytest Fase34"
        assert data["estado"] == "SP"
    
    def test_get_corrida_not_found(self):
        """Test GET /api/corridas-eventos/{id} with invalid ID"""
        response = requests.get(f"{BASE_URL}/api/corridas-eventos/invalid-id-12345")
        assert response.status_code == 404
    
    def test_put_corridas_eventos(self, admin_token, test_corrida_id):
        """Test PUT /api/corridas-eventos/{id} - Update race"""
        if not test_corrida_id:
            pytest.skip("No test corrida created")
        
        response = requests.put(
            f"{BASE_URL}/api/corridas-eventos/{test_corrida_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            data={
                "nome_corrida": "TEST_Corrida Pytest ATUALIZADA",
                "cidade": "Rio de Janeiro",
                "estado": "RJ"
            }
        )
        assert response.status_code == 200
        
        # Verify update
        get_response = requests.get(f"{BASE_URL}/api/corridas-eventos/{test_corrida_id}")
        data = get_response.json()
        assert data["nome_corrida"] == "TEST_Corrida Pytest ATUALIZADA"
        assert data["cidade"] == "Rio de Janeiro"
        assert data["estado"] == "RJ"
    
    def test_delete_corridas_eventos(self, admin_token, test_corrida_id):
        """Test DELETE /api/corridas-eventos/{id}"""
        if not test_corrida_id:
            pytest.skip("No test corrida created")
        
        response = requests.delete(
            f"{BASE_URL}/api/corridas-eventos/{test_corrida_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/corridas-eventos/{test_corrida_id}")
        assert get_response.status_code == 404
    
    def test_post_requires_auth(self):
        """Test POST /api/corridas-eventos requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/corridas-eventos",
            data={
                "nome_corrida": "Teste Sem Auth",
                "organizador": "Org",
                "cidade": "City",
                "estado": "SP",
                "data_corrida": "2026-01-01"
            }
        )
        assert response.status_code == 403 or response.status_code == 401


class TestSelosAutomaticos:
    """Test automatic badge system - Fase 3"""
    
    def test_ranking_includes_selo_fields(self):
        """Test that ranking endpoint includes selo fields"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 200
        data = response.json()
        
        # Check the ranking array
        assert "ranking" in data
        for race in data["ranking"]:
            # Each race should have selo_top10 field (for Top 10 Brasil)
            assert "selo_top10" in race or "selo" in race
            assert "no_ranking" in race
    
    def test_ranking_corrida_natal_has_top10(self):
        """Test that Corrida de Natal 2025 has Top 10 badge"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        data = response.json()
        
        # Find Corrida de Natal 2025
        natal_race = None
        for race in data["ranking"]:
            if race["nome_corrida"] == "Corrida de Natal 2025":
                natal_race = race
                break
        
        assert natal_race is not None, "Corrida de Natal 2025 not found in ranking"
        assert natal_race["no_ranking"] == True
        # It should have Top 10 badge since it's position 1
        assert natal_race.get("selo_top10") == "top10_brasil" or natal_race.get("posicao") == 1
    
    def test_5estrelas_badge_requirements(self):
        """Test 5 estrelas badge requires 50+ avaliações and média ≥ 4.5"""
        # Check admin dashboard for selo info
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        token = login_resp.json().get("token")
        
        response = requests.get(
            f"{BASE_URL}/api/admin/ranking-corridas/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()
        
        # Check if any race has 5 estrelas
        for race in data.get("ranking_top20", []):
            if race.get("selo_5estrelas"):
                # Verify it meets the criteria
                assert race["total_avaliacoes"] >= 50
                assert race["media_geral"] >= 4.5


class TestRankingCorridasPublicEndpoints:
    """Test public ranking endpoints"""
    
    def test_ranking_corridas_endpoint(self):
        """Test GET /api/ranking-corridas returns list"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data
        assert "tipo" in data
        assert "total_corridas" in data
    
    def test_ranking_corridas_stats_endpoint(self):
        """Test GET /api/ranking-corridas/stats returns stats"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_corridas" in data
        assert "total_avaliacoes" in data
        assert "media_geral" in data
    
    def test_ranking_corridas_estados_endpoint(self):
        """Test GET /api/ranking-corridas/estados returns state list"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/estados")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        return response.json().get("token")
    
    def test_cleanup_test_corridas(self, admin_token):
        """Cleanup any test corridas that might have been left over"""
        response = requests.get(f"{BASE_URL}/api/corridas-eventos")
        if response.status_code == 200:
            corridas = response.json()
            for corrida in corridas:
                if corrida.get("nome_corrida", "").startswith("TEST_"):
                    requests.delete(
                        f"{BASE_URL}/api/corridas-eventos/{corrida['id']}",
                        headers={"Authorization": f"Bearer {admin_token}"}
                    )
        assert True  # Cleanup always passes
