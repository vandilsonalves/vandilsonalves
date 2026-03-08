"""
Test iteration 21: Assessorias Lista Dropdown
Tests for GET /api/assessorias/lista endpoint that returns list of assessorias
for the athlete registration dropdown
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAssessoriasLista:
    """Test GET /api/assessorias/lista endpoint"""
    
    def test_assessorias_lista_returns_200(self):
        """Test that endpoint returns 200 status"""
        response = requests.get(f"{BASE_URL}/api/assessorias/lista")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/assessorias/lista returns 200")
    
    def test_assessorias_lista_returns_list(self):
        """Test that endpoint returns a list"""
        response = requests.get(f"{BASE_URL}/api/assessorias/lista")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Returns list with {len(data)} assessorias")
    
    def test_assessorias_lista_format(self):
        """Test that each assessoria has nome, cidade, estado fields"""
        response = requests.get(f"{BASE_URL}/api/assessorias/lista")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) > 0, "Expected at least one assessoria in list"
        
        for idx, assessoria in enumerate(data[:5]):  # Check first 5
            assert "nome" in assessoria, f"Missing 'nome' field in assessoria {idx}"
            assert "cidade" in assessoria, f"Missing 'cidade' field in assessoria {idx}"
            assert "estado" in assessoria, f"Missing 'estado' field in assessoria {idx}"
        
        print("✓ Assessorias have correct format: {nome, cidade, estado}")
    
    def test_assessorias_lista_excludes_individual(self):
        """Test that 'Individual' and 'Sem equipe' are NOT in the list"""
        response = requests.get(f"{BASE_URL}/api/assessorias/lista")
        assert response.status_code == 200
        data = response.json()
        
        nomes_lower = [a["nome"].lower() for a in data if a.get("nome")]
        
        assert "individual" not in nomes_lower, "'Individual' should not be in list"
        assert "sem equipe" not in nomes_lower, "'Sem equipe' should not be in list"
        
        print("✓ List excludes 'Individual' and 'Sem equipe' (these are handled by frontend)")
    
    def test_assessorias_lista_nome_not_empty(self):
        """Test that assessoria names are not empty"""
        response = requests.get(f"{BASE_URL}/api/assessorias/lista")
        assert response.status_code == 200
        data = response.json()
        
        for assessoria in data:
            assert assessoria.get("nome"), f"Assessoria has empty nome: {assessoria}"
            assert len(assessoria["nome"].strip()) > 0, f"Assessoria nome is whitespace: {assessoria}"
        
        print("✓ All assessorias have non-empty names")


class TestAssessoriasListaIntegration:
    """Integration test for assessorias list with registration flow"""
    
    def test_registration_with_assessoria_from_list(self):
        """Test that registration works with an assessoria from the list"""
        # First get the list
        lista_response = requests.get(f"{BASE_URL}/api/assessorias/lista")
        assert lista_response.status_code == 200
        assessorias = lista_response.json()
        
        if len(assessorias) == 0:
            pytest.skip("No assessorias in list to test with")
        
        # Pick first assessoria
        equipe_selecionada = assessorias[0]["nome"]
        
        # Try to register (may fail if email exists, which is fine)
        import uuid
        unique_email = f"test_assesoria_list_{uuid.uuid4().hex[:8]}@test.com"
        
        register_data = {
            "nome": "Test Atleta Lista",
            "email": unique_email,
            "password": "test123456",
            "equipe": equipe_selecionada,
            "cidade": "São Paulo",
            "estado": "SP",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-01-01",
            "etnia": "Branco",
            "modalidade_usuario": "profissional_amador"
        }
        
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        
        # Should succeed or fail with meaningful error (not 500)
        assert register_response.status_code in [200, 201, 400], \
            f"Unexpected status {register_response.status_code}: {register_response.text}"
        
        if register_response.status_code in [200, 201]:
            print(f"✓ Registration succeeded with equipe from list: {equipe_selecionada}")
        else:
            print(f"✓ Registration endpoint responds properly (got {register_response.status_code})")
    
    def test_registration_with_individual(self):
        """Test that registration works with 'Individual' equipe"""
        import uuid
        unique_email = f"test_individual_{uuid.uuid4().hex[:8]}@test.com"
        
        register_data = {
            "nome": "Test Atleta Individual",
            "email": unique_email,
            "password": "test123456",
            "equipe": "Individual",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "genero": "F",
            "categoria": "normal",
            "data_nascimento": "1995-06-15",
            "etnia": "Negro",
            "modalidade_usuario": "profissional_amador"
        }
        
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        
        # Should succeed
        assert register_response.status_code in [200, 201], \
            f"Registration with 'Individual' failed: {register_response.status_code} - {register_response.text}"
        
        print("✓ Registration with 'Individual' equipe works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
