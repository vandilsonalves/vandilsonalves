# /app/backend/tests/test_iter53_ranking_cidade.py
# Tests for Ranking por Cidade feature - Estados, Cidades filtering, and Ranking by City
# Iteration 53: Testing city-based ranking for Profissional/Amador and Povão modalities

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ranking-run-v2.preview.emergentagent.com')

class TestRankingEstados:
    """Tests for GET /api/ranking/estados endpoint"""
    
    def test_get_estados_returns_200(self):
        """Test that estados endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/ranking/estados")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ GET /api/ranking/estados returned 200")
    
    def test_get_estados_returns_list(self):
        """Test that estados endpoint returns a list of estados"""
        response = requests.get(f"{BASE_URL}/api/ranking/estados")
        assert response.status_code == 200
        data = response.json()
        
        assert "estados" in data, "Response should contain 'estados' key"
        assert isinstance(data["estados"], list), "Estados should be a list"
        assert len(data["estados"]) > 0, "Estados list should not be empty"
        print(f"✓ GET /api/ranking/estados returned {len(data['estados'])} estados: {data['estados']}")
    
    def test_get_estados_contains_sp(self):
        """Test that SP is in the list of estados"""
        response = requests.get(f"{BASE_URL}/api/ranking/estados")
        assert response.status_code == 200
        data = response.json()
        
        assert "SP" in data["estados"], "SP should be in the list of estados"
        print(f"✓ SP is present in the estados list")


class TestRankingCidades:
    """Tests for GET /api/ranking/cidades endpoint"""
    
    def test_get_cidades_returns_200(self):
        """Test that cidades endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/ranking/cidades")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ GET /api/ranking/cidades returned 200")
    
    def test_get_cidades_returns_list_with_atletas_count(self):
        """Test that cidades endpoint returns cities with athlete count"""
        response = requests.get(f"{BASE_URL}/api/ranking/cidades")
        assert response.status_code == 200
        data = response.json()
        
        assert "cidades" in data, "Response should contain 'cidades' key"
        assert isinstance(data["cidades"], list), "Cidades should be a list"
        assert len(data["cidades"]) > 0, "Cidades list should not be empty"
        
        # Check structure of first city
        first_city = data["cidades"][0]
        assert "nome" in first_city, "City should have 'nome' field"
        assert "estado" in first_city, "City should have 'estado' field"
        assert "atletas" in first_city, "City should have 'atletas' count"
        
        print(f"✓ GET /api/ranking/cidades returned {len(data['cidades'])} cities")
        print(f"  First city: {first_city['nome']}/{first_city['estado']} with {first_city['atletas']} athletes")
    
    def test_get_cidades_filtered_by_estado_sp(self):
        """Test filtering cities by estado=SP"""
        response = requests.get(f"{BASE_URL}/api/ranking/cidades?estado=SP")
        assert response.status_code == 200
        data = response.json()
        
        assert "cidades" in data, "Response should contain 'cidades' key"
        assert len(data["cidades"]) > 0, "SP should have cities"
        
        # All cities should be from SP
        for city in data["cidades"]:
            assert city["estado"] == "SP", f"City {city['nome']} should be from SP, got {city['estado']}"
        
        print(f"✓ GET /api/ranking/cidades?estado=SP returned {len(data['cidades'])} cities in SP")
    
    def test_get_cidades_sp_contains_sao_paulo(self):
        """Test that São Paulo is in the list of SP cities"""
        response = requests.get(f"{BASE_URL}/api/ranking/cidades?estado=SP")
        assert response.status_code == 200
        data = response.json()
        
        city_names = [c["nome"] for c in data["cidades"]]
        assert "São Paulo" in city_names, "São Paulo should be in the list of SP cities"
        
        # Check São Paulo athlete count
        sao_paulo = next(c for c in data["cidades"] if c["nome"] == "São Paulo")
        assert sao_paulo["atletas"] > 10, f"São Paulo should have 14+ athletes, got {sao_paulo['atletas']}"
        print(f"✓ São Paulo has {sao_paulo['atletas']} athletes")


