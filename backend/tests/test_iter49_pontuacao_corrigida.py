"""
Iteration 49: Test scoring table fix (Tabela de Pontuação Corrigida)

Verifica que a tabela de pontuação foi corrigida:
- Normal: 1º=10pts, 2º=9pts, 3º=8pts, 4º=7pts, 5º=6pts, 6º=5pts, 7º=4pts, 8º=3pts, 9º=2pts, 10º=1pt
- PCD/Cadeirante: 1º=10pts, 2º=9pts, 3º=8pts
- Povão: 5-9km=5pts, 10-20km=7pts, 21km+=9pts

O sistema anterior tinha valores 10x maiores (1º=100pts), agora está correto.
"""

import pytest
import requests
import os
import sys

# Add backend to path for direct function testing
sys.path.insert(0, '/app/backend')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://feed-likes-comments.preview.emergentagent.com').rstrip('/')


class TestCalcularPontosColocacao:
    """Test the calcular_pontos_colocacao function returns correct values"""
    
    def test_normal_first_place_10_points(self):
        """Normal category: 1st place = 10 points"""
        from routes.admin_routes import calcular_pontos_colocacao
        pontos = calcular_pontos_colocacao(1, "normal")
        assert pontos == 10, f"Expected 10 points for 1st place, got {pontos}"
        print(f"✅ Normal 1º lugar = {pontos} pontos (esperado: 10)")
    
    def test_normal_second_place_9_points(self):
        """Normal category: 2nd place = 9 points"""
        from routes.admin_routes import calcular_pontos_colocacao
        pontos = calcular_pontos_colocacao(2, "normal")
        assert pontos == 9, f"Expected 9 points for 2nd place, got {pontos}"
        print(f"✅ Normal 2º lugar = {pontos} pontos (esperado: 9)")
    
    def test_normal_third_place_8_points(self):
        """Normal category: 3rd place = 8 points"""
        from routes.admin_routes import calcular_pontos_colocacao
        pontos = calcular_pontos_colocacao(3, "normal")
        assert pontos == 8, f"Expected 8 points for 3rd place, got {pontos}"
        print(f"✅ Normal 3º lugar = {pontos} pontos (esperado: 8)")
    
    def test_normal_full_table(self):
        """Test complete scoring table for Normal category"""
        from routes.admin_routes import calcular_pontos_colocacao
        
        expected = {
            1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
            6: 5, 7: 4, 8: 3, 9: 2, 10: 1
        }
        
        for colocacao, pontos_esperado in expected.items():
            pontos = calcular_pontos_colocacao(colocacao, "normal")
            assert pontos == pontos_esperado, f"Position {colocacao}: expected {pontos_esperado}, got {pontos}"
            print(f"✅ Normal {colocacao}º = {pontos} pontos")
    
    def test_normal_beyond_10th_place_zero_points(self):
        """Normal category: positions beyond 10th get 0 points"""
        from routes.admin_routes import calcular_pontos_colocacao
        
        for colocacao in [11, 15, 20, 100]:
            pontos = calcular_pontos_colocacao(colocacao, "normal")
            assert pontos == 0, f"Expected 0 points for position {colocacao}, got {pontos}"
        print("✅ Colocações > 10º = 0 pontos")
    
    def test_pcd_first_place_10_points(self):
        """PCD category: 1st place = 10 points"""
        from routes.admin_routes import calcular_pontos_colocacao
        pontos = calcular_pontos_colocacao(1, "pcd")
        assert pontos == 10, f"Expected 10 points for PCD 1st place, got {pontos}"
        print(f"✅ PCD 1º lugar = {pontos} pontos (esperado: 10)")
    
    def test_pcd_second_place_9_points(self):
        """PCD category: 2nd place = 9 points"""
        from routes.admin_routes import calcular_pontos_colocacao
        pontos = calcular_pontos_colocacao(2, "pcd")
        assert pontos == 9, f"Expected 9 points for PCD 2nd place, got {pontos}"
        print(f"✅ PCD 2º lugar = {pontos} pontos (esperado: 9)")
    
    def test_pcd_third_place_8_points(self):
        """PCD category: 3rd place = 8 points"""
        from routes.admin_routes import calcular_pontos_colocacao
        pontos = calcular_pontos_colocacao(3, "pcd")
        assert pontos == 8, f"Expected 8 points for PCD 3rd place, got {pontos}"
        print(f"✅ PCD 3º lugar = {pontos} pontos (esperado: 8)")
    
    def test_pcd_fourth_place_zero_points(self):
        """PCD category: 4th place and beyond = 0 points"""
        from routes.admin_routes import calcular_pontos_colocacao
        
        for colocacao in [4, 5, 6, 10]:
            pontos = calcular_pontos_colocacao(colocacao, "pcd")
            assert pontos == 0, f"Expected 0 points for PCD position {colocacao}, got {pontos}"
        print("✅ PCD colocações > 3º = 0 pontos")
    
    def test_cadeirante_same_as_pcd(self):
        """Cadeirante category uses same rules as PCD"""
        from routes.admin_routes import calcular_pontos_colocacao
        
        expected = {1: 10, 2: 9, 3: 8, 4: 0, 5: 0, 10: 0}
        
        for colocacao, pontos_esperado in expected.items():
            pontos = calcular_pontos_colocacao(colocacao, "cadeirante")
            assert pontos == pontos_esperado, f"Cadeirante position {colocacao}: expected {pontos_esperado}, got {pontos}"
        print("✅ Cadeirante usa mesma tabela do PCD")


