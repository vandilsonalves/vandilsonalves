# /app/backend/tests/test_iter114_precos_dinamicos.py
# Tests for dynamic pricing feature - Iteration 114
# Features: Editable prices for Atleta Premium plan via Admin dashboard
# Endpoints: GET/POST /api/admin/financeiro/config-precos, GET /api/financeiro/config-precos-publico

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


class TestPrecosPublico:
    """Tests for public pricing endpoint (no auth required)"""

    def test_get_precos_publico_returns_200(self):
        """GET /api/financeiro/config-precos-publico should return 200"""
        res = requests.get(f"{BASE_URL}/api/financeiro/config-precos-publico")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        print("PASS: GET /api/financeiro/config-precos-publico returns 200")

    def test_get_precos_publico_has_required_fields(self):
        """Public pricing endpoint should return all required fields"""
        res = requests.get(f"{BASE_URL}/api/financeiro/config-precos-publico")
        assert res.status_code == 200
        data = res.json()
        
        required_fields = [
            "preco_original", "preco_desconto", "parcelas", "valor_parcela",
            "max_parcelas_cartao", "data_fim_oferta", "validade_acesso",
            "nome_plano", "preco_pos_oferta", "parcelas_pos_oferta", "ativo"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
            print(f"  - Field '{field}' present: {data[field]}")
        
        print("PASS: All required fields present in public pricing response")

    def test_get_precos_publico_values_are_valid(self):
        """Public pricing values should be valid numbers/strings"""
        res = requests.get(f"{BASE_URL}/api/financeiro/config-precos-publico")
        assert res.status_code == 200
        data = res.json()
        
        # Numeric validations
        assert isinstance(data["preco_original"], (int, float)) and data["preco_original"] > 0
        assert isinstance(data["preco_desconto"], (int, float)) and data["preco_desconto"] > 0
        assert isinstance(data["parcelas"], int) and data["parcelas"] >= 1
        assert isinstance(data["valor_parcela"], (int, float)) and data["valor_parcela"] > 0
        assert isinstance(data["max_parcelas_cartao"], int) and data["max_parcelas_cartao"] >= 1
        
        # String validations (dates)
        assert isinstance(data["data_fim_oferta"], str) and len(data["data_fim_oferta"]) == 10
        assert isinstance(data["validade_acesso"], str) and len(data["validade_acesso"]) == 10
        
        print(f"PASS: Pricing values are valid - desconto={data['preco_desconto']}, parcelas={data['parcelas']}")


class TestPrecosAdmin:
    """Tests for admin pricing endpoints (auth required)"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin before each test"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
        self.admin_token = login_res.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.admin_token}"}

    def test_get_admin_precos_requires_auth(self):
        """GET /api/admin/financeiro/config-precos should require auth"""
        res = requests.get(f"{BASE_URL}/api/admin/financeiro/config-precos")
        assert res.status_code in [401, 403], f"Expected 401/403 without auth, got {res.status_code}"
        print("PASS: Admin pricing endpoint requires authentication")

    def test_get_admin_precos_returns_200_with_auth(self):
        """GET /api/admin/financeiro/config-precos should return 200 with admin auth"""
        res = requests.get(f"{BASE_URL}/api/admin/financeiro/config-precos", headers=self.headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        print("PASS: GET /api/admin/financeiro/config-precos returns 200 with admin auth")

    def test_get_admin_precos_has_all_fields(self):
        """Admin pricing endpoint should return all config fields"""
        res = requests.get(f"{BASE_URL}/api/admin/financeiro/config-precos", headers=self.headers)
        assert res.status_code == 200
        data = res.json()
        
        required_fields = [
            "id", "preco_original", "preco_desconto", "parcelas", "valor_parcela",
            "max_parcelas_cartao", "data_fim_oferta", "validade_acesso",
            "nome_plano", "preco_pos_oferta", "parcelas_pos_oferta", "ativo"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        assert data["id"] == "precos_premium", f"Expected id='precos_premium', got {data['id']}"
        print("PASS: Admin pricing endpoint returns all config fields")

    def test_post_admin_precos_requires_auth(self):
        """POST /api/admin/financeiro/config-precos should require auth"""
        res = requests.post(f"{BASE_URL}/api/admin/financeiro/config-precos", json={
            "preco_original": 197.00,
            "preco_desconto": 97.00,
            "parcelas": 5,
            "valor_parcela": 19.40,
            "data_fim_oferta": "2026-12-14",
            "validade_acesso": "2026-12-31",
        })
        assert res.status_code in [401, 403, 422], f"Expected 401/403/422 without auth, got {res.status_code}"
        print("PASS: POST admin pricing endpoint requires authentication")

    def test_post_admin_precos_saves_and_recalculates(self):
        """POST /api/admin/financeiro/config-precos should save and recalculate valor_parcela"""
        # First get current values
        get_res = requests.get(f"{BASE_URL}/api/admin/financeiro/config-precos", headers=self.headers)
        original_data = get_res.json()
        
        # Update with new values
        new_preco_desconto = 100.00
        new_parcelas = 4
        expected_valor_parcela = round(new_preco_desconto / new_parcelas, 2)  # 25.00
        
        update_payload = {
            "preco_original": original_data.get("preco_original", 197.00),
            "preco_desconto": new_preco_desconto,
            "parcelas": new_parcelas,
            "valor_parcela": 0,  # Should be recalculated
            "max_parcelas_cartao": original_data.get("max_parcelas_cartao", 12),
            "data_fim_oferta": original_data.get("data_fim_oferta", "2026-12-14"),
            "validade_acesso": original_data.get("validade_acesso", "2026-12-31"),
            "nome_plano": original_data.get("nome_plano", "Atleta Premium"),
            "descricao_oferta": original_data.get("descricao_oferta", ""),
            "preco_pos_oferta": original_data.get("preco_pos_oferta", 119.00),
            "parcelas_pos_oferta": original_data.get("parcelas_pos_oferta", 12),
            "ativo": True,
        }
        
        post_res = requests.post(
            f"{BASE_URL}/api/admin/financeiro/config-precos",
            headers=self.headers,
            json=update_payload
        )
        assert post_res.status_code == 200, f"Expected 200, got {post_res.status_code}: {post_res.text}"
        
        result = post_res.json()
        assert "config" in result, "Response should contain 'config' field"
        
        saved_config = result["config"]
        assert saved_config["preco_desconto"] == new_preco_desconto
        assert saved_config["parcelas"] == new_parcelas
        assert saved_config["valor_parcela"] == expected_valor_parcela, \
            f"Expected valor_parcela={expected_valor_parcela}, got {saved_config['valor_parcela']}"
        
        print(f"PASS: POST saves and recalculates valor_parcela correctly ({expected_valor_parcela})")
        
        # Restore original values
        restore_payload = {
            "preco_original": original_data.get("preco_original", 197.00),
            "preco_desconto": original_data.get("preco_desconto", 97.00),
            "parcelas": original_data.get("parcelas", 5),
            "valor_parcela": original_data.get("valor_parcela", 19.40),
            "max_parcelas_cartao": original_data.get("max_parcelas_cartao", 12),
            "data_fim_oferta": original_data.get("data_fim_oferta", "2026-12-14"),
            "validade_acesso": original_data.get("validade_acesso", "2026-12-31"),
            "nome_plano": original_data.get("nome_plano", "Atleta Premium"),
            "descricao_oferta": original_data.get("descricao_oferta", ""),
            "preco_pos_oferta": original_data.get("preco_pos_oferta", 119.00),
            "parcelas_pos_oferta": original_data.get("parcelas_pos_oferta", 12),
            "ativo": True,
        }
        requests.post(f"{BASE_URL}/api/admin/financeiro/config-precos", headers=self.headers, json=restore_payload)

    def test_post_admin_precos_validates_preco_desconto(self):
        """POST should reject preco_desconto <= 0"""
        invalid_payload = {
            "preco_original": 197.00,
            "preco_desconto": 0,  # Invalid
            "parcelas": 5,
            "valor_parcela": 19.40,
            "max_parcelas_cartao": 12,
            "data_fim_oferta": "2026-12-14",
            "validade_acesso": "2026-12-31",
        }
        res = requests.post(
            f"{BASE_URL}/api/admin/financeiro/config-precos",
            headers=self.headers,
            json=invalid_payload
        )
        assert res.status_code == 400, f"Expected 400 for invalid preco_desconto, got {res.status_code}"
        print("PASS: POST validates preco_desconto > 0")

    def test_post_admin_precos_validates_parcelas(self):
        """POST should reject parcelas < 1"""
        invalid_payload = {
            "preco_original": 197.00,
            "preco_desconto": 97.00,
            "parcelas": 0,  # Invalid
            "valor_parcela": 19.40,
            "max_parcelas_cartao": 12,
            "data_fim_oferta": "2026-12-14",
            "validade_acesso": "2026-12-31",
        }
        res = requests.post(
            f"{BASE_URL}/api/admin/financeiro/config-precos",
            headers=self.headers,
            json=invalid_payload
        )
        assert res.status_code == 400, f"Expected 400 for invalid parcelas, got {res.status_code}"
        print("PASS: POST validates parcelas >= 1")


class TestFinanceiroResumo:
    """Tests for financial dashboard summary endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin before each test"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
        self.admin_token = login_res.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.admin_token}"}

    def test_get_resumo_financeiro_returns_200(self):
        """GET /api/admin/financeiro/resumo should return 200"""
        res = requests.get(f"{BASE_URL}/api/admin/financeiro/resumo", headers=self.headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        print("PASS: GET /api/admin/financeiro/resumo returns 200")

    def test_get_resumo_financeiro_has_required_sections(self):
        """Financial summary should have all required sections"""
        res = requests.get(f"{BASE_URL}/api/admin/financeiro/resumo", headers=self.headers)
        assert res.status_code == 200
        data = res.json()
        
        required_sections = ["totais", "distribuicao_gateway", "receita_diaria", "receita_mensal", "transacoes_recentes"]
        for section in required_sections:
            assert section in data, f"Missing section: {section}"
        
        # Check totais fields
        totais = data["totais"]
        assert "receita_total" in totais
        assert "receita_pix" in totais
        assert "receita_cartao" in totais
        assert "total_transacoes" in totais
        
        print("PASS: Financial summary has all required sections")


class TestPagamentosPlanos:
    """Tests for /api/pagamentos/planos endpoint (dynamic plan data)"""

    def test_get_planos_returns_200(self):
        """GET /api/pagamentos/planos should return 200"""
        res = requests.get(f"{BASE_URL}/api/pagamentos/planos")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        print("PASS: GET /api/pagamentos/planos returns 200")

    def test_get_planos_has_dynamic_values(self):
        """Planos endpoint should return dynamic values from DB config"""
        # First get the public pricing config
        precos_res = requests.get(f"{BASE_URL}/api/financeiro/config-precos-publico")
        precos = precos_res.json()
        
        # Then get planos
        planos_res = requests.get(f"{BASE_URL}/api/pagamentos/planos")
        assert planos_res.status_code == 200
        planos = planos_res.json()
        
        assert "plano_vigente" in planos, "Missing plano_vigente"
        plano = planos["plano_vigente"]
        
        # Verify values match the config
        assert plano["valor"] == precos["preco_desconto"], \
            f"Plano valor ({plano['valor']}) should match preco_desconto ({precos['preco_desconto']})"
        assert plano["valor_original"] == precos["preco_original"], \
            f"Plano valor_original ({plano['valor_original']}) should match preco_original ({precos['preco_original']})"
        
        print(f"PASS: Planos endpoint returns dynamic values (valor={plano['valor']}, original={plano['valor_original']})")


class TestAtletaAccess:
    """Tests to verify atleta can access public pricing"""

    def test_atleta_can_access_public_precos(self):
        """Atleta should be able to access public pricing endpoint"""
        # Login as atleta
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        assert login_res.status_code == 200, f"Atleta login failed: {login_res.text}"
        
        # Access public pricing (no auth needed)
        res = requests.get(f"{BASE_URL}/api/financeiro/config-precos-publico")
        assert res.status_code == 200
        data = res.json()
        assert "preco_desconto" in data
        print("PASS: Atleta can access public pricing endpoint")

    def test_atleta_cannot_access_admin_precos(self):
        """Atleta should NOT be able to access admin pricing endpoint"""
        # Login as atleta
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        assert login_res.status_code == 200
        atleta_token = login_res.json().get("token")
        
        # Try to access admin pricing
        res = requests.get(
            f"{BASE_URL}/api/admin/financeiro/config-precos",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert res.status_code in [401, 403], f"Expected 401/403 for atleta, got {res.status_code}"
        print("PASS: Atleta cannot access admin pricing endpoint")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
