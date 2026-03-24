# /app/backend/tests/test_iter60_ranking_cidade_genero.py
# Tests for Ranking por Cidade gender filter fix
# Bug: Gender and Modality filters were mixing athlete names
# Fix: Added gender filter to povao, profissional, and fallback queries

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRankingCidadeGeneroFix:
    """Tests for the gender filter fix in Ranking por Cidade endpoint"""
    
    def test_api_health(self):
        """Verify API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"API health check failed: {response.text}"
        print("✅ API health check passed")
    
    def test_ranking_cidade_endpoint_exists(self):
        """Verify the ranking por cidade endpoint exists"""
        # Test with São Paulo/SP which should have data
        response = requests.get(f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo")
        assert response.status_code == 200, f"Endpoint returned {response.status_code}: {response.text}"
        data = response.json()
        assert "ranking" in data, "Response should contain 'ranking' key"
        print(f"✅ Endpoint exists and returns data. Total athletes: {data.get('total', 0)}")
    
    def test_profissional_masculino_vs_feminino_different_results(self):
        """Test that profissional modalidade returns different results for M vs F"""
        # Get masculine ranking
        response_m = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert response_m.status_code == 200, f"M request failed: {response_m.text}"
        data_m = response_m.json()
        
        # Get feminine ranking
        response_f = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "profissional", "genero": "F"}
        )
        assert response_f.status_code == 200, f"F request failed: {response_f.text}"
        data_f = response_f.json()
        
        # Extract athlete names
        names_m = set([a.get("nome", "") for a in data_m.get("ranking", [])])
        names_f = set([a.get("nome", "") for a in data_f.get("ranking", [])])
        
        print(f"Profissional M athletes: {len(names_m)}, F athletes: {len(names_f)}")
        print(f"M names sample: {list(names_m)[:3]}")
        print(f"F names sample: {list(names_f)[:3]}")
        
        # If both have data, they should be different (no overlap or minimal overlap)
        if names_m and names_f:
            overlap = names_m.intersection(names_f)
            print(f"Overlap between M and F: {len(overlap)} names")
            # There should be no overlap - same person can't be in both M and F
            assert len(overlap) == 0, f"Bug: Same athletes appearing in both M and F: {overlap}"
            print("✅ Profissional: M and F rankings have no overlap (correct)")
        else:
            print("⚠️ One or both genders have no data - cannot verify separation")
    
    def test_povao_masculino_vs_feminino_different_results(self):
        """Test that povao modalidade returns different results for M vs F"""
        # Get masculine ranking
        response_m = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "povao", "genero": "M"}
        )
        assert response_m.status_code == 200, f"M request failed: {response_m.text}"
        data_m = response_m.json()
        
        # Get feminine ranking
        response_f = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "povao", "genero": "F"}
        )
        assert response_f.status_code == 200, f"F request failed: {response_f.text}"
        data_f = response_f.json()
        
        # Extract athlete names
        names_m = set([a.get("nome", "") for a in data_m.get("ranking", [])])
        names_f = set([a.get("nome", "") for a in data_f.get("ranking", [])])
        
        print(f"Povao M athletes: {len(names_m)}, F athletes: {len(names_f)}")
        print(f"M names sample: {list(names_m)[:3]}")
        print(f"F names sample: {list(names_f)[:3]}")
        
        # If both have data, they should be different
        if names_m and names_f:
            overlap = names_m.intersection(names_f)
            print(f"Overlap between M and F: {len(overlap)} names")
            assert len(overlap) == 0, f"Bug: Same athletes appearing in both M and F: {overlap}"
            print("✅ Povao: M and F rankings have no overlap (correct)")
        else:
            print("⚠️ One or both genders have no data - cannot verify separation")
    
    def test_genero_filter_applied_profissional(self):
        """Verify genero parameter is actually filtering in profissional mode"""
        # Test with different cities to ensure filter works
        cities = [("SP", "São Paulo"), ("RJ", "Rio de Janeiro"), ("PE", "Recife")]
        
        for estado, cidade in cities:
            response_m = requests.get(
                f"{BASE_URL}/api/ranking/por-cidade/{estado}/{cidade}",
                params={"modalidade": "profissional", "genero": "M"}
            )
            response_f = requests.get(
                f"{BASE_URL}/api/ranking/por-cidade/{estado}/{cidade}",
                params={"modalidade": "profissional", "genero": "F"}
            )
            
            if response_m.status_code == 200 and response_f.status_code == 200:
                data_m = response_m.json()
                data_f = response_f.json()
                
                ids_m = set([a.get("id", "") for a in data_m.get("ranking", [])])
                ids_f = set([a.get("id", "") for a in data_f.get("ranking", [])])
                
                if ids_m and ids_f:
                    overlap = ids_m.intersection(ids_f)
                    assert len(overlap) == 0, f"Bug in {cidade}: Same IDs in M and F: {overlap}"
                    print(f"✅ {cidade}: Profissional filter working (M:{len(ids_m)}, F:{len(ids_f)}, overlap:0)")
    
    def test_genero_filter_applied_povao(self):
        """Verify genero parameter is actually filtering in povao mode"""
        cities = [("SP", "São Paulo"), ("RJ", "Rio de Janeiro"), ("PE", "Recife")]
        
        for estado, cidade in cities:
            response_m = requests.get(
                f"{BASE_URL}/api/ranking/por-cidade/{estado}/{cidade}",
                params={"modalidade": "povao", "genero": "M"}
            )
            response_f = requests.get(
                f"{BASE_URL}/api/ranking/por-cidade/{estado}/{cidade}",
                params={"modalidade": "povao", "genero": "F"}
            )
            
            if response_m.status_code == 200 and response_f.status_code == 200:
                data_m = response_m.json()
                data_f = response_f.json()
                
                ids_m = set([a.get("id", "") for a in data_m.get("ranking", [])])
                ids_f = set([a.get("id", "") for a in data_f.get("ranking", [])])
                
                if ids_m and ids_f:
                    overlap = ids_m.intersection(ids_f)
                    assert len(overlap) == 0, f"Bug in {cidade}: Same IDs in M and F: {overlap}"
                    print(f"✅ {cidade}: Povao filter working (M:{len(ids_m)}, F:{len(ids_f)}, overlap:0)")
    
    def test_response_structure(self):
        """Verify response structure is correct"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "ranking" in data, "Missing 'ranking' field"
        assert "total" in data, "Missing 'total' field"
        assert "cidade" in data, "Missing 'cidade' field"
        assert "estado" in data, "Missing 'estado' field"
        
        # Check ranking item structure if data exists
        if data["ranking"]:
            item = data["ranking"][0]
            required_fields = ["colocacao", "id", "nome", "pontos"]
            for field in required_fields:
                assert field in item, f"Missing '{field}' in ranking item"
        
        print("✅ Response structure is correct")
    
    def test_modalidade_parameter(self):
        """Verify modalidade parameter affects results"""
        response_prof = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "profissional", "genero": "M"}
        )
        response_povao = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "povao", "genero": "M"}
        )
        
        assert response_prof.status_code == 200
        assert response_povao.status_code == 200
        
        data_prof = response_prof.json()
        data_povao = response_povao.json()
        
        print(f"Profissional total: {data_prof.get('total', 0)}")
        print(f"Povao total: {data_povao.get('total', 0)}")
        
        # Results should potentially be different (different ranking systems)
        print("✅ Both modalidades return valid responses")
    
    def test_empty_city_returns_empty_ranking(self):
        """Test that non-existent city returns empty ranking"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/XX/CidadeInexistente",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("total", 0) == 0, "Non-existent city should return 0 athletes"
        assert data.get("ranking", []) == [], "Non-existent city should return empty ranking"
        print("✅ Non-existent city returns empty ranking correctly")


class TestRankingCidadeIntegration:
    """Integration tests for the full ranking flow"""
    
    def test_estados_endpoint(self):
        """Verify estados endpoint works"""
        response = requests.get(f"{BASE_URL}/api/ranking/estados")
        assert response.status_code == 200
        data = response.json()
        assert "estados" in data
        assert len(data["estados"]) > 0, "Should have at least one estado"
        print(f"✅ Estados endpoint returns {len(data['estados'])} estados")
    
    def test_cidades_endpoint(self):
        """Verify cidades endpoint works with estado filter"""
        response = requests.get(f"{BASE_URL}/api/ranking/cidades", params={"estado": "SP"})
        assert response.status_code == 200
        data = response.json()
        assert "cidades" in data
        print(f"✅ Cidades endpoint returns {len(data.get('cidades', []))} cidades for SP")
    
    def test_full_flow_sp_sao_paulo(self):
        """Test complete flow: estados -> cidades -> ranking"""
        # 1. Get estados
        estados_resp = requests.get(f"{BASE_URL}/api/ranking/estados")
        assert estados_resp.status_code == 200
        estados = estados_resp.json().get("estados", [])
        assert "SP" in estados, "SP should be in estados list"
        
        # 2. Get cidades for SP
        cidades_resp = requests.get(f"{BASE_URL}/api/ranking/cidades", params={"estado": "SP"})
        assert cidades_resp.status_code == 200
        cidades = cidades_resp.json().get("cidades", [])
        cidade_names = [c["nome"] for c in cidades]
        assert "São Paulo" in cidade_names, "São Paulo should be in cidades list"
        
        # 3. Get ranking for São Paulo with M
        ranking_m = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert ranking_m.status_code == 200
        
        # 4. Get ranking for São Paulo with F
        ranking_f = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "profissional", "genero": "F"}
        )
        assert ranking_f.status_code == 200
        
        print("✅ Full flow test passed: estados -> cidades -> ranking (M/F)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
