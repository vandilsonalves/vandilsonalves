"""
Backend API tests for Ranking Semanal, Mensal, and Destaque do Mês
Testing new endpoints:
- /api/ranking/semanal - Weekly ranking
- /api/ranking/mensal - Monthly ranking
- /api/ranking/destaque-mes - Month highlights (most active, most points)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://admin-mensagens.preview.emergentagent.com')


class TestRankingSemanal:
    """Tests for weekly ranking endpoint /api/ranking/semanal"""
    
    def test_ranking_semanal_masculino(self):
        """Test GET /api/ranking/semanal?categoria=masculino"""
        response = requests.get(f"{BASE_URL}/api/ranking/semanal?categoria=masculino")
        assert response.status_code == 200
        
        data = response.json()
        # Validate response structure
        assert "periodo" in data, "Missing 'periodo' in response"
        assert "categoria" in data, "Missing 'categoria' in response"
        assert "ranking" in data, "Missing 'ranking' in response"
        
        # Validate categoria value
        assert data["categoria"] == "masculino"
        
        # Validate ranking is a list
        assert isinstance(data["ranking"], list)
        
        # If there's data, validate athlete structure
        if len(data["ranking"]) > 0:
            atleta = data["ranking"][0]
            assert "posicao" in atleta
            assert "atleta_id" in atleta
            assert "nome" in atleta
            assert "equipe" in atleta
            assert "pontos_semana" in atleta
            assert "corridas_semana" in atleta
            # Validate top 3 have medals (position 1-3)
            assert atleta["posicao"] >= 1
        
        print(f"✓ GET /api/ranking/semanal?categoria=masculino - {len(data['ranking'])} atletas")
    
    def test_ranking_semanal_feminino(self):
        """Test GET /api/ranking/semanal?categoria=feminino"""
        response = requests.get(f"{BASE_URL}/api/ranking/semanal?categoria=feminino")
        assert response.status_code == 200
        
        data = response.json()
        assert data["categoria"] == "feminino"
        assert isinstance(data["ranking"], list)
        print(f"✓ GET /api/ranking/semanal?categoria=feminino - {len(data['ranking'])} atletas")
    
    def test_ranking_semanal_pcd_m(self):
        """Test GET /api/ranking/semanal?categoria=pcd-m"""
        response = requests.get(f"{BASE_URL}/api/ranking/semanal?categoria=pcd-m")
        assert response.status_code == 200
        
        data = response.json()
        assert data["categoria"] == "pcd-m"
        print(f"✓ GET /api/ranking/semanal?categoria=pcd-m - {len(data['ranking'])} atletas")
    
    def test_ranking_semanal_cadeirante_m(self):
        """Test GET /api/ranking/semanal?categoria=cadeirante-m"""
        response = requests.get(f"{BASE_URL}/api/ranking/semanal?categoria=cadeirante-m")
        assert response.status_code == 200
        
        data = response.json()
        assert data["categoria"] == "cadeirante-m"
        print(f"✓ GET /api/ranking/semanal?categoria=cadeirante-m - {len(data['ranking'])} atletas")
    
    def test_ranking_semanal_limite_top10(self):
        """Test that semanal ranking returns max 10 athletes"""
        response = requests.get(f"{BASE_URL}/api/ranking/semanal?categoria=masculino")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["ranking"]) <= 10, "Weekly ranking should return at most 10 athletes"
        print("✓ Weekly ranking respects Top 10 limit")


class TestRankingMensal:
    """Tests for monthly ranking endpoint /api/ranking/mensal"""
    
    def test_ranking_mensal_masculino(self):
        """Test GET /api/ranking/mensal?categoria=masculino"""
        response = requests.get(f"{BASE_URL}/api/ranking/mensal?categoria=masculino")
        assert response.status_code == 200
        
        data = response.json()
        # Validate response structure
        assert "mes" in data, "Missing 'mes' in response"
        assert "ano" in data, "Missing 'ano' in response"
        assert "categoria" in data, "Missing 'categoria' in response"
        assert "ranking" in data, "Missing 'ranking' in response"
        
        # Validate categoria value
        assert data["categoria"] == "masculino"
        
        # Validate ranking is a list
        assert isinstance(data["ranking"], list)
        
        # If there's data, validate athlete structure
        if len(data["ranking"]) > 0:
            atleta = data["ranking"][0]
            assert "posicao" in atleta
            assert "atleta_id" in atleta
            assert "nome" in atleta
            assert "pontos_mes" in atleta
            assert "corridas_mes" in atleta
        
        print(f"✓ GET /api/ranking/mensal?categoria=masculino - {data['mes']} {data['ano']}, {len(data['ranking'])} atletas")
    
    def test_ranking_mensal_feminino(self):
        """Test GET /api/ranking/mensal?categoria=feminino"""
        response = requests.get(f"{BASE_URL}/api/ranking/mensal?categoria=feminino")
        assert response.status_code == 200
        
        data = response.json()
        assert data["categoria"] == "feminino"
        print(f"✓ GET /api/ranking/mensal?categoria=feminino - {len(data['ranking'])} atletas")
    
    def test_ranking_mensal_with_custom_month(self):
        """Test GET /api/ranking/mensal with custom month parameter"""
        response = requests.get(f"{BASE_URL}/api/ranking/mensal?categoria=masculino&mes=1&ano=2026")
        assert response.status_code == 200
        
        data = response.json()
        assert data["mes"] == "Janeiro"
        assert data["ano"] == 2026
        print("✓ GET /api/ranking/mensal with custom month - Janeiro 2026")
    
    def test_ranking_mensal_limite_top10(self):
        """Test that mensal ranking returns max 10 athletes"""
        response = requests.get(f"{BASE_URL}/api/ranking/mensal?categoria=masculino")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["ranking"]) <= 10, "Monthly ranking should return at most 10 athletes"
        print("✓ Monthly ranking respects Top 10 limit")


class TestDestaqueMes:
    """Tests for month highlights endpoint /api/ranking/destaque-mes"""
    
    def test_destaque_mes_structure(self):
        """Test GET /api/ranking/destaque-mes returns correct structure"""
        response = requests.get(f"{BASE_URL}/api/ranking/destaque-mes")
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate main structure
        assert "mes" in data, "Missing 'mes' in response"
        assert "ano" in data, "Missing 'ano' in response"
        assert "total_corridas_mes" in data, "Missing 'total_corridas_mes' in response"
        assert "destaques_categoria" in data, "Missing 'destaques_categoria' in response"
        assert "mais_ativo_mes" in data, "Missing 'mais_ativo_mes' in response"
        assert "mais_pontos_mes" in data, "Missing 'mais_pontos_mes' in response"
        
        print(f"✓ GET /api/ranking/destaque-mes - {data['mes']} {data['ano']}")
    
    def test_destaque_mes_categorias(self):
        """Test that destaques_categoria contains all 6 categories"""
        response = requests.get(f"{BASE_URL}/api/ranking/destaque-mes")
        assert response.status_code == 200
        
        data = response.json()
        destaques = data["destaques_categoria"]
        
        # Check all 6 categories are present
        expected_categories = [
            "Masculino",
            "Feminino",
            "PCD Masculino",
            "PCD Feminino",
            "Cadeirante Masculino",
            "Cadeirante Feminino"
        ]
        
        for cat in expected_categories:
            assert cat in destaques, f"Missing category '{cat}' in destaques_categoria"
            assert isinstance(destaques[cat], list), f"Category '{cat}' should be a list"
        
        print("✓ All 6 categories present in destaques_categoria")
    
    def test_destaque_mes_mais_ativo(self):
        """Test mais_ativo_mes structure"""
        response = requests.get(f"{BASE_URL}/api/ranking/destaque-mes")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["mais_ativo_mes"] is not None:
            mais_ativo = data["mais_ativo_mes"]
            assert "atleta_id" in mais_ativo
            assert "nome" in mais_ativo
            assert "equipe" in mais_ativo
            assert "total_corridas" in mais_ativo
            assert mais_ativo["total_corridas"] >= 1
            print(f"✓ mais_ativo_mes: {mais_ativo['nome']} - {mais_ativo['total_corridas']} corridas")
        else:
            print("✓ mais_ativo_mes: No active athlete this month")
    
    def test_destaque_mes_mais_pontos(self):
        """Test mais_pontos_mes structure"""
        response = requests.get(f"{BASE_URL}/api/ranking/destaque-mes")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["mais_pontos_mes"] is not None:
            mais_pontos = data["mais_pontos_mes"]
            assert "atleta_id" in mais_pontos
            assert "nome" in mais_pontos
            assert "equipe" in mais_pontos
            assert "total_pontos" in mais_pontos
            assert mais_pontos["total_pontos"] >= 0
            print(f"✓ mais_pontos_mes: {mais_pontos['nome']} - {mais_pontos['total_pontos']} pontos")
        else:
            print("✓ mais_pontos_mes: No points recorded this month")
    
    def test_destaque_mes_custom_month(self):
        """Test destaque-mes with custom month parameter"""
        response = requests.get(f"{BASE_URL}/api/ranking/destaque-mes?mes=1&ano=2025")
        assert response.status_code == 200
        
        data = response.json()
        assert data["mes"] == "Janeiro"
        assert data["ano"] == 2025
        print("✓ GET /api/ranking/destaque-mes with custom month - Janeiro 2025")
    
    def test_destaque_mes_top3_per_category(self):
        """Test that each category has max 3 athletes (podium)"""
        response = requests.get(f"{BASE_URL}/api/ranking/destaque-mes")
        assert response.status_code == 200
        
        data = response.json()
        
        for cat, atletas in data["destaques_categoria"].items():
            assert len(atletas) <= 3, f"Category '{cat}' should have max 3 athletes (podium)"
            if len(atletas) > 0:
                # Validate athlete structure
                for atleta in atletas:
                    assert "atleta_id" in atleta
                    assert "nome" in atleta
                    assert "pontos_mes" in atleta
        
        print("✓ All categories respect Top 3 (podium) limit")


class TestMedals:
    """Tests to verify medal colors based on position"""
    
    def test_ranking_semanal_positions(self):
        """Test that semanal ranking has correct position ordering"""
        response = requests.get(f"{BASE_URL}/api/ranking/semanal?categoria=masculino")
        assert response.status_code == 200
        
        data = response.json()
        ranking = data["ranking"]
        
        if len(ranking) >= 2:
            # Verify positions are in order
            for i in range(1, len(ranking)):
                assert ranking[i]["posicao"] > ranking[i-1]["posicao"], "Positions should be in ascending order"
        
        # Verify first position is 1
        if len(ranking) >= 1:
            assert ranking[0]["posicao"] == 1, "First position should be 1 (gold medal)"
        
        if len(ranking) >= 3:
            assert ranking[0]["posicao"] == 1, "Position 1 = Gold medal"
            assert ranking[1]["posicao"] == 2, "Position 2 = Silver medal"
            assert ranking[2]["posicao"] == 3, "Position 3 = Bronze medal"
        
        print("✓ Medal positions (1=gold, 2=silver, 3=bronze) verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