class TestCalcularPontosPovao:
    """Test Povão scoring based on distance"""
    
    def test_povao_5km_5_points(self):
        """Povão: 5km = 5 points"""
        from routes.admin_routes import calcular_pontos_povao
        pontos = calcular_pontos_povao("5km")
        assert pontos == 5, f"Expected 5 points for 5km, got {pontos}"
        print(f"✅ Povão 5km = {pontos} pontos (esperado: 5)")
    
    def test_povao_9km_5_points(self):
        """Povão: 9km = 5 points (5-9km range)"""
        from routes.admin_routes import calcular_pontos_povao
        pontos = calcular_pontos_povao("9km")
        assert pontos == 5, f"Expected 5 points for 9km, got {pontos}"
        print(f"✅ Povão 9km = {pontos} pontos (esperado: 5)")
    
    def test_povao_10km_7_points(self):
        """Povão: 10km = 7 points"""
        from routes.admin_routes import calcular_pontos_povao
        pontos = calcular_pontos_povao("10km")
        assert pontos == 7, f"Expected 7 points for 10km, got {pontos}"
        print(f"✅ Povão 10km = {pontos} pontos (esperado: 7)")
    
    def test_povao_20km_7_points(self):
        """Povão: 20km = 7 points (10-20km range)"""
        from routes.admin_routes import calcular_pontos_povao
        pontos = calcular_pontos_povao("20km")
        assert pontos == 7, f"Expected 7 points for 20km, got {pontos}"
        print(f"✅ Povão 20km = {pontos} pontos (esperado: 7)")
    
    def test_povao_21km_9_points(self):
        """Povão: 21km = 9 points (meia maratona)"""
        from routes.admin_routes import calcular_pontos_povao
        pontos = calcular_pontos_povao("21km")
        assert pontos == 9, f"Expected 9 points for 21km, got {pontos}"
        print(f"✅ Povão 21km = {pontos} pontos (esperado: 9)")
    
    def test_povao_42km_9_points(self):
        """Povão: 42km = 9 points (maratona)"""
        from routes.admin_routes import calcular_pontos_povao
        pontos = calcular_pontos_povao("42km")
        assert pontos == 9, f"Expected 9 points for 42km, got {pontos}"
        print(f"✅ Povão 42km = {pontos} pontos (esperado: 9)")
    
    def test_povao_less_than_5km_zero_points(self):
        """Povão: less than 5km = 0 points"""
        from routes.admin_routes import calcular_pontos_povao
        pontos = calcular_pontos_povao("3km")
        assert pontos == 0, f"Expected 0 points for 3km, got {pontos}"
        print("✅ Povão < 5km = 0 pontos")


