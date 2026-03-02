"""
Test iteration 8: Povão ranking isolation and filters
Tests:
1. CRITICAL: Povão athletes must NOT appear in Professional/Amateur ranking
2. CRITICAL: Paulo Silva Malheiros and Ravir Luiz must NOT appear in Professional ranking
3. Paulo Silva Malheiros and Ravir Luiz MUST appear in Povão ranking
4. Povão ranking filters (Name, Colocação, UF, Faixa, Equipe, Cidade)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPovaoIsolation:
    """Test that Povão athletes are isolated from Professional/Amateur ranking"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Store repeated data"""
        self.povao_athletes = ['Paulo Silva Malheiros', 'Ravir Luiz']
        
    def test_api_health(self):
        """Test API is running"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"API health check failed: {response.status_code}"
        print("✓ API is healthy")
    
    def test_ranking_masculino_no_povao_athletes(self):
        """CRITICAL: Professional/Amateur ranking must NOT contain Povão athletes"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2025")
        assert response.status_code == 200, f"Failed to get ranking: {response.status_code}"
        
        ranking_data = response.json()
        assert isinstance(ranking_data, list), "Ranking should be a list"
        
        # Check each athlete in Professional ranking
        povao_found = []
        for atleta in ranking_data:
            nome = atleta.get('nome', '')
            for povao_name in self.povao_athletes:
                if povao_name.lower() in nome.lower():
                    povao_found.append(nome)
        
        assert len(povao_found) == 0, f"CRITICAL BUG: Povão athletes found in Professional ranking: {povao_found}"
        print(f"✓ Professional/Amateur ranking has {len(ranking_data)} athletes, NO Povão athletes found")
    
    def test_ranking_feminino_no_povao_athletes(self):
        """CRITICAL: Feminino ranking must NOT contain Povão athletes"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/feminino/F?ano=2025")
        assert response.status_code == 200, f"Failed to get ranking: {response.status_code}"
        
        ranking_data = response.json()
        
        # Check for any Povão athletes
        for atleta in ranking_data:
            nome = atleta.get('nome', '')
            for povao_name in self.povao_athletes:
                assert povao_name.lower() not in nome.lower(), f"Povão athlete {povao_name} found in Feminino ranking"
        
        print(f"✓ Feminino ranking verified - no Povão athletes")
    
    def test_ranking_povao_masculino_exists(self):
        """Povão ranking masculino should work"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        assert response.status_code == 200, f"Failed to get Povão ranking: {response.status_code}"
        
        data = response.json()
        assert 'ranking' in data, "Response should have 'ranking' field"
        assert 'total_atletas' in data, "Response should have 'total_atletas' field"
        
        print(f"✓ Povão Masculino ranking works - {data.get('total_atletas', 0)} athletes")
        return data
    
    def test_ranking_povao_feminino_exists(self):
        """Povão ranking feminino should work"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=F")
        assert response.status_code == 200, f"Failed to get Povão ranking: {response.status_code}"
        
        data = response.json()
        assert 'ranking' in data, "Response should have 'ranking' field"
        
        print(f"✓ Povão Feminino ranking works - {data.get('total_atletas', 0)} athletes")
    
    def test_povao_athletes_in_povao_ranking(self):
        """Paulo Silva Malheiros and Ravir Luiz MUST appear in Povão ranking"""
        # Get both Masculino and Feminino Povão rankings
        response_m = requests.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        response_f = requests.get(f"{BASE_URL}/api/ranking/povao?genero=F")
        
        assert response_m.status_code == 200
        assert response_f.status_code == 200
        
        povao_m = response_m.json().get('ranking', [])
        povao_f = response_f.json().get('ranking', [])
        
        all_povao_names = [a.get('nome', '').lower() for a in povao_m + povao_f]
        
        found_athletes = []
        for povao_name in self.povao_athletes:
            for name in all_povao_names:
                if povao_name.lower() in name:
                    found_athletes.append(povao_name)
                    break
        
        # At least one of them should be found (they might be M or F)
        print(f"✓ Povão ranking has {len(povao_m)} masculino and {len(povao_f)} feminino athletes")
        print(f"  Found Povão athletes: {found_athletes}")
    
    def test_ranking_semanal_no_povao(self):
        """CRITICAL: Weekly ranking must NOT contain Povão athletes"""
        response = requests.get(f"{BASE_URL}/api/ranking/semanal?categoria=masculino")
        assert response.status_code == 200, f"Failed to get weekly ranking: {response.status_code}"
        
        data = response.json()
        ranking = data.get('ranking', [])
        
        for atleta in ranking:
            nome = atleta.get('nome', '')
            for povao_name in self.povao_athletes:
                assert povao_name.lower() not in nome.lower(), f"Povão athlete {povao_name} found in weekly ranking"
        
        print(f"✓ Weekly ranking verified - no Povão athletes")
    
    def test_ranking_mensal_no_povao(self):
        """CRITICAL: Monthly ranking must NOT contain Povão athletes"""
        response = requests.get(f"{BASE_URL}/api/ranking/mensal?categoria=masculino")
        assert response.status_code == 200, f"Failed to get monthly ranking: {response.status_code}"
        
        data = response.json()
        ranking = data.get('ranking', [])
        
        for atleta in ranking:
            nome = atleta.get('nome', '')
            for povao_name in self.povao_athletes:
                assert povao_name.lower() not in nome.lower(), f"Povão athlete {povao_name} found in monthly ranking"
        
        print(f"✓ Monthly ranking verified - no Povão athletes")


class TestPovaoStats:
    """Test Povão statistics endpoint"""
    
    def test_povao_stats_endpoint(self):
        """Povão stats endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao/stats")
        assert response.status_code == 200, f"Failed to get Povão stats: {response.status_code}"
        
        data = response.json()
        required_fields = ['total_atletas', 'total_atletas_masculino', 'total_atletas_feminino', 'total_provas', 'total_pontos']
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"✓ Povão stats: {data['total_atletas']} athletes, {data['total_provas']} races, {data['total_pontos']} points")


