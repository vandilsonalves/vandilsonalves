"""
Tests for new features:
- Etnia and Apelido fields in registration and profile
- Bio do Atleta field with 150 char limit
- Instagram + Apelido and Facebook + First Name display in athlete details
- Admin Aniversariantes tab with interactive calendar and birthday message system
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthAndNewFields:
    """Test registration and profile fields including etnia and apelido"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.admin_credentials = {"email": "admin@runpro.com", "password": "admin123"}
        self.atleta_credentials = {"email": "gabrielsouza_normal_1@email.com", "password": "atleta123"}
        self.test_atleta_id = "a6a1828a-68de-432f-817d-8aa4b3167404"  # João Silva Neto
    
    def get_admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=self.admin_credentials)
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def get_atleta_token(self):
        """Get atleta authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=self.atleta_credentials)
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    # Test 1: Auth login returns success
    def test_admin_login(self):
        """Test admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=self.admin_credentials)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print(f"PASS: Admin login works, role={data['user']['role']}")
    
    def test_atleta_login(self):
        """Test atleta login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=self.atleta_credentials)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"PASS: Atleta login works")


class TestAtletaDetailsAPI:
    """Test atleta details API returns new fields: bio, apelido, etnia, instagram_url, facebook_url"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.test_atleta_id = "a6a1828a-68de-432f-817d-8aa4b3167404"
    
    def test_atleta_details_returns_new_fields(self):
        """GET /api/atletas/{id} returns bio, apelido, etnia, instagram_url, facebook_url"""
        response = requests.get(f"{BASE_URL}/api/atletas/{self.test_atleta_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check presence of new fields
        assert "bio" in data, "bio field missing from response"
        assert "apelido" in data, "apelido field missing from response"
        assert "etnia" in data, "etnia field missing from response"
        assert "instagram_url" in data, "instagram_url field missing from response"
        assert "facebook_url" in data, "facebook_url field missing from response"
        
        print(f"PASS: Atleta details has all new fields")
        print(f"  - bio: {data.get('bio', '')[:50]}...")
        print(f"  - apelido: {data.get('apelido', '')}")
        print(f"  - etnia: {data.get('etnia', '')}")
        print(f"  - instagram_url: {data.get('instagram_url', '')}")
        print(f"  - facebook_url: {data.get('facebook_url', '')}")
    
    def test_atleta_details_has_basic_fields(self):
        """Verify basic fields still work"""
        response = requests.get(f"{BASE_URL}/api/atletas/{self.test_atleta_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check basic fields
        assert "id" in data
        assert "nome" in data
        assert "cidade" in data
        assert "estado" in data
        assert "equipe" in data
        assert "pontos_carreira" in data
        assert "total_corridas" in data
        
        print(f"PASS: Atleta details has basic fields: {data['nome']}")


class TestPerfilUpdateAPI:
    """Test profile update API with new fields"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.admin_credentials = {"email": "admin@runpro.com", "password": "admin123"}
        self.atleta_credentials = {"email": "gabrielsouza_normal_1@email.com", "password": "atleta123"}
    
    def get_atleta_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=self.atleta_credentials)
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_profile_update_bio_field(self):
        """Test PATCH /api/atletas/perfil with bio field"""
        token = self.get_atleta_token()
        if not token:
            pytest.skip("Could not get atleta token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update bio
        bio_text = "Corredor apaixonado por superação. 🏃"
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            json={"bio": bio_text},
            headers=headers
        )
        assert response.status_code == 200
        print(f"PASS: Bio update successful")
    
    def test_profile_update_etnia_field(self):
        """Test PATCH /api/atletas/perfil with etnia field"""
        token = self.get_atleta_token()
        if not token:
            pytest.skip("Could not get atleta token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            json={"etnia": "Pardo"},
            headers=headers
        )
        assert response.status_code == 200
        print(f"PASS: Etnia update successful")
    
    def test_profile_update_apelido_field(self):
        """Test PATCH /api/atletas/perfil with apelido field"""
        token = self.get_atleta_token()
        if not token:
            pytest.skip("Could not get atleta token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            json={"apelido": "Gabi"},
            headers=headers
        )
        assert response.status_code == 200
        print(f"PASS: Apelido update successful")
    
    def test_bio_limit_150_chars(self):
        """Test bio field respects 150 character limit"""
        token = self.get_atleta_token()
        if not token:
            pytest.skip("Could not get atleta token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send bio with more than 150 chars
        long_bio = "A" * 200
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            json={"bio": long_bio},
            headers=headers
        )
        assert response.status_code == 200
        
        # Verify truncation on get
        profile_response = requests.get(f"{BASE_URL}/api/atletas/meu-perfil", headers=headers)
        assert profile_response.status_code == 200
        data = profile_response.json()
        
        # Bio should be truncated to 150 chars
        assert len(data.get("bio", "")) <= 150, f"Bio length {len(data.get('bio', ''))} exceeds 150"
        print(f"PASS: Bio truncated to 150 chars or less ({len(data.get('bio', ''))} chars)")


class TestAniversariantesAPI:
    """Test admin aniversariantes API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.admin_credentials = {"email": "admin@runpro.com", "password": "admin123"}
    
    def get_admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=self.admin_credentials)
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_get_aniversariantes_mes(self):
        """GET /api/admin/aniversariantes returns calendar structure"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        headers = {"Authorization": f"Bearer {token}"}
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        response = requests.get(
            f"{BASE_URL}/api/admin/aniversariantes",
            params={"mes": current_month, "ano": current_year},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "mes" in data, "mes field missing"
        assert "ano" in data, "ano field missing"
        assert "calendario" in data, "calendario field missing"
        assert "total_aniversariantes" in data, "total_aniversariantes field missing"
        
        # Check calendario structure (should have days 1-31)
        assert isinstance(data["calendario"], dict), "calendario should be a dict"
        
        print(f"PASS: Aniversariantes API returns correct structure")
        print(f"  - Mês: {data['mes']} {data['ano']}")
        print(f"  - Total aniversariantes: {data['total_aniversariantes']}")
    
    def test_get_aniversariantes_hoje(self):
        """GET /api/admin/aniversariantes/hoje returns today's birthdays"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/admin/aniversariantes/hoje",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "aniversariantes" in data
        assert "data" in data
        assert isinstance(data["aniversariantes"], list)
        
        print(f"PASS: Aniversariantes hoje API works")
        print(f"  - Data: {data['data']}")
        print(f"  - Aniversariantes hoje: {len(data['aniversariantes'])}")
    
    def test_enviar_mensagem_aniversario(self):
        """POST /api/admin/aniversariantes/enviar-mensagem sends birthday message"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get an atleta to send message to
        atletas_response = requests.get(f"{BASE_URL}/api/admin/atletas", headers=headers)
        if atletas_response.status_code != 200 or not atletas_response.json():
            pytest.skip("No atletas available for test")
        
        atleta_id = atletas_response.json()[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/admin/aniversariantes/enviar-mensagem",
            json={
                "atleta_ids": [atleta_id],
                "mensagem": "Feliz Aniversário de teste! 🎂"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "1 mensagem" in data["message"] or "mensagem(ns) enviada(s)" in data["message"]
        
        print(f"PASS: Enviar mensagem aniversário API works")
    
    def test_get_configuracao_aniversario(self):
        """GET /api/admin/aniversariantes/configuracao returns config"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/admin/aniversariantes/configuracao",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "mensagem_padrao" in data or "tipo" in data
        print(f"PASS: Configuracao aniversário API works")


class TestAtletaMensagemAniversario:
    """Test atleta birthday message endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.atleta_credentials = {"email": "gabrielsouza_normal_1@email.com", "password": "atleta123"}
    
    def get_atleta_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=self.atleta_credentials)
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_get_mensagem_aniversario(self):
        """GET /api/atletas/mensagem-aniversario returns message or null"""
        token = self.get_atleta_token()
        if not token:
            pytest.skip("Could not get atleta token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/atletas/mensagem-aniversario",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mensagem" in data
        print(f"PASS: Get mensagem aniversário endpoint works")
    
    def test_marcar_mensagem_visualizada(self):
        """POST /api/atletas/mensagem-aniversario/visualizar marks message as read"""
        token = self.get_atleta_token()
        if not token:
            pytest.skip("Could not get atleta token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/atletas/mensagem-aniversario/visualizar",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"PASS: Marcar mensagem visualizada endpoint works")


class TestRegistrationNewFields:
    """Test registration accepts new fields etnia and apelido"""
    
    def test_register_endpoint_accepts_etnia_apelido(self):
        """Verify POST /api/auth/register schema includes etnia and apelido"""
        import uuid
        unique_email = f"test_etnia_apelido_{uuid.uuid4().hex[:8]}@test.com"
        
        payload = {
            "nome": "Test Etnia Apelido",
            "email": unique_email,
            "password": "test123456",
            "equipe": "Test Team",
            "cidade": "São Paulo",
            "estado": "SP",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-01-15",
            "etnia": "Pardo",
            "apelido": "TestApelido"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        
        print(f"PASS: Registration with etnia and apelido works")
        print(f"  - User: {data['user']['nome']}")
        
        # Cleanup: delete test user
        admin_response = requests.post(
            f"{BASE_URL}/api/auth/login", 
            json={"email": "admin@runpro.com", "password": "admin123"}
        )
        if admin_response.status_code == 200:
            admin_token = admin_response.json().get("token")
            user_id = data['user']['id']
            requests.delete(
                f"{BASE_URL}/api/admin/atletas/{user_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            print(f"  - Test user cleaned up")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
