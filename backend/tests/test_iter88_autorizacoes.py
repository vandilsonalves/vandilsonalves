"""
Iteration 88: Testing Autorizacoes Admin Features
- POST /api/admin/autorizacoes/autorizar with tipo_plano='ate_fim_ano' -> data_expiracao 31/12/2026
- POST /api/admin/autorizacoes/autorizar with tipo_plano='plano_anual' -> data_expiracao 1 year from now
- POST /api/admin/autorizacoes/revogar with atleta_id -> revokes all active authorizations
- POST /api/admin/autorizacoes/revogar with atleta without authorization -> returns 404
- GET /api/efi/pagamento/status -> vendas_abertas=true (before 15/12/2026)
- GET /api/efi/config -> is_sandbox=false and environment=production (production credentials configured)
"""

import pytest
import requests
import os
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
TEST_ATLETA_EMAIL = "monica_vieira_336@email.com"


class TestAdminAutorizacoes:
    """Tests for admin authorization endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        # API returns 'token' not 'access_token'
        token = data.get("access_token") or data.get("token")
        assert token, "No token in response"
        return token
    
    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Headers with admin auth"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    @pytest.fixture(scope="class")
    def test_atleta_id(self, admin_headers):
        """Get Monica Vieira's atleta_id for testing"""
        # First, get the list of atletas
        response = requests.get(f"{BASE_URL}/api/admin/autorizacoes/atletas-completo", headers=admin_headers)
        assert response.status_code == 200, f"Failed to get atletas: {response.text}"
        data = response.json()
        atletas = data.get("atletas", [])
        
        # Find Monica Vieira
        monica = None
        for atleta in atletas:
            if "monica" in atleta.get("nome", "").lower() or "monica" in atleta.get("email", "").lower():
                monica = atleta
                break
        
        if not monica:
            # If Monica not found, use first atleta that is not authorized
            for atleta in atletas:
                if atleta.get("status_periodo") != "autorizado":
                    monica = atleta
                    break
        
        if not monica and atletas:
            monica = atletas[0]
        
        assert monica is not None, "No test atleta found"
        return monica["id"]
    
    def test_autorizar_ate_fim_ano(self, admin_headers, test_atleta_id):
        """Test POST /api/admin/autorizacoes/autorizar with tipo_plano='ate_fim_ano'"""
        # First, revoke any existing authorization to ensure clean state
        requests.post(f"{BASE_URL}/api/admin/autorizacoes/revogar", 
                     json={"atleta_id": test_atleta_id}, 
                     headers=admin_headers)
        
        # Now authorize with ate_fim_ano
        response = requests.post(f"{BASE_URL}/api/admin/autorizacoes/autorizar", 
                                json={
                                    "atleta_id": test_atleta_id,
                                    "tipo_plano": "ate_fim_ano"
                                }, 
                                headers=admin_headers)
        
        assert response.status_code == 200, f"Autorizar failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "message" in data, "No message in response"
        assert "data_expiracao" in data, "No data_expiracao in response"
        assert "autorizacao_id" in data, "No autorizacao_id in response"
        
        # Verify data_expiracao is 31/12/2026
        data_exp = datetime.fromisoformat(data["data_expiracao"].replace("Z", "+00:00"))
        assert data_exp.year == 2026, f"Expected year 2026, got {data_exp.year}"
        assert data_exp.month == 12, f"Expected month 12, got {data_exp.month}"
        assert data_exp.day == 31, f"Expected day 31, got {data_exp.day}"
        
        print(f"✓ Autorizar ate_fim_ano: data_expiracao = {data['data_expiracao']}")
    
    def test_autorizar_plano_anual(self, admin_headers, test_atleta_id):
        """Test POST /api/admin/autorizacoes/autorizar with tipo_plano='plano_anual'"""
        # First, revoke any existing authorization
        requests.post(f"{BASE_URL}/api/admin/autorizacoes/revogar", 
                     json={"atleta_id": test_atleta_id}, 
                     headers=admin_headers)
        
        # Now authorize with plano_anual
        response = requests.post(f"{BASE_URL}/api/admin/autorizacoes/autorizar", 
                                json={
                                    "atleta_id": test_atleta_id,
                                    "tipo_plano": "plano_anual"
                                }, 
                                headers=admin_headers)
        
        assert response.status_code == 200, f"Autorizar failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "message" in data, "No message in response"
        assert "data_expiracao" in data, "No data_expiracao in response"
        
        # Verify data_expiracao is approximately 1 year from now
        data_exp = datetime.fromisoformat(data["data_expiracao"].replace("Z", "+00:00"))
        agora = datetime.now(timezone.utc)
        diff_days = (data_exp - agora).days
        
        # Should be approximately 365 days (allow some margin for test execution time)
        assert 360 <= diff_days <= 370, f"Expected ~365 days, got {diff_days} days"
        
        print(f"✓ Autorizar plano_anual: data_expiracao = {data['data_expiracao']} ({diff_days} days from now)")
    
    def test_revogar_atleta_com_autorizacao(self, admin_headers, test_atleta_id):
        """Test POST /api/admin/autorizacoes/revogar with atleta that has authorization"""
        # First, ensure atleta has an authorization
        requests.post(f"{BASE_URL}/api/admin/autorizacoes/autorizar", 
                     json={
                         "atleta_id": test_atleta_id,
                         "tipo_plano": "ate_fim_ano"
                     }, 
                     headers=admin_headers)
        
        # Now revoke
        response = requests.post(f"{BASE_URL}/api/admin/autorizacoes/revogar", 
                                json={"atleta_id": test_atleta_id}, 
                                headers=admin_headers)
        
        assert response.status_code == 200, f"Revogar failed: {response.text}"
        data = response.json()
        
        assert "message" in data, "No message in response"
        assert "revogada" in data["message"].lower(), f"Expected 'revogada' in message, got: {data['message']}"
        
        print(f"✓ Revogar atleta com autorizacao: {data['message']}")
    
    def test_revogar_atleta_sem_autorizacao(self, admin_headers, test_atleta_id):
        """Test POST /api/admin/autorizacoes/revogar with atleta without authorization -> 404"""
        # First, ensure atleta has no authorization (revoke if any)
        requests.post(f"{BASE_URL}/api/admin/autorizacoes/revogar", 
                     json={"atleta_id": test_atleta_id}, 
                     headers=admin_headers)
        
        # Now try to revoke again - should return 404
        response = requests.post(f"{BASE_URL}/api/admin/autorizacoes/revogar", 
                                json={"atleta_id": test_atleta_id}, 
                                headers=admin_headers)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "detail" in data, "No detail in error response"
        print(f"✓ Revogar atleta sem autorizacao: 404 - {data['detail']}")
    
    def test_autorizar_atleta_inexistente(self, admin_headers):
        """Test POST /api/admin/autorizacoes/autorizar with non-existent atleta_id -> 404"""
        response = requests.post(f"{BASE_URL}/api/admin/autorizacoes/autorizar", 
                                json={
                                    "atleta_id": "non-existent-id-12345",
                                    "tipo_plano": "ate_fim_ano"
                                }, 
                                headers=admin_headers)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ Autorizar atleta inexistente: 404")