class TestRankingAssessoriasAPI:
    """Test the ranking endpoint returns consistent data with corrected points"""
    
    @pytest.fixture
    def api_client(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    def test_ranking_endpoint_accessible(self, api_client):
        """Test ranking endpoint is accessible"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Endpoint /api/liga-assessorias/ranking acessível")
    
    def test_ranking_returns_expected_structure(self, api_client):
        """Test ranking returns correct data structure"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check main structure
        assert "ranking" in data, "Response missing 'ranking' field"
        assert "total_assessorias" in data, "Response missing 'total_assessorias' field"
        assert "tipo" in data, "Response missing 'tipo' field"
        
        print(f"✅ Estrutura do ranking correta. Total assessorias: {data['total_assessorias']}")
    
    def test_ranking_assessorias_have_correct_point_fields(self, api_client):
        """Test each assessoria has correct point fields"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        
        data = response.json()
        ranking = data.get("ranking", [])
        
        if len(ranking) == 0:
            pytest.skip("No assessorias in ranking")
        
        first_assessoria = ranking[0]
        
        required_fields = ["nome", "pontos_total", "pontos_cadastro", "pontos_resultados", 
                          "total_atletas", "total_resultados"]
        
        for field in required_fields:
            assert field in first_assessoria, f"Missing field: {field}"
        
        # Validate that pontos_total is reasonable (not 10x inflated)
        pontos = first_assessoria.get("pontos_total", 0)
        print(f"✅ Primeira assessoria: {first_assessoria['nome']} com {pontos} pontos")
        
        # If there's a TOP RUN assessoria, verify its points
        for assessoria in ranking:
            if "TOP RUN" in assessoria.get("nome", "").upper():
                pontos_top_run = assessoria.get("pontos_total", 0)
                # Should be around ~34 points, not 124
                assert pontos_top_run < 100, f"TOP RUN points too high: {pontos_top_run}. Should be ~34 after fix"
                print(f"✅ TOP RUN encontrada com {pontos_top_run} pontos (esperado: ~34, não 124)")
                break
    
    def test_top_run_assessoria_points_reasonable(self, api_client):
        """Verify TOP RUN assessoria has corrected points (~34, not 124)"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        
        data = response.json()
        ranking = data.get("ranking", [])
        
        top_run = None
        for assessoria in ranking:
            nome = assessoria.get("nome", "").upper()
            if "TOP RUN" in nome:
                top_run = assessoria
                break
        
        if top_run is None:
            # Try to find it in assessoria details
            response_detail = api_client.get(f"{BASE_URL}/api/liga-assessorias/assessoria/TOP%20RUN")
            if response_detail.status_code == 200:
                top_run = response_detail.json()
        
        if top_run is None:
            pytest.skip("TOP RUN assessoria not found - cannot verify points correction")
        
        pontos = top_run.get("pontos_total", 0)
        
        # The old system had 1º=100pts, so TOP RUN had ~124 points
        # The new system has 1º=10pts, so should be ~34 points
        # Allow margin for calculation differences
        assert pontos < 100, f"TOP RUN still has inflated points: {pontos}. Expected <100 after fix"
        
        print(f"✅ TOP RUN: {pontos} pontos (fix aplicado corretamente - era ~124, agora deve ser ~34)")


class TestAssessoriaDetailsAPI:
    """Test assessoria details endpoint shows athletes with correct points"""
    
    @pytest.fixture
    def api_client(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    def test_assessoria_details_endpoint(self, api_client):
        """Test assessoria details endpoint is accessible"""
        # First get a list of assessorias
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        
        data = response.json()
        ranking = data.get("ranking", [])
        
        if len(ranking) == 0:
            pytest.skip("No assessorias available")
        
        # Get details of first assessoria
        import urllib.parse
        nome = ranking[0].get("nome", "")
        nome_encoded = urllib.parse.quote(nome)
        
        response_detail = api_client.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{nome_encoded}")
        assert response_detail.status_code == 200, f"Expected 200, got {response_detail.status_code}"
        
        print(f"✅ Detalhes da assessoria '{nome}' acessíveis")
    
    def test_assessoria_details_athletes_have_points(self, api_client):
        """Test athletes in assessoria details have points field"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        
        data = response.json()
        ranking = data.get("ranking", [])
        
        if len(ranking) == 0:
            pytest.skip("No assessorias available")
        
        import urllib.parse
        nome = ranking[0].get("nome", "")
        nome_encoded = urllib.parse.quote(nome)
        
        response_detail = api_client.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{nome_encoded}")
        assert response_detail.status_code == 200
        
        details = response_detail.json()
        atletas = details.get("atletas", [])
        
        if len(atletas) == 0:
            pytest.skip("No athletes in this assessoria")
        
        # Check athletes have pontos and total_corridas fields
        for atleta in atletas[:5]:  # Check first 5
            # pontos field should exist
            assert "pontos" in atleta or "pontos_total" in atleta, f"Athlete missing points field: {atleta.get('nome', 'Unknown')}"
            print(f"  - {atleta.get('nome', 'N/A')}: {atleta.get('pontos', atleta.get('pontos_total', 0))} pontos")
        
        print(f"✅ Atletas da assessoria '{nome}' têm campo de pontos")
    
    def test_assessoria_points_total_consistency(self, api_client):
        """Test that assessoria pontos_total is consistent with sum of parts"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        
        data = response.json()
        ranking = data.get("ranking", [])
        
        if len(ranking) == 0:
            pytest.skip("No assessorias available")
        
        for assessoria in ranking[:5]:  # Check first 5
            pontos_total = assessoria.get("pontos_total", 0)
            pontos_cadastro = assessoria.get("pontos_cadastro", 0)
            pontos_resultados = assessoria.get("pontos_resultados", 0)
            
            expected_total = round(pontos_cadastro + pontos_resultados, 1)
            
            assert abs(pontos_total - expected_total) < 0.5, \
                f"{assessoria['nome']}: pontos_total ({pontos_total}) != cadastro ({pontos_cadastro}) + resultados ({pontos_resultados})"
            
            print(f"✅ {assessoria['nome']}: {pontos_total} = {pontos_cadastro} (cadastro) + {pontos_resultados} (resultados)")


class TestNoInflatedPoints:
    """Verify no assessorias have the old inflated points (100+ for simple placements)"""
    
    @pytest.fixture
    def api_client(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    def test_no_assessoria_has_inflated_points_from_single_race(self, api_client):
        """No single race should give more than 10 points"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        
        data = response.json()
        ranking = data.get("ranking", [])
        
        for assessoria in ranking:
            total_resultados = assessoria.get("total_resultados", 0)
            pontos_resultados = assessoria.get("pontos_resultados", 0)
            
            if total_resultados > 0:
                # Average points per race should not exceed 10 (max single race)
                avg_pontos = pontos_resultados / total_resultados
                assert avg_pontos <= 10, \
                    f"{assessoria['nome']}: avg points/race = {avg_pontos:.1f} (should be ≤10)"
        
        print("✅ Nenhuma assessoria com pontos inflados (média por corrida ≤ 10)")
    
    def test_max_points_per_colocacao_is_10(self, api_client):
        """Direct function test: max points for any position is 10"""
        from routes.admin_routes import calcular_pontos_colocacao
        
        for colocacao in range(1, 15):
            for categoria in ["normal", "pcd", "cadeirante", "amador"]:
                pontos = calcular_pontos_colocacao(colocacao, categoria)
                assert pontos <= 10, f"Position {colocacao}, category {categoria}: {pontos} > 10"
        
        print("✅ Máximo de 10 pontos por colocação em todas as categorias")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
