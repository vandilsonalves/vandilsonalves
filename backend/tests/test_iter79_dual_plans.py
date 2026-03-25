"""
Iteration 79: Dual Plan System Tests
Tests for P1 (Lancamento vs Anual plans), P2 (Print Protection), P3 (Admin Dashboard cleanup)

Features tested:
- GET /api/pagamentos/planos returns plano_vigente with lancamento plan (R$97, valor_original 197)
- GET /api/pagamentos/planos shows eh_periodo_lancamento: true (current date is before 15/12/2026)
- GET /api/pagamentos/planos shows plano_anual as null during lancamento period
- GET /api/pagamentos/meu-plano now includes plano_vigente object
- POST /api/pagamentos/checkout creates session with R$97 amount (lancamento plan)
- GET /api/pagamentos/meu-plano returns expirado for expired user with plano_vigente info
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://geo-filtered-admin.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
EXPIRED_USER_EMAIL = "expirado@teste.com"
EXPIRED_USER_PASSWORD = "123456"
VALID_USER_EMAIL = "teste.dono@teste.com"
VALID_USER_PASSWORD = "123456"


class TestDualPlanSystem:
    """Tests for the dual plan system (P1 - Lancamento vs Anual)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def login(self, email, password):
        """Helper to login and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    # ============ /api/pagamentos/planos Tests ============
    
    def test_01_planos_returns_plano_vigente(self):
        """GET /api/pagamentos/planos returns plano_vigente with lancamento plan"""
        response = self.session.get(f"{BASE_URL}/api/pagamentos/planos")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "plano_vigente" in data, "Response should contain plano_vigente"
        
        plano = data["plano_vigente"]
        assert plano["id"] == "atleta_premium_lancamento", f"Expected lancamento plan, got {plano['id']}"
        assert plano["valor"] == 97.0, f"Expected valor 97.0, got {plano['valor']}"
        assert plano["valor_original"] == 197.0, f"Expected valor_original 197.0, got {plano['valor_original']}"
        print("PASSED: plano_vigente contains lancamento plan with R$97 (de R$197)")
    
    def test_02_planos_eh_periodo_lancamento_true(self):
        """GET /api/pagamentos/planos shows eh_periodo_lancamento: true"""
        response = self.session.get(f"{BASE_URL}/api/pagamentos/planos")
        assert response.status_code == 200
        
        data = response.json()
        assert "eh_periodo_lancamento" in data, "Response should contain eh_periodo_lancamento"
        assert data["eh_periodo_lancamento"] == True, f"Expected eh_periodo_lancamento=True, got {data['eh_periodo_lancamento']}"
        print("PASSED: eh_periodo_lancamento is True (current date before 15/12/2026)")
    
    def test_03_planos_anual_null_during_lancamento(self):
        """GET /api/pagamentos/planos shows plano_anual as null during lancamento period"""
        response = self.session.get(f"{BASE_URL}/api/pagamentos/planos")
        assert response.status_code == 200
        
        data = response.json()
        assert "plano_anual" in data, "Response should contain plano_anual key"
        assert data["plano_anual"] is None, f"Expected plano_anual=None during lancamento, got {data['plano_anual']}"
        print("PASSED: plano_anual is null during lancamento period")
    
    def test_04_planos_lancamento_not_null(self):
        """GET /api/pagamentos/planos shows plano_lancamento during lancamento period"""
        response = self.session.get(f"{BASE_URL}/api/pagamentos/planos")
        assert response.status_code == 200
        
        data = response.json()
        assert "plano_lancamento" in data, "Response should contain plano_lancamento key"
        assert data["plano_lancamento"] is not None, "plano_lancamento should not be null during lancamento period"
        assert data["plano_lancamento"]["valor"] == 97.0, "plano_lancamento valor should be 97.0"
        print("PASSED: plano_lancamento is available during lancamento period")
    
    def test_05_planos_data_transicao(self):
        """GET /api/pagamentos/planos shows correct data_transicao"""
        response = self.session.get(f"{BASE_URL}/api/pagamentos/planos")
        assert response.status_code == 200
        
        data = response.json()
        assert "data_transicao" in data, "Response should contain data_transicao"
        assert data["data_transicao"] == "2026-12-15", f"Expected data_transicao=2026-12-15, got {data['data_transicao']}"
        print("PASSED: data_transicao is 2026-12-15")
    
    # ============ /api/pagamentos/meu-plano Tests ============
    
    def test_06_meu_plano_admin_includes_plano_vigente(self):
        """GET /api/pagamentos/meu-plano for admin includes plano_vigente"""
        token = self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert token, "Admin login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/pagamentos/meu-plano",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "plano_vigente" in data, "Response should contain plano_vigente"
        assert data["plano_vigente"]["id"] == "atleta_premium_lancamento"
        assert data["plano_vigente"]["valor"] == 97.0
        assert data["status"] == "autorizado"
        assert data["tipo"] == "admin"
        print("PASSED: Admin meu-plano includes plano_vigente with lancamento plan")
    
    def test_07_meu_plano_expired_user_includes_plano_vigente(self):
        """GET /api/pagamentos/meu-plano for expired user includes plano_vigente"""
        token = self.login(EXPIRED_USER_EMAIL, EXPIRED_USER_PASSWORD)
        assert token, "Expired user login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/pagamentos/meu-plano",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "plano_vigente" in data, "Response should contain plano_vigente"
        assert data["plano_vigente"]["id"] == "atleta_premium_lancamento"
        assert data["plano_vigente"]["valor"] == 97.0
        assert data["plano_vigente"]["valor_original"] == 197.0
        assert data["status"] == "expirado", f"Expected status=expirado, got {data['status']}"
        assert data["tem_acesso_premium"] == False
        print("PASSED: Expired user meu-plano includes plano_vigente with lancamento plan")
    
    def test_08_meu_plano_valid_user_includes_plano_vigente(self):
        """GET /api/pagamentos/meu-plano for valid user includes plano_vigente"""
        token = self.login(VALID_USER_EMAIL, VALID_USER_PASSWORD)
        assert token, "Valid user login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/pagamentos/meu-plano",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "plano_vigente" in data, "Response should contain plano_vigente"
        assert data["plano_vigente"]["id"] == "atleta_premium_lancamento"
        # Valid user should be in test period or authorized
        assert data["status"] in ["em_teste", "autorizado"], f"Expected em_teste or autorizado, got {data['status']}"
        print(f"PASSED: Valid user meu-plano includes plano_vigente (status: {data['status']})")
    
    # ============ /api/pagamentos/checkout Tests ============
    
    def test_09_checkout_uses_lancamento_plan(self):
        """POST /api/pagamentos/checkout creates session with R$97 amount"""
        token = self.login(EXPIRED_USER_EMAIL, EXPIRED_USER_PASSWORD)
        assert token, "Expired user login failed"
        
        response = self.session.post(
            f"{BASE_URL}/api/pagamentos/checkout",
            headers={"Authorization": f"Bearer {token}"},
            json={"origin_url": "https://geo-filtered-admin.preview.emergentagent.com"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, "Response should contain Stripe URL"
        assert "plano" in data, "Response should contain plano info"
        assert data["plano"]["id"] == "atleta_premium_lancamento", f"Expected lancamento plan, got {data['plano']['id']}"
        assert data["plano"]["valor"] == 97.0, f"Expected valor 97.0, got {data['plano']['valor']}"
        assert "checkout.stripe.com" in data["url"], "URL should be Stripe checkout"
        print("PASSED: Checkout creates session with lancamento plan (R$97)")
    
    def test_10_checkout_requires_auth(self):
        """POST /api/pagamentos/checkout requires authentication"""
        response = self.session.post(
            f"{BASE_URL}/api/pagamentos/checkout",
            json={"origin_url": "https://example.com"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASSED: Checkout requires authentication")
    
    # ============ Plan Structure Validation ============
    
    def test_11_plano_lancamento_structure(self):
        """Validate PLANO_LANCAMENTO structure"""
        response = self.session.get(f"{BASE_URL}/api/pagamentos/planos")
        assert response.status_code == 200
        
        plano = response.json()["plano_lancamento"]
        
        # Validate all required fields
        assert plano["id"] == "atleta_premium_lancamento"
        assert plano["nome"] == "Atleta Premium"
        assert plano["valor"] == 97.0
        assert plano["valor_original"] == 197.0
        assert plano["moeda"] == "brl"
        assert plano["tipo"] == "pagamento_unico"
        assert plano["validade"] == "2026-12-31"
        assert plano["disponivel_ate"] == "2026-12-14"
        assert "De R$ 197,00 por R$ 97,00" in plano["descricao"]
        print("PASSED: PLANO_LANCAMENTO structure is correct")
    
    def test_12_plano_vigente_matches_lancamento(self):
        """plano_vigente should match plano_lancamento during lancamento period"""
        response = self.session.get(f"{BASE_URL}/api/pagamentos/planos")
        assert response.status_code == 200
        
        data = response.json()
        assert data["plano_vigente"] == data["plano_lancamento"], "plano_vigente should equal plano_lancamento during lancamento period"
        print("PASSED: plano_vigente matches plano_lancamento")


class TestPublicAccess:
    """Tests for public access (rankings should work for all users)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_13_ranking_nacional_public(self):
        """GET /api/ranking/nacional works without auth"""
        response = self.session.get(f"{BASE_URL}/api/ranking/nacional")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASSED: Ranking nacional is publicly accessible")
    
    def test_14_planos_endpoint_public(self):
        """GET /api/pagamentos/planos works without auth"""
        response = self.session.get(f"{BASE_URL}/api/pagamentos/planos")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASSED: Planos endpoint is publicly accessible")


class TestAdminDashboard:
    """Tests for Admin Dashboard (P3 - cleanup verification)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def login_admin(self):
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_15_admin_stats_endpoint(self):
        """GET /api/admin/stats works for admin"""
        token = self.login_admin()
        assert token, "Admin login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASSED: Admin stats endpoint works")
    
    def test_16_admin_stats_estados_endpoint(self):
        """GET /api/admin/stats/estados works for admin"""
        token = self.login_admin()
        assert token, "Admin login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/stats/estados",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASSED: Admin stats/estados endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