class TestEfiPagamentoStatus:
    """Tests for Efi payment status endpoint"""
    
    def test_pagamento_status_vendas_abertas(self):
        """Test GET /api/efi/pagamento/status returns vendas_abertas=true (before 15/12/2026)"""
        response = requests.get(f"{BASE_URL}/api/efi/pagamento/status")
        
        assert response.status_code == 200, f"Failed to get pagamento status: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "vendas_abertas" in data, "No vendas_abertas in response"
        assert "data_limite" in data, "No data_limite in response"
        
        # Current date is 28/03/2026, so vendas should be open (before 15/12/2026)
        assert data["vendas_abertas"] == True, f"Expected vendas_abertas=true, got {data['vendas_abertas']}"
        
        # Verify data_limite is 15/12/2026
        data_limite = datetime.fromisoformat(data["data_limite"].replace("Z", "+00:00"))
        assert data_limite.year == 2026, f"Expected year 2026, got {data_limite.year}"
        assert data_limite.month == 12, f"Expected month 12, got {data_limite.month}"
        assert data_limite.day == 15, f"Expected day 15, got {data_limite.day}"
        
        print(f"✓ Pagamento status: vendas_abertas={data['vendas_abertas']}, data_limite={data['data_limite']}")


class TestEfiConfig:
    """Tests for Efi configuration endpoint"""
    
    @pytest.fixture(scope="class")
    def user_token(self):
        """Get user authentication token"""
        # Try with test user
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teste.dono@teste.com",
            "password": "123456"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        
        # Fallback to admin
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    def test_efi_config_production(self, user_token):
        """Test GET /api/efi/config returns is_sandbox=false and environment=production"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/api/efi/config", headers=headers)
        
        assert response.status_code == 200, f"Failed to get efi config: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "is_sandbox" in data, "No is_sandbox in response"
        assert "environment" in data, "No environment in response"
        assert "payee_code" in data, "No payee_code in response"
        
        # Verify production credentials are configured
        # Based on backend/.env: EFI_CLIENT_ID_PROD is set, so should be production
        assert data["environment"] == "production", f"Expected environment=production, got {data['environment']}"
        assert data["is_sandbox"] == False, f"Expected is_sandbox=false, got {data['is_sandbox']}"
        
        print(f"✓ Efi config: environment={data['environment']}, is_sandbox={data['is_sandbox']}")


class TestPixCartaoBloqueio:
    """Tests for PIX/Cartao payment date blocking (15/12/2026)"""
    
    def test_pix_criar_code_review(self):
        """Code review: POST /api/efi/pix/criar has date blocking for 15/12/2026"""
        # Read the efi_routes.py file to verify the date blocking code exists
        import os
        efi_routes_path = "/app/backend/routes/efi_routes.py"
        
        with open(efi_routes_path, 'r') as f:
            content = f.read()
        
        # Check for date blocking in criar_cobranca_pix
        assert "data_limite_pagamentos = datetime(2026, 12, 15" in content, \
            "Date blocking for 15/12/2026 not found in pix/criar"
        assert "Periodo de vendas encerrado" in content, \
            "Error message for closed sales period not found"
        
        print("✓ Code review: POST /api/efi/pix/criar has date blocking for 15/12/2026")
    
    def test_cartao_criar_code_review(self):
        """Code review: POST /api/efi/cartao/criar has date blocking for 15/12/2026"""
        import os
        efi_routes_path = "/app/backend/routes/efi_routes.py"
        
        with open(efi_routes_path, 'r') as f:
            content = f.read()
        
        # The date blocking should appear twice (once for PIX, once for Cartao)
        count = content.count("data_limite_pagamentos = datetime(2026, 12, 15")
        assert count >= 2, f"Expected date blocking in both PIX and Cartao, found {count} occurrences"
        
        print("✓ Code review: POST /api/efi/cartao/criar has date blocking for 15/12/2026")


class TestAtletasCompletoEndpoint:
    """Tests for admin atletas-completo endpoint used by DashboardAutorizacoes"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    def test_atletas_completo(self, admin_token):
        """Test GET /api/admin/autorizacoes/atletas-completo returns atletas with status"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/autorizacoes/atletas-completo", headers=headers)
        
        assert response.status_code == 200, f"Failed to get atletas: {response.text}"
        data = response.json()
        
        assert "atletas" in data, "No atletas in response"
        atletas = data["atletas"]
        
        assert len(atletas) > 0, "No atletas returned"
        
        # Verify atleta structure
        atleta = atletas[0]
        assert "id" in atleta, "No id in atleta"
        assert "nome" in atleta, "No nome in atleta"
        assert "email" in atleta, "No email in atleta"
        assert "status_periodo" in atleta, "No status_periodo in atleta"
        
        # Count by status
        status_counts = {"em_teste": 0, "autorizado": 0, "expirado": 0}
        for a in atletas:
            status = a.get("status_periodo", "")
            if status in status_counts:
                status_counts[status] += 1
        
        print(f"✓ Atletas completo: {len(atletas)} atletas")
        print(f"  - Em teste: {status_counts['em_teste']}")
        print(f"  - Autorizados: {status_counts['autorizado']}")
        print(f"  - Expirados: {status_counts['expirado']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
