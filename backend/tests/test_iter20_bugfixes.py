"""
Test file for iteration 20 bug fixes:
1. POST /api/auth/register - Cadastro de atleta funcionando
2. GET /api/atletas/{id} - Detalhes do atleta funcionando (corrigido KeyError faixa_etaria)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAuthRegister:
    """Test athlete registration endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.test_email = f"test_atleta_{uuid.uuid4().hex[:8]}@test.com"
        self.test_data = {
            "nome": "Test Atleta Cadastro",
            "email": self.test_email,
            "password": "senha123456",
            "equipe": "Test Equipe",
            "cidade": "São Paulo",
            "estado": "SP",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-05-15",
            "etnia": "Pardo",
            "apelido": "TestRunner",
            "modalidade_usuario": "profissional_amador"
        }
        yield
        # Cleanup: Try to delete the test user
        # (Note: No public endpoint for this, so we leave it)
    
    def test_register_success(self):
        """Test successful athlete registration"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json=self.test_data)
        
        print(f"Register response status: {response.status_code}")
        print(f"Register response: {response.json() if response.status_code < 500 else response.text}")
        
        # Check status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Check response structure
        data = response.json()
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user"
        assert "message" in data, "Response should contain message"
        
        # Check user data
        user = data["user"]
        assert user["nome"] == self.test_data["nome"]
        assert user["email"] == self.test_data["email"]
        assert user["role"] == "atleta"
        assert user["modalidade_usuario"] == "profissional_amador"
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email fails"""
        # First register
        response1 = requests.post(f"{BASE_URL}/api/auth/register", json=self.test_data)
        assert response1.status_code == 200, f"First register failed: {response1.text}"
        
        # Try to register again with same email
        response2 = requests.post(f"{BASE_URL}/api/auth/register", json=self.test_data)
        
        print(f"Duplicate register response: {response2.status_code}")
        assert response2.status_code == 400, f"Expected 400 for duplicate, got {response2.status_code}"
        assert "já cadastrado" in response2.json().get("detail", "").lower() or "cadastrado" in response2.json().get("detail", "").lower()
    
    def test_register_pcd_cannot_use_povao(self):
        """Test PCD athletes cannot use Povão modality"""
        pcd_data = {
            **self.test_data,
            "email": f"pcd_test_{uuid.uuid4().hex[:8]}@test.com",
            "categoria": "pcd",
            "modalidade_usuario": "povao_pace_livre"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=pcd_data)
        
        print(f"PCD Povão response: {response.status_code}")
        # Should fail because PCD cannot use Povão
        assert response.status_code == 400, f"Expected 400 for PCD+Povão, got {response.status_code}"


class TestAtletaDetalhes:
    """Test GET /api/atletas/{id} endpoint - KeyError faixa_etaria fix"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    @pytest.fixture
    def test_atleta_id(self, admin_token):
        """Get an existing atleta ID from the system"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/atletas", headers=headers)
        
        if response.status_code == 200 and len(response.json()) > 0:
            return response.json()[0]["id"]
        pytest.skip("No atletas found in system")
    
    def test_atleta_detalhes_success(self, test_atleta_id):
        """Test getting athlete details works without KeyError"""
        response = requests.get(f"{BASE_URL}/api/atletas/{test_atleta_id}")
        
        print(f"Atleta detalhes response status: {response.status_code}")
        print(f"Atleta detalhes response: {response.json() if response.status_code < 500 else response.text}")
        
        # Check status code - should NOT be 500 (KeyError fix)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Check response structure
        data = response.json()
        assert "id" in data
        assert "nome" in data
        assert "cidade" in data
        assert "estado" in data
        assert "faixa_etaria" in data  # This was causing KeyError before fix
        assert "pontos_carreira" in data
        assert "total_corridas" in data
        assert "melhor_colocacao" in data
        
        # Check faixa_etaria has a valid value or default
        assert data["faixa_etaria"] is not None
        print(f"faixa_etaria value: {data['faixa_etaria']}")
    
    def test_atleta_detalhes_not_found(self):
        """Test 404 for non-existent athlete"""
        fake_id = "non-existent-id-12345"
        response = requests.get(f"{BASE_URL}/api/atletas/{fake_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_atleta_detalhes_includes_all_fields(self, test_atleta_id):
        """Test that all expected fields are present in response"""
        response = requests.get(f"{BASE_URL}/api/atletas/{test_atleta_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields from AtletaDetalhes model
        expected_fields = [
            "id", "nome", "cidade", "estado", "genero", "categoria",
            "faixa_etaria", "foto_url", "equipe", "pontos_carreira",
            "total_corridas", "melhor_colocacao", "is_pendente",
            "bio", "apelido", "etnia", "instagram_url", "facebook_url",
            "modalidade_usuario"
        ]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"All {len(expected_fields)} fields present in response")


class TestAtletaCorridas:
    """Test GET /api/atletas/{id}/corridas endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    @pytest.fixture
    def test_atleta_id(self, admin_token):
        """Get an existing atleta ID from the system"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/atletas", headers=headers)
        
        if response.status_code == 200 and len(response.json()) > 0:
            return response.json()[0]["id"]
        pytest.skip("No atletas found in system")
    
    def test_atleta_corridas(self, test_atleta_id):
        """Test getting athlete corridas"""
        response = requests.get(f"{BASE_URL}/api/atletas/{test_atleta_id}/corridas")
        
        print(f"Atleta corridas response status: {response.status_code}")
        
        # Should return 200 and a list (even if empty)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert isinstance(response.json(), list), "Response should be a list"


class TestNewAtletaRegistration:
    """Test creating a new athlete and verifying their details page works"""
    
    def test_register_and_view_details(self):
        """Test full flow: register new athlete and view their details"""
        # Step 1: Register new athlete
        unique_id = uuid.uuid4().hex[:8]
        register_data = {
            "nome": f"Novo Atleta {unique_id}",
            "email": f"novo_atleta_{unique_id}@test.com",
            "password": "teste123456",
            "equipe": "Assessoria Test",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "genero": "F",
            "categoria": "normal",
            "data_nascimento": "1995-08-20",
            "etnia": "Negro",
            "apelido": f"Runner{unique_id}",
            "modalidade_usuario": "profissional_amador"
        }
        
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Register response: {register_response.status_code}")
        
        assert register_response.status_code == 200, f"Register failed: {register_response.text}"
        
        # Get the new athlete's ID
        atleta_id = register_response.json()["user"]["id"]
        print(f"New athlete ID: {atleta_id}")
        
        # Step 2: Get athlete details (the bug fix test)
        details_response = requests.get(f"{BASE_URL}/api/atletas/{atleta_id}")
        print(f"Details response: {details_response.status_code}")
        
        assert details_response.status_code == 200, f"Details failed: {details_response.text}"
        
        # Verify the details
        data = details_response.json()
        assert data["nome"] == register_data["nome"]
        assert data["cidade"] == register_data["cidade"]
        assert data["estado"] == register_data["estado"]
        assert data["categoria"] == register_data["categoria"]
        assert "faixa_etaria" in data  # This was the bug - KeyError
        assert data["faixa_etaria"] is not None
        
        print(f"✅ New athlete faixa_etaria: {data['faixa_etaria']}")
        print(f"✅ Full flow working: Register → View Details")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
