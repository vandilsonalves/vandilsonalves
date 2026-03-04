"""
Test Module: Liga Nacional de Assessorias - ROE-RR System
Tests for Phase 1 of Liga Assessorias implementation
- Stats endpoint
- Ranking endpoint with various filters
- Assessoria details endpoint
- Estados and Cidades endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://athlete-onboarding-1.preview.emergentagent.com')

class TestLigaAssessorias:
    """Test suite for Liga de Assessorias API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        assert response.status_code == 200, "Admin login failed"
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    # === STATS ENDPOINT TESTS ===
    
    def test_get_liga_stats_returns_200(self):
        """Test GET /api/liga-assessorias/stats returns 200"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/stats", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_assessorias" in data
        assert "total_atletas_vinculados" in data
        assert "total_resultados_aprovados" in data
        assert "distribuicao_estados" in data
        print(f"✓ Liga Stats: {data['total_assessorias']} assessorias, {data['total_atletas_vinculados']} atletas")
    
    def test_liga_stats_has_valid_values(self):
        """Test stats values are valid integers"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/stats", headers=self.headers)
        data = response.json()
        
        assert isinstance(data["total_assessorias"], int)
        assert isinstance(data["total_atletas_vinculados"], int)
        assert isinstance(data["total_resultados_aprovados"], int)
        assert data["total_assessorias"] >= 0
        assert data["total_atletas_vinculados"] >= 0
        print(f"✓ Stats values validated: {data['total_assessorias']} assessorias")
    
    def test_liga_stats_distribuicao_estados(self):
        """Test estados distribution is a list with valid structure"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/stats", headers=self.headers)
        data = response.json()
        
        assert isinstance(data["distribuicao_estados"], list)
        if len(data["distribuicao_estados"]) > 0:
            first_estado = data["distribuicao_estados"][0]
            assert "estado" in first_estado
            assert "equipes" in first_estado
            print(f"✓ Top estado: {first_estado['estado']} with {first_estado['equipes']} equipes")
    
    # === RANKING ENDPOINT TESTS ===
    
    def test_get_ranking_nacional_returns_200(self):
        """Test GET /api/liga-assessorias/ranking?tipo=nacional returns 200"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "tipo" in data
        assert data["tipo"] == "nacional"
        assert "ranking" in data
        assert "total_assessorias" in data
        print(f"✓ Ranking Nacional: {data['total_assessorias']} assessorias")
    
    def test_ranking_structure_has_required_fields(self):
        """Test ranking items have all required fields"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional", headers=self.headers)
        data = response.json()
        
        assert len(data["ranking"]) > 0, "Ranking should not be empty"
        first_assessoria = data["ranking"][0]
        
        required_fields = ["posicao", "nome", "estado", "cidade", "total_atletas", 
                          "pontos_total", "total_resultados", "total_primeiros", "selo"]
        for field in required_fields:
            assert field in first_assessoria, f"Missing field: {field}"
        
        print(f"✓ Top assessoria: {first_assessoria['nome']} - {first_assessoria['pontos_total']} pts")
    
    def test_ranking_selo_values(self):
        """Test selo values are ouro/prata/bronze based on position"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional", headers=self.headers)
        data = response.json()
        
        valid_selos = ["ouro", "prata", "bronze"]
        for item in data["ranking"]:
            assert item["selo"] in valid_selos, f"Invalid selo: {item['selo']}"
            # Top 20 should be ouro
            if item["posicao"] <= 20:
                assert item["selo"] == "ouro", f"Position {item['posicao']} should be ouro"
        
        print("✓ Selo validation passed")
    
    def test_ranking_estadual_filter(self):
        """Test ranking with estado filter"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual&estado=SP", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["tipo"] == "estadual"
        # All results should be from SP
        for item in data["ranking"]:
            assert item["estado"] == "SP", f"Expected SP, got {item['estado']}"
        
        print(f"✓ Ranking Estadual SP: {data['total_assessorias']} assessorias")
    
    def test_ranking_mensal(self):
        """Test ranking mensal filter"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=mensal", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["tipo"] == "mensal"
        print(f"✓ Ranking Mensal: {data['total_assessorias']} assessorias")
    
    def test_ranking_anual(self):
        """Test ranking anual filter"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=anual", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["tipo"] == "anual"
        print(f"✓ Ranking Anual: {data['total_assessorias']} assessorias")
    
    def test_ranking_historico(self):
        """Test ranking historico filter"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=historico", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["tipo"] == "historico"
        print(f"✓ Ranking Histórico: {data['total_assessorias']} assessorias")
    
    def test_ranking_ordering_by_points(self):
        """Test ranking is ordered by points descending"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional", headers=self.headers)
        data = response.json()
        
        rankings = data["ranking"]
        for i in range(len(rankings) - 1):
            assert rankings[i]["pontos_total"] >= rankings[i+1]["pontos_total"], \
                f"Ranking not ordered: {rankings[i]['pontos_total']} < {rankings[i+1]['pontos_total']}"
        
        print("✓ Ranking correctly ordered by points")
    
    # === ASSESSORIA DETAILS ENDPOINT TESTS ===
    
    def test_get_assessoria_details_returns_200(self):
        """Test GET /api/liga-assessorias/assessoria/{nome} returns 200"""
        # First get the top assessoria name
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional", headers=self.headers)
        top_assessoria = response.json()["ranking"][0]["nome"]
        
        import urllib.parse
        nome_encoded = urllib.parse.quote(top_assessoria)
        
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{nome_encoded}", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nome"] == top_assessoria
        print(f"✓ Assessoria Details: {data['nome']}")
    
    def test_assessoria_details_structure(self):
        """Test assessoria details has required fields"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional", headers=self.headers)
        top_assessoria = response.json()["ranking"][0]["nome"]
        
        import urllib.parse
        nome_encoded = urllib.parse.quote(top_assessoria)
        
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{nome_encoded}", headers=self.headers)
        data = response.json()
        
        required_fields = ["nome", "estado", "cidade", "total_atletas", "pontos_cadastro",
                          "pontos_resultados", "pontos_total", "total_resultados", 
                          "total_primeiros", "total_podios", "posicao_nacional", 
                          "selo", "atletas", "evolucao_mensal"]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"✓ Assessoria structure validated with {len(data['atletas'])} atletas")
    
    def test_assessoria_evolucao_mensal(self):
        """Test evolucao_mensal has correct structure"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional", headers=self.headers)
        top_assessoria = response.json()["ranking"][0]["nome"]
        
        import urllib.parse
        nome_encoded = urllib.parse.quote(top_assessoria)
        
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{nome_encoded}", headers=self.headers)
        data = response.json()
        
        assert isinstance(data["evolucao_mensal"], list)
        if len(data["evolucao_mensal"]) > 0:
            first_month = data["evolucao_mensal"][0]
            assert "mes" in first_month
            assert "resultados" in first_month
            assert "pontos" in first_month
        
        print(f"✓ Evolução mensal: {len(data['evolucao_mensal'])} months")
    
    def test_assessoria_not_found_returns_404(self):
        """Test non-existent assessoria returns 404"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/NonExistentTeam12345", headers=self.headers)
        assert response.status_code == 404
        print("✓ Non-existent assessoria returns 404")
    
    # === ESTADOS AND CIDADES ENDPOINTS TESTS ===
    
    def test_get_estados_returns_list(self):
        """Test GET /api/liga-assessorias/estados returns list of states"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/estados", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check states are 2-letter codes
        for estado in data:
            assert len(estado) == 2
        
        print(f"✓ Estados: {len(data)} states - {data[:5]}...")
    
    def test_get_cidades_returns_list(self):
        """Test GET /api/liga-assessorias/cidades returns list of cities"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/cidades", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        print(f"✓ Cidades: {len(data)} cities")
    
    def test_get_cidades_filtered_by_estado(self):
        """Test GET /api/liga-assessorias/cidades?estado=SP returns filtered cities"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/cidades?estado=SP", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Cidades SP: {len(data)} cities")
    
    # === POINTS CALCULATION TESTS ===
    
    def test_points_calculation_consistency(self):
        """Test points calculation: 0.5*atletas + 1.0*resultados + bonus"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional", headers=self.headers)
        data = response.json()
        
        for assessoria in data["ranking"][:5]:  # Check top 5
            import urllib.parse
            nome_encoded = urllib.parse.quote(assessoria["nome"])
            
            detail_response = requests.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{nome_encoded}", headers=self.headers)
            if detail_response.status_code == 200:
                detail = detail_response.json()
                
                # pontos_cadastro = 0.5 * total_atletas
                expected_cadastro = detail["total_atletas"] * 0.5
                assert detail["pontos_cadastro"] == expected_cadastro, \
                    f"Cadastro points mismatch for {detail['nome']}"
        
        print("✓ Points calculation validated")
    
    # === AUTHENTICATION TESTS ===
    
    def test_ranking_requires_auth(self):
        """Test ranking endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        assert response.status_code in [401, 403], "Should require authentication"
        print("✓ Ranking requires authentication")
    
    def test_stats_requires_auth(self):
        """Test stats endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/stats")
        assert response.status_code in [401, 403], "Should require authentication"
        print("✓ Stats requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
