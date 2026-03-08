"""
Tests for Iteration 23: Assessoria Page - Responsável and BIO display
Testing the new header fields showing owner name and BIO message
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

class TestAssessoriaEndpointReturnsResponsavelAndBio:
    """Test that GET /api/liga-assessorias/assessoria/{nome} returns responsavel_nome and mensagem_bio"""
    
    def test_assessoria_cafav_returns_responsavel_nome(self):
        """Test that Assessoria CAFAV returns responsavel_nome"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "responsavel_nome" in data, "Response should contain responsavel_nome field"
        assert data["responsavel_nome"] != "", "responsavel_nome should not be empty"
        print(f"✓ responsavel_nome: {data['responsavel_nome']}")
    
    def test_assessoria_cafav_returns_responsavel_id(self):
        """Test that Assessoria CAFAV returns responsavel_id"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        assert response.status_code == 200
        
        data = response.json()
        assert "responsavel_id" in data, "Response should contain responsavel_id field"
        assert data["responsavel_id"] != "", "responsavel_id should not be empty"
        print(f"✓ responsavel_id: {data['responsavel_id']}")
    
    def test_assessoria_cafav_returns_mensagem_bio(self):
        """Test that Assessoria CAFAV returns mensagem_bio"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        assert response.status_code == 200
        
        data = response.json()
        assert "mensagem_bio" in data, "Response should contain mensagem_bio field"
        assert data["mensagem_bio"] != "", "mensagem_bio should not be empty"
        assert "Atletas" in data["mensagem_bio"], "BIO should contain 'Atletas'"
        print(f"✓ mensagem_bio: {data['mensagem_bio']}")
    
    def test_assessoria_cafav_returns_foto_assessoria(self):
        """Test that Assessoria CAFAV returns foto_assessoria field (can be empty)"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        assert response.status_code == 200
        
        data = response.json()
        assert "foto_assessoria" in data, "Response should contain foto_assessoria field"
        print(f"✓ foto_assessoria: '{data['foto_assessoria']}'")
    
    def test_assessoria_returns_complete_data_structure(self):
        """Test that the response contains all required fields for header display"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = [
            "nome", "estado", "cidade", "total_atletas",
            "responsavel_nome", "responsavel_id", "mensagem_bio", "foto_assessoria",
            "pontos_total", "posicao_nacional", "selo"
        ]
        
        for field in required_fields:
            assert field in data, f"Response should contain {field} field"
        
        print("✓ All required fields present in response")


class TestAdminSetupAssessoriaDono:
    """Test POST /api/admin/setup-assessoria-dono/{equipe_nome}"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_setup_assessoria_requires_authentication(self):
        """Test that setup endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/setup-assessoria-dono/Assessoria%20CAFAV")
        assert response.status_code in [401, 403], "Should require authentication"
    
    def test_setup_assessoria_works_with_valid_equipe(self, auth_token):
        """Test setting up an assessoria dono"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/admin/setup-assessoria-dono/Assessoria%20CAFAV",
            headers=headers
        )
        
        # May return 200 or 404 if no atleta found (already setup)
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "dono" in data or "dono_id" in data
            print(f"✓ Setup response: {data}")
    
    def test_setup_assessoria_nonexistent_returns_404(self, auth_token):
        """Test that non-existent equipe returns 404"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/admin/setup-assessoria-dono/EQUIPE_INEXISTENTE_12345",
            headers=headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestAssessoriaResponsavelNameFormat:
    """Test that the responsavel_nome follows the expected format"""
    
    def test_responsavel_nome_format_gustavo_gomes(self):
        """Verify Assessoria CAFAV has Gustavo Gomes as responsavel"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        assert response.status_code == 200
        
        data = response.json()
        # The context mentions "Gustavo Gomes" as the dono
        assert "Gustavo" in data["responsavel_nome"], f"Expected 'Gustavo' in name, got {data['responsavel_nome']}"
        print(f"✓ Responsável is: {data['responsavel_nome']}")
    
    def test_bio_message_expected_content(self):
        """Verify the BIO message content"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        assert response.status_code == 200
        
        data = response.json()
        expected_bio = "Ajudamos milhares de Atletas pelo Brasil, faça parte do nosso Time!"
        assert data["mensagem_bio"] == expected_bio, f"Expected '{expected_bio}', got '{data['mensagem_bio']}'"
        print(f"✓ BIO message: {data['mensagem_bio']}")


class TestOtherAssessoriasResponsavelAndBio:
    """Test that other assessorias also have these fields (may be empty)"""
    
    def test_other_assessoria_has_responsavel_field(self):
        """Test another assessoria to ensure all have the fields"""
        # Get list of assessorias first
        response = requests.get(f"{BASE_URL}/api/liga-assessorias?tipo=nacional")
        if response.status_code != 200:
            pytest.skip("Could not get assessorias list")
        
        data = response.json()
        ranking = data.get("ranking", [])
        
        if len(ranking) < 2:
            pytest.skip("Not enough assessorias to test")
        
        # Get a different assessoria
        for assessoria in ranking:
            if assessoria["nome"] != "Assessoria CAFAV":
                nome = assessoria["nome"]
                break
        else:
            pytest.skip("Could not find another assessoria")
        
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{nome}")
        assert response.status_code == 200
        
        data = response.json()
        # Fields should exist even if empty
        assert "responsavel_nome" in data
        assert "mensagem_bio" in data
        print(f"✓ {nome} - responsavel_nome: '{data['responsavel_nome']}', mensagem_bio: '{data['mensagem_bio'][:30] if data['mensagem_bio'] else ''}...'")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
