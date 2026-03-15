# /app/backend/tests/test_iter35_indicacao_notificacao.py
# Tests for referral notifications and MinhasIndicacoes component
# Features tested:
# 1. Push notification when someone registers with referral code
# 2. Notification appears in indicator's notification dropdown
# 3. Public endpoint GET /api/indicacao/atleta/{id}/publico
# 4. Embaixador badge at 5 indicações

import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

class TestIndicacaoNotificationSystem:
    """Tests for referral notification system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for tests"""
        self.base_url = BASE_URL.rstrip('/') if BASE_URL else None
        if not self.base_url:
            pytest.skip("REACT_APP_BACKEND_URL not configured")
    
    def get_auth_token(self, email, password):
        """Helper to login and get token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    # ==================== INDICAÇÃO PUBLIC ENDPOINT ====================
    
    def test_indicacao_publico_endpoint_exists(self):
        """Test GET /api/indicacao/atleta/{id}/publico endpoint exists"""
        # Use Carlos Silva's ID (indicador from test data)
        atleta_id = "d3f2640e-794d-49f8-9efb-aab0e536b826"
        
        response = requests.get(f"{self.base_url}/api/indicacao/atleta/{atleta_id}/publico")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "total_indicacoes" in data
        assert "is_embaixador" in data
        assert "indicacoes" in data
        assert isinstance(data["indicacoes"], list)
        print(f"✅ Endpoint /indicacao/atleta/{atleta_id}/publico working")
        print(f"   Total indicações: {data['total_indicacoes']}")
        print(f"   Is embaixador: {data['is_embaixador']}")
        print(f"   Lista de indicados: {len(data['indicacoes'])} pessoas")
    
    def test_indicacao_publico_nonexistent_atleta(self):
        """Test endpoint returns empty data for non-existent atleta"""
        fake_id = "nonexistent-id-12345"
        
        response = requests.get(f"{self.base_url}/api/indicacao/atleta/{fake_id}/publico")
        
        assert response.status_code == 200  # Should return 200 with empty data
        data = response.json()
        
        assert data["total_indicacoes"] == 0
        assert data["is_embaixador"] == False
        assert data["indicacoes"] == []
        print("✅ Non-existent atleta returns empty data correctly")
    
    # ==================== NOTIFICATIONS ENDPOINT ====================
    
    def test_notificacoes_endpoint_requires_auth(self):
        """Test notifications endpoint requires authentication"""
        response = requests.get(f"{self.base_url}/api/notificacoes")
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403]
        print("✅ Notifications endpoint correctly requires authentication")
    
    def test_notificacoes_for_indicador(self):
        """Test that indicador can see their notifications"""
        token = self.get_auth_token("carlos.silva@teste.com", "senha123")
        
        if not token:
            pytest.skip("Could not authenticate as Carlos Silva")
        
        response = requests.get(
            f"{self.base_url}/api/notificacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "notificacoes" in data
        assert "nao_lidas" in data
        assert isinstance(data["notificacoes"], list)
        
        # Check if there are any indicacao notifications
        indicacao_notifs = [n for n in data["notificacoes"] if n.get("tipo") == "indicacao"]
        print(f"✅ Notifications endpoint working")
        print(f"   Total notifications: {len(data['notificacoes'])}")
        print(f"   Unread count: {data['nao_lidas']}")
        print(f"   Indicacao notifications: {len(indicacao_notifs)}")
    
    def test_notification_structure_for_indicacao(self):
        """Test that indicacao notifications have correct structure"""
        token = self.get_auth_token("carlos.silva@teste.com", "senha123")
        
        if not token:
            pytest.skip("Could not authenticate as Carlos Silva")
        
        response = requests.get(
            f"{self.base_url}/api/notificacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Find indicacao notifications
        indicacao_notifs = [n for n in data["notificacoes"] if n.get("tipo") == "indicacao"]
        
        if indicacao_notifs:
            notif = indicacao_notifs[0]
            # Check notification structure
            assert "id" in notif
            assert "tipo" in notif
            assert "titulo" in notif
            assert "mensagem" in notif
            assert "lida" in notif
            assert "data_criacao" in notif
            
            # Check if titulo contains expected pattern
            assert "indicação" in notif["titulo"].lower() or "🎉" in notif["titulo"]
            print(f"✅ Indicacao notification structure correct")
            print(f"   Title: {notif['titulo']}")
            print(f"   Message: {notif['mensagem']}")
        else:
            print("⚠️ No indicacao notifications found - may need to trigger a new registration")
    
    # ==================== MEU-CODIGO ENDPOINT ====================
    
    def test_meu_codigo_endpoint(self):
        """Test GET /api/indicacao/meu-codigo returns user's referral code"""
        token = self.get_auth_token("carlos.silva@teste.com", "senha123")
        
        if not token:
            pytest.skip("Could not authenticate")
        
        response = requests.get(
            f"{self.base_url}/api/indicacao/meu-codigo",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "codigo" in data
        assert "link" in data
        assert "total_indicacoes" in data
        assert "indicacoes_para_embaixador" in data
        assert "is_embaixador" in data
        
        # Carlos should have code REF-CSAC0455
        assert data["codigo"] == "REF-CSAC0455"
        print(f"✅ Meu-codigo endpoint working")
        print(f"   Code: {data['codigo']}")
        print(f"   Total: {data['total_indicacoes']}")
        print(f"   Is embaixador: {data['is_embaixador']}")
    
    # ==================== MINHAS-INDICACOES ENDPOINT ====================
    
    def test_minhas_indicacoes_endpoint(self):
        """Test GET /api/indicacao/minhas-indicacoes returns list of referrals"""
        token = self.get_auth_token("carlos.silva@teste.com", "senha123")
        
        if not token:
            pytest.skip("Could not authenticate")
        
        response = requests.get(
            f"{self.base_url}/api/indicacao/minhas-indicacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert "indicacoes" in data
        assert isinstance(data["indicacoes"], list)
        
        if data["indicacoes"]:
            indicacao = data["indicacoes"][0]
            assert "id" in indicacao
            assert "nome" in indicacao
            assert "data_cadastro" in indicacao
            print(f"✅ Minhas-indicacoes endpoint working")
            print(f"   Total indicados: {data['total']}")
            for ind in data["indicacoes"]:
                print(f"   - {ind['nome']} (cadastro: {ind['data_cadastro'][:10]})")
        else:
            print("✅ Minhas-indicacoes endpoint working (no referrals yet)")
    
    # ==================== REGISTRATION WITH CODE CREATES NOTIFICATION ====================
    
    def test_registration_with_valid_code_creates_notification(self):
        """Test that registering with a valid code creates a notification for the indicador"""
        # First, get current notification count for Carlos
        token = self.get_auth_token("carlos.silva@teste.com", "senha123")
        
        if not token:
            pytest.skip("Could not authenticate as Carlos Silva")
        
        response_before = requests.get(
            f"{self.base_url}/api/notificacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        notifs_before = len(response_before.json().get("notificacoes", []))
        
        # Register new user with Carlos's referral code
        unique_id = str(uuid.uuid4())[:8]
        new_user_data = {
            "nome": f"TEST_NotifTest_{unique_id}",
            "email": f"test_notif_{unique_id}@teste.com",
            "password": "senha123",
            "equipe": "Teste",
            "cidade": "São Paulo",
            "estado": "SP",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-01-01",
            "modalidade_usuario": "profissional_amador",
            "codigo_indicacao": "REF-CSAC0455"  # Carlos's code
        }
        
        register_response = requests.post(
            f"{self.base_url}/api/auth/register",
            json=new_user_data
        )
        
        assert register_response.status_code == 200
        reg_data = register_response.json()
        
        # Verify indicação was registered
        assert reg_data.get("indicacao", {}).get("registrada") == True
        print(f"✅ New user registered with referral code")
        print(f"   Indicador: {reg_data.get('indicacao', {}).get('indicador_nome')}")
        
        # Wait a moment for notification to be created
        time.sleep(0.5)
        
        # Check Carlos's notifications again
        response_after = requests.get(
            f"{self.base_url}/api/notificacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        notifs_after = response_after.json().get("notificacoes", [])
        
        # Should have at least one more notification
        assert len(notifs_after) > notifs_before
        
        # Check if latest notification is about the new indicação
        latest_notif = notifs_after[0]  # Notifications are sorted by date desc
        
        assert latest_notif.get("tipo") == "indicacao"
        assert "🎉" in latest_notif.get("titulo", "")
        assert new_user_data["nome"].replace("TEST_NotifTest_", "") in latest_notif.get("mensagem", "") or "NotifTest" in latest_notif.get("mensagem", "")
        
        print(f"✅ Push notification created for indicador")
        print(f"   Title: {latest_notif.get('titulo')}")
        print(f"   Message: {latest_notif.get('mensagem')}")
    
    # ==================== EMBAIXADOR BADGE ====================
    
    def test_embaixador_badge_threshold(self):
        """Test that embaixador badge is granted at 5 indicações"""
        token = self.get_auth_token("carlos.silva@teste.com", "senha123")
        
        if not token:
            pytest.skip("Could not authenticate")
        
        response = requests.get(
            f"{self.base_url}/api/indicacao/meu-codigo",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = response.json()
        total = data.get("total_indicacoes", 0)
        is_embaixador = data.get("is_embaixador", False)
        indicacoes_para = data.get("indicacoes_para_embaixador", 0)
        
        # Verify logic is correct
        if total >= 5:
            assert is_embaixador == True
            assert indicacoes_para == 0
            print(f"✅ Embaixador badge logic correct (is embaixador with {total} indicações)")
        else:
            assert is_embaixador == False
            assert indicacoes_para == 5 - total
            print(f"✅ Embaixador badge logic correct ({indicacoes_para} more needed)")
    
    def test_embaixador_badge_in_public_endpoint(self):
        """Test that embaixador status is shown in public endpoint"""
        atleta_id = "d3f2640e-794d-49f8-9efb-aab0e536b826"
        
        response = requests.get(f"{self.base_url}/api/indicacao/atleta/{atleta_id}/publico")
        
        assert response.status_code == 200
        data = response.json()
        
        # Embaixador should be calculated correctly
        total = data.get("total_indicacoes", 0)
        is_embaixador = data.get("is_embaixador", False)
        
        expected_embaixador = total >= 5
        assert is_embaixador == expected_embaixador
        print(f"✅ Public endpoint shows correct embaixador status: {is_embaixador}")


class TestIndicacoesPublicVsPrivateData:
    """Tests to verify owner vs visitor data separation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_url = BASE_URL.rstrip('/') if BASE_URL else None
        if not self.base_url:
            pytest.skip("REACT_APP_BACKEND_URL not configured")
    
    def test_public_endpoint_no_codigo(self):
        """Test that public endpoint does NOT expose referral code"""
        atleta_id = "d3f2640e-794d-49f8-9efb-aab0e536b826"
        
        response = requests.get(f"{self.base_url}/api/indicacao/atleta/{atleta_id}/publico")
        
        data = response.json()
        
        # Public endpoint should NOT have these fields
        assert "codigo" not in data
        assert "link" not in data
        print("✅ Public endpoint correctly hides referral code")
    
    def test_meu_codigo_exposes_codigo(self):
        """Test that authenticated endpoint DOES expose referral code"""
        token = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": "carlos.silva@teste.com", "password": "senha123"}
        ).json().get("token")
        
        if not token:
            pytest.skip("Could not authenticate")
        
        response = requests.get(
            f"{self.base_url}/api/indicacao/meu-codigo",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = response.json()
        
        # Authenticated endpoint SHOULD have these fields
        assert "codigo" in data
        assert "link" in data
        print(f"✅ Authenticated endpoint correctly exposes referral code: {data['codigo']}")


class TestNotificationMarkAsRead:
    """Tests for notification read functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_url = BASE_URL.rstrip('/') if BASE_URL else None
        if not self.base_url:
            pytest.skip("REACT_APP_BACKEND_URL not configured")
    
    def test_mark_notification_as_read(self):
        """Test marking a single notification as read"""
        token = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": "carlos.silva@teste.com", "password": "senha123"}
        ).json().get("token")
        
        if not token:
            pytest.skip("Could not authenticate")
        
        # Get notifications
        response = requests.get(
            f"{self.base_url}/api/notificacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        notifs = response.json().get("notificacoes", [])
        
        if not notifs:
            print("⚠️ No notifications to mark as read")
            return
        
        # Mark first notification as read
        notif_id = notifs[0]["id"]
        mark_response = requests.post(
            f"{self.base_url}/api/notificacoes/{notif_id}/ler",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert mark_response.status_code == 200
        print("✅ Mark notification as read endpoint working")
    
    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        token = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": "carlos.silva@teste.com", "password": "senha123"}
        ).json().get("token")
        
        if not token:
            pytest.skip("Could not authenticate")
        
        response = requests.post(
            f"{self.base_url}/api/notificacoes/ler-todas",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        print("✅ Mark all notifications as read endpoint working")
