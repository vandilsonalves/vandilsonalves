# /app/backend/tests/test_iter90_pagination.py
# Iteration 90: Testing Pagination for Ranking tabs (Profissional, Galera, Equipes)
# Tests: Backend API pagination for ranking endpoints

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://geo-filtered-admin.preview.emergentagent.com')

class TestRankingProfissionalPagination:
    """Tests for Profissional ranking pagination - GET /api/ranking/categoria/{categoria}/{genero}"""
    
    def test_ranking_profissional_masculino_page1(self):
        """Test first page of Profissional Masculino ranking"""
        url = f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2026&page=1&limit=20"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify pagination structure
        assert "ranking" in data, "Response should have 'ranking' field"
        assert "has_more" in data, "Response should have 'has_more' field"
        assert "total_atletas" in data, "Response should have 'total_atletas' field"
        assert "page" in data, "Response should have 'page' field"
        
        # Verify page value
        assert data["page"] == 1, f"Expected page=1, got {data['page']}"
        
        # Verify limit is respected
        assert len(data["ranking"]) <= 20, f"Expected max 20 items, got {len(data['ranking'])}"
        
        print(f"✓ Profissional Masculino page 1: {len(data['ranking'])} atletas, has_more={data['has_more']}, total={data['total_atletas']}")
    
    def test_ranking_profissional_feminino_page1(self):
        """Test first page of Profissional Feminino ranking"""
        url = f"{BASE_URL}/api/ranking/categoria/feminino/F?ano=2026&page=1&limit=20"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "ranking" in data
        assert "has_more" in data
        assert "total_atletas" in data
        assert "page" in data
        assert data["page"] == 1
        
        print(f"✓ Profissional Feminino page 1: {len(data['ranking'])} atletas, has_more={data['has_more']}, total={data['total_atletas']}")
    
    def test_ranking_profissional_page2(self):
        """Test second page of Profissional ranking"""
        url = f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2026&page=2&limit=20"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "ranking" in data
        assert "page" in data
        assert data["page"] == 2, f"Expected page=2, got {data['page']}"
        
        print(f"✓ Profissional Masculino page 2: {len(data['ranking'])} atletas, has_more={data['has_more']}")
    
    def test_ranking_profissional_pcd_m(self):
        """Test PCD Masculino ranking pagination"""
        url = f"{BASE_URL}/api/ranking/categoria/pcd-m/M?ano=2026&page=1&limit=20"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "ranking" in data
        assert "has_more" in data
        
        print(f"✓ PCD Masculino page 1: {len(data['ranking'])} atletas, has_more={data['has_more']}")


class TestRankingGaleraPagination:
    """Tests for Galera (Povao) ranking pagination - GET /api/ranking/povao"""
    
    def test_ranking_galera_masculino_page1(self):
        """Test first page of Galera Masculino ranking"""
        url = f"{BASE_URL}/api/ranking/povao?genero=M&page=1&limit=20"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify pagination structure
        assert "ranking" in data, "Response should have 'ranking' field"
        assert "has_more" in data, "Response should have 'has_more' field"
        assert "total_atletas" in data, "Response should have 'total_atletas' field"
        assert "page" in data, "Response should have 'page' field"
        
        # Verify page value
        assert data["page"] == 1, f"Expected page=1, got {data['page']}"
        
        # Verify limit is respected
        assert len(data["ranking"]) <= 20, f"Expected max 20 items, got {len(data['ranking'])}"
        
        print(f"✓ Galera Masculino page 1: {len(data['ranking'])} atletas, has_more={data['has_more']}, total={data['total_atletas']}")
    
    def test_ranking_galera_feminino_page1(self):
        """Test first page of Galera Feminino ranking"""
        url = f"{BASE_URL}/api/ranking/povao?genero=F&page=1&limit=20"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "ranking" in data
        assert "has_more" in data
        assert "total_atletas" in data
        assert "page" in data
        assert data["page"] == 1
        
        print(f"✓ Galera Feminino page 1: {len(data['ranking'])} atletas, has_more={data['has_more']}, total={data['total_atletas']}")
    
    def test_ranking_galera_page2(self):
        """Test second page of Galera ranking"""
        url = f"{BASE_URL}/api/ranking/povao?genero=M&page=2&limit=20"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "ranking" in data
        assert "page" in data
        assert data["page"] == 2, f"Expected page=2, got {data['page']}"
        
        print(f"✓ Galera Masculino page 2: {len(data['ranking'])} atletas, has_more={data['has_more']}")
    
    def test_ranking_galera_stats(self):
        """Test Galera stats endpoint"""
        url = f"{BASE_URL}/api/ranking/povao/stats"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "total_atletas" in data
        assert "total_atletas_masculino" in data
        assert "total_atletas_feminino" in data
        
        print(f"✓ Galera stats: total={data['total_atletas']}, M={data['total_atletas_masculino']}, F={data['total_atletas_feminino']}")


