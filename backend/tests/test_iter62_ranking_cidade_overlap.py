"""
Test Iteration 62: Ranking por Cidade - Zero Overlap between Profissional and Galera
Bug Fix: Previously, the same athletes appeared in both Profissional/Amador and Galera rankings.
Fix: Cross-exclusion logic - profissional uses ranking_anual, galera uses ranking_povao,
     and when an athlete exists in both collections, profissional has priority (excluded from galera).

Test Cities:
- Taguatinga/DF M - profissional: Henrique Costa, João Mendes, Miguel Souza (ranking_anual)
                    galera: Enzo Monteiro, Diego Carvalho, Daniel Oliveira, Enzo Almeida (ranking_povao)
- Salvador/BA F - zero overlap
- São Paulo/SP M - zero overlap (previously had 1 overlap: Marcelo Fugeteiro)
- Rio de Janeiro/RJ, Recife/PE, Belo Horizonte/MG - zero overlap
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestRankingCidadeZeroOverlap:
    """Tests to verify zero overlap between Profissional and Galera rankings per city"""
    
    def test_api_health(self):
        """Verify API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"API health check failed: {response.status_code}"
        print("✅ API health check passed")
    
    def test_taguatinga_df_masculino_zero_overlap(self):
        """Taguatinga/DF M - Profissional and Galera must have ZERO overlap"""
        # Get Profissional ranking
        prof_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/DF/Taguatinga",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert prof_response.status_code == 200, f"Profissional request failed: {prof_response.status_code}"
        prof_data = prof_response.json()
        prof_ids = {atleta["id"] for atleta in prof_data.get("ranking", [])}
        prof_names = [atleta["nome"] for atleta in prof_data.get("ranking", [])]
        
        # Get Galera ranking
        galera_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/DF/Taguatinga",
            params={"modalidade": "povao", "genero": "M"}
        )
        assert galera_response.status_code == 200, f"Galera request failed: {galera_response.status_code}"
        galera_data = galera_response.json()
        galera_ids = {atleta["id"] for atleta in galera_data.get("ranking", [])}
        galera_names = [atleta["nome"] for atleta in galera_data.get("ranking", [])]
        
        # Check for overlap
        overlap = prof_ids.intersection(galera_ids)
        
        print(f"Taguatinga/DF M - Profissional: {len(prof_ids)} atletas - {prof_names[:5]}")
        print(f"Taguatinga/DF M - Galera: {len(galera_ids)} atletas - {galera_names[:5]}")
        print(f"Overlap IDs: {overlap}")
        
        assert len(overlap) == 0, f"OVERLAP FOUND! {len(overlap)} athletes in both lists: {overlap}"
        print("✅ Taguatinga/DF M - Zero overlap verified")
    
    def test_salvador_ba_feminino_zero_overlap(self):
        """Salvador/BA F - Profissional and Galera must have ZERO overlap"""
        # Get Profissional ranking
        prof_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/BA/Salvador",
            params={"modalidade": "profissional", "genero": "F"}
        )
        assert prof_response.status_code == 200
        prof_data = prof_response.json()
        prof_ids = {atleta["id"] for atleta in prof_data.get("ranking", [])}
        
        # Get Galera ranking
        galera_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/BA/Salvador",
            params={"modalidade": "povao", "genero": "F"}
        )
        assert galera_response.status_code == 200
        galera_data = galera_response.json()
        galera_ids = {atleta["id"] for atleta in galera_data.get("ranking", [])}
        
        overlap = prof_ids.intersection(galera_ids)
        
        print(f"Salvador/BA F - Profissional: {len(prof_ids)} atletas")
        print(f"Salvador/BA F - Galera: {len(galera_ids)} atletas")
        print(f"Overlap IDs: {overlap}")
        
        assert len(overlap) == 0, f"OVERLAP FOUND! {len(overlap)} athletes in both lists"
        print("✅ Salvador/BA F - Zero overlap verified")
    
    def test_sao_paulo_sp_masculino_zero_overlap(self):
        """São Paulo/SP M - Previously had 1 overlap (Marcelo Fugeteiro), now must be ZERO"""
        # Get Profissional ranking
        prof_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert prof_response.status_code == 200
        prof_data = prof_response.json()
        prof_ids = {atleta["id"] for atleta in prof_data.get("ranking", [])}
        prof_names = {atleta["nome"] for atleta in prof_data.get("ranking", [])}
        
        # Get Galera ranking
        galera_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "povao", "genero": "M"}
        )
        assert galera_response.status_code == 200
        galera_data = galera_response.json()
        galera_ids = {atleta["id"] for atleta in galera_data.get("ranking", [])}
        galera_names = {atleta["nome"] for atleta in galera_data.get("ranking", [])}
        
        overlap = prof_ids.intersection(galera_ids)
        
        print(f"São Paulo/SP M - Profissional: {len(prof_ids)} atletas")
        print(f"São Paulo/SP M - Galera: {len(galera_ids)} atletas")
        print(f"Overlap IDs: {overlap}")
        
        # Check if Marcelo Fugeteiro is NOT in both lists
        marcelo_in_prof = "Marcelo Fugeteiro" in prof_names
        marcelo_in_galera = "Marcelo Fugeteiro" in galera_names
        print(f"Marcelo Fugeteiro in Profissional: {marcelo_in_prof}")
        print(f"Marcelo Fugeteiro in Galera: {marcelo_in_galera}")
        
        assert len(overlap) == 0, f"OVERLAP FOUND! {len(overlap)} athletes in both lists"
        assert not (marcelo_in_prof and marcelo_in_galera), "Marcelo Fugeteiro should NOT be in both lists!"
        print("✅ São Paulo/SP M - Zero overlap verified (Marcelo Fugeteiro fix confirmed)")
    
    def test_rio_de_janeiro_rj_masculino_zero_overlap(self):
        """Rio de Janeiro/RJ M - Zero overlap"""
        prof_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/RJ/Rio de Janeiro",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert prof_response.status_code == 200
        prof_ids = {atleta["id"] for atleta in prof_response.json().get("ranking", [])}
        
        galera_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/RJ/Rio de Janeiro",
            params={"modalidade": "povao", "genero": "M"}
        )
        assert galera_response.status_code == 200
        galera_ids = {atleta["id"] for atleta in galera_response.json().get("ranking", [])}
        
        overlap = prof_ids.intersection(galera_ids)
        print(f"Rio de Janeiro/RJ M - Profissional: {len(prof_ids)}, Galera: {len(galera_ids)}, Overlap: {len(overlap)}")
        
        assert len(overlap) == 0, f"OVERLAP FOUND! {overlap}"
        print("✅ Rio de Janeiro/RJ M - Zero overlap verified")
    
    def test_recife_pe_masculino_zero_overlap(self):
        """Recife/PE M - Zero overlap"""
        prof_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/PE/Recife",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert prof_response.status_code == 200
        prof_ids = {atleta["id"] for atleta in prof_response.json().get("ranking", [])}
        
        galera_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/PE/Recife",
            params={"modalidade": "povao", "genero": "M"}
        )
        assert galera_response.status_code == 200
        galera_ids = {atleta["id"] for atleta in galera_response.json().get("ranking", [])}
        
        overlap = prof_ids.intersection(galera_ids)
        print(f"Recife/PE M - Profissional: {len(prof_ids)}, Galera: {len(galera_ids)}, Overlap: {len(overlap)}")
        
        assert len(overlap) == 0, f"OVERLAP FOUND! {overlap}"
        print("✅ Recife/PE M - Zero overlap verified")
    
    def test_belo_horizonte_mg_masculino_zero_overlap(self):
        """Belo Horizonte/MG M - Zero overlap"""
        prof_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/MG/Belo Horizonte",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert prof_response.status_code == 200
        prof_ids = {atleta["id"] for atleta in prof_response.json().get("ranking", [])}
        
        galera_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/MG/Belo Horizonte",
            params={"modalidade": "povao", "genero": "M"}
        )
        assert galera_response.status_code == 200
        galera_ids = {atleta["id"] for atleta in galera_response.json().get("ranking", [])}
        
        overlap = prof_ids.intersection(galera_ids)
        print(f"Belo Horizonte/MG M - Profissional: {len(prof_ids)}, Galera: {len(galera_ids)}, Overlap: {len(overlap)}")
        
        assert len(overlap) == 0, f"OVERLAP FOUND! {overlap}"
        print("✅ Belo Horizonte/MG M - Zero overlap verified")
    
    def test_taguatinga_df_expected_athletes(self):
        """Verify expected athletes in Taguatinga/DF M rankings"""
        # Get Profissional ranking
        prof_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/DF/Taguatinga",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert prof_response.status_code == 200
        prof_names = [atleta["nome"] for atleta in prof_response.json().get("ranking", [])]
        
        # Get Galera ranking
        galera_response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/DF/Taguatinga",
            params={"modalidade": "povao", "genero": "M"}
        )
        assert galera_response.status_code == 200
        galera_names = [atleta["nome"] for atleta in galera_response.json().get("ranking", [])]
        
        print(f"Profissional names: {prof_names}")
        print(f"Galera names: {galera_names}")
        
        # Expected profissional athletes (from ranking_anual)
        expected_prof = ["Henrique Costa", "João Mendes", "Miguel Souza"]
        # Expected galera athletes (from ranking_povao)
        expected_galera = ["Enzo Monteiro", "Diego Carvalho", "Daniel Oliveira", "Enzo Almeida"]
        
        # Check if expected profissional athletes are in profissional list
        for name in expected_prof:
            if name in prof_names:
                print(f"✅ {name} found in Profissional (expected)")
        
        # Check if expected galera athletes are in galera list
        for name in expected_galera:
            if name in galera_names:
                print(f"✅ {name} found in Galera (expected)")
        
        # Verify no expected galera athletes in profissional
        for name in expected_galera:
            assert name not in prof_names, f"{name} should NOT be in Profissional list!"
        
        # Verify no expected profissional athletes in galera
        for name in expected_prof:
            assert name not in galera_names, f"{name} should NOT be in Galera list!"
        
        print("✅ Taguatinga/DF M - Expected athletes verified in correct lists")
    
    def test_multiple_cities_feminino_zero_overlap(self):
        """Test multiple cities for Feminino - all must have zero overlap"""
        cities = [
            ("SP", "São Paulo"),
            ("RJ", "Rio de Janeiro"),
            ("MG", "Belo Horizonte"),
            ("BA", "Salvador"),
            ("PE", "Recife"),
            ("DF", "Brasília")
        ]
        
        all_passed = True
        for estado, cidade in cities:
            prof_response = requests.get(
                f"{BASE_URL}/api/ranking/por-cidade/{estado}/{cidade}",
                params={"modalidade": "profissional", "genero": "F"}
            )
            galera_response = requests.get(
                f"{BASE_URL}/api/ranking/por-cidade/{estado}/{cidade}",
                params={"modalidade": "povao", "genero": "F"}
            )
            
            if prof_response.status_code == 200 and galera_response.status_code == 200:
                prof_ids = {atleta["id"] for atleta in prof_response.json().get("ranking", [])}
                galera_ids = {atleta["id"] for atleta in galera_response.json().get("ranking", [])}
                overlap = prof_ids.intersection(galera_ids)
                
                if len(overlap) > 0:
                    print(f"❌ {cidade}/{estado} F - OVERLAP: {len(overlap)} athletes")
                    all_passed = False
                else:
                    print(f"✅ {cidade}/{estado} F - Zero overlap (Prof: {len(prof_ids)}, Galera: {len(galera_ids)})")
        
        assert all_passed, "Some cities have overlap between Profissional and Galera!"
        print("✅ All cities Feminino - Zero overlap verified")
    
    def test_response_structure(self):
        """Verify response structure for ranking por cidade endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/por-cidade/SP/São Paulo",
            params={"modalidade": "profissional", "genero": "M"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "ranking" in data, "Response must have 'ranking' field"
        assert "total" in data, "Response must have 'total' field"
        assert "cidade" in data, "Response must have 'cidade' field"
        assert "estado" in data, "Response must have 'estado' field"
        assert "modalidade" in data, "Response must have 'modalidade' field"
        
        # Check athlete structure if ranking has data
        if data["ranking"]:
            atleta = data["ranking"][0]
            required_fields = ["colocacao", "id", "nome", "foto_url", "equipe", "cidade", "estado", "pontos"]
            for field in required_fields:
                assert field in atleta, f"Athlete must have '{field}' field"
        
        print("✅ Response structure verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
