# /app/backend/tests/test_iter81_efi_pix.py
# Tests for Efí Bank PIX integration (iteration 81)
# Tests: POST /api/efi/pix/criar, GET /api/efi/pix/status/{txid}, POST /api/efi/webhook/pix
# Also tests existing payment endpoints: GET /api/pagamentos/planos, GET /api/pagamentos/meu-plano

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEfiBankPix:
    """Tests for Efí Bank PIX integration"""
    
    @pytest.fixture(scope="class")
    def atleta_token(self):
        """Get authentication token for atleta user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teste.dono@teste.com",
            "password": "123456"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        pytest.skip("Authentication failed for atleta user")
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get authentication token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        pytest.skip("Authentication failed for admin user")
    
    # ==================== EXISTING PAYMENT ENDPOINTS ====================
    
    def test_01_planos_endpoint_returns_plano_vigente(self):
        """GET /api/pagamentos/planos - Returns plano_vigente with correct structure"""
        response = requests.get(f"{BASE_URL}/api/pagamentos/planos")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "plano_vigente" in data, "Response should contain plano_vigente"
        assert "eh_periodo_lancamento" in data, "Response should contain eh_periodo_lancamento"
        
        plano = data["plano_vigente"]
        assert plano["id"] == "atleta_premium_lancamento", "Should be lancamento plan"
        assert plano["valor"] == 97.00, "Valor should be 97.00"
        assert plano["valor_original"] == 197.00, "Valor original should be 197.00"
        print("PASSED: /api/pagamentos/planos returns correct plano_vigente")
    
    def test_02_meu_plano_requires_auth(self):
        """GET /api/pagamentos/meu-plano - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/pagamentos/meu-plano")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASSED: /api/pagamentos/meu-plano requires authentication")
    
    def test_03_meu_plano_returns_user_plan_info(self, atleta_token):
        """GET /api/pagamentos/meu-plano - Returns user plan info"""
        response = requests.get(
            f"{BASE_URL}/api/pagamentos/meu-plano",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Response should contain status"
        assert "tem_acesso_premium" in data, "Response should contain tem_acesso_premium"
        assert "plano_vigente" in data, "Response should contain plano_vigente"
        print(f"PASSED: /api/pagamentos/meu-plano returns user plan info (status: {data['status']})")
    
    def test_04_meu_plano_admin_is_premium(self, admin_token):
        """GET /api/pagamentos/meu-plano - Admin always has premium access"""
        response = requests.get(
            f"{BASE_URL}/api/pagamentos/meu-plano",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "autorizado", "Admin should be autorizado"
        assert data["tem_acesso_premium"] == True, "Admin should have premium access"
        assert data["tipo"] == "admin", "Admin tipo should be 'admin'"
        print("PASSED: Admin has premium access")
    
    # ==================== EFÍ BANK PIX ENDPOINTS ====================
    
    def test_05_pix_criar_requires_auth(self):
        """POST /api/efi/pix/criar - Requires authentication"""
        response = requests.post(f"{BASE_URL}/api/efi/pix/criar", json={})
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASSED: /api/efi/pix/criar requires authentication")
    
    def test_06_pix_criar_returns_txid_and_qrcode(self, atleta_token):
        """POST /api/efi/pix/criar - Creates PIX charge and returns txid, qrcode, status ATIVA"""
        response = requests.post(
            f"{BASE_URL}/api/efi/pix/criar",
            headers={
                "Authorization": f"Bearer {atleta_token}",
                "Content-Type": "application/json"
            },
            json={}
        )
        
        # May return 400 if user already has premium, or 200/201 if successful
        if response.status_code == 400:
            data = response.json()
            if "ja possui acesso Premium" in data.get("detail", ""):
                print("SKIPPED: User already has premium access")
                pytest.skip("User already has premium access")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "txid" in data, "Response should contain txid"
        assert "status" in data, "Response should contain status"
        assert "qrcode" in data, "Response should contain qrcode"
        assert "valor" in data, "Response should contain valor"
        assert "plano" in data, "Response should contain plano"
        
        assert data["status"] == "ATIVA", f"Status should be ATIVA, got {data['status']}"
        assert data["valor"] == "97.00", f"Valor should be 97.00, got {data['valor']}"
        assert data["plano"] == "Atleta Premium", f"Plano should be 'Atleta Premium', got {data['plano']}"
        
        # QR Code should have qrcode and imagemQrcode
        qrcode = data["qrcode"]
        if qrcode:
            assert "qrcode" in qrcode, "QR Code should contain copia-cola code"
            assert "imagemQrcode" in qrcode, "QR Code should contain image"
        
        print(f"PASSED: PIX charge created with txid={data['txid']}, status={data['status']}")
        return data["txid"]
    
    def test_07_pix_status_requires_auth(self):
        """GET /api/efi/pix/status/{txid} - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/efi/pix/status/test-txid")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASSED: /api/efi/pix/status requires authentication")
    
    def test_08_pix_status_returns_404_for_invalid_txid(self, atleta_token):
        """GET /api/efi/pix/status/{txid} - Returns 404 for invalid txid"""
        response = requests.get(
            f"{BASE_URL}/api/efi/pix/status/invalid-txid-12345",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASSED: /api/efi/pix/status returns 404 for invalid txid")
    
    def test_09_pix_status_returns_charge_status(self, atleta_token):
        """GET /api/efi/pix/status/{txid} - Returns status for valid txid"""
        # First create a PIX charge
        create_response = requests.post(
            f"{BASE_URL}/api/efi/pix/criar",
            headers={
                "Authorization": f"Bearer {atleta_token}",
                "Content-Type": "application/json"
            },
            json={}
        )
        
        if create_response.status_code == 400:
            data = create_response.json()
            if "ja possui acesso Premium" in data.get("detail", ""):
                print("SKIPPED: User already has premium access")
                pytest.skip("User already has premium access")
        
        if create_response.status_code != 200:
            pytest.skip(f"Could not create PIX charge: {create_response.text}")
        
        txid = create_response.json()["txid"]
        
        # Now check status
        status_response = requests.get(
            f"{BASE_URL}/api/efi/pix/status/{txid}",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        
        assert status_response.status_code == 200, f"Expected 200, got {status_response.status_code}"
        
        data = status_response.json()
        assert "status" in data, "Response should contain status"
        assert "payment_status" in data, "Response should contain payment_status"
        assert "plano" in data, "Response should contain plano"
        
        # Status should be ATIVA (pending) or CONCLUIDA (paid)
        assert data["status"] in ["ATIVA", "CONCLUIDA"], f"Status should be ATIVA or CONCLUIDA, got {data['status']}"
        print(f"PASSED: PIX status returned for txid={txid}, status={data['status']}")
    
    def test_10_webhook_pix_endpoint_exists(self):
        """POST /api/efi/webhook/pix - Webhook endpoint exists and returns ok"""
        response = requests.post(
            f"{BASE_URL}/api/efi/webhook/pix",
            headers={"Content-Type": "application/json"},
            json={"pix": []}
        )
        
        # Webhook should return 200 with status ok
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got {data}"
        print("PASSED: /api/efi/webhook/pix endpoint exists and returns ok")
    
    def test_11_webhook_pix_processes_payment(self):
        """POST /api/efi/webhook/pix - Processes payment notification"""
        # Send a webhook with a fake txid (should not fail, just log warning)
        response = requests.post(
            f"{BASE_URL}/api/efi/webhook/pix",
            headers={"Content-Type": "application/json"},
            json={
                "pix": [
                    {"txid": "fake-txid-for-testing", "valor": "97.00"}
                ]
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got {data}"
        print("PASSED: Webhook processes payment notification (fake txid logged as warning)")
    
    # ==================== INTEGRATION TESTS ====================
    
    def test_12_pix_flow_create_and_check_status(self, atleta_token):
        """Integration: Create PIX charge and verify status polling works"""
        # Create PIX charge
        create_response = requests.post(
            f"{BASE_URL}/api/efi/pix/criar",
            headers={
                "Authorization": f"Bearer {atleta_token}",
                "Content-Type": "application/json"
            },
            json={}
        )
        
        if create_response.status_code == 400:
            data = create_response.json()
            if "ja possui acesso Premium" in data.get("detail", ""):
                print("SKIPPED: User already has premium access")
                pytest.skip("User already has premium access")
        
        if create_response.status_code != 200:
            pytest.skip(f"Could not create PIX charge: {create_response.text}")
        
        create_data = create_response.json()
        txid = create_data["txid"]
        
        # Verify QR Code data
        assert create_data["qrcode"] is not None, "QR Code should be generated"
        assert create_data["qrcode"]["qrcode"] is not None, "PIX copia-cola should exist"
        assert create_data["qrcode"]["imagemQrcode"] is not None, "QR Code image should exist"
        
        # Check status (should be ATIVA/pending)
        status_response = requests.get(
            f"{BASE_URL}/api/efi/pix/status/{txid}",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["payment_status"] == "pending", "Payment should be pending"
        
        print(f"PASSED: Full PIX flow - created txid={txid}, status=pending, QR Code generated")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
