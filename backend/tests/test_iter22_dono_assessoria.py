"""
Test iteration 22: Dono de Assessoria feature
Tests the registration flow for users who are owners of assessoria/equipe
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestDonoAssessoriaRegistration:
    """Test registration as dono de assessoria"""
    
    def test_register_as_dono_assessoria_returns_201(self, api_client):
        """Test that registering as dono de assessoria returns success"""
        unique_id = str(uuid.uuid4())[:8]
        assessoria_nome = f"TEST_Assessoria_{unique_id}"
        
        payload = {
            "nome": f"Test Dono {unique_id}",
            "email": f"test_dono_{unique_id}@test.com",
            "password": "teste123",
            "equipe": "Individual",  # Will be replaced with assessoria_nome
            "cidade": "São Paulo",
            "estado": "SP",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-01-15",
            "etnia": "Pardo",
            "apelido": "Test",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": True,
            "assessoria_data": {
                "nome": assessoria_nome,
                "estado": "SP",
                "cidade": "São Paulo",
                "mensagem_bio": "Esta é uma assessoria de teste para atletas de corrida de rua."
            }
        }
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user"
        
    def test_register_as_dono_returns_role_dono_assessoria(self, api_client):
        """Test that user registered as dono gets role='dono_assessoria'"""
        unique_id = str(uuid.uuid4())[:8]
        assessoria_nome = f"TEST_RoleTest_{unique_id}"
        
        payload = {
            "nome": f"Test Role User {unique_id}",
            "email": f"test_role_{unique_id}@test.com",
            "password": "teste123",
            "equipe": "Individual",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "genero": "F",
            "categoria": "normal",
            "data_nascimento": "1985-06-20",
            "etnia": "Negro",
            "apelido": "TestRole",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": True,
            "assessoria_data": {
                "nome": assessoria_nome,
                "estado": "RJ",
                "cidade": "Rio de Janeiro",
                "mensagem_bio": "Assessoria de atletas de elite"
            }
        }
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user"]["role"] == "dono_assessoria", f"Expected role='dono_assessoria', got {data['user']['role']}"
        
    def test_register_as_dono_creates_assessoria(self, api_client):
        """Test that registering as dono creates an assessoria in /api/assessorias/lista"""
        unique_id = str(uuid.uuid4())[:8]
        assessoria_nome = f"TEST_NewAssessoria_{unique_id}"
        
        payload = {
            "nome": f"Test Assessoria Creator {unique_id}",
            "email": f"test_creator_{unique_id}@test.com",
            "password": "teste123",
            "equipe": "Individual",
            "cidade": "Belo Horizonte",
            "estado": "MG",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1988-03-10",
            "etnia": "Branco",
            "apelido": "Creator",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": True,
            "assessoria_data": {
                "nome": assessoria_nome,
                "estado": "MG",
                "cidade": "Belo Horizonte",
                "mensagem_bio": "Assessoria mineira de corrida"
            }
        }
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        
        # Check if assessoria appears in the list
        lista_response = api_client.get(f"{BASE_URL}/api/assessorias/lista")
        assert lista_response.status_code == 200
        
        assessorias = lista_response.json()
        assessoria_names = [a["nome"] for a in assessorias]
        
        assert assessoria_nome in assessoria_names, f"Assessoria '{assessoria_nome}' not found in lista"
        
    def test_register_as_dono_sets_equipe_as_assessoria_name(self, api_client):
        """Test that dono's equipe is set to the assessoria name"""
        unique_id = str(uuid.uuid4())[:8]
        assessoria_nome = f"TEST_EquipeTest_{unique_id}"
        
        payload = {
            "nome": f"Test Equipe User {unique_id}",
            "email": f"test_equipe_{unique_id}@test.com",
            "password": "teste123",
            "equipe": "Individual",
            "cidade": "Salvador",
            "estado": "BA",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1992-08-05",
            "etnia": "Negro",
            "apelido": "Equipe",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": True,
            "assessoria_data": {
                "nome": assessoria_nome,
                "estado": "BA",
                "cidade": "Salvador",
                "mensagem_bio": "Assessoria baiana de corrida"
            }
        }
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        token = data["token"]
        
        # Get user profile to check equipe
        headers = {"Authorization": f"Bearer {token}"}
        me_response = api_client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # Get full profile
        profile_response = api_client.get(f"{BASE_URL}/api/atletas/meu-perfil", headers=headers)
        assert profile_response.status_code == 200
        
        profile_data = profile_response.json()
        assert profile_data.get("equipe") == assessoria_nome, f"Expected equipe='{assessoria_nome}', got '{profile_data.get('equipe')}'"


