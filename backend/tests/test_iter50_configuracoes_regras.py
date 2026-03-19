# /app/backend/tests/test_iter50_configuracoes_regras.py
# Tests for Sistema de Configurações e Regras
# Features: Página pública de Regras, Painel Admin de Configurações

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPublicRegras:
    """Testes para o endpoint público de regras GET /api/configuracoes/regras"""
    
    def test_get_regras_returns_200(self):
        """Verifica que o endpoint público de regras retorna status 200"""
        response = requests.get(f"{BASE_URL}/api/configuracoes/regras")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ GET /api/configuracoes/regras returns 200")
    
    def test_regras_has_ranking_profissional(self):
        """Verifica que as regras contêm dados do ranking profissional"""
        response = requests.get(f"{BASE_URL}/api/configuracoes/regras")
        data = response.json()
        
        assert "ranking_profissional" in data, "Missing 'ranking_profissional' in response"
        rp = data["ranking_profissional"]
        
        assert "titulo" in rp, "Missing 'titulo' in ranking_profissional"
        assert "descricao" in rp, "Missing 'descricao' in ranking_profissional"
        assert "pontuacao_normal" in rp, "Missing 'pontuacao_normal' in ranking_profissional"
        assert "pontuacao_pcd" in rp, "Missing 'pontuacao_pcd' in ranking_profissional"
        
        # Verify pontuacao_normal has expected structure
        assert len(rp["pontuacao_normal"]) == 10, f"Expected 10 positions in pontuacao_normal, got {len(rp['pontuacao_normal'])}"
        assert rp["pontuacao_normal"][0]["posicao"] == "1º lugar"
        assert isinstance(rp["pontuacao_normal"][0]["pontos"], int)
        
        # Verify pontuacao_pcd has expected structure
        assert len(rp["pontuacao_pcd"]) == 3, f"Expected 3 positions in pontuacao_pcd, got {len(rp['pontuacao_pcd'])}"
        
        print("✅ ranking_profissional has correct structure")
    
    def test_regras_has_ranking_povao(self):
        """Verifica que as regras contêm dados do ranking povão"""
        response = requests.get(f"{BASE_URL}/api/configuracoes/regras")
        data = response.json()
        
        assert "ranking_povao" in data, "Missing 'ranking_povao' in response"
        rp = data["ranking_povao"]
        
        assert "titulo" in rp, "Missing 'titulo' in ranking_povao"
        assert "descricao" in rp, "Missing 'descricao' in ranking_povao"
        assert "faixas" in rp, "Missing 'faixas' in ranking_povao"
        
        # Verify faixas has expected structure (3 distance bands)
        assert len(rp["faixas"]) == 3, f"Expected 3 faixas, got {len(rp['faixas'])}"
        
        faixas_distancias = [f["distancia"] for f in rp["faixas"]]
        assert "5km a 9km" in faixas_distancias
        assert "10km a 20km" in faixas_distancias
        assert "21km ou mais" in faixas_distancias
        
        print("✅ ranking_povao has correct structure")
    
    def test_regras_has_ranking_equipes(self):
        """Verifica que as regras contêm dados do ranking de equipes"""
        response = requests.get(f"{BASE_URL}/api/configuracoes/regras")
        data = response.json()
        
        assert "ranking_equipes" in data, "Missing 'ranking_equipes' in response"
        re = data["ranking_equipes"]
        
        assert "titulo" in re, "Missing 'titulo' in ranking_equipes"
        assert "descricao" in re, "Missing 'descricao' in ranking_equipes"
        assert "pontuacao" in re, "Missing 'pontuacao' in ranking_equipes"
        
        # Verify pontuacao has expected structure (4 criteria)
        assert len(re["pontuacao"]) == 4, f"Expected 4 pontuacao criteria, got {len(re['pontuacao'])}"
        
        criterios = [p["criterio"] for p in re["pontuacao"]]
        assert "Por atleta vinculado" in criterios
        assert "Por resultado aprovado" in criterios
        
        print("✅ ranking_equipes has correct structure")
    
    def test_regras_has_configuracoes_gerais(self):
        """Verifica que as regras contêm configurações gerais"""
        response = requests.get(f"{BASE_URL}/api/configuracoes/regras")
        data = response.json()
        
        assert "configuracoes_gerais" in data, "Missing 'configuracoes_gerais' in response"
        cg = data["configuracoes_gerais"]
        
        assert "prazo_submissao_dias" in cg, "Missing 'prazo_submissao_dias'"
        assert "minimo_provas_normal" in cg, "Missing 'minimo_provas_normal'"
        assert "minimo_provas_pcd" in cg, "Missing 'minimo_provas_pcd'"
        assert "pontos_status_elite" in cg, "Missing 'pontos_status_elite'"
        
        # Verify values are integers
        assert isinstance(cg["prazo_submissao_dias"], int)
        assert isinstance(cg["minimo_provas_normal"], int)
        
        print("✅ configuracoes_gerais has correct structure")


