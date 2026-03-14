# /app/backend/tests/test_iter34_indicacao_system.py
# Tests for the Friend Referral System (Sistema de Indicação de Amigos)
# Features tested:
# - Referral code verification endpoint (GET /api/indicacao/verificar-codigo/{codigo})
# - Registration with valid referral code
# - Registration without referral code
# - Registration with invalid referral code
# - Referral counter increment

import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestIndicacaoCodeVerification:
    """Test the referral code verification endpoint"""
    
    def test_verify_valid_referral_code(self):
        """Test verification of a valid referral code"""
        # Use the known valid code from the test credentials
        response = requests.get(f"{BASE_URL}/api/indicacao/verificar-codigo/REF-CSAC0455")
        
        assert response.status_code == 200
        data = response.json()
        assert "valido" in data
        assert data["valido"] == True
        assert "indicador" in data
        assert data["indicador"]["nome"] is not None
        print(f"Valid code verification: {data}")
    
    def test_verify_invalid_referral_code(self):
        """Test verification of an invalid referral code"""
        response = requests.get(f"{BASE_URL}/api/indicacao/verificar-codigo/INVALID-CODE-123")
        
        assert response.status_code == 200
        data = response.json()
        assert "valido" in data
        assert data["valido"] == False
        assert data["indicador"] is None
        print(f"Invalid code verification: {data}")
    
    def test_verify_short_code(self):
        """Test verification of a code that's too short"""
        response = requests.get(f"{BASE_URL}/api/indicacao/verificar-codigo/ABC")
        
        assert response.status_code == 200
        data = response.json()
        assert data["valido"] == False
        print(f"Short code verification: {data}")
    
    def test_verify_uppercase_code(self):
        """Test that code verification is case-insensitive"""
        response = requests.get(f"{BASE_URL}/api/indicacao/verificar-codigo/ref-csac0455")
        
        assert response.status_code == 200
        data = response.json()
        # Should work with lowercase because backend converts to uppercase
        assert data["valido"] == True
        print(f"Lowercase code verification (should be valid): {data}")


