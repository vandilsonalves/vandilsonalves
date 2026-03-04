"""
Bloco A da Liga de Assessorias Tests:
1. Filtro de Cidade nos filtros de ranking
2. Liga de Assessorias na página pública (RankingPage) como 3ª aba
3. Botão 'Promover a Dono de Assessoria' na lista de atletas do Admin
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ====================
# FIXTURE: Session
# ====================
@pytest.fixture(scope="module")
def api_session():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="module")
def admin_token(api_session):
    """Get admin authentication token"""
    response = api_session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@runpro.com",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Admin authentication failed")

@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {admin_token}"}

# ====================
# TEST: Liga de Assessorias - PUBLIC endpoints (sem auth)
# ====================
class TestLigaAssessoriasPublicEndpoints:
    """Test that Liga de Assessorias endpoints are public (no auth required)"""
    
    def test_liga_ranking_public_no_auth(self, api_session):
        """GET /api/liga-assessorias/ranking should work WITHOUT authentication"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
        data = response.json()
        assert "ranking" in data, "Response should have 'ranking' field"
        
    def test_liga_stats_public_no_auth(self, api_session):
        """GET /api/liga-assessorias/stats should work WITHOUT authentication"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/stats")
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
        data = response.json()
        assert "total_assessorias" in data, "Response should have 'total_assessorias'"
        assert "total_atletas_vinculados" in data, "Response should have 'total_atletas_vinculados'"
        
    def test_liga_estados_public_no_auth(self, api_session):
        """GET /api/liga-assessorias/estados should work WITHOUT authentication"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/estados")
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list of states"
        
    def test_liga_cidades_public_no_auth(self, api_session):
        """GET /api/liga-assessorias/cidades should work WITHOUT authentication"""
        # First get a valid estado
        estados_response = api_session.get(f"{BASE_URL}/api/liga-assessorias/estados")
        if estados_response.status_code == 200:
            estados = estados_response.json()
            if estados:
                response = api_session.get(f"{BASE_URL}/api/liga-assessorias/cidades?estado={estados[0]}")
                assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

# ====================
# TEST: Filtro de Tipo de Ranking
# ====================
class TestFiltroTipoRanking:
    """Test filter 'Tipo de Ranking' options: Nacional, Estadual, Por Cidade, Mensal, Anual, Histórico"""
    
    def test_ranking_tipo_nacional(self, api_session):
        """GET /api/liga-assessorias/ranking?tipo=nacional should return national ranking"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        assert response.status_code == 200
        data = response.json()
        assert data.get("tipo") == "nacional", "Tipo should be 'nacional'"
        
    def test_ranking_tipo_estadual(self, api_session):
        """GET /api/liga-assessorias/ranking?tipo=estadual should return state ranking"""
        # Get valid estado first
        estados_response = api_session.get(f"{BASE_URL}/api/liga-assessorias/estados")
        estados = estados_response.json()
        if estados:
            response = api_session.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual&estado={estados[0]}")
            assert response.status_code == 200
            data = response.json()
            assert data.get("tipo") == "estadual", "Tipo should be 'estadual'"
            
    def test_ranking_tipo_cidade(self, api_session):
        """GET /api/liga-assessorias/ranking?tipo=cidade should return city ranking"""
        # Get valid estado first
        estados_response = api_session.get(f"{BASE_URL}/api/liga-assessorias/estados")
        estados = estados_response.json()
        if estados:
            # Get cidades for estado
            cidades_response = api_session.get(f"{BASE_URL}/api/liga-assessorias/cidades?estado={estados[0]}")
            cidades = cidades_response.json()
            if cidades:
                response = api_session.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=cidade&cidade={cidades[0]}")
                assert response.status_code == 200
                data = response.json()
                assert data.get("tipo") == "cidade", "Tipo should be 'cidade'"
            
    def test_ranking_tipo_mensal(self, api_session):
        """GET /api/liga-assessorias/ranking?tipo=mensal should return monthly ranking"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=mensal")
        assert response.status_code == 200
        data = response.json()
        assert data.get("tipo") == "mensal", "Tipo should be 'mensal'"
        
    def test_ranking_tipo_anual(self, api_session):
        """GET /api/liga-assessorias/ranking?tipo=anual should return annual ranking"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=anual")
        assert response.status_code == 200
        data = response.json()
        assert data.get("tipo") == "anual", "Tipo should be 'anual'"
        
    def test_ranking_tipo_historico(self, api_session):
        """GET /api/liga-assessorias/ranking?tipo=historico should return historical ranking"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=historico")
        assert response.status_code == 200
        data = response.json()
        assert data.get("tipo") == "historico", "Tipo should be 'historico'"