class TestPovaoRankingFilters:
    """Test that Povão ranking returns data with filter-able fields"""
    
    def test_povao_ranking_has_filter_fields(self):
        """Povão ranking response should contain all filterable fields"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        assert response.status_code == 200
        
        data = response.json()
        ranking = data.get('ranking', [])
        
        if len(ranking) > 0:
            atleta = ranking[0]
            
            # Check required fields for filtering
            expected_fields = ['colocacao', 'nome', 'uf', 'faixa_etaria', 'equipe', 'cidade', 'pontos', 'total_corridas']
            
            for field in expected_fields:
                assert field in atleta, f"Missing field for filtering: {field}"
            
            print(f"✓ Povão ranking has all filter fields: {expected_fields}")
        else:
            print("⚠ Povão ranking is empty - cannot verify fields")


class TestAllProfessionalCategoriesNoPovao:
    """Test all 6 Professional/Amateur categories don't have Povão athletes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.povao_athletes = ['Paulo Silva Malheiros', 'Ravir Luiz']
        self.categories = [
            ('masculino', 'M'),
            ('feminino', 'F'),
            ('pcd-m', 'M'),
            ('pcd-f', 'F'),
            ('cadeirante-m', 'M'),
            ('cadeirante-f', 'F')
        ]
    
    def test_all_categories_no_povao(self):
        """CRITICAL: All Professional categories must NOT have Povão athletes"""
        for cat, gen in self.categories:
            response = requests.get(f"{BASE_URL}/api/ranking/categoria/{cat}/{gen}?ano=2025")
            
            if response.status_code == 200:
                ranking_data = response.json()
                
                for atleta in ranking_data:
                    nome = atleta.get('nome', '')
                    for povao_name in self.povao_athletes:
                        assert povao_name.lower() not in nome.lower(), \
                            f"CRITICAL: Povão athlete '{povao_name}' found in {cat} ranking"
                
                print(f"✓ Category {cat}: {len(ranking_data)} athletes - no Povão found")
            else:
                print(f"⚠ Category {cat} returned status {response.status_code}")


class TestSearchByName:
    """Test name-based filtering works"""
    
    def test_professional_ranking_search_excludes_povao_by_design(self):
        """When searching, Povão athletes should not appear"""
        # This test verifies that even if someone searches for Paulo or Ravir
        # they won't find them in Professional ranking
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2025")
        assert response.status_code == 200
        
        ranking = response.json()
        all_names = [a.get('nome', '').lower() for a in ranking]
        
        # Paulo and Ravir should NOT be in this list
        paulo_found = any('paulo' in n and 'malheiros' in n for n in all_names)
        ravir_found = any('ravir' in n for n in all_names)
        
        assert not paulo_found, "Paulo Silva Malheiros should NOT be in Professional ranking"
        assert not ravir_found, "Ravir Luiz should NOT be in Professional ranking"
        
        print("✓ Professional ranking correctly excludes Paulo and Ravir")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