class TestRankingEquipesPagination:
    """Tests for Equipes (Liga Assessorias) ranking - GET /api/liga-assessorias/ranking
    Note: This endpoint does NOT support server-side pagination. Frontend handles pagination client-side.
    """
    
    def test_ranking_equipes_nacional(self):
        """Test Liga Assessorias Nacional ranking"""
        url = f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify structure
        assert "ranking" in data, "Response should have 'ranking' field"
        
        # Note: This endpoint returns ALL assessorias at once (no server-side pagination)
        # Frontend limits display to 20 at a time using displayCount state
        
        print(f"✓ Equipes Nacional: {len(data['ranking'])} assessorias (all returned, frontend paginates)")
    
    def test_ranking_equipes_stats(self):
        """Test Liga Assessorias stats endpoint"""
        url = f"{BASE_URL}/api/liga-assessorias/stats"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "total_assessorias" in data
        assert "total_atletas_vinculados" in data
        
        print(f"✓ Equipes stats: total_assessorias={data['total_assessorias']}, atletas_vinculados={data['total_atletas_vinculados']}")


class TestPaginationConsistency:
    """Tests for pagination consistency across pages"""
    
    def test_profissional_pagination_consistency(self):
        """Verify that page 1 and page 2 return different data"""
        url_page1 = f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2026&page=1&limit=20"
        url_page2 = f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2026&page=2&limit=20"
        
        response1 = requests.get(url_page1)
        response2 = requests.get(url_page2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # If there's data on both pages, they should be different
        if len(data1["ranking"]) > 0 and len(data2["ranking"]) > 0:
            ids_page1 = set(r.get("id") for r in data1["ranking"])
            ids_page2 = set(r.get("id") for r in data2["ranking"])
            
            # Pages should not overlap
            overlap = ids_page1.intersection(ids_page2)
            assert len(overlap) == 0, f"Pages should not overlap, found {len(overlap)} common items"
            
            print(f"✓ Pagination consistency: page1 has {len(ids_page1)} unique, page2 has {len(ids_page2)} unique, no overlap")
        else:
            print(f"✓ Pagination consistency: Not enough data to verify (page1={len(data1['ranking'])}, page2={len(data2['ranking'])})")
    
    def test_galera_pagination_consistency(self):
        """Verify that Galera page 1 and page 2 return different data"""
        url_page1 = f"{BASE_URL}/api/ranking/povao?genero=M&page=1&limit=20"
        url_page2 = f"{BASE_URL}/api/ranking/povao?genero=M&page=2&limit=20"
        
        response1 = requests.get(url_page1)
        response2 = requests.get(url_page2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # If there's data on both pages, they should be different
        if len(data1["ranking"]) > 0 and len(data2["ranking"]) > 0:
            ids_page1 = set(r.get("atleta_id") for r in data1["ranking"])
            ids_page2 = set(r.get("atleta_id") for r in data2["ranking"])
            
            # Pages should not overlap
            overlap = ids_page1.intersection(ids_page2)
            assert len(overlap) == 0, f"Pages should not overlap, found {len(overlap)} common items"
            
            print(f"✓ Galera pagination consistency: page1 has {len(ids_page1)} unique, page2 has {len(ids_page2)} unique, no overlap")
        else:
            print(f"✓ Galera pagination consistency: Not enough data to verify (page1={len(data1['ranking'])}, page2={len(data2['ranking'])})")


class TestFilterResetsPagination:
    """Tests to verify that changing filters should reset pagination (frontend behavior)
    Backend just needs to return correct data for page=1 with different filters
    """
    
    def test_profissional_filter_by_faixa(self):
        """Test Profissional ranking with faixa filter"""
        url = f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2026&page=1&limit=20&faixa=30-39"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "ranking" in data
        assert "page" in data
        assert data["page"] == 1
        
        print(f"✓ Profissional with faixa=30-39: {len(data['ranking'])} atletas")
    
    def test_profissional_filter_by_equipe(self):
        """Test Profissional ranking with equipe filter"""
        url = f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2026&page=1&limit=20&equipe=teste"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "ranking" in data
        assert "page" in data
        
        print(f"✓ Profissional with equipe filter: {len(data['ranking'])} atletas")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
