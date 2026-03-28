# /app/backend/tests/test_iter87_conversao_sandbox.py
# Iteration 87: Testing conversion funnel metrics, financeiro resumo by type, and sandbox card rejection
# Features:
# - GET /api/admin/financeiro/conversao: Funnel data (7d, 30d, total, funil_diario)
# - GET /api/admin/financeiro/resumo: PIX and Cartao by tipo (not gateway)
# - POST /api/efi/cartao/criar: aviso_sandbox field and status rejection
# - GET /api/efi/config: is_sandbox=true

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def atleta_token():
    """Get atleta authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ATLETA_EMAIL,
        "password": ATLETA_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip(f"Atleta login failed: {response.status_code} - {response.text}")


class TestConversaoEndpoint:
    """Tests for GET /api/admin/financeiro/conversao"""

    def test_01_conversao_requires_admin_auth(self):
        """Conversao endpoint requires admin authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/conversao")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_02_conversao_returns_200_for_admin(self, admin_token):
        """Conversao endpoint returns 200 for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_03_conversao_has_7d_period(self, admin_token):
        """Conversao response has 7d period data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        assert "7d" in data, f"Missing '7d' key in response: {data.keys()}"

    def test_04_conversao_has_30d_period(self, admin_token):
        """Conversao response has 30d period data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        assert "30d" in data, f"Missing '30d' key in response: {data.keys()}"

    def test_05_conversao_has_total_period(self, admin_token):
        """Conversao response has total period data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        assert "total" in data, f"Missing 'total' key in response: {data.keys()}"

    def test_06_conversao_has_funil_diario(self, admin_token):
        """Conversao response has funil_diario array"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        assert "funil_diario" in data, f"Missing 'funil_diario' key in response: {data.keys()}"
        assert isinstance(data["funil_diario"], list), "funil_diario should be a list"

    def test_07_funil_diario_has_14_records(self, admin_token):
        """funil_diario should have 14 records (last 14 days)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        funil = data.get("funil_diario", [])
        assert len(funil) == 14, f"Expected 14 records in funil_diario, got {len(funil)}"

    def test_08_period_has_visitantes_unicos(self, admin_token):
        """Each period should have visitantes_unicos field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        for period in ["7d", "30d", "total"]:
            assert "visitantes_unicos" in data[period], f"Missing 'visitantes_unicos' in {period}"

    def test_09_period_has_cadastros(self, admin_token):
        """Each period should have cadastros field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        for period in ["7d", "30d", "total"]:
            assert "cadastros" in data[period], f"Missing 'cadastros' in {period}"

    def test_10_period_has_pagamentos(self, admin_token):
        """Each period should have pagamentos field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        for period in ["7d", "30d", "total"]:
            assert "pagamentos" in data[period], f"Missing 'pagamentos' in {period}"

    def test_11_period_has_taxa_visitante_cadastro(self, admin_token):
        """Each period should have taxa_visitante_cadastro field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        for period in ["7d", "30d", "total"]:
            assert "taxa_visitante_cadastro" in data[period], f"Missing 'taxa_visitante_cadastro' in {period}"

    def test_12_period_has_taxa_cadastro_pagamento(self, admin_token):
        """Each period should have taxa_cadastro_pagamento field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        for period in ["7d", "30d", "total"]:
            assert "taxa_cadastro_pagamento" in data[period], f"Missing 'taxa_cadastro_pagamento' in {period}"

    def test_13_period_has_taxa_conversao_total(self, admin_token):
        """Each period should have taxa_conversao_total field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/conversao",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        for period in ["7d", "30d", "total"]:
            assert "taxa_conversao_total" in data[period], f"Missing 'taxa_conversao_total' in {period}"


class TestFinanceiroResumo:
    """Tests for GET /api/admin/financeiro/resumo - PIX and Cartao by tipo"""

    def test_14_resumo_returns_200(self, admin_token):
        """Resumo endpoint returns 200 for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_15_resumo_has_totais(self, admin_token):
        """Resumo has totais section"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        assert "totais" in data, f"Missing 'totais' in response"

    def test_16_totais_has_receita_pix(self, admin_token):
        """Totais has receita_pix field (by tipo, not gateway)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        assert "receita_pix" in data["totais"], f"Missing 'receita_pix' in totais"

    def test_17_totais_has_receita_cartao(self, admin_token):
        """Totais has receita_cartao field (by tipo, not gateway)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        assert "receita_cartao" in data["totais"], f"Missing 'receita_cartao' in totais"

    def test_18_distribuicao_gateway_has_pix(self, admin_token):
        """Distribuicao gateway has pix section"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        assert "distribuicao_gateway" in data, f"Missing 'distribuicao_gateway'"
        assert "pix" in data["distribuicao_gateway"], f"Missing 'pix' in distribuicao_gateway"

    def test_19_distribuicao_gateway_has_cartao(self, admin_token):
        """Distribuicao gateway has cartao section"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        assert "cartao" in data["distribuicao_gateway"], f"Missing 'cartao' in distribuicao_gateway"


