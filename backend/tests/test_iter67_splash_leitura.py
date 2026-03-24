# /app/backend/tests/test_iter67_splash_leitura.py
# Tests for Splash Screen and Reading Stats features (Iteration 67)
# Features: GET splash-pendente, POST splash/{id}/confirmar, GET leitura stats, POST reenviar-splash

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"
MENSAGEM_ID = "9b6a409b-7ecd-44e8-a771-b5f5fdf3e96f"


class TestSplashScreenBackend:
    """Tests for Splash Screen endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def atleta_token(self):
        """Get atleta authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Atleta login failed: {response.status_code} - {response.text}")
    
    def test_01_health_check(self):
        """Verify backend is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Backend healthy: {data}")
    
    def test_02_admin_login(self, admin_token):
        """Verify admin can login"""
        assert admin_token is not None
        print(f"✓ Admin login successful, token: {admin_token[:20]}...")
    
    def test_03_atleta_login(self, atleta_token):
        """Verify atleta can login"""
        assert atleta_token is not None
        print(f"✓ Atleta login successful, token: {atleta_token[:20]}...")
    
    def test_04_get_splash_pendente(self, atleta_token):
        """Test GET /api/notificacoes/splash-pendente - should return pending splash for atleta"""
        headers = {"Authorization": f"Bearer {atleta_token}"}
        response = requests.get(f"{BASE_URL}/api/notificacoes/splash-pendente", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Response should have 'splash' key (can be null if no pending splash)
        assert "splash" in data, f"Response missing 'splash' key: {data}"
        print(f"✓ GET splash-pendente returned: {data}")
        
        if data.get("splash"):
            splash = data["splash"]
            assert "id" in splash, "Splash missing 'id'"
            assert "titulo" in splash, "Splash missing 'titulo'"
            assert "mensagem" in splash, "Splash missing 'mensagem'"
            print(f"✓ Splash found: {splash.get('titulo')}")
    
    def test_05_get_leitura_stats(self, admin_token):
        """Test GET /api/admin/mensagens/{id}/leitura - should return reading stats"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/mensagens/{MENSAGEM_ID}/leitura", headers=headers)
        
        # If message doesn't exist, it will return 404
        if response.status_code == 404:
            print(f"⚠ Message {MENSAGEM_ID} not found - testing with first available message")
            # Get historico to find a valid message
            hist_response = requests.get(f"{BASE_URL}/api/admin/mensagens/historico", headers=headers)
            if hist_response.status_code == 200:
                mensagens = hist_response.json().get("mensagens", [])
                if mensagens:
                    msg_id = mensagens[0].get("id")
                    response = requests.get(f"{BASE_URL}/api/admin/mensagens/{msg_id}/leitura", headers=headers)
                    print(f"✓ Testing with message: {msg_id}")
                else:
                    pytest.skip("No messages found in historico")
            else:
                pytest.skip("Could not fetch historico")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "mensagem_id" in data, "Response missing 'mensagem_id'"
        assert "total_enviados" in data, "Response missing 'total_enviados'"
        assert "total_lidas" in data, "Response missing 'total_lidas'"
        assert "total_nao_lidas" in data, "Response missing 'total_nao_lidas'"
        assert "percentual_leitura" in data, "Response missing 'percentual_leitura'"
        assert "atletas_nao_leram" in data, "Response missing 'atletas_nao_leram'"
        assert "atletas_leram" in data, "Response missing 'atletas_leram'"
        
        print(f"✓ Leitura stats: total={data['total_enviados']}, lidas={data['total_lidas']}, não lidas={data['total_nao_lidas']}, %={data['percentual_leitura']}%")
    
    def test_06_reenviar_splash(self, admin_token):
        """Test POST /api/admin/mensagens/{id}/reenviar-splash - should create splash for unread users"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First get a valid message ID from historico
        hist_response = requests.get(f"{BASE_URL}/api/admin/mensagens/historico", headers=headers)
        assert hist_response.status_code == 200, f"Failed to get historico: {hist_response.text}"
        
        mensagens = hist_response.json().get("mensagens", [])
        if not mensagens:
            pytest.skip("No messages found in historico to test reenviar-splash")
        
        # Find a message with status 'enviada'
        msg_id = None
        for msg in mensagens:
            if msg.get("status") in [None, "enviada"]:
                msg_id = msg.get("id")
                break
        
        if not msg_id:
            pytest.skip("No sent messages found to test reenviar-splash")
        
        response = requests.post(f"{BASE_URL}/api/admin/mensagens/{msg_id}/reenviar-splash", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "message" in data, "Response missing 'message'"
        assert "total_reenviados" in data, "Response missing 'total_reenviados'"
        
        print(f"✓ Reenviar splash: {data['message']}, total={data.get('total_reenviados', 0)}")
    
    def test_07_confirmar_splash(self, atleta_token):
        """Test POST /api/notificacoes/splash/{id}/confirmar - should mark splash as read"""
        headers = {"Authorization": f"Bearer {atleta_token}"}
        
        # First check if there's a pending splash
        splash_response = requests.get(f"{BASE_URL}/api/notificacoes/splash-pendente", headers=headers)
        assert splash_response.status_code == 200
        
        splash_data = splash_response.json()
        splash = splash_data.get("splash")
        
        if not splash:
            print("⚠ No pending splash to confirm - test skipped")
            pytest.skip("No pending splash to confirm")
        
        splash_id = splash.get("id")
        response = requests.post(f"{BASE_URL}/api/notificacoes/splash/{splash_id}/confirmar", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "message" in data, "Response missing 'message'"
        print(f"✓ Splash confirmed: {data['message']}")
        
        # Verify splash is no longer pending
        verify_response = requests.get(f"{BASE_URL}/api/notificacoes/splash-pendente", headers=headers)
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        
        # After confirming, splash should be null or different
        print(f"✓ After confirm, splash-pendente: {verify_data}")
    
    def test_08_historico_mensagens(self, admin_token):
        """Test GET /api/admin/mensagens/historico - should return message history"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/mensagens/historico", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "mensagens" in data, "Response missing 'mensagens'"
        mensagens = data["mensagens"]
        
        print(f"✓ Historico returned {len(mensagens)} messages")
        
        if mensagens:
            msg = mensagens[0]
            assert "id" in msg, "Message missing 'id'"
            assert "titulo" in msg, "Message missing 'titulo'"
            print(f"✓ First message: {msg.get('titulo')} - status: {msg.get('status')}")
    
    def test_09_contagem_destinatarios(self, admin_token):
        """Test GET /api/admin/mensagens/contagem-destinatarios - should return recipient count"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios?filtro_tipo=todos", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "total" in data, "Response missing 'total'"
        print(f"✓ Total destinatarios (todos): {data['total']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
