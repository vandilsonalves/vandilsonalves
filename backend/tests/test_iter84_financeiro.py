# /app/backend/tests/test_iter84_financeiro.py
# Tests for Financial Dashboard API - GET /api/admin/financeiro/resumo
# Iteration 84: Admin Financial Dashboard with KPIs, charts, and transactions table

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from iteration_83
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


class TestFinanceiroAPI:
    """Tests for GET /api/admin/financeiro/resumo endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_admin_token(self):
        """Get admin authentication token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        return None
    
    def get_atleta_token(self):
        """Get non-admin (atleta) authentication token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        return None
    
    # ============ Authentication Tests ============
    
    def test_01_financeiro_requires_auth(self):
        """Test that /admin/financeiro/resumo requires authentication"""
        response = self.session.get(f"{BASE_URL}/api/admin/financeiro/resumo")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASSED: Financeiro endpoint requires authentication")
    
    def test_02_financeiro_rejects_non_admin(self):
        """Test that non-admin users get 403 Forbidden"""
        token = self.get_atleta_token()
        if not token:
            pytest.skip("Could not get atleta token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("PASSED: Non-admin users rejected with 403")
    
    def test_03_financeiro_allows_admin(self):
        """Test that admin users can access the endpoint"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200 for admin, got {response.status_code}"
        print("PASSED: Admin users can access financeiro endpoint")
    
    # ============ Response Structure Tests ============
    
    def test_04_response_has_totais_section(self):
        """Test that response contains 'totais' section with required fields"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "totais" in data, "Response missing 'totais' section"
        totais = data["totais"]
        
        # Check required fields
        required_fields = [
            "receita_total", "receita_pix", "receita_cartao", 
            "ticket_medio", "total_transacoes", "transacoes_pagas", "transacoes_pendentes"
        ]
        for field in required_fields:
            assert field in totais, f"totais missing field: {field}"
        
        print(f"PASSED: totais section has all required fields: {list(totais.keys())}")
    
    def test_05_response_has_distribuicao_gateway(self):
        """Test that response contains 'distribuicao_gateway' with pix and cartao"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "distribuicao_gateway" in data, "Response missing 'distribuicao_gateway'"
        dist = data["distribuicao_gateway"]
        
        assert "pix" in dist, "distribuicao_gateway missing 'pix'"
        assert "cartao" in dist, "distribuicao_gateway missing 'cartao'"
        
        # Check pix has count and valor
        assert "count" in dist["pix"], "pix missing 'count'"
        assert "valor" in dist["pix"], "pix missing 'valor'"
        
        # Check cartao has count and valor
        assert "count" in dist["cartao"], "cartao missing 'count'"
        assert "valor" in dist["cartao"], "cartao missing 'valor'"
        
        print(f"PASSED: distribuicao_gateway has pix={dist['pix']} and cartao={dist['cartao']}")
    
    def test_06_response_has_receita_diaria(self):
        """Test that response contains 'receita_diaria' array (31 days)"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "receita_diaria" in data, "Response missing 'receita_diaria'"
        receita_diaria = data["receita_diaria"]
        
        assert isinstance(receita_diaria, list), "receita_diaria should be a list"
        assert len(receita_diaria) == 31, f"receita_diaria should have 31 days, got {len(receita_diaria)}"
        
        # Check structure of first item
        if receita_diaria:
            first = receita_diaria[0]
            assert "data" in first, "receita_diaria item missing 'data'"
            assert "valor" in first, "receita_diaria item missing 'valor'"
        
        print(f"PASSED: receita_diaria has {len(receita_diaria)} days")
    
    def test_07_response_has_receita_mensal(self):
        """Test that response contains 'receita_mensal' array (up to 12 months)"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "receita_mensal" in data, "Response missing 'receita_mensal'"
        receita_mensal = data["receita_mensal"]
        
        assert isinstance(receita_mensal, list), "receita_mensal should be a list"
        assert len(receita_mensal) <= 12, f"receita_mensal should have max 12 months, got {len(receita_mensal)}"
        
        # Check structure of first item
        if receita_mensal:
            first = receita_mensal[0]
            assert "mes" in first, "receita_mensal item missing 'mes'"
            assert "valor" in first, "receita_mensal item missing 'valor'"
        
        print(f"PASSED: receita_mensal has {len(receita_mensal)} months")
    
    def test_08_response_has_transacoes_recentes(self):
        """Test that response contains 'transacoes_recentes' array (max 20)"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "transacoes_recentes" in data, "Response missing 'transacoes_recentes'"
        transacoes = data["transacoes_recentes"]
        
        assert isinstance(transacoes, list), "transacoes_recentes should be a list"
        assert len(transacoes) <= 20, f"transacoes_recentes should have max 20, got {len(transacoes)}"
        
        print(f"PASSED: transacoes_recentes has {len(transacoes)} transactions")
    
    def test_09_transacoes_recentes_structure(self):
        """Test that transacoes_recentes items have required fields"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        transacoes = data.get("transacoes_recentes", [])
        if not transacoes:
            pytest.skip("No transactions to verify structure")
        
        # Check required fields in first transaction
        tx = transacoes[0]
        required_fields = ["gateway", "amount", "payment_status", "user_nome", "data_criacao"]
        for field in required_fields:
            assert field in tx, f"Transaction missing field: {field}"
        
        print(f"PASSED: Transaction has required fields: {list(tx.keys())}")
    
    # ============ Data Type Tests ============
    
    def test_10_totais_numeric_values(self):
        """Test that totais fields are numeric"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        totais = data["totais"]
        
        # Check numeric fields
        assert isinstance(totais["receita_total"], (int, float)), "receita_total should be numeric"
        assert isinstance(totais["receita_pix"], (int, float)), "receita_pix should be numeric"
        assert isinstance(totais["receita_cartao"], (int, float)), "receita_cartao should be numeric"
        assert isinstance(totais["ticket_medio"], (int, float)), "ticket_medio should be numeric"
        assert isinstance(totais["total_transacoes"], int), "total_transacoes should be int"
        assert isinstance(totais["transacoes_pagas"], int), "transacoes_pagas should be int"
        assert isinstance(totais["transacoes_pendentes"], int), "transacoes_pendentes should be int"
        
        print(f"PASSED: All totais fields have correct numeric types")
    
    def test_11_receita_values_non_negative(self):
        """Test that receita values are non-negative"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        totais = data["totais"]
        
        assert totais["receita_total"] >= 0, "receita_total should be non-negative"
        assert totais["receita_pix"] >= 0, "receita_pix should be non-negative"
        assert totais["receita_cartao"] >= 0, "receita_cartao should be non-negative"
        assert totais["ticket_medio"] >= 0, "ticket_medio should be non-negative"
        
        print(f"PASSED: All receita values are non-negative")
    
    def test_12_gateway_distribution_consistency(self):
        """Test that gateway distribution values are consistent"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        dist = data["distribuicao_gateway"]
        
        # Count and valor should be non-negative
        assert dist["pix"]["count"] >= 0, "pix count should be non-negative"
        assert dist["pix"]["valor"] >= 0, "pix valor should be non-negative"
        assert dist["cartao"]["count"] >= 0, "cartao count should be non-negative"
        assert dist["cartao"]["valor"] >= 0, "cartao valor should be non-negative"
        
        print(f"PASSED: Gateway distribution values are consistent")
    
    # ============ Business Logic Tests ============
    
    def test_13_receita_diaria_date_format(self):
        """Test that receita_diaria dates are in YYYY-MM-DD format"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        receita_diaria = data["receita_diaria"]
        if receita_diaria:
            # Check date format (YYYY-MM-DD)
            import re
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            for item in receita_diaria[:5]:  # Check first 5
                assert re.match(date_pattern, item["data"]), f"Invalid date format: {item['data']}"
        
        print(f"PASSED: receita_diaria dates are in correct format")
    
    def test_14_receita_mensal_month_format(self):
        """Test that receita_mensal months are in YYYY-MM format"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        receita_mensal = data["receita_mensal"]
        if receita_mensal:
            # Check month format (YYYY-MM)
            import re
            month_pattern = r'^\d{4}-\d{2}$'
            for item in receita_mensal[:5]:  # Check first 5
                assert re.match(month_pattern, item["mes"]), f"Invalid month format: {item['mes']}"
        
        print(f"PASSED: receita_mensal months are in correct format")
    
    def test_15_transacoes_sorted_by_date_desc(self):
        """Test that transacoes_recentes are sorted by date descending"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        transacoes = data["transacoes_recentes"]
        if len(transacoes) >= 2:
            # Check that dates are in descending order
            dates = [tx.get("data_criacao", "") for tx in transacoes if tx.get("data_criacao")]
            for i in range(len(dates) - 1):
                assert dates[i] >= dates[i+1], f"Transactions not sorted: {dates[i]} < {dates[i+1]}"
        
        print(f"PASSED: transacoes_recentes are sorted by date descending")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
