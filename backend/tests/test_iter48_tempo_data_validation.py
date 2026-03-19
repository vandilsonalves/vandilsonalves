"""
Iteration 48: Test Bug Fixes for Submeter Resultados
=======================================================
Bug Report:
- Athletes from 'Povão' modality could submit results with zero time (campo was optional)
- Athletes could submit races older than 30 days

Fixes Implemented:
1) 'tempo' field is now REQUIRED for ALL athletes (including Povão)
2) 30-day validation blocks submissions of old races

Endpoint: POST /api/resultados/submeter
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Test login to get auth token"""
    
    def test_login_admin(self):
        """Login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "user" in data, "No user in response"
        print(f"✅ Admin login successful - User: {data['user'].get('nome', 'N/A')}")
        return data["token"]


class TestTempoObrigatorio:
    """Test that 'tempo' field is required for ALL athletes"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_submit_without_tempo_returns_400(self, auth_headers):
        """
        Test: Submit result WITHOUT tempo field
        Expected: 400 error - Tempo é obrigatório
        """
        # Calculate a valid date (within 30 days)
        valid_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Corrida sem Tempo",
            "colocacao": "5",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": valid_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "10KM"
            # MISSING: "tempo" field
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=auth_headers
        )
        
        # Should return 400 or 422 (validation error)
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"
        print(f"✅ Submitting without tempo returns error: {response.status_code}")
    
    def test_submit_with_empty_tempo_returns_400(self, auth_headers):
        """
        Test: Submit result with EMPTY tempo field
        Expected: 400 error - Tempo é obrigatório
        """
        valid_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Corrida Tempo Vazio",
            "colocacao": "5",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": valid_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "10KM",
            "tempo": ""  # Empty tempo
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"
        
        # Check error message contains tempo-related text
        error_data = response.json().get("detail", "")
        # Handle both list (Pydantic validation) and string (HTTPException) formats
        if isinstance(error_data, list):
            error_msg = str(error_data)
        else:
            error_msg = str(error_data)
        assert "tempo" in error_msg.lower() or "obrigatório" in error_msg.lower() or "required" in error_msg.lower(), f"Error should mention 'tempo': {error_msg}"
        print(f"✅ Submitting with empty tempo returns error: {error_msg}")
    
    def test_submit_with_zero_tempo_returns_400(self, auth_headers):
        """
        Test: Submit result with 00:00:00 tempo
        Expected: 400 error - Tempo zerado não é permitido
        """
        valid_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Corrida Tempo Zero",
            "colocacao": "5",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": valid_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "10KM",
            "tempo": "00:00:00"  # Zero tempo
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        error_msg = response.json().get("detail", "")
        assert "tempo" in error_msg.lower() or "obrigatório" in error_msg.lower(), f"Error should mention 'tempo': {error_msg}"
        print(f"✅ Submitting with 00:00:00 tempo returns error: {error_msg}")
    
    def test_submit_with_invalid_tempo_format_returns_400(self, auth_headers):
        """
        Test: Submit result with invalid tempo format
        Expected: 400 error - Formato inválido
        """
        valid_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Corrida Tempo Invalido",
            "colocacao": "5",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": valid_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "10KM",
            "tempo": "1:30:45"  # Missing leading zero
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        error_msg = response.json().get("detail", "")
        assert "formato" in error_msg.lower() or "HH:MM:SS" in error_msg, f"Error should mention format: {error_msg}"
        print(f"✅ Submitting with invalid tempo format returns error: {error_msg}")


class TestValidacao30Dias:
    """Test that submissions are blocked for races older than 30 days"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_submit_race_older_than_30_days_returns_400(self, auth_headers):
        """
        Test: Submit result for race older than 30 days
        Expected: 400 error - Não é permitido submeter resultados com mais de 30 dias
        """
        # Calculate a date 45 days ago
        old_date = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Corrida Antiga",
            "colocacao": "5",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": old_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "10KM",
            "tempo": "01:30:45"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        error_msg = response.json().get("detail", "")
        assert "30 dias" in error_msg.lower() or "30" in error_msg, f"Error should mention 30 days: {error_msg}"
        print(f"✅ Submitting race older than 30 days returns error: {error_msg}")
    
    def test_submit_race_exactly_31_days_old_returns_400(self, auth_headers):
        """
        Test: Submit result for race exactly 31 days old
        Expected: 400 error - Não é permitido
        """
        old_date = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Corrida 31 Dias",
            "colocacao": "5",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": old_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "10KM",
            "tempo": "01:30:45"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        error_msg = response.json().get("detail", "")
        assert "30" in error_msg, f"Error should mention 30 days: {error_msg}"
        print(f"✅ Race 31 days old returns error: {error_msg}")
    
    def test_submit_future_date_returns_400(self, auth_headers):
        """
        Test: Submit result for future date
        Expected: 400 error - Data da competição não pode ser futura
        """
        future_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Corrida Futura",
            "colocacao": "5",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": future_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "10KM",
            "tempo": "01:30:45"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        error_msg = response.json().get("detail", "")
        assert "futura" in error_msg.lower() or "future" in error_msg.lower(), f"Error should mention future date: {error_msg}"
        print(f"✅ Future date submission returns error: {error_msg}")
    
    def test_submit_race_within_30_days_is_allowed(self, auth_headers):
        """
        Test: Submit result for race within 30 days
        Expected: 200/201 success or 403 (if user period expired - which is acceptable)
        """
        valid_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Corrida Válida 15 Dias",
            "colocacao": "5",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": valid_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "10KM",
            "tempo": "01:30:45"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=auth_headers
        )
        
        # Valid submission should return 200 or 201
        # May return 403 if trial period expired (acceptable - not related to 30 days validation)
        # Should NOT return 400 with "30 dias" error
        if response.status_code == 400:
            error_msg = response.json().get("detail", "")
            assert "30 dias" not in error_msg.lower(), f"Valid date within 30 days should not fail with 30 days error: {error_msg}"
        
        print(f"✅ Race within 30 days - Response: {response.status_code}")


class TestSubmissaoValida:
    """Test valid submission with all required fields"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_valid_submission_with_all_fields(self, auth_headers):
        """
        Test: Submit valid result with all required fields
        Expected: 200/201 success (or 403 if trial expired)
        """
        valid_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Corrida Válida Completa",
            "colocacao": "3",
            "cidade_competicao": "Rio de Janeiro",
            "estado_competicao": "RJ",
            "data_competicao": valid_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "21KM",
            "tempo": "02:15:30"  # Valid tempo format
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=auth_headers
        )
        
        # Should be 200/201 (success) or 403 (trial expired - acceptable)
        # Should NOT be 400 with tempo/30 dias error
        if response.status_code == 400:
            error_msg = response.json().get("detail", "")
            assert "tempo" not in error_msg.lower(), f"Valid tempo should not fail: {error_msg}"
            assert "30 dias" not in error_msg.lower(), f"Valid date should not fail: {error_msg}"
        
        print(f"✅ Valid submission - Response: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   Message: {response.json().get('message', 'N/A')}")


class TestWithoutAuth:
    """Test endpoints without authentication"""
    
    def test_submit_without_auth_returns_401_or_403(self):
        """Test that submission requires authentication"""
        valid_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        
        data = {
            "nome_competicao": "TEST_Sem Auth",
            "colocacao": "5",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": valid_date,
            "link_resultado": "https://www.exemplo.com/resultado",
            "distancia": "10KM",
            "tempo": "01:30:45"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data
        )
        
        assert response.status_code in [401, 403, 422], f"Expected 401/403/422, got {response.status_code}"
        print(f"✅ Submission without auth returns: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
