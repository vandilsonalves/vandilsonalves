"""
Test iteration 40: Solicitações de entrada em assessorias
Tests for:
- GET /api/assessorias/solicitacoes-pendentes - List pending requests for assessoria owner
- POST /api/assessorias/aprovar-solicitacao/{id} - Approve request and add athlete to team
- POST /api/assessorias/reprovar-solicitacao/{id} - Reject request
- POST /api/assessorias/solicitar-entrada - Athlete without team requests to join
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSolicitacoesAssessoria:
    """Tests for assessoria entry requests system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get tokens for different user types"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as dono_assessoria
        dono_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "dono@speedteam.com",
            "password": "senha123"
        })
        if dono_response.status_code == 200:
            self.dono_token = dono_response.json().get("token")
            self.dono_user = dono_response.json().get("user")
        else:
            self.dono_token = None
            self.dono_user = None
        
        # Login as admin (super_admin)
        admin_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        if admin_response.status_code == 200:
            self.admin_token = admin_response.json().get("token")
        else:
            self.admin_token = None
    
    # ==================== GET /api/assessorias/solicitacoes-pendentes ====================
    
    def test_get_solicitacoes_pendentes_as_dono(self):
        """Test that dono_assessoria can see pending requests for their team"""
        if not self.dono_token:
            pytest.skip("Dono token not available")
        
        response = self.session.get(
            f"{BASE_URL}/api/assessorias/solicitacoes-pendentes",
            headers={"Authorization": f"Bearer {self.dono_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "solicitacoes" in data
        assert "total_pendentes" in data
        assert isinstance(data["solicitacoes"], list)
        assert isinstance(data["total_pendentes"], int)
        
        # Verify we have at least 1 pending request (Maria Corredora)
        assert data["total_pendentes"] >= 1
        
        # Check structure of a solicitacao
        if len(data["solicitacoes"]) > 0:
            solicitacao = data["solicitacoes"][0]
            assert "id" in solicitacao
            assert "atleta_id" in solicitacao
            assert "atleta_nome" in solicitacao
            assert "assessoria_nome" in solicitacao
            assert "status" in solicitacao
            assert solicitacao["status"] == "pendente"
    
    def test_get_solicitacoes_pendentes_without_auth(self):
        """Test that unauthenticated users cannot see requests"""
        response = self.session.get(f"{BASE_URL}/api/assessorias/solicitacoes-pendentes")
        
        # Should return 401 or 403
        assert response.status_code in [401, 403]
    
    def test_get_solicitacoes_pendentes_as_admin(self):
        """Test that admin can also see pending requests"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        response = self.session.get(
            f"{BASE_URL}/api/assessorias/solicitacoes-pendentes",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "solicitacoes" in data
        assert "total_pendentes" in data
    
    # ==================== POST /api/assessorias/solicitar-entrada ====================
    
    def test_solicitar_entrada_without_auth(self):
        """Test that unauthenticated users cannot request entry"""
        response = self.session.post(
            f"{BASE_URL}/api/assessorias/solicitar-entrada",
            json={"assessoria_nome": "Speed Team", "mensagem": "Test"}
        )
        
        assert response.status_code in [401, 403]
    
    # ==================== POST /api/assessorias/aprovar-solicitacao/{id} ====================
    
    def test_aprovar_solicitacao_invalid_id(self):
        """Test approval with non-existent request ID returns 404"""
        if not self.dono_token:
            pytest.skip("Dono token not available")
        
        fake_id = str(uuid.uuid4())
        response = self.session.post(
            f"{BASE_URL}/api/assessorias/aprovar-solicitacao/{fake_id}",
            headers={"Authorization": f"Bearer {self.dono_token}"},
            json={}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_aprovar_solicitacao_without_auth(self):
        """Test that unauthenticated users cannot approve requests"""
        fake_id = str(uuid.uuid4())
        response = self.session.post(
            f"{BASE_URL}/api/assessorias/aprovar-solicitacao/{fake_id}",
            json={}
        )
        
        assert response.status_code in [401, 403]
    
    # ==================== POST /api/assessorias/reprovar-solicitacao/{id} ====================
    
    def test_reprovar_solicitacao_invalid_id(self):
        """Test rejection with non-existent request ID returns 404"""
        if not self.dono_token:
            pytest.skip("Dono token not available")
        
        fake_id = str(uuid.uuid4())
        response = self.session.post(
            f"{BASE_URL}/api/assessorias/reprovar-solicitacao/{fake_id}",
            headers={"Authorization": f"Bearer {self.dono_token}"},
            json={"motivo": "Test reason"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_reprovar_solicitacao_without_auth(self):
        """Test that unauthenticated users cannot reject requests"""
        fake_id = str(uuid.uuid4())
        response = self.session.post(
            f"{BASE_URL}/api/assessorias/reprovar-solicitacao/{fake_id}",
            json={"motivo": "Test reason"}
        )
        
        assert response.status_code in [401, 403]
    
    # ==================== GET /api/assessorias/minhas-solicitacoes ====================
    
    def test_minhas_solicitacoes_without_auth(self):
        """Test that unauthenticated users cannot see their requests"""
        response = self.session.get(f"{BASE_URL}/api/assessorias/minhas-solicitacoes")
        
        assert response.status_code in [401, 403]
    
    # ==================== Verify existing pending request ====================
    
    def test_verify_maria_corredora_pending_request(self):
        """Verify the existing pending request from Maria Corredora"""
        if not self.dono_token:
            pytest.skip("Dono token not available")
        
        response = self.session.get(
            f"{BASE_URL}/api/assessorias/solicitacoes-pendentes",
            headers={"Authorization": f"Bearer {self.dono_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Find Maria Corredora's request
        maria_request = None
        for solicitacao in data["solicitacoes"]:
            if solicitacao.get("atleta_nome") == "Maria Corredora":
                maria_request = solicitacao
                break
        
        assert maria_request is not None, "Maria Corredora's pending request not found"
        assert maria_request["atleta_nome"] == "Maria Corredora"
        assert maria_request["assessoria_nome"] == "Speed Team"
        assert maria_request["status"] == "pendente"
        assert maria_request["atleta_cidade"] == "Curitiba"
        assert maria_request["atleta_estado"] == "PR"


class TestDonoAssessoriaDashboardEndpoints:
    """Tests for DonoAssessoriaDashboard related endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get dono token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as dono_assessoria
        dono_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "dono@speedteam.com",
            "password": "senha123"
        })
        if dono_response.status_code == 200:
            self.dono_token = dono_response.json().get("token")
            self.dono_user = dono_response.json().get("user")
        else:
            self.dono_token = None
            self.dono_user = None
    
    def test_dono_user_has_correct_role(self):
        """Verify dono user has role dono_assessoria"""
        assert self.dono_user is not None
        assert self.dono_user.get("role") == "dono_assessoria"
    
    def test_get_assessoria_details(self):
        """Test getting assessoria details for dono's team"""
        if not self.dono_user:
            pytest.skip("Dono user not available")
        
        equipe = self.dono_user.get("equipe") or "Speed Team"
        
        import urllib.parse
        encoded_equipe = urllib.parse.quote(equipe)
        
        response = self.session.get(
            f"{BASE_URL}/api/liga-assessorias/assessoria/{encoded_equipe}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify assessoria data structure
        assert "nome" in data
        assert "total_atletas" in data
        assert "pontos_total" in data
        assert "atletas" in data
    
    def test_liga_assessorias_ranking(self):
        """Test liga assessorias ranking endpoint"""
        response = self.session.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data
        assert "total_assessorias" in data
        assert isinstance(data["ranking"], list)


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
    
    def test_dono_login(self):
        """Test login with dono credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "dono@speedteam.com", "password": "senha123"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "dono_assessoria"
        assert data["user"]["email"] == "dono@speedteam.com"
    
    def test_admin_login(self):
        """Test login with admin credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@rankingrun.com", "password": "admin123"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