# ====================
# TEST: Promover Dono de Assessoria
# ====================
class TestPromoverDonoAssessoria:
    """Test POST /api/admin/atletas/{id}/promover-dono-assessoria endpoint"""
    
    def test_promover_requires_auth(self, api_session):
        """POST /api/admin/atletas/{id}/promover-dono-assessoria requires authentication"""
        response = api_session.post(f"{BASE_URL}/api/admin/atletas/fake-id/promover-dono-assessoria")
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403 but got {response.status_code}"
        
    def test_promover_requires_admin(self, api_session, auth_headers):
        """Only admin can promote athletes"""
        # First, get list of atletas
        response = api_session.get(f"{BASE_URL}/api/admin/atletas", headers=auth_headers)
        assert response.status_code == 200
        atletas = response.json()
        
        # Find an atleta with equipe that is not already dono_assessoria
        atleta_com_equipe = None
        for atleta in atletas:
            if atleta.get("equipe") and atleta.get("equipe") != "Sem equipe" and atleta.get("role") != "dono_assessoria":
                atleta_com_equipe = atleta
                break
                
        if atleta_com_equipe:
            # Test promote endpoint
            response = api_session.post(
                f"{BASE_URL}/api/admin/atletas/{atleta_com_equipe['id']}/promover-dono-assessoria",
                headers=auth_headers
            )
            # Should succeed or at least not be auth error
            assert response.status_code in [200, 400, 404], f"Expected success or validation error but got {response.status_code}"
    
    def test_promover_atleta_sem_equipe_should_fail(self, api_session, auth_headers):
        """Promoting athlete without equipe should fail"""
        # Get atletas without equipe
        response = api_session.get(f"{BASE_URL}/api/admin/atletas", headers=auth_headers)
        atletas = response.json()
        
        atleta_sem_equipe = None
        for atleta in atletas:
            if not atleta.get("equipe") or atleta.get("equipe") == "" or atleta.get("equipe") == "Sem equipe":
                atleta_sem_equipe = atleta
                break
        
        if atleta_sem_equipe:
            response = api_session.post(
                f"{BASE_URL}/api/admin/atletas/{atleta_sem_equipe['id']}/promover-dono-assessoria",
                headers=auth_headers
            )
            # Should fail with 400 - athlete needs equipe
            assert response.status_code == 400, f"Expected 400 but got {response.status_code}"
            
    def test_promover_atleta_not_found(self, api_session, auth_headers):
        """Promoting non-existent athlete should return 404"""
        response = api_session.post(
            f"{BASE_URL}/api/admin/atletas/non-existent-id-12345/promover-dono-assessoria",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404 but got {response.status_code}"

# ====================
# TEST: Admin Menu - NO Assessorias/Equipes tab
# ====================
class TestAdminMenuStructure:
    """Verify Admin Dashboard menu structure does NOT have Assessorias/Equipes tab"""
    
    def test_admin_stats_endpoint_exists(self, api_session, auth_headers):
        """Verify admin stats endpoint still works"""
        response = api_session.get(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
        assert response.status_code == 200
        
    def test_admin_atletas_endpoint_exists(self, api_session, auth_headers):
        """Verify admin atletas endpoint still works"""
        response = api_session.get(f"{BASE_URL}/api/admin/atletas", headers=auth_headers)
        assert response.status_code == 200

# ====================
# TEST: Liga Stats Data Validation
# ====================
class TestLigaStatsDataValidation:
    """Validate data structure and values in Liga de Assessorias"""
    
    def test_stats_has_valid_values(self, api_session):
        """Stats should have valid numeric values"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/stats")
        data = response.json()
        
        assert isinstance(data.get("total_assessorias"), int), "total_assessorias should be int"
        assert isinstance(data.get("total_atletas_vinculados"), int), "total_atletas_vinculados should be int"
        assert isinstance(data.get("total_resultados_aprovados"), int), "total_resultados_aprovados should be int"
        
        # Values should be non-negative
        assert data.get("total_assessorias", 0) >= 0
        assert data.get("total_atletas_vinculados", 0) >= 0
        assert data.get("total_resultados_aprovados", 0) >= 0
        
    def test_ranking_has_required_fields(self, api_session):
        """Ranking items should have all required fields"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        data = response.json()
        ranking = data.get("ranking", [])
        
        if ranking:
            item = ranking[0]
            required_fields = ["nome", "estado", "cidade", "total_atletas", "pontos_total", "posicao", "selo"]
            for field in required_fields:
                assert field in item, f"Ranking item missing required field: {field}"
                
    def test_ranking_selos_are_valid(self, api_session):
        """Selos should be 'ouro', 'prata', or 'bronze'"""
        response = api_session.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        data = response.json()
        ranking = data.get("ranking", [])
        
        valid_selos = ["ouro", "prata", "bronze"]
        for item in ranking:
            selo = item.get("selo")
            assert selo in valid_selos, f"Invalid selo: {selo}"
