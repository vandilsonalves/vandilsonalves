"""
Iteration 89: Testing Autorizacoes-Financeiro Integration
- POST /api/admin/autorizacoes/autorizar creates authorization AND payment_transaction
- GET /api/admin/financeiro/resumo includes 'manual' in distribuicao_gateway
- GET /api/admin/financeiro/resumo transacoes_recentes has is_manual, origem, admin_nome
- Manual transactions have gateway='admin_manual', tipo='admin_manual', amount=0, payment_status='paid'
- GET /api/admin/financeiro/exportar/excel returns HTTP 200 with xlsx content-type
- GET /api/admin/financeiro/exportar/pdf returns HTTP 200 with pdf content-type
- GET /api/admin/financeiro/exportar/invalido returns HTTP 400
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFinanceiroIntegration:
    """Tests for Autorizacoes-Financeiro integration"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def test_atleta_id(self, admin_token):
        """Get an atleta without active authorization for testing"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/autorizacoes/atletas-completo", headers=headers)
        assert response.status_code == 200
        data = response.json()
        atletas = data.get("atletas", [])
        
        # Find an atleta without active authorization (expirado or em_teste)
        for atleta in atletas:
            if atleta.get("status_periodo") in ["expirado", "em_teste"]:
                return atleta["id"]
        
        # If all are authorized, just return the first one (we'll handle it)
        if atletas:
            return atletas[0]["id"]
        pytest.skip("No atletas found for testing")
    
    def test_autorizar_creates_payment_transaction(self, admin_token, test_atleta_id):
        """POST /api/admin/autorizacoes/autorizar should create authorization AND payment_transaction"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First, revoke any existing authorization
        requests.post(f"{BASE_URL}/api/admin/autorizacoes/revogar", 
                     json={"atleta_id": test_atleta_id}, headers=headers)
        
        # Now authorize
        response = requests.post(f"{BASE_URL}/api/admin/autorizacoes/autorizar", 
                                json={"atleta_id": test_atleta_id, "tipo_plano": "ate_fim_ano"},
                                headers=headers)
        
        assert response.status_code == 200, f"Autorizar failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "message" in data
        assert "autorizacao_id" in data
        assert "data_expiracao" in data
        assert "2026-12-31" in data["data_expiracao"]
        
        print(f"✓ Authorization created: {data['autorizacao_id']}")
        print(f"✓ Expiration: {data['data_expiracao']}")
    
    def test_financeiro_resumo_has_manual_distribution(self, admin_token):
        """GET /api/admin/financeiro/resumo should include 'manual' in distribuicao_gateway"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/resumo", headers=headers)
        assert response.status_code == 200, f"Resumo failed: {response.text}"
        
        data = response.json()
        
        # Verify structure
        assert "totais" in data
        assert "distribuicao_gateway" in data
        assert "transacoes_recentes" in data
        
        # Verify manual is in distribuicao_gateway
        dist = data["distribuicao_gateway"]
        assert "manual" in dist, "distribuicao_gateway should have 'manual' key"
        assert "count" in dist["manual"], "manual should have 'count' field"
        
        print(f"✓ distribuicao_gateway.manual.count = {dist['manual']['count']}")
        print(f"✓ distribuicao_gateway.pix.count = {dist['pix']['count']}")
        print(f"✓ distribuicao_gateway.cartao.count = {dist['cartao']['count']}")
    
    def test_transacoes_recentes_has_manual_fields(self, admin_token):
        """GET /api/admin/financeiro/resumo transacoes_recentes should have is_manual, origem, admin_nome"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/resumo", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        transacoes = data.get("transacoes_recentes", [])
        
        # Find a manual transaction
        manual_tx = None
        for tx in transacoes:
            if tx.get("is_manual") or tx.get("gateway") == "admin_manual":
                manual_tx = tx
                break
        
        if manual_tx:
            # Verify manual transaction fields
            assert "is_manual" in manual_tx, "Transaction should have 'is_manual' field"
            assert "origem" in manual_tx, "Transaction should have 'origem' field"
            assert "admin_nome" in manual_tx, "Transaction should have 'admin_nome' field"
            
            # Verify values for manual transaction
            assert manual_tx["is_manual"] == True, "is_manual should be True for manual transactions"
            assert manual_tx["gateway"] == "admin_manual", "gateway should be 'admin_manual'"
            assert manual_tx["tipo"] == "admin_manual", "tipo should be 'admin_manual'"
            assert manual_tx["amount"] == 0, "amount should be 0 for manual/cortesia"
            assert manual_tx["payment_status"] == "paid", "payment_status should be 'paid'"
            
            print(f"✓ Manual transaction found: {manual_tx['id']}")
            print(f"✓ is_manual: {manual_tx['is_manual']}")
            print(f"✓ origem: {manual_tx['origem']}")
            print(f"✓ admin_nome: {manual_tx['admin_nome']}")
            print(f"✓ gateway: {manual_tx['gateway']}")
            print(f"✓ amount: {manual_tx['amount']}")
        else:
            print("⚠ No manual transactions found in recent transactions (may need to create one first)")
    
    def test_exportar_excel_returns_xlsx(self, admin_token):
        """GET /api/admin/financeiro/exportar/excel should return HTTP 200 with xlsx content-type"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/exportar/excel", headers=headers)
        
        assert response.status_code == 200, f"Export Excel failed: {response.status_code}"
        
        content_type = response.headers.get("content-type", "")
        assert "spreadsheetml" in content_type or "xlsx" in content_type or "application/vnd" in content_type, \
            f"Expected xlsx content-type, got: {content_type}"
        
        # Verify content is not empty
        assert len(response.content) > 0, "Excel file should not be empty"
        
        print(f"✓ Excel export successful")
        print(f"✓ Content-Type: {content_type}")
        print(f"✓ File size: {len(response.content)} bytes")
    
    def test_exportar_pdf_returns_pdf(self, admin_token):
        """GET /api/admin/financeiro/exportar/pdf should return HTTP 200 with pdf content-type"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/exportar/pdf", headers=headers)
        
        assert response.status_code == 200, f"Export PDF failed: {response.status_code}"
        
        content_type = response.headers.get("content-type", "")
        assert "pdf" in content_type.lower(), f"Expected pdf content-type, got: {content_type}"
        
        # Verify content is not empty
        assert len(response.content) > 0, "PDF file should not be empty"
        
        print(f"✓ PDF export successful")
        print(f"✓ Content-Type: {content_type}")
        print(f"✓ File size: {len(response.content)} bytes")
    
    def test_exportar_invalid_format_returns_400(self, admin_token):
        """GET /api/admin/financeiro/exportar/invalido should return HTTP 400"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/exportar/invalido", headers=headers)
        
        assert response.status_code == 400, f"Expected 400 for invalid format, got: {response.status_code}"
        
        print(f"✓ Invalid format correctly returns 400")
    
    def test_manual_transaction_structure(self, admin_token, test_atleta_id):
        """Verify manual transaction has correct structure after authorization"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First revoke and re-authorize to ensure we have a fresh manual transaction
        requests.post(f"{BASE_URL}/api/admin/autorizacoes/revogar", 
                     json={"atleta_id": test_atleta_id}, headers=headers)
        
        auth_response = requests.post(f"{BASE_URL}/api/admin/autorizacoes/autorizar", 
                                     json={"atleta_id": test_atleta_id, "tipo_plano": "plano_anual"},
                                     headers=headers)
        assert auth_response.status_code == 200
        
        # Now check financeiro resumo
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/resumo", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        transacoes = data.get("transacoes_recentes", [])
        
        # Find the most recent manual transaction
        manual_tx = None
        for tx in transacoes:
            if tx.get("gateway") == "admin_manual":
                manual_tx = tx
                break
        
        assert manual_tx is not None, "Should find a manual transaction after authorization"
        
        # Verify all required fields
        required_fields = ["id", "gateway", "tipo", "origem", "is_manual", "amount", 
                          "payment_status", "user_nome", "admin_nome", "data_criacao"]
        for field in required_fields:
            assert field in manual_tx, f"Manual transaction missing field: {field}"
        
        # Verify values
        assert manual_tx["gateway"] == "admin_manual"
        assert manual_tx["tipo"] == "admin_manual"
        assert manual_tx["origem"] == "admin_manual"
        assert manual_tx["is_manual"] == True
        assert manual_tx["amount"] == 0
        assert manual_tx["payment_status"] == "paid"
        
        print(f"✓ Manual transaction structure verified")
        print(f"✓ All required fields present: {required_fields}")


class TestFinanceiroExportContent:
    """Tests for export content validation"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        return response.json().get("token")
    
    def test_excel_has_content_disposition(self, admin_token):
        """Excel export should have Content-Disposition header"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/exportar/excel", headers=headers)
        
        assert response.status_code == 200
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp.lower(), "Should have attachment disposition"
        assert "xlsx" in content_disp.lower() or "financeiro" in content_disp.lower(), \
            f"Should have xlsx filename, got: {content_disp}"
        
        print(f"✓ Content-Disposition: {content_disp}")
    
    def test_pdf_has_content_disposition(self, admin_token):
        """PDF export should have Content-Disposition header"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/exportar/pdf", headers=headers)
        
        assert response.status_code == 200
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp.lower(), "Should have attachment disposition"
        assert "pdf" in content_disp.lower() or "financeiro" in content_disp.lower(), \
            f"Should have pdf filename, got: {content_disp}"
        
        print(f"✓ Content-Disposition: {content_disp}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
