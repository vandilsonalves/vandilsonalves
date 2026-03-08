"""
Test iteration 24: Verificar sincronização entre as 3 modalidades de ranking:
1. Ranking do Povão (pontuação por distância)
2. Ranking Profissional/Amador (pontuação por colocação)
3. Ranking de Equipes (Liga de Assessorias)

Sistema de pontuação:
- Equipes: Atleta=+0.5, Resultado=+1.0, 2º-5º=+0.5, 1º=+1.0
- Povão: 5km-9km=5pts, 10km-20km=7pts, 21km+=9pts
- Profissional: 1º=10pts até 10º=1pt
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestRankingPovao:
    """Testes do Ranking do Povão"""
    
    def test_ranking_povao_masculino_returns_data(self):
        """GET /api/ranking/povao?genero=M retorna atletas"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        assert "total_atletas" in data
        assert len(data["ranking"]) > 0
        print(f"✓ Ranking Povão Masculino: {data['total_atletas']} atletas")
    
    def test_ranking_povao_feminino_returns_data(self):
        """GET /api/ranking/povao?genero=F retorna atletas"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=F")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        assert "total_atletas" in data
        print(f"✓ Ranking Povão Feminino: {data['total_atletas']} atletas")
    
    def test_ranking_povao_has_correct_fields(self):
        """Atletas do Povão têm campos corretos"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["ranking"]) > 0:
            atleta = data["ranking"][0]
            required_fields = ["colocacao", "atleta_id", "nome", "pontos", "total_corridas", "distancia_acumulada", "equipe"]
            for field in required_fields:
                assert field in atleta, f"Campo '{field}' ausente no atleta"
            print(f"✓ Primeiro atleta Povão: {atleta['nome']} ({atleta['equipe']}) - {atleta['pontos']} pts")
    
    def test_ranking_povao_stats_correct(self):
        """Stats do Povão mostram 40 atletas (20M + 20F)"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_atletas" in data
        assert "total_atletas_masculino" in data
        assert "total_atletas_feminino" in data
        
        # Verificar se total = masculino + feminino
        total = data["total_atletas"]
        masc = data["total_atletas_masculino"]
        fem = data["total_atletas_feminino"]
        
        assert total == masc + fem, f"Total ({total}) != Masculino ({masc}) + Feminino ({fem})"
        print(f"✓ Stats Povão: Total={total}, Masculino={masc}, Feminino={fem}")
        
        # Deve ter 40 atletas conforme especificado
        assert total == 40, f"Total esperado 40, obtido {total}"


class TestRankingProfissional:
    """Testes do Ranking Profissional/Amador"""
    
    def test_ranking_profissional_masculino_returns_data(self):
        """GET /api/ranking/categoria/masculino/M retorna atletas"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/masculino/M")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"✓ Ranking Profissional Masculino: {len(data)} atletas")
    
    def test_ranking_profissional_feminino_returns_data(self):
        """GET /api/ranking/categoria/feminino/M retorna atletas"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/feminino/M")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Ranking Profissional Feminino: {len(data)} atletas")
    
    def test_ranking_profissional_has_correct_fields(self):
        """Atletas Profissional têm campos corretos"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/masculino/M")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) > 0:
            atleta = data[0]
            required_fields = ["id", "colocacao", "nome", "pontos", "total_corridas", "equipe", "is_elite", "is_pendente"]
            for field in required_fields:
                assert field in atleta, f"Campo '{field}' ausente no atleta"
            print(f"✓ Primeiro atleta Profissional: {atleta['nome']} ({atleta['equipe']}) - {atleta['pontos']} pts")


