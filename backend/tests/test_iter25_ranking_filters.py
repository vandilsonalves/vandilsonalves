"""
Test Suite for Iteration 25: Ranking de Equipes Filters
Tests the new filter system: Nacional, Estadual, Cidade, Histórico tabs
and the month dropdown filter
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestRankingEquipesTabs:
    """Test the new tab system: Nacional, Estadual, Cidade, Histórico"""
    
    def test_ranking_nacional_returns_data(self):
        """Test Nacional tab returns ranking data"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        assert len(data["ranking"]) > 0
        print(f"Nacional tab: {len(data['ranking'])} assessorias")
    
    def test_ranking_estadual_without_estado(self):
        """Test Estadual tab without estado parameter"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        print(f"Estadual tab (no filter): {len(data['ranking'])} assessorias")
    
    def test_ranking_estadual_with_estado(self):
        """Test Estadual tab with estado=SP"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual&estado=SP")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        # All results should be from SP
        for equipe in data["ranking"]:
            assert equipe["estado"] == "SP", f"Expected estado SP, got {equipe['estado']}"
        print(f"Estadual SP: {len(data['ranking'])} assessorias")
    
    def test_ranking_cidade_with_filters(self):
        """Test Cidade tab with city filter"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=cidade&cidade=São Paulo")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        print(f"Cidade São Paulo: {len(data['ranking'])} assessorias")
    
    def test_ranking_historico_returns_all_time_data(self):
        """Test Histórico tab returns all-time data (no date filter)"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=historico")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        # Histórico should have higher point totals than monthly filters
        if len(data["ranking"]) > 0:
            first_place_points = data["ranking"][0]["pontos_total"]
            print(f"Histórico 1st place: {data['ranking'][0]['nome']} - {first_place_points} pts")
            assert first_place_points > 0


class TestMonthFilter:
    """Test the month dropdown filter (mes parameter)"""
    
    def test_month_filter_january(self):
        """Test filtering by January (mes=1)"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional&mes=1")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        print(f"Month filter January: {len(data['ranking'])} assessorias")
    
    def test_month_filter_february(self):
        """Test filtering by February (mes=2)"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional&mes=2")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        print(f"Month filter February: {len(data['ranking'])} assessorias")
    
    def test_month_filter_march(self):
        """Test filtering by March (mes=3) - current month"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional&mes=3")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        print(f"Month filter March: {len(data['ranking'])} assessorias")
    
    def test_month_filter_invalid_month(self):
        """Test with invalid month (mes=13) - should be ignored or handled gracefully"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional&mes=13")
        # Should still return 200, just with unfiltered data or empty
        assert response.status_code == 200
    
    def test_month_filter_combined_with_estadual(self):
        """Test month filter combined with estadual filter"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual&estado=SP&mes=1")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        print(f"Estadual SP + January: {len(data['ranking'])} assessorias")
    
    def test_historico_ignores_month_filter(self):
        """Test that histórico type ignores the month filter"""
        # With month filter
        response_with_month = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=historico&mes=1")
        # Without month filter
        response_no_month = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=historico")
        
        assert response_with_month.status_code == 200
        assert response_no_month.status_code == 200
        
        data_with = response_with_month.json()
        data_without = response_no_month.json()
        
        # Both should return the same data (histórico ignores month)
        # The point totals should be the same
        if len(data_with["ranking"]) > 0 and len(data_without["ranking"]) > 0:
            assert data_with["ranking"][0]["pontos_total"] == data_without["ranking"][0]["pontos_total"]
            print(f"Histórico correctly ignores month filter")


class TestMonthFilterComparison:
    """Compare results between different months to verify filtering works"""
    
    def test_compare_month_vs_all(self):
        """Compare single month vs all months - all should have >= single month points"""
        # Get all months (no month filter)
        response_all = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        # Get single month
        response_jan = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional&mes=1")
        
        assert response_all.status_code == 200
        assert response_jan.status_code == 200
        
        data_all = response_all.json()
        data_jan = response_jan.json()
        
        # Create lookup for January data
        jan_points = {e["nome"]: e["pontos_total"] for e in data_jan["ranking"]}
        
        # For each assessoria in all months, compare with January
        # All months should have >= January points (since it includes all months)
        for equipe in data_all["ranking"]:
            nome = equipe["nome"]
            all_pts = equipe["pontos_total"]
            jan_pts = jan_points.get(nome, 0)
            # All months points should be >= single month
            assert all_pts >= jan_pts, f"{nome}: all={all_pts}, jan={jan_pts}"
        
        print("Month filtering comparison verified")


class TestRankingDataStructure:
    """Test the structure of ranking response data"""
    
    def test_ranking_response_structure(self):
        """Verify ranking response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data
        
        if len(data["ranking"]) > 0:
            equipe = data["ranking"][0]
            # Check required fields
            assert "nome" in equipe
            assert "estado" in equipe
            assert "cidade" in equipe
            assert "total_atletas" in equipe
            assert "pontos_total" in equipe
            assert "posicao" in equipe
            print(f"Data structure verified: {equipe['nome']}")


class TestEstadosEndpoint:
    """Test the estados endpoint for dropdown"""
    
    def test_get_estados_com_assessorias(self):
        """Get list of states with assessorias"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/estados")
        assert response.status_code == 200
        estados = response.json()
        assert isinstance(estados, list)
        assert len(estados) > 0
        print(f"Estados with assessorias: {estados}")


class TestCidadesEndpoint:
    """Test the cidades endpoint for dropdown"""
    
    def test_get_cidades_por_estado(self):
        """Get list of cities by state"""
        # First get estados
        response_estados = requests.get(f"{BASE_URL}/api/liga-assessorias/estados")
        if response_estados.status_code == 200 and len(response_estados.json()) > 0:
            estado = response_estados.json()[0]
            response = requests.get(f"{BASE_URL}/api/liga-assessorias/cidades?estado={estado}")
            assert response.status_code == 200
            cidades = response.json()
            assert isinstance(cidades, list)
            print(f"Cidades in {estado}: {cidades}")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
