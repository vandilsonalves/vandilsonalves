"""
Test cases for Iteration 28: AssessoriaPage improvements
- Tests the assessoria details endpoint
- Verifies responsavel_nome, responsavel_id, and mensagem_bio are returned
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAssessoriaDetailsEndpoint:
    """Tests for GET /api/liga-assessorias/assessoria/{nome_equipe}"""
    
    def test_assessoria_cafav_loads(self):
        """Test that Assessoria CAFAV details load correctly"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        
        assert response.status_code == 200
        data = response.json()
        
        # Basic fields
        assert data["nome"] == "Assessoria CAFAV"
        assert "estado" in data
        assert "cidade" in data
        print(f"✓ Assessoria CAFAV loaded: {data['cidade']}, {data['estado']}")
    
    def test_assessoria_has_responsavel_info(self):
        """Test that responsavel_nome and responsavel_id are returned"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        
        assert response.status_code == 200
        data = response.json()
        
        # Responsavel fields
        assert "responsavel_nome" in data
        assert "responsavel_id" in data
        assert data["responsavel_nome"] == "Gustavo Souza"
        assert len(data["responsavel_id"]) > 0
        print(f"✓ Responsável: {data['responsavel_nome']} (ID: {data['responsavel_id']})")
    
    def test_assessoria_has_bio(self):
        """Test that mensagem_bio is returned"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        
        assert response.status_code == 200
        data = response.json()
        
        # Bio field
        assert "mensagem_bio" in data
        assert len(data["mensagem_bio"]) > 0
        print(f"✓ Bio: {data['mensagem_bio'][:50]}...")
    
    def test_assessoria_has_stats(self):
        """Test that all statistics fields are present"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        
        assert response.status_code == 200
        data = response.json()
        
        # Stats fields
        assert "total_atletas" in data
        assert "pontos_cadastro" in data
        assert "pontos_resultados" in data
        assert "pontos_total" in data
        assert "total_resultados" in data
        assert "total_primeiros" in data
        assert "total_podios" in data
        assert "posicao_nacional" in data
        assert "selo" in data
        
        print(f"✓ Stats - Atletas: {data['total_atletas']}, Total Points: {data['pontos_total']}, Rank: {data['posicao_nacional']}º")
    
    def test_assessoria_has_selo(self):
        """Test that selo is calculated correctly"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        
        assert response.status_code == 200
        data = response.json()
        
        # Selo should be 'ouro' for top 20 national
        assert data["selo"] in ["ouro", "prata", "bronze"]
        
        # Based on position, check selo
        pos = data.get("posicao_nacional")
        if pos and pos <= 20:
            assert data["selo"] == "ouro"
        elif pos and pos <= 50:
            assert data["selo"] == "prata"
        
        print(f"✓ Selo: {data['selo'].upper()} (Position: {data['posicao_nacional']}º)")
    
    def test_assessoria_has_atletas_list(self):
        """Test that atletas list is returned with correct structure"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        
        assert response.status_code == 200
        data = response.json()
        
        # Atletas list
        assert "atletas" in data
        assert isinstance(data["atletas"], list)
        assert len(data["atletas"]) > 0
        
        # Check atleta structure
        atleta = data["atletas"][0]
        assert "id" in atleta
        assert "nome" in atleta
        assert "foto_url" in atleta
        assert "categoria" in atleta
        assert "genero" in atleta
        
        print(f"✓ Atletas: {len(data['atletas'])} members")
    
    def test_assessoria_has_evolucao_mensal(self):
        """Test that evolucao_mensal is returned"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        
        assert response.status_code == 200
        data = response.json()
        
        # Evolution data
        assert "evolucao_mensal" in data
        assert isinstance(data["evolucao_mensal"], list)
        
        if len(data["evolucao_mensal"]) > 0:
            ev = data["evolucao_mensal"][0]
            assert "mes" in ev
            assert "resultados" in ev
            assert "pontos" in ev
        
        print(f"✓ Evolução mensal: {len(data['evolucao_mensal'])} meses de dados")
    
    def test_assessoria_not_found(self):
        """Test 404 for non-existent assessoria"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20Inexistente%20XYZ")
        
        assert response.status_code == 404
        print("✓ 404 returned for non-existent assessoria")


class TestAtletaProfileEndpoint:
    """Tests for the atleta profile navigation (responsavel profile)"""
    
    def test_atleta_profile_loads(self):
        """Test that the responsavel's profile can be loaded"""
        # First get the responsavel_id
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/Assessoria%20CAFAV")
        assert response.status_code == 200
        
        responsavel_id = response.json()["responsavel_id"]
        
        # Then get the atleta profile
        profile_response = requests.get(f"{BASE_URL}/api/atletas/{responsavel_id}")
        
        assert profile_response.status_code == 200
        profile = profile_response.json()
        
        assert profile["nome"] == "Gustavo Souza"
        print(f"✓ Responsável profile loaded: {profile['nome']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