class TestDonoAssessoriaNormalRegistration:
    """Test normal registration (not as dono)"""
    
    def test_register_normal_returns_role_atleta(self, api_client):
        """Test that normal registration returns role='atleta'"""
        unique_id = str(uuid.uuid4())[:8]
        
        payload = {
            "nome": f"Test Normal User {unique_id}",
            "email": f"test_normal_{unique_id}@test.com",
            "password": "teste123",
            "equipe": "Individual",
            "cidade": "Porto Alegre",
            "estado": "RS",
            "genero": "F",
            "categoria": "normal",
            "data_nascimento": "1995-12-25",
            "etnia": "Branco",
            "apelido": "Normal",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": False,
            "assessoria_data": None
        }
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user"]["role"] == "atleta", f"Expected role='atleta', got {data['user']['role']}"
        
    def test_register_without_is_dono_flag_returns_role_atleta(self, api_client):
        """Test that registration without is_dono_assessoria flag returns role='atleta'"""
        unique_id = str(uuid.uuid4())[:8]
        
        payload = {
            "nome": f"Test No Flag User {unique_id}",
            "email": f"test_noflag_{unique_id}@test.com",
            "password": "teste123",
            "equipe": "Individual",
            "cidade": "Curitiba",
            "estado": "PR",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1991-07-18",
            "etnia": "Pardo",
            "apelido": "NoFlag",
            "modalidade_usuario": "profissional_amador"
            # No is_dono_assessoria field
        }
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user"]["role"] == "atleta", f"Expected role='atleta', got {data['user']['role']}"


class TestDonoAssessoriaValidation:
    """Test validation for dono de assessoria registration"""
    
    def test_duplicate_assessoria_name_returns_error(self, api_client):
        """Test that registering with duplicate assessoria name returns error"""
        unique_id = str(uuid.uuid4())[:8]
        assessoria_nome = f"TEST_Duplicate_{unique_id}"
        
        # First registration - should succeed
        payload1 = {
            "nome": f"Test First Dono {unique_id}",
            "email": f"test_first_{unique_id}@test.com",
            "password": "teste123",
            "equipe": "Individual",
            "cidade": "Recife",
            "estado": "PE",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-01-15",
            "etnia": "Negro",
            "apelido": "First",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": True,
            "assessoria_data": {
                "nome": assessoria_nome,
                "estado": "PE",
                "cidade": "Recife",
                "mensagem_bio": "Primeira assessoria"
            }
        }
        
        response1 = api_client.post(f"{BASE_URL}/api/auth/register", json=payload1)
        assert response1.status_code == 200
        
        # Second registration with same assessoria name - should fail
        payload2 = {
            "nome": f"Test Second Dono {unique_id}",
            "email": f"test_second_{unique_id}@test.com",
            "password": "teste123",
            "equipe": "Individual",
            "cidade": "Recife",
            "estado": "PE",
            "genero": "F",
            "categoria": "normal",
            "data_nascimento": "1992-05-20",
            "etnia": "Pardo",
            "apelido": "Second",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": True,
            "assessoria_data": {
                "nome": assessoria_nome,  # Same name!
                "estado": "PE",
                "cidade": "Recife",
                "mensagem_bio": "Segunda assessoria"
            }
        }
        
        response2 = api_client.post(f"{BASE_URL}/api/auth/register", json=payload2)
        assert response2.status_code == 400, f"Expected 400 for duplicate assessoria, got {response2.status_code}"
        
        data = response2.json()
        assert "assessoria" in data.get("detail", "").lower() or "existe" in data.get("detail", "").lower(), \
            f"Error message should mention assessoria exists: {data}"


class TestAssessoriasListaWithNewAssessoria:
    """Test that newly created assessorias appear in the lista endpoint"""
    
    def test_new_assessoria_appears_in_lista_with_correct_format(self, api_client):
        """Test that new assessoria has nome, cidade, estado in lista"""
        unique_id = str(uuid.uuid4())[:8]
        assessoria_nome = f"TEST_FormatCheck_{unique_id}"
        assessoria_cidade = "Florianópolis"
        assessoria_estado = "SC"
        
        payload = {
            "nome": f"Test Format Check User {unique_id}",
            "email": f"test_format_{unique_id}@test.com",
            "password": "teste123",
            "equipe": "Individual",
            "cidade": "Florianópolis",
            "estado": "SC",
            "genero": "F",
            "categoria": "normal",
            "data_nascimento": "1987-09-30",
            "etnia": "Branco",
            "apelido": "Format",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": True,
            "assessoria_data": {
                "nome": assessoria_nome,
                "estado": assessoria_estado,
                "cidade": assessoria_cidade,
                "mensagem_bio": "Assessoria catarinense de corrida"
            }
        }
        
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        
        # Check assessoria in lista
        lista_response = api_client.get(f"{BASE_URL}/api/assessorias/lista")
        assert lista_response.status_code == 200
        
        assessorias = lista_response.json()
        
        # Find the created assessoria
        created_assessoria = None
        for a in assessorias:
            if a["nome"] == assessoria_nome:
                created_assessoria = a
                break
        
        assert created_assessoria is not None, f"Assessoria '{assessoria_nome}' not found"
        assert created_assessoria["cidade"] == assessoria_cidade, f"Expected cidade='{assessoria_cidade}'"
        assert created_assessoria["estado"] == assessoria_estado, f"Expected estado='{assessoria_estado}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