class TestRankingEquipes:
    """Testes do Ranking de Equipes (Liga de Assessorias)"""
    
    def test_ranking_equipes_returns_data(self):
        """GET /api/liga-assessorias/ranking retorna equipes"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        assert "total_assessorias" in data
        assert len(data["ranking"]) > 0
        print(f"✓ Ranking Equipes: {data['total_assessorias']} assessorias")
    
    def test_ranking_equipes_has_correct_fields(self):
        """Equipes têm campos corretos"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["ranking"]) > 0:
            equipe = data["ranking"][0]
            required_fields = ["nome", "total_atletas", "pontos_total", "total_resultados", "posicao", "selo"]
            for field in required_fields:
                assert field in equipe, f"Campo '{field}' ausente na equipe"
            print(f"✓ Primeira equipe: {equipe['nome']} - {equipe['pontos_total']} pts, {equipe['total_atletas']} atletas")
    
    def test_ranking_equipes_pontuacao_correta(self):
        """Verificar sistema de pontuação: Atleta=+0.5, Resultado=+1.0, 2º-5º=+0.5, 1º=+1.0"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        data = response.json()
        
        for equipe in data["ranking"][:5]:
            # Verificar se os campos de pontuação existem
            assert "pontos_cadastro" in equipe, "Campo pontos_cadastro ausente"
            assert "pontos_resultados" in equipe, "Campo pontos_resultados ausente"
            
            # pontos_cadastro = atletas * 0.5
            expected_cadastro = equipe["total_atletas"] * 0.5
            assert equipe["pontos_cadastro"] == expected_cadastro, \
                f"pontos_cadastro incorreto para {equipe['nome']}: esperado {expected_cadastro}, obtido {equipe['pontos_cadastro']}"
            
            # pontos_total = pontos_cadastro + pontos_resultados
            total_calculado = equipe["pontos_cadastro"] + equipe["pontos_resultados"]
            assert abs(equipe["pontos_total"] - total_calculado) < 0.1, \
                f"pontos_total incorreto para {equipe['nome']}: esperado {total_calculado}, obtido {equipe['pontos_total']}"
            
            print(f"✓ {equipe['nome']}: cadastro={equipe['pontos_cadastro']}, resultados={equipe['pontos_resultados']}, total={equipe['pontos_total']}")


class TestAtletasWithEquipesInAllRankings:
    """Verificar que atletas com equipe aparecem nas 3 modalidades"""
    
    def test_champions_sc_in_equipes_ranking(self):
        """Champions SC aparece no ranking de equipes"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        data = response.json()
        
        champions = [e for e in data["ranking"] if "Champions" in e["nome"]]
        assert len(champions) > 0, "Champions SC não encontrada no ranking de equipes"
        
        equipe = champions[0]
        print(f"✓ Champions SC no ranking de equipes: posição {equipe['posicao']}, {equipe['total_atletas']} atletas, {equipe['pontos_total']} pts")
    
    def test_pedro_araujo_in_povao_ranking(self):
        """Pedro Araújo (Champions SC) aparece no ranking do Povão em 1º lugar"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        assert response.status_code == 200
        data = response.json()
        
        # Procurar Pedro Araújo
        pedro = [a for a in data["ranking"] if "Pedro" in a["nome"] and "Araújo" in a["nome"]]
        assert len(pedro) > 0, "Pedro Araújo não encontrado no ranking do Povão"
        
        atleta = pedro[0]
        assert atleta["equipe"] == "Champions SC", f"Equipe incorreta: {atleta['equipe']}"
        assert atleta["colocacao"] == 1, f"Colocação incorreta: {atleta['colocacao']} (esperado 1)"
        assert atleta["pontos"] == 117, f"Pontos incorretos: {atleta['pontos']} (esperado 117)"
        
        print(f"✓ Pedro Araújo (Champions SC) no Povão: {atleta['colocacao']}º lugar, {atleta['pontos']} pts")
    
    def test_champions_sc_atletas_appear_in_equipes(self):
        """Atletas Champions SC aparecem na lista de atletas da equipe"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        assert response.status_code == 200
        data = response.json()
        
        champions = [e for e in data["ranking"] if "Champions" in e["nome"]]
        assert len(champions) > 0
        
        equipe = champions[0]
        atletas = equipe.get("atletas", [])
        
        # Verificar se Pedro Araújo está na lista
        pedro_found = any("Pedro" in a["nome"] and "Araújo" in a["nome"] for a in atletas)
        assert pedro_found, "Pedro Araújo não encontrado na lista de atletas da Champions SC"
        
        print(f"✓ Champions SC tem {len(atletas)} atletas na lista, incluindo Pedro Araújo")


class TestRecalcularRankings:
    """Testes do endpoint de recálculo de rankings"""
    
    @pytest.fixture
    def admin_token(self):
        """Obtém token de admin"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@runpro.com", "password": "admin123"}
        )
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    def test_recalcular_rankings_requires_auth(self):
        """POST /api/admin/recalcular-rankings requer autenticação"""
        response = requests.post(f"{BASE_URL}/api/admin/recalcular-rankings")
        assert response.status_code in [401, 403]
        print("✓ Endpoint recalcular-rankings requer autenticação")
    
    def test_recalcular_rankings_success(self, admin_token):
        """POST /api/admin/recalcular-rankings recalcula com sucesso"""
        response = requests.post(
            f"{BASE_URL}/api/admin/recalcular-rankings",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "ranking_profissional" in data
        assert "ranking_povao" in data
        
        print(f"✓ Rankings recalculados: Profissional={data['ranking_profissional']}, Povão={data['ranking_povao']}")
        
        # Verificar valores esperados
        assert data["ranking_profissional"] == 33, f"Profissional esperado 33, obtido {data['ranking_profissional']}"
        assert data["ranking_povao"] == 40, f"Povão esperado 40, obtido {data['ranking_povao']}"


class TestFrontendTabs:
    """Verificar que as 4 abas estão disponíveis via API"""
    
    def test_all_ranking_types_available(self):
        """Verificar que os 3 tipos de ranking estão acessíveis"""
        endpoints = [
            ("/api/ranking/categoria/masculino/M", "Profissional"),
            ("/api/ranking/povao?genero=M", "Povão"),
            ("/api/liga-assessorias/ranking", "Equipes"),
        ]
        
        for endpoint, nome in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Endpoint {nome} ({endpoint}) falhou com status {response.status_code}"
            print(f"✓ Endpoint {nome} acessível")


# Executar testes se chamado diretamente
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