class TestRankingPorCidadeProfissional:
    """Tests for GET /api/ranking/por-cidade/{estado}/{cidade} for Profissional modality"""
    
    def test_ranking_sp_sao_paulo_profissional_returns_200(self):
        """Test that profissional ranking for SP/São Paulo returns 200"""
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/SP/S%C3%A3o%20Paulo?modalidade=profissional&genero=M")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ GET /api/ranking/por-cidade/SP/São Paulo (profissional) returned 200")
    
    def test_ranking_sp_sao_paulo_profissional_has_ranking(self):
        """Test that profissional ranking for SP/São Paulo returns ranking list"""
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/SP/S%C3%A3o%20Paulo?modalidade=profissional&genero=M")
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data, "Response should contain 'ranking' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "cidade" in data, "Response should contain 'cidade' key"
        assert "estado" in data, "Response should contain 'estado' key"
        
        assert data["cidade"] == "São Paulo", f"Expected 'São Paulo', got {data['cidade']}"
        assert data["estado"] == "SP", f"Expected 'SP', got {data['estado']}"
        
        print(f"✓ Profissional ranking for São Paulo/SP has {data['total']} athletes")
    
    def test_ranking_sp_sao_paulo_profissional_athlete_structure(self):
        """Test that profissional ranking returns athletes with correct structure"""
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/SP/S%C3%A3o%20Paulo?modalidade=profissional&genero=M")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["ranking"]) > 0, "Ranking should not be empty"
        
        first_athlete = data["ranking"][0]
        expected_fields = ["colocacao", "id", "nome", "pontos", "total_corridas", "is_elite"]
        for field in expected_fields:
            assert field in first_athlete, f"Athlete should have '{field}' field"
        
        # Check ordering - first should have colocacao 1
        assert first_athlete["colocacao"] == 1, f"First athlete should have colocacao 1, got {first_athlete['colocacao']}"
        
        print(f"✓ First athlete: {first_athlete['nome']} - {first_athlete['pontos']} pts, {first_athlete['total_corridas']} corridas")
    
    def test_ranking_profissional_athletes_ordered_by_points(self):
        """Test that athletes are ordered by points descending"""
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/SP/S%C3%A3o%20Paulo?modalidade=profissional&genero=M")
        assert response.status_code == 200
        data = response.json()
        
        ranking = data["ranking"]
        if len(ranking) > 1:
            for i in range(len(ranking) - 1):
                assert ranking[i]["pontos"] >= ranking[i+1]["pontos"], \
                    f"Athletes should be ordered by points: {ranking[i]['pontos']} should be >= {ranking[i+1]['pontos']}"
        
        print(f"✓ Athletes are correctly ordered by points")


class TestRankingPorCidadePovao:
    """Tests for GET /api/ranking/por-cidade/{estado}/{cidade} for Povão modality"""
    
    def test_ranking_sp_sao_paulo_povao_returns_200(self):
        """Test that povao ranking for SP/São Paulo returns 200"""
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/SP/S%C3%A3o%20Paulo?modalidade=povao&genero=M")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ GET /api/ranking/por-cidade/SP/São Paulo (povao) returned 200")
    
    def test_ranking_sp_sao_paulo_povao_response_structure(self):
        """Test that povao ranking returns correct response structure"""
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/SP/S%C3%A3o%20Paulo?modalidade=povao&genero=M")
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data, "Response should contain 'ranking' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "cidade" in data, "Response should contain 'cidade' key"
        assert "estado" in data, "Response should contain 'estado' key"
        assert "modalidade" in data, "Response should contain 'modalidade' key"
        
        assert data["modalidade"] == "povao", f"Expected modalidade 'povao', got {data['modalidade']}"
        
        print(f"✓ Povao ranking for São Paulo/SP - structure verified, total: {data['total']}")


class TestRankingPorCidadeOtherCases:
    """Additional test cases for edge cases"""
    
    def test_ranking_rj_rio_profissional(self):
        """Test ranking for Rio de Janeiro"""
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/RJ/Rio%20de%20Janeiro?modalidade=profissional&genero=M")
        assert response.status_code == 200
        data = response.json()
        
        assert data["cidade"] == "Rio de Janeiro"
        assert data["estado"] == "RJ"
        print(f"✓ RJ/Rio de Janeiro ranking returned {data['total']} athletes")
    
    def test_ranking_nonexistent_city(self):
        """Test ranking for a non-existent city"""
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/SP/CidadeInexistente?modalidade=profissional&genero=M")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ranking"] == [], "Non-existent city should return empty ranking"
        assert data["total"] == 0, "Non-existent city should return total 0"
        print(f"✓ Non-existent city returns empty ranking")
    
    def test_ranking_with_feminino_genero(self):
        """Test ranking with genero=F"""
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/SP/S%C3%A3o%20Paulo?modalidade=profissional&genero=F")
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data
        print(f"✓ Feminino ranking for São Paulo/SP has {data['total']} athletes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
