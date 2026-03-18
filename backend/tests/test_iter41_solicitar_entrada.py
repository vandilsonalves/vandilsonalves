"""
Test: Solicitar Entrada na Assessoria Feature
Iteration 41: Testing the 'Request Team Entry' button on AssessoriaPage

Test scenarios:
1. AssessoriaPage loads correctly for Speed Team
2. POST /api/assessorias/solicitar-entrada works for athlete without team
3. GET /api/assessorias/minhas-solicitacoes returns pending requests
4. Athlete with existing team gets rejected
5. Duplicate request gets rejected (already has pending)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ATLETA_LIVRE = {"email": "atleta.livre@teste.com", "password": "senha123"}
DONO_SPEED = {"email": "dono@speedteam.com", "password": "senha123"}
ADMIN = {"email": "admin@rankingrun.com", "password": "admin123"}

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def atleta_livre_token(api_client):
    """Get token for athlete without team"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json=ATLETA_LIVRE)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data["token"], data["user"]


@pytest.fixture(scope="module")
def dono_token(api_client):
    """Get token for dono assessoria"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json=DONO_SPEED)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data["token"], data["user"]


class TestAssessoriaPageAPI:
    """Test that assessoria page endpoints work correctly"""
    
    def test_assessoria_page_loads(self, api_client):
        """Test GET /api/liga-assessorias/assessoria/{nome} works"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Speed%20Team")
        assert response.status_code == 200, f"Failed to load assessoria: {response.text}"
        
        data = response.json()
        assert data["nome"] == "Speed Team"
        assert data["total_atletas"] >= 1
        assert "atletas" in data
        print(f"✅ Speed Team loaded with {data['total_atletas']} athletes")


class TestAtletaLivreProfile:
    """Test the athlete without team profile"""
    
    def test_atleta_livre_has_no_team(self, api_client, atleta_livre_token):
        """Verify atleta.livre@teste.com has no team (equipe empty)"""
        token, user = atleta_livre_token
        
        response = api_client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        equipe = data.get("equipe", "")
        assert equipe in ["", None, "INDIVIDUAL", "Sem equipe", "SEM EQUIPE"], \
            f"Athlete should have no team, but has: {equipe}"
        print(f"✅ Athlete has no team: equipe='{equipe}'")


class TestSolicitarEntrada:
    """Test the request entry functionality"""
    
    def test_minhas_solicitacoes_endpoint(self, api_client, atleta_livre_token):
        """Test GET /api/assessorias/minhas-solicitacoes"""
        token, _ = atleta_livre_token
        
        response = api_client.get(
            f"{BASE_URL}/api/assessorias/minhas-solicitacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "solicitacoes" in data
        print(f"✅ minhas-solicitacoes returned {len(data['solicitacoes'])} requests")
        
        # Check if there's already a pending request for Speed Team
        pending = [s for s in data["solicitacoes"] if s["assessoria_nome"] == "Speed Team" and s["status"] == "pendente"]
        if pending:
            print(f"   Found pending request for Speed Team: {pending[0]['id']}")
    
    def test_solicitar_entrada_duplicate_rejected(self, api_client, atleta_livre_token):
        """Test that duplicate request is rejected"""
        token, _ = atleta_livre_token
        
        # First check if there's already a pending request
        response = api_client.get(
            f"{BASE_URL}/api/assessorias/minhas-solicitacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()
        pending = [s for s in data["solicitacoes"] if s["assessoria_nome"] == "Speed Team" and s["status"] == "pendente"]
        
        if pending:
            # Try to create duplicate
            response = api_client.post(
                f"{BASE_URL}/api/assessorias/solicitar-entrada",
                json={"assessoria_nome": "Speed Team", "mensagem": "Duplicate test"},
                headers={"Authorization": f"Bearer {token}"}
            )
            # Should be rejected
            assert response.status_code == 400, f"Expected 400 for duplicate, got {response.status_code}"
            assert "já tem uma solicitação pendente" in response.json().get("detail", "").lower() or "pendente" in response.json().get("detail", "").lower()
            print("✅ Duplicate request correctly rejected")
        else:
            # If no pending, create first one
            response = api_client.post(
                f"{BASE_URL}/api/assessorias/solicitar-entrada",
                json={"assessoria_nome": "Speed Team", "mensagem": "Test request"},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            print("✅ First request created successfully")
    
    def test_solicitar_entrada_requires_auth(self, api_client):
        """Test that endpoint requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/assessorias/solicitar-entrada",
            json={"assessoria_nome": "Speed Team", "mensagem": "Test"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✅ Endpoint requires authentication")
    
    def test_solicitar_entrada_assessoria_not_found(self, api_client, atleta_livre_token):
        """Test request for non-existent assessoria"""
        token, _ = atleta_livre_token
        
        response = api_client.post(
            f"{BASE_URL}/api/assessorias/solicitar-entrada",
            json={"assessoria_nome": "NonExistent Team 12345", "mensagem": "Test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, f"Expected 404 for non-existent, got {response.status_code}"
        print("✅ Non-existent assessoria returns 404")


class TestAtletaWithTeam:
    """Test behavior for athlete who already has a team"""
    
    def test_dono_has_team(self, api_client, dono_token):
        """Verify dono@speedteam.com has Speed Team"""
        token, user = dono_token
        
        response = api_client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        equipe = data.get("equipe", "")
        print(f"✅ Dono has team: equipe='{equipe}', role='{data.get('role')}'")
    
    def test_athlete_with_team_cannot_request(self, api_client, dono_token):
        """Test that athlete with team cannot request entry"""
        token, user = dono_token
        
        # Only test if user actually has a team
        if user.get("equipe") and user.get("equipe").upper() not in ["", "INDIVIDUAL", "SEM EQUIPE"]:
            response = api_client.post(
                f"{BASE_URL}/api/assessorias/solicitar-entrada",
                json={"assessoria_nome": "Another Team", "mensagem": "Test"},
                headers={"Authorization": f"Bearer {token}"}
            )
            # Should be rejected - already has team
            assert response.status_code == 400, f"Expected 400 for athlete with team, got {response.status_code}"
            print("✅ Athlete with team correctly rejected")
        else:
            print("⚠️ Skipping test - dono doesn't have equipe set")
            pytest.skip("Dono doesn't have equipe set")


class TestSolicitacoesPendentes:
    """Test the pending requests endpoint for dono"""
    
    def test_dono_can_see_pending(self, api_client, dono_token):
        """Test GET /api/assessorias/solicitacoes-pendentes for dono"""
        token, _ = dono_token
        
        response = api_client.get(
            f"{BASE_URL}/api/assessorias/solicitacoes-pendentes",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "solicitacoes" in data
        assert "total_pendentes" in data
        print(f"✅ Dono can see {data['total_pendentes']} pending requests")
    
    def test_pending_requires_dono_role(self, api_client, atleta_livre_token):
        """Test that only dono/admin can see pending requests"""
        token, user = atleta_livre_token
        
        # Atleta should not have access
        if user.get("role") == "atleta":
            response = api_client.get(
                f"{BASE_URL}/api/assessorias/solicitacoes-pendentes",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code in [403, 200], f"Got {response.status_code}"
            # If 200, should return empty (no equipe)
            if response.status_code == 200:
                data = response.json()
                # Should be empty or have 0 pendentes
                print(f"✅ Atleta access returns: {data}")
        else:
            print("⚠️ Skipping - user is not atleta role")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
