"""
Test Suite for Hall da Fama Feature - Iteration 117
Tests the Hall da Fama (Hall of Fame) feature showing champions from finalized seasons.

Features tested:
- GET /api/temporadas/historico - Returns all seasons including finalized ones
- GET /api/temporadas/{season_id}/ranking-final - Returns snapshot with all ranking categories
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestTemporadasHistorico:
    """Tests for GET /api/temporadas/historico endpoint"""
    
    def test_historico_returns_200(self):
        """Test that historico endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/temporadas/historico")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/temporadas/historico returns 200")
    
    def test_historico_returns_temporadas_list(self):
        """Test that historico returns a list of temporadas"""
        response = requests.get(f"{BASE_URL}/api/temporadas/historico")
        data = response.json()
        
        assert "temporadas" in data, "Response should contain 'temporadas' key"
        assert isinstance(data["temporadas"], list), "temporadas should be a list"
        print(f"✓ Historico returns {len(data['temporadas'])} temporadas")
    
    def test_historico_contains_finalized_season_2025(self):
        """Test that historico contains finalized season 2025"""
        response = requests.get(f"{BASE_URL}/api/temporadas/historico")
        data = response.json()
        
        temporadas = data.get("temporadas", [])
        season_2025 = next((t for t in temporadas if t.get("season_id") == 2025), None)
        
        assert season_2025 is not None, "Season 2025 should exist in historico"
        assert season_2025.get("status") == "finalizada", f"Season 2025 should be 'finalizada', got {season_2025.get('status')}"
        print("✓ Season 2025 exists with status 'finalizada'")
    
    def test_historico_season_has_required_fields(self):
        """Test that each season has required fields"""
        response = requests.get(f"{BASE_URL}/api/temporadas/historico")
        data = response.json()
        
        required_fields = ["season_id", "status", "data_inicio", "data_fim"]
        
        for temp in data.get("temporadas", []):
            for field in required_fields:
                assert field in temp, f"Season {temp.get('season_id')} missing field: {field}"
        
        print("✓ All seasons have required fields")


class TestRankingFinal:
    """Tests for GET /api/temporadas/{season_id}/ranking-final endpoint"""
    
    def test_ranking_final_2025_returns_200(self):
        """Test that ranking-final for season 2025 returns 200"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/temporadas/2025/ranking-final returns 200")
    
    def test_ranking_final_contains_all_categories(self):
        """Test that ranking-final contains all ranking categories"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        required_categories = [
            "ranking_profissional",
            "ranking_galera",
            "ranking_assessorias",
            "ranking_corridas"
        ]
        
        for category in required_categories:
            assert category in data, f"Missing category: {category}"
        
        print("✓ Ranking final contains all required categories")
    
    def test_ranking_profissional_has_masculino_feminino(self):
        """Test that ranking_profissional has both M and F genders"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_pro = data.get("ranking_profissional", [])
        genders = [r.get("genero") for r in ranking_pro]
        
        assert "M" in genders, "ranking_profissional should have Masculino (M)"
        assert "F" in genders, "ranking_profissional should have Feminino (F)"
        print("✓ Ranking profissional has both M and F genders")
    
    def test_ranking_profissional_has_atletas(self):
        """Test that ranking_profissional categories have atletas"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_pro = data.get("ranking_profissional", [])
        
        for category in ranking_pro:
            atletas = category.get("atletas", [])
            assert len(atletas) > 0, f"Category {category.get('genero')} should have atletas"
            
            # Check first athlete has required fields
            if atletas:
                first = atletas[0]
                assert "nome" in first, "Atleta should have 'nome'"
                assert "pontos_total" in first, "Atleta should have 'pontos_total'"
                assert "posicao" in first, "Atleta should have 'posicao'"
        
        print("✓ Ranking profissional categories have atletas with required fields")
    
    def test_ranking_galera_has_masculino_feminino(self):
        """Test that ranking_galera has both M and F genders"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_galera = data.get("ranking_galera", [])
        genders = [r.get("genero") for r in ranking_galera]
        
        assert "M" in genders, "ranking_galera should have Masculino (M)"
        assert "F" in genders, "ranking_galera should have Feminino (F)"
        print("✓ Ranking galera has both M and F genders")
    
    def test_ranking_galera_has_atletas_with_pontos_povao(self):
        """Test that ranking_galera atletas have pontos_povao field"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_galera = data.get("ranking_galera", [])
        
        for category in ranking_galera:
            atletas = category.get("atletas", [])
            if atletas:
                first = atletas[0]
                assert "pontos_povao" in first, "Galera atleta should have 'pontos_povao'"
        
        print("✓ Ranking galera atletas have pontos_povao field")
    
    def test_ranking_corridas_has_required_fields(self):
        """Test that ranking_corridas has required fields"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_corridas = data.get("ranking_corridas", [])
        
        if ranking_corridas:
            first = ranking_corridas[0]
            required_fields = ["nome_corrida", "media_geral", "posicao"]
            for field in required_fields:
                assert field in first, f"Corrida should have '{field}'"
        
        print("✓ Ranking corridas has required fields")
    
    def test_ranking_final_has_season_metadata(self):
        """Test that ranking-final has season metadata"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        assert data.get("season_id") == 2025, "Should have season_id 2025"
        assert data.get("status") == "finalizada", "Should have status 'finalizada'"
        print("✓ Ranking final has correct season metadata")
    
    def test_ranking_final_nonexistent_season_returns_404(self):
        """Test that ranking-final for nonexistent season returns 404"""
        response = requests.get(f"{BASE_URL}/api/temporadas/1999/ranking-final")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Nonexistent season returns 404")


