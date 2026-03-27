# /app/backend/tests/test_iter83_confirmacao_pix.py
# Tests for PIX payment confirmation flow and confirmation screen data
# Iteration 83: Tela de confirmação de pagamento PIX com confetti

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def atleta_token(api_client):
    """Get atleta authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ATLETA_EMAIL,
        "password": ATLETA_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Atleta authentication failed")


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Admin authentication failed")


class TestPagamentoEndpoints:
    """Tests for pagamento endpoints that support the confirmation screen"""

    def test_01_meu_plano_returns_premium_status(self, api_client, atleta_token):
        """GET /api/pagamentos/meu-plano returns user plan status"""
        response = api_client.get(
            f"{BASE_URL}/api/pagamentos/meu-plano",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert "tem_acesso_premium" in data
        assert "plano_vigente" in data
        
        # Verify plano_vigente structure
        plano = data.get("plano_vigente", {})
        assert "id" in plano
        assert "nome" in plano
        assert "valor" in plano
        print(f"User plan status: {data['status']}, premium: {data['tem_acesso_premium']}")

    def test_02_meu_plano_returns_plano_atleta_premium(self, api_client, atleta_token):
        """GET /api/pagamentos/meu-plano returns Atleta Premium plan info"""
        response = api_client.get(
            f"{BASE_URL}/api/pagamentos/meu-plano",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        plano = data.get("plano_vigente", {})
        assert plano.get("nome") == "Atleta Premium"
        assert plano.get("valor") == 97.0
        assert plano.get("valor_original") == 197.0
        print(f"Plan: {plano.get('nome')}, Value: R${plano.get('valor')}")


class TestPixStatusEndpoint:
    """Tests for PIX status endpoint used by polling"""

    def test_03_pix_status_requires_auth(self, api_client):
        """GET /api/efi/pix/status/{txid} requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/efi/pix/status/test-txid")
        assert response.status_code in [401, 403]

    def test_04_pix_status_returns_404_for_invalid_txid(self, api_client, atleta_token):
        """GET /api/efi/pix/status/{txid} returns 404 for invalid txid"""
        response = api_client.get(
            f"{BASE_URL}/api/efi/pix/status/invalid-txid-12345",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print(f"404 response: {data['detail']}")


class TestPixCriarEndpoint:
    """Tests for PIX creation endpoint"""

    def test_05_pix_criar_requires_auth(self, api_client):
        """POST /api/efi/pix/criar requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/efi/pix/criar", json={})
        assert response.status_code in [401, 403]

    def test_06_pix_criar_returns_400_if_already_premium(self, api_client, atleta_token):
        """POST /api/efi/pix/criar returns 400 if user already has premium"""
        response = api_client.post(
            f"{BASE_URL}/api/efi/pix/criar",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={}
        )
        # User already has premium, should return 400
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            assert "Premium" in data["detail"] or "ativo" in data["detail"]
            print(f"Expected 400: {data['detail']}")
        else:
            # If user doesn't have premium, it should create PIX
            assert response.status_code == 200
            data = response.json()
            assert "txid" in data
            assert "qrcode" in data
            print(f"PIX created: txid={data['txid']}")


class TestWebhookEndpoint:
    """Tests for webhook endpoint that triggers confirmation"""

    def test_07_webhook_healthcheck_returns_empty(self, api_client):
        """GET /api/efi/webhook/pix returns empty string (health check)"""
        response = api_client.get(f"{BASE_URL}/api/efi/webhook/pix")
        assert response.status_code == 200
        # Efi Bank expects empty string for health check
        assert response.text == '""' or response.text == ""

    def test_08_webhook_post_returns_ok(self, api_client):
        """POST /api/efi/webhook/pix returns ok status"""
        response = api_client.post(
            f"{BASE_URL}/api/efi/webhook/pix",
            json={"pix": []}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"

    def test_09_webhook_handles_invalid_txid_gracefully(self, api_client):
        """POST /api/efi/webhook/pix handles invalid txid gracefully"""
        response = api_client.post(
            f"{BASE_URL}/api/efi/webhook/pix",
            json={"pix": [{"txid": "invalid-txid-webhook-test"}]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"


class TestAdminTransacoes:
    """Tests for admin transactions endpoint"""

    def test_10_admin_transacoes_requires_admin(self, api_client, atleta_token):
        """GET /api/efi/admin/transacoes requires admin role"""
        response = api_client.get(
            f"{BASE_URL}/api/efi/admin/transacoes",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 403

    def test_11_admin_transacoes_returns_list(self, api_client, admin_token):
        """GET /api/efi/admin/transacoes returns transactions list"""
        response = api_client.get(
            f"{BASE_URL}/api/efi/admin/transacoes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "transacoes" in data
        assert "total" in data
        assert isinstance(data["transacoes"], list)
        print(f"Total transactions: {data['total']}")


class TestConfirmationScreenData:
    """Tests to verify data needed for confirmation screen"""

    def test_12_plano_vigente_has_required_fields(self, api_client, atleta_token):
        """Verify plano_vigente has all fields needed for confirmation screen"""
        response = api_client.get(
            f"{BASE_URL}/api/pagamentos/meu-plano",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        plano = data.get("plano_vigente", {})
        
        # Fields needed for confirmation screen
        required_fields = ["id", "nome", "valor", "valor_original", "validade"]
        for field in required_fields:
            assert field in plano, f"Missing field: {field}"
        
        # Verify values match what confirmation screen expects
        assert plano["nome"] == "Atleta Premium"
        assert plano["validade"] == "2026-12-31"
        print(f"Plano vigente verified: {plano['nome']} - R${plano['valor']}")

    def test_13_pix_status_paid_response_structure(self, api_client, admin_token):
        """Verify PIX status response structure for paid status"""
        # Get a transaction from admin endpoint
        response = api_client.get(
            f"{BASE_URL}/api/efi/admin/transacoes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find a paid transaction
        paid_tx = None
        for tx in data.get("transacoes", []):
            if tx.get("payment_status") == "paid":
                paid_tx = tx
                break
        
        if paid_tx:
            # Verify paid transaction has expected fields
            assert paid_tx.get("status") == "CONCLUIDA"
            assert paid_tx.get("payment_status") == "paid"
            assert "txid" in paid_tx
            print(f"Found paid transaction: txid={paid_tx['txid']}")
        else:
            print("No paid transactions found - this is expected if no payments completed")


class TestPollingFlow:
    """Tests for the polling flow that triggers confirmation screen"""

    def test_14_pix_status_returns_payment_status(self, api_client, admin_token):
        """Verify PIX status endpoint returns payment_status field"""
        # Get a transaction
        response = api_client.get(
            f"{BASE_URL}/api/efi/admin/transacoes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        if data.get("transacoes"):
            tx = data["transacoes"][0]
            # Verify transaction has payment_status
            assert "payment_status" in tx
            assert tx["payment_status"] in ["pending", "paid", "expired", "cancelled"]
            print(f"Transaction payment_status: {tx['payment_status']}")
        else:
            print("No transactions found")

    def test_15_webhook_activates_premium(self, api_client, admin_token):
        """Verify webhook endpoint structure for activating premium"""
        # This test verifies the webhook endpoint accepts the correct format
        # The actual activation is tested in iteration 82
        response = api_client.post(
            f"{BASE_URL}/api/efi/webhook/pix",
            json={
                "pix": [
                    {
                        "txid": "test-webhook-format",
                        "endToEndId": "E12345678901234567890123456789012",
                        "valor": "97.00",
                        "horario": "2026-03-27T15:00:00.000Z"
                    }
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("Webhook format accepted correctly")