class TestAdminConfiguracoes:
    """Testes para endpoints admin de configurações"""
    
    @pytest.fixture
    def admin_token(self):
        """Login como admin e retorna token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@runpro.com", "password": "admin"}
        )
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
        
        data = response.json()
        token = data.get("access_token") or data.get("token")
        if not token:
            pytest.skip(f"No token in response: {data}")
        
        print(f"✅ Admin logged in successfully")
        return token
    
    def test_admin_get_configuracoes_without_auth_fails(self):
        """Verifica que GET /api/admin/configuracoes sem auth retorna 401/403"""
        response = requests.get(f"{BASE_URL}/api/admin/configuracoes")
        assert response.status_code in [401, 403, 422], f"Expected 401/403, got {response.status_code}"
        print(f"✅ GET /api/admin/configuracoes without auth returns {response.status_code}")
    
    def test_admin_get_configuracoes_with_auth(self, admin_token):
        """Verifica que GET /api/admin/configuracoes com auth retorna 200"""
        response = requests.get(
            f"{BASE_URL}/api/admin/configuracoes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify structure for admin panel
        assert "pontuacao_normal" in data, "Missing 'pontuacao_normal'"
        assert "pontuacao_pcd" in data, "Missing 'pontuacao_pcd'"
        assert "pontuacao_povao" in data, "Missing 'pontuacao_povao'"
        assert "pontuacao_equipes" in data, "Missing 'pontuacao_equipes'"
        assert "configuracoes_gerais" in data, "Missing 'configuracoes_gerais'"
        assert "textos" in data, "Missing 'textos'"
        
        print("✅ GET /api/admin/configuracoes returns correct structure")
    
    def test_admin_put_configuracoes_without_auth_fails(self):
        """Verifica que PUT /api/admin/configuracoes sem auth retorna 401/403"""
        response = requests.put(
            f"{BASE_URL}/api/admin/configuracoes",
            json={"pontuacao_normal": {"primeiro": 10}}
        )
        assert response.status_code in [401, 403, 422], f"Expected 401/403, got {response.status_code}"
        print(f"✅ PUT /api/admin/configuracoes without auth returns {response.status_code}")
    
    def test_admin_put_configuracoes_with_auth(self, admin_token):
        """Verifica que PUT /api/admin/configuracoes com auth atualiza corretamente"""
        # First, get current config
        get_response = requests.get(
            f"{BASE_URL}/api/admin/configuracoes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        original_config = get_response.json()
        
        # Prepare update payload with valid structure
        update_payload = {
            "pontuacao_normal": original_config.get("pontuacao_normal", {
                "primeiro": 10, "segundo": 9, "terceiro": 8, "quarto": 7, "quinto": 6,
                "sexto": 5, "setimo": 4, "oitavo": 3, "nono": 2, "decimo": 1
            }),
            "pontuacao_pcd": original_config.get("pontuacao_pcd", {
                "primeiro": 10, "segundo": 9, "terceiro": 8
            }),
            "pontuacao_povao": original_config.get("pontuacao_povao", {
                "faixa_5_9km": 5, "faixa_10_20km": 7, "faixa_21km_mais": 9
            }),
            "pontuacao_equipes": original_config.get("pontuacao_equipes", {
                "por_atleta": 0.5, "por_resultado": 1.0,
                "bonus_2_a_5_lugar": 0.5, "bonus_1_lugar": 1.0
            }),
            "configuracoes_gerais": original_config.get("configuracoes_gerais", {
                "prazo_submissao_dias": 30,
                "minimo_provas_normal": 12,
                "minimo_provas_pcd": 8,
                "pontos_status_elite": 100
            }),
            "textos": original_config.get("textos", {
                "titulo_profissional": "RANKING PROFISSIONAL/AMADOR",
                "descricao_profissional": "Os atletas acumulam pontos ao participar de corridas oficiais.",
                "titulo_povao": "RANKING DO POVÃO",
                "descricao_povao": "O Ranking do Povão é uma modalidade especial.",
                "titulo_equipes": "RANKING DAS EQUIPES",
                "descricao_equipes": "A Liga Nacional de Assessorias."
            })
        }
        
        # Make update
        response = requests.put(
            f"{BASE_URL}/api/admin/configuracoes",
            json=update_payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Missing 'message' in response"
        assert "atualizado_em" in data or "atualizado" in data.get("message", "").lower(), "Missing update confirmation"
        
        print("✅ PUT /api/admin/configuracoes updates successfully")
    
    def test_admin_reset_configuracoes_without_auth_fails(self):
        """Verifica que POST /api/admin/configuracoes/resetar sem auth retorna 401/403"""
        response = requests.post(f"{BASE_URL}/api/admin/configuracoes/resetar")
        assert response.status_code in [401, 403, 422], f"Expected 401/403, got {response.status_code}"
        print(f"✅ POST /api/admin/configuracoes/resetar without auth returns {response.status_code}")


class TestPontuacaoValuesFromRegras:
    """Verifica que os valores de pontuação na API pública estão corretos"""
    
    def test_pontuacao_normal_values(self):
        """Verifica valores da pontuação normal (1º=10, 2º=9, etc)"""
        response = requests.get(f"{BASE_URL}/api/configuracoes/regras")
        data = response.json()
        
        pontos = data["ranking_profissional"]["pontuacao_normal"]
        
        # Verificar que temos os valores esperados (baseado em CONFIGURACOES_PADRAO)
        expected_values = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        actual_values = [p["pontos"] for p in pontos]
        
        for i, (expected, actual) in enumerate(zip(expected_values, actual_values)):
            assert actual == expected, f"Position {i+1}: expected {expected}, got {actual}"
        
        print("✅ Pontuação normal values are correct (10, 9, 8, 7, 6, 5, 4, 3, 2, 1)")
    
    def test_pontuacao_pcd_values(self):
        """Verifica valores da pontuação PCD (1º=10, 2º=9, 3º=8)"""
        response = requests.get(f"{BASE_URL}/api/configuracoes/regras")
        data = response.json()
        
        pontos = data["ranking_profissional"]["pontuacao_pcd"]
        
        expected_values = [10, 9, 8]
        actual_values = [p["pontos"] for p in pontos]
        
        for i, (expected, actual) in enumerate(zip(expected_values, actual_values)):
            assert actual == expected, f"Position {i+1}: expected {expected}, got {actual}"
        
        print("✅ Pontuação PCD values are correct (10, 9, 8)")
    
    def test_pontuacao_povao_values(self):
        """Verifica valores da pontuação povão por distância"""
        response = requests.get(f"{BASE_URL}/api/configuracoes/regras")
        data = response.json()
        
        faixas = data["ranking_povao"]["faixas"]
        
        # Create dict for easier checking
        faixas_dict = {f["distancia"]: f["pontos"] for f in faixas}
        
        assert faixas_dict["5km a 9km"] == 5, f"5km-9km: expected 5, got {faixas_dict['5km a 9km']}"
        assert faixas_dict["10km a 20km"] == 7, f"10km-20km: expected 7, got {faixas_dict['10km a 20km']}"
        assert faixas_dict["21km ou mais"] == 9, f"21km+: expected 9, got {faixas_dict['21km ou mais']}"
        
        print("✅ Pontuação povão values are correct (5, 7, 9)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