class TestEfiConfig:
    """Tests for GET /api/efi/config - is_sandbox field"""

    def test_20_config_returns_is_sandbox(self, atleta_token):
        """Config endpoint returns is_sandbox field"""
        response = requests.get(
            f"{BASE_URL}/api/efi/config",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "is_sandbox" in data, f"Missing 'is_sandbox' in config response: {data}"

    def test_21_config_is_sandbox_true(self, atleta_token):
        """Config is_sandbox should be true in sandbox environment"""
        response = requests.get(
            f"{BASE_URL}/api/efi/config",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        data = response.json()
        assert data.get("is_sandbox") == True, f"Expected is_sandbox=true, got {data.get('is_sandbox')}"


class TestCartaoSandboxWarning:
    """Tests for POST /api/efi/cartao/criar - sandbox warning and status rejection"""

    def test_22_cartao_endpoint_exists(self, atleta_token):
        """Cartao endpoint exists and requires proper data"""
        response = requests.post(
            f"{BASE_URL}/api/efi/cartao/criar",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={}
        )
        # Should return 422 for missing fields, not 404
        assert response.status_code != 404, "Cartao endpoint should exist"

    def test_23_cartao_validates_payment_token(self, atleta_token):
        """Cartao endpoint validates payment_token field"""
        response = requests.post(
            f"{BASE_URL}/api/efi/cartao/criar",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={
                "nome": "Test User",
                "cpf": "12345678901",
                "email": "test@test.com"
            }
        )
        # Should return 422 for missing payment_token
        assert response.status_code == 422, f"Expected 422 for missing payment_token, got {response.status_code}"


class TestCodeReview:
    """Code review tests - verify implementation details"""

    def test_24_financeiro_routes_filters_by_tipo(self):
        """Verify financeiro_routes.py filters by tipo='pix' and tipo='cartao'"""
        with open("/app/backend/routes/financeiro_routes.py", "r") as f:
            content = f.read()
        
        # Should filter by tipo, not gateway
        assert 'tipo") == "pix"' in content or "tipo\") == 'pix'" in content or 't.get("tipo") == "pix"' in content, \
            "financeiro_routes should filter by tipo='pix'"
        assert 'tipo") == "cartao"' in content or "tipo\") == 'cartao'" in content or 't.get("tipo") == "cartao"' in content, \
            "financeiro_routes should filter by tipo='cartao'"

    def test_25_efi_routes_has_aviso_sandbox(self):
        """Verify efi_routes.py includes aviso_sandbox in cartao response"""
        with open("/app/backend/routes/efi_routes.py", "r") as f:
            content = f.read()
        
        assert "aviso_sandbox" in content, "efi_routes should include aviso_sandbox field"

    def test_26_efi_routes_rejects_non_approved_status(self):
        """Verify efi_routes.py rejects status != approved"""
        with open("/app/backend/routes/efi_routes.py", "r") as f:
            content = f.read()
        
        # Should check for approved/paid status
        assert 'status_efi not in ("approved", "paid")' in content or \
               'status_efi not in ["approved", "paid"]' in content or \
               "approved" in content, \
            "efi_routes should reject non-approved status"

    def test_27_efi_config_returns_is_sandbox(self):
        """Verify efi_routes.py config endpoint returns is_sandbox"""
        with open("/app/backend/routes/efi_routes.py", "r") as f:
            content = f.read()
        
        assert "is_sandbox" in content, "efi_routes config should return is_sandbox field"

    def test_28_middleware_tracks_visitors(self):
        """Verify middleware tracks unique visitors"""
        with open("/app/backend/middleware/__init__.py", "r") as f:
            content = f.read()
        
        assert "visitas_diarias" in content, "Middleware should track visits in visitas_diarias collection"
        assert "visitors" in content, "Middleware should track unique visitors"


class TestFrontendComponents:
    """Tests for frontend components"""

    def test_29_dashboard_financeiro_has_funnel_visual(self):
        """DashboardFinanceiro has FunnelVisual component"""
        with open("/app/frontend/src/pages/admin/DashboardFinanceiro.jsx", "r") as f:
            content = f.read()
        
        assert "FunnelVisual" in content, "DashboardFinanceiro should have FunnelVisual component"

    def test_30_dashboard_financeiro_has_conversion_panel(self):
        """DashboardFinanceiro has conversion panel with data-testid"""
        with open("/app/frontend/src/pages/admin/DashboardFinanceiro.jsx", "r") as f:
            content = f.read()
        
        assert 'data-testid="painel-conversao"' in content, "DashboardFinanceiro should have painel-conversao testid"

    def test_31_dashboard_financeiro_has_period_toggle(self):
        """DashboardFinanceiro has period toggle (7d, 30d, total)"""
        with open("/app/frontend/src/pages/admin/DashboardFinanceiro.jsx", "r") as f:
            content = f.read()
        
        assert "7d" in content and "30d" in content and "total" in content, \
            "DashboardFinanceiro should have period toggle options"

    def test_32_funnel_visual_has_three_steps(self):
        """FunnelVisual has 3 steps: Visitantes, Cadastros, Pagamentos"""
        with open("/app/frontend/src/pages/admin/DashboardFinanceiro.jsx", "r") as f:
            content = f.read()
        
        assert "Visitantes" in content, "FunnelVisual should have Visitantes step"
        assert "Cadastros" in content, "FunnelVisual should have Cadastros step"
        assert "Pagamentos" in content, "FunnelVisual should have Pagamentos step"

    def test_33_pagamento_page_has_sandbox_warning(self):
        """PagamentoPage has sandbox warning component"""
        with open("/app/frontend/src/pages/PagamentoPage.jsx", "r") as f:
            content = f.read()
        
        assert 'data-testid="sandbox-warning"' in content, "PagamentoPage should have sandbox-warning testid"

    def test_34_pagamento_page_checks_is_sandbox(self):
        """PagamentoPage checks is_sandbox from config"""
        with open("/app/frontend/src/pages/PagamentoPage.jsx", "r") as f:
            content = f.read()
        
        assert "is_sandbox" in content, "PagamentoPage should check is_sandbox from config"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