class TestHallDaFamaDataIntegrity:
    """Tests for data integrity in Hall da Fama"""
    
    def test_top_5_profissional_masculino(self):
        """Test that profissional masculino has at least 5 atletas"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_pro = data.get("ranking_profissional", [])
        masculino = next((r for r in ranking_pro if r.get("genero") == "M"), None)
        
        assert masculino is not None, "Should have masculino category"
        atletas = masculino.get("atletas", [])
        assert len(atletas) >= 5, f"Should have at least 5 atletas, got {len(atletas)}"
        
        # Verify positions are sequential
        for i, atleta in enumerate(atletas[:5]):
            assert atleta.get("posicao") == i + 1, f"Position should be {i+1}, got {atleta.get('posicao')}"
        
        print(f"✓ Profissional Masculino has {len(atletas)} atletas with correct positions")
    
    def test_top_5_profissional_feminino(self):
        """Test that profissional feminino has at least 5 atletas"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_pro = data.get("ranking_profissional", [])
        feminino = next((r for r in ranking_pro if r.get("genero") == "F"), None)
        
        assert feminino is not None, "Should have feminino category"
        atletas = feminino.get("atletas", [])
        assert len(atletas) >= 5, f"Should have at least 5 atletas, got {len(atletas)}"
        
        print(f"✓ Profissional Feminino has {len(atletas)} atletas")
    
    def test_top_5_galera_masculino(self):
        """Test that galera masculino has at least 5 atletas"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_galera = data.get("ranking_galera", [])
        masculino = next((r for r in ranking_galera if r.get("genero") == "M"), None)
        
        assert masculino is not None, "Should have masculino category"
        atletas = masculino.get("atletas", [])
        assert len(atletas) >= 5, f"Should have at least 5 atletas, got {len(atletas)}"
        
        print(f"✓ Galera Masculino has {len(atletas)} atletas")
    
    def test_top_5_galera_feminino(self):
        """Test that galera feminino has at least 5 atletas"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_galera = data.get("ranking_galera", [])
        feminino = next((r for r in ranking_galera if r.get("genero") == "F"), None)
        
        assert feminino is not None, "Should have feminino category"
        atletas = feminino.get("atletas", [])
        assert len(atletas) >= 5, f"Should have at least 5 atletas, got {len(atletas)}"
        
        print(f"✓ Galera Feminino has {len(atletas)} atletas")
    
    def test_corridas_avaliadas_has_ratings(self):
        """Test that corridas avaliadas have media_geral ratings"""
        response = requests.get(f"{BASE_URL}/api/temporadas/2025/ranking-final")
        data = response.json()
        
        ranking_corridas = data.get("ranking_corridas", [])
        
        if ranking_corridas:
            for corrida in ranking_corridas:
                media = corrida.get("media_geral")
                assert media is not None, f"Corrida {corrida.get('nome_corrida')} should have media_geral"
                assert 0 <= media <= 5, f"media_geral should be between 0 and 5, got {media}"
        
        print(f"✓ Corridas avaliadas have valid ratings ({len(ranking_corridas)} corridas)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
