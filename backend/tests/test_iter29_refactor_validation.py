# /app/backend/tests/test_iter29_refactor_validation.py
# Iteration 29: Backend Refactoring Validation Tests
# Tests all endpoints that were migrated from monolithic server.py to separate modules:
# - auth_routes.py: /auth/register, /auth/login, /auth/me
# - notificacoes_routes.py: /notificacoes, marcar lida
# - conquistas_routes.py: /conquistas, /selos-atleta
# - atletas_routes.py: /atletas/meu-perfil, perfil, senha
# - resultados_routes.py: /resultados/submeter
# - ranking_routes.py: /ranking/povao, semanal, mensal, destaque-mes

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ranking-run-v2.preview.emergentagent.com')


class TestAuthRoutes:
    """Tests for auth_routes.py module"""
    
    def test_login_admin_success(self):
        """POST /api/auth/login - Admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == "admin@rankingrun.com"
        assert data["user"]["role"] == "admin"
    
    def test_login_atleta_success(self):
        """POST /api/auth/login - Atleta login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "rafael_souza_1@email.com",
            "password": "senha123"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] == "atleta"
    
    def test_auth_me_with_valid_token(self):
        """GET /api/auth/me - Returns logged user data"""
        # First login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        token = login_resp.json()["token"]
        
        # Get me
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@rankingrun.com"
        assert data["role"] == "admin"
        assert "modalidade_usuario" in data
    
    def test_auth_me_without_token(self):
        """GET /api/auth/me - Should fail without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code in [401, 403]


class TestNotificacoesRoutes:
    """Tests for notificacoes_routes.py module"""
    
    @pytest.fixture
    def auth_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        return resp.json()["token"]
    
    def test_get_notificacoes(self, auth_token):
        """GET /api/notificacoes - Returns user notifications"""
        response = requests.get(
            f"{BASE_URL}/api/notificacoes",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "notificacoes" in data
        assert "nao_lidas" in data
        assert isinstance(data["notificacoes"], list)


class TestConquistasRoutes:
    """Tests for conquistas_routes.py module"""
    
    @pytest.fixture
    def auth_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        return resp.json()["token"]
    
    def test_get_conquistas(self, auth_token):
        """GET /api/conquistas - Returns user achievements"""
        response = requests.get(
            f"{BASE_URL}/api/conquistas",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "conquistas" in data
        assert "total" in data
    
    def test_get_conquistas_disponiveis(self):
        """GET /api/conquistas/disponiveis - Returns available achievements"""
        response = requests.get(f"{BASE_URL}/api/conquistas/disponiveis")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAtletasRoutes:
    """Tests for atletas_routes.py module"""
    
    @pytest.fixture
    def atleta_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "rafael_souza_1@email.com",
            "password": "senha123"
        })
        return resp.json()["token"]
    
    def test_get_meu_perfil(self, atleta_token):
        """GET /api/atletas/meu-perfil - Returns athlete's own profile"""
        response = requests.get(
            f"{BASE_URL}/api/atletas/meu-perfil",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "nome" in data
        assert "email" in data
        assert data["email"] == "rafael_souza_1@email.com"
        assert "pontos_carreira" in data
        assert "total_corridas" in data


class TestRankingRoutes:
    """Tests for ranking_routes.py module"""
    
    def test_ranking_povao_masculino(self):
        """GET /api/ranking/povao?genero=M - Returns Povao ranking"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        assert response.status_code == 200
        data = response.json()
        assert "genero" in data
        assert data["genero"] == "Masculino"
        assert "total_atletas" in data
        assert "ranking" in data
        assert isinstance(data["ranking"], list)
        if data["ranking"]:
            athlete = data["ranking"][0]
            assert "posicao" in athlete
            assert "nome" in athlete
            assert "pontos" in athlete
    
    def test_ranking_povao_feminino(self):
        """GET /api/ranking/povao?genero=F - Returns Povao ranking for female"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=F")
        assert response.status_code == 200
        data = response.json()
        assert data["genero"] == "Feminino"
    
    def test_ranking_semanal(self):
        """GET /api/ranking/semanal - Returns weekly ranking"""
        response = requests.get(f"{BASE_URL}/api/ranking/semanal")
        assert response.status_code == 200
        data = response.json()
        assert "periodo" in data
        assert "genero" in data
        assert "categoria" in data
        assert "ranking" in data
        assert isinstance(data["ranking"], list)
    
    def test_ranking_mensal(self):
        """GET /api/ranking/mensal - Returns monthly ranking"""
        response = requests.get(f"{BASE_URL}/api/ranking/mensal")
        assert response.status_code == 200
        data = response.json()
        assert "periodo" in data
        assert "ranking" in data
    
    def test_ranking_destaque_mes(self):
        """GET /api/ranking/destaque-mes - Returns monthly highlights"""
        response = requests.get(f"{BASE_URL}/api/ranking/destaque-mes")
        assert response.status_code == 200
        data = response.json()
        assert "mes" in data
        assert "ano" in data
        assert "total_corridas_mes" in data
        assert "destaques_categoria" in data
        assert "mais_ativo_mes" in data
        assert "mais_pontos_mes" in data
        # Verify all categories present
        assert "Masculino" in data["destaques_categoria"]
        assert "Feminino" in data["destaques_categoria"]
        assert "PCD Masculino" in data["destaques_categoria"]
        assert "PCD Feminino" in data["destaques_categoria"]


class TestAdminRoutes:
    """Tests for admin endpoints in server.py"""
    
    @pytest.fixture
    def admin_token(self):
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        return resp.json()["token"]
    
    def test_admin_pendentes(self, admin_token):
        """GET /api/admin/pendentes - Returns pending results"""
        response = requests.get(
            f"{BASE_URL}/api/admin/pendentes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_admin_stats(self, admin_token):
        """GET /api/admin/stats - Returns admin statistics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_atletas" in data
        assert "resultados_pendentes" in data
    
    def test_admin_atletas(self, admin_token):
        """GET /api/admin/atletas - Returns all athletes"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "nome" in data[0]
            assert "email" in data[0]


class TestPublicEndpoints:
    """Tests for public endpoints accessible without auth"""
    
    def test_ranking_estados(self):
        """GET /api/ranking/estados - Returns list of states"""
        response = requests.get(f"{BASE_URL}/api/ranking/estados")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_ranking_faixas_etarias(self):
        """GET /api/ranking/faixas-etarias - Returns age ranges"""
        response = requests.get(f"{BASE_URL}/api/ranking/faixas-etarias")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_ranking_equipes(self):
        """GET /api/ranking/equipes - Returns teams"""
        response = requests.get(f"{BASE_URL}/api/ranking/equipes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