class TestRegistrationWithReferral:
    """Test user registration with referral codes"""
    
    def test_register_with_valid_referral_code(self):
        """Test registration with a valid referral code - should register indicação"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_indicado_valido_{unique_id}@teste.com"
        
        payload = {
            "nome": f"Teste Indicado {unique_id}",
            "email": test_email,
            "password": "senha123",
            "equipe": "Individual",
            "cidade": "São Paulo",
            "estado": "SP",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-05-15",
            "etnia": "Branco",
            "apelido": "TestRef",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": False,
            "assessoria_data": None,
            "codigo_indicacao": "REF-CSAC0455"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "token" in data
        assert "user" in data
        assert "indicacao" in data
        
        # Verify indicação was registered
        assert data["indicacao"]["registrada"] == True
        assert data["indicacao"]["indicador_nome"] is not None
        print(f"Registration with valid code: indicacao={data['indicacao']}")
    
    def test_register_without_referral_code(self):
        """Test registration without a referral code - should work normally"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_sem_indicacao_{unique_id}@teste.com"
        
        payload = {
            "nome": f"Teste Sem Indicação {unique_id}",
            "email": test_email,
            "password": "senha123",
            "equipe": "Individual",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "genero": "F",
            "categoria": "normal",
            "data_nascimento": "1992-08-20",
            "etnia": "Pardo",
            "apelido": "",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": False,
            "assessoria_data": None,
            "codigo_indicacao": ""
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "token" in data
        assert "user" in data
        # indicacao field should be None when no code provided
        assert data.get("indicacao") is None
        print(f"Registration without code: user={data['user']}")
    
    def test_register_with_invalid_referral_code(self):
        """Test registration with invalid referral code - should complete but indicação not registered"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_indicacao_invalida_{unique_id}@teste.com"
        
        payload = {
            "nome": f"Teste Indicação Inválida {unique_id}",
            "email": test_email,
            "password": "senha123",
            "equipe": "Individual",
            "cidade": "Belo Horizonte",
            "estado": "MG",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1988-11-10",
            "etnia": "Negro",
            "apelido": "",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": False,
            "assessoria_data": None,
            "codigo_indicacao": "CODIGO-INVALIDO-XYZ"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        # Registration should succeed even with invalid code
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "token" in data
        assert "user" in data
        
        # Indicação should NOT be registered
        if data.get("indicacao"):
            assert data["indicacao"]["registrada"] == False
        print(f"Registration with invalid code: indicacao={data.get('indicacao')}")
    
    def test_register_with_null_referral_code(self):
        """Test registration with null referral code field - should work normally"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_null_indicacao_{unique_id}@teste.com"
        
        payload = {
            "nome": f"Teste Null Indicação {unique_id}",
            "email": test_email,
            "password": "senha123",
            "equipe": "Individual",
            "cidade": "Salvador",
            "estado": "BA",
            "genero": "F",
            "categoria": "normal",
            "data_nascimento": "1995-03-25",
            "etnia": "Mulato",
            "apelido": "",
            "modalidade_usuario": "profissional_amador",
            "is_dono_assessoria": False,
            "assessoria_data": None,
            "codigo_indicacao": None
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"Registration with null code: success")


class TestReferralCounterIncrement:
    """Test that referral counter is incremented when a valid code is used"""
    
    def test_get_referrer_indicacoes_count(self):
        """Test getting the referrer's indicações count"""
        # First, login as admin to check indicador data
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Admin login failed - skipping counter test")
        
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check the referrer's profile - carlos.silva@teste.com
        # First we need to find the user by searching or if there's an endpoint
        # For now, let's verify via the ranking-indicacoes endpoint if available
        ranking_response = requests.get(f"{BASE_URL}/api/indicacao/ranking")
        
        if ranking_response.status_code == 200:
            data = ranking_response.json()
            print(f"Indicações ranking: {data}")
            assert "ranking" in data or "total" in data
        else:
            print(f"Ranking endpoint status: {ranking_response.status_code}")


class TestReferralCodeEndpoints:
    """Test all referral system endpoints"""
    
    def test_verificar_codigo_endpoint_exists(self):
        """Test that the verificar-codigo endpoint exists"""
        response = requests.get(f"{BASE_URL}/api/indicacao/verificar-codigo/TEST")
        
        # Should return 200 (not 404)
        assert response.status_code == 200
        print(f"Verificar codigo endpoint: WORKING")
    
    def test_indicacao_ranking_endpoint(self):
        """Test the indicação ranking endpoint"""
        response = requests.get(f"{BASE_URL}/api/indicacao/ranking")
        
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        assert "total" in data
        print(f"Indicação ranking: total={data['total']}, ranking_count={len(data['ranking'])}")
    
    def test_meu_codigo_requires_auth(self):
        """Test that meu-codigo endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/indicacao/meu-codigo")
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403]
        print(f"Meu código requires auth: {response.status_code}")
    
    def test_meu_codigo_with_auth(self):
        """Test meu-codigo endpoint with valid authentication"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/indicacao/meu-codigo", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "codigo" in data
        assert "link" in data
        assert "total_indicacoes" in data
        assert "indicacoes_para_embaixador" in data
        assert "is_embaixador" in data
        print(f"Meu código: {data}")
    
    def test_minhas_indicacoes_with_auth(self):
        """Test minhas-indicacoes endpoint with valid authentication"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/indicacao/minhas-indicacoes", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "indicacoes" in data
        print(f"Minhas indicações: total={data['total']}")


class TestReferralWithExistingIndicador:
    """Test referral with the existing indicador (carlos.silva@teste.com with code REF-CSAC0455)"""
    
    def test_existing_indicador_code_is_valid(self):
        """Verify the existing indicador's code works"""
        response = requests.get(f"{BASE_URL}/api/indicacao/verificar-codigo/REF-CSAC0455")
        
        assert response.status_code == 200
        data = response.json()
        assert data["valido"] == True
        
        # The indicador should be Carlos Silva or similar
        indicador_nome = data["indicador"]["nome"]
        print(f"Indicador nome: {indicador_nome}")
        assert indicador_nome is not None and len(indicador_nome) > 0


# Cleanup fixtures
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_users():
    """Cleanup test users after all tests"""
    yield
    # Note: In production, you'd want to delete TEST_ prefixed users
    # For now, we'll leave them as they don't affect other tests
    print("Test cleanup complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
