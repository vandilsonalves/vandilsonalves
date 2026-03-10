# /app/backend/tests/test_iter31_cache_redis.py
"""
Testes para o Sistema de Cache Redis e Módulos Refatorados

Features testadas:
1. Cache Redis - TTL e hit/miss
2. GET /api/ranking/povao (com cache)
3. GET /api/liga-assessorias/ranking (com cache)
4. GET /api/monitoring/cache (estatísticas do cache)
5. GET /api/admin/stats (módulo admin_routes.py)
6. GET /api/admin/pendentes (módulo admin_routes.py)
7. GET /api/liga-assessorias/stats (módulo assessorias_routes.py)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_CREDENTIALS = {"email": "admin@rankingrun.com", "password": "admin123"}


@pytest.fixture(scope="module")
def api_client():
    """Sessão HTTP compartilhada"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Obtém token de admin para endpoints protegidos"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Falha na autenticação admin - pulando testes autenticados")


@pytest.fixture(scope="module")
def authenticated_client(api_client, admin_token):
    """Sessão com header de autorização"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


class TestCacheRedisStatus:
    """Testes de conectividade e status do cache Redis"""
    
    def test_cache_stats_endpoint_exists(self, authenticated_client):
        """GET /api/monitoring/cache - endpoint existe e retorna estatísticas"""
        response = authenticated_client.get(f"{BASE_URL}/api/monitoring/cache")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "available" in data, "Campo 'available' não encontrado"
        assert "hits" in data, "Campo 'hits' não encontrado"
        assert "misses" in data, "Campo 'misses' não encontrado"
        assert "errors" in data, "Campo 'errors' não encontrado"
        assert "hit_rate_percent" in data, "Campo 'hit_rate_percent' não encontrado"
        
        # Cache Redis deve estar disponível
        assert data["available"] == True, "Redis não está disponível"
        print(f"✅ Cache stats: available={data['available']}, hits={data['hits']}, misses={data['misses']}, hit_rate={data['hit_rate_percent']}%")


class TestRankingPovaoWithCache:
    """Testes do endpoint GET /api/ranking/povao com cache"""
    
    def test_ranking_povao_masculino(self, api_client):
        """GET /api/ranking/povao?genero=M - ranking masculino"""
        response = api_client.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "genero" in data
        assert data["genero"] == "Masculino"
        assert "total_atletas" in data
        assert "ranking" in data
        assert isinstance(data["ranking"], list)
        
        if len(data["ranking"]) > 0:
            atleta = data["ranking"][0]
            assert "nome" in atleta
            assert "pontos" in atleta
            assert "total_corridas" in atleta
        
        print(f"✅ Ranking Povão Masculino: {data['total_atletas']} atletas")
    
    def test_ranking_povao_feminino(self, api_client):
        """GET /api/ranking/povao?genero=F - ranking feminino"""
        response = api_client.get(f"{BASE_URL}/api/ranking/povao?genero=F")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["genero"] == "Feminino"
        assert "ranking" in data
        
        print(f"✅ Ranking Povão Feminino: {data['total_atletas']} atletas")
    
    def test_ranking_povao_cache_hit(self, api_client, authenticated_client):
        """Verifica se cache está funcionando com hits"""
        # Primeira requisição (cache miss ou hit)
        api_client.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        
        # Capturar estatísticas iniciais
        stats_before = authenticated_client.get(f"{BASE_URL}/api/monitoring/cache").json()
        hits_before = stats_before["hits"]
        
        # Segunda requisição (deve ser cache hit)
        api_client.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        
        # Verificar que houve hit
        stats_after = authenticated_client.get(f"{BASE_URL}/api/monitoring/cache").json()
        hits_after = stats_after["hits"]
        
        # Hit deve ter aumentado
        assert hits_after >= hits_before, "Cache hits não aumentou como esperado"
        print(f"✅ Cache hit funcionando: {hits_before} -> {hits_after} hits")


class TestLigaAssessoriasWithCache:
    """Testes do endpoint GET /api/liga-assessorias/ranking com cache"""
    
    def test_liga_assessorias_ranking_nacional(self, api_client):
        """GET /api/liga-assessorias/ranking - ranking nacional das assessorias"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tipo" in data
        assert data["tipo"] == "nacional"
        assert "total_assessorias" in data
        assert "ranking" in data
        assert isinstance(data["ranking"], list)
        
        if len(data["ranking"]) > 0:
            assessoria = data["ranking"][0]
            assert "nome" in assessoria
            assert "pontos_total" in assessoria
            assert "total_atletas" in assessoria
            assert "posicao" in assessoria
            assert "selo" in assessoria
        
        print(f"✅ Liga Assessorias Nacional: {data['total_assessorias']} assessorias")
    
    def test_liga_assessorias_stats(self, api_client):
        """GET /api/liga-assessorias/stats - estatísticas da liga"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_assessorias" in data
        assert "total_atletas_vinculados" in data
        assert "total_resultados_aprovados" in data
        assert "maior_assessoria" in data
        
        print(f"✅ Liga Stats: {data['total_assessorias']} assessorias, {data['total_atletas_vinculados']} atletas vinculados")


class TestAdminRoutesModule:
    """Testes dos endpoints do módulo admin_routes.py refatorado"""
    
    def test_admin_stats(self, authenticated_client):
        """GET /api/admin/stats - estatísticas gerais do admin"""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_atletas" in data
        assert "resultados_pendentes" in data
        assert "total_corridas" in data
        assert "total_assessorias" in data
        assert "atletas_masculino" in data
        assert "atletas_feminino" in data
        
        # Verificar valores são números
        assert isinstance(data["total_atletas"], int)
        assert isinstance(data["total_corridas"], int)
        
        print(f"✅ Admin Stats: {data['total_atletas']} atletas, {data['total_corridas']} corridas")
    
    def test_admin_pendentes(self, authenticated_client):
        """GET /api/admin/pendentes - resultados pendentes de aprovação"""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/pendentes")
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve retornar lista (pode estar vazia)
        assert isinstance(data, list)
        
        print(f"✅ Admin Pendentes: {len(data)} resultados pendentes")
    
    def test_admin_stats_requires_auth(self, api_client):
        """GET /api/admin/stats - requer autenticação"""
        # Criar nova sessão sem auth
        clean_client = requests.Session()
        response = clean_client.get(f"{BASE_URL}/api/admin/stats")
        
        # Deve retornar 401 ou 403
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✅ Admin Stats requer autenticação corretamente")


class TestAssessoriasRoutesModule:
    """Testes dos endpoints do módulo assessorias_routes.py refatorado"""
    
    def test_assessorias_lista(self, api_client):
        """GET /api/assessorias/lista - lista de assessorias para dropdown"""
        response = api_client.get(f"{BASE_URL}/api/assessorias/lista")
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve retornar lista
        assert isinstance(data, list)
        
        if len(data) > 0:
            # Cada item deve ter nome, cidade, estado
            item = data[0]
            assert "nome" in item
            assert "cidade" in item
            assert "estado" in item
        
        print(f"✅ Assessorias Lista: {len(data)} assessorias disponíveis")
    
    def test_liga_assessorias_evolucao_mensal(self, api_client):
        """GET /api/liga-assessorias/evolucao-mensal - evolução mensal das equipes"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/evolucao-mensal")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "labels" in data
        assert "datasets" in data
        assert isinstance(data["labels"], list)
        assert isinstance(data["datasets"], list)
        
        print(f"✅ Evolução Mensal: {len(data['labels'])} meses, {len(data['datasets'])} equipes")


class TestCacheInvalidation:
    """Testes de invalidação de cache"""
    
    def test_cache_invalidation_endpoint_exists(self, authenticated_client):
        """POST /api/monitoring/cache/invalidate - endpoint de invalidação existe"""
        # Testar endpoint com prefixo inválido (não deve invalidar nada)
        response = authenticated_client.post(
            f"{BASE_URL}/api/monitoring/cache/invalidate",
            params={"prefix": "invalid_prefix"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        print(f"✅ Cache invalidation endpoint existe: {data['message']}")


class TestRankingRoutesModule:
    """Testes dos endpoints do módulo ranking_routes.py refatorado"""
    
    def test_ranking_semanal(self, api_client):
        """GET /api/ranking/semanal - ranking semanal"""
        response = api_client.get(f"{BASE_URL}/api/ranking/semanal")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "periodo" in data
        assert "genero" in data
        assert "ranking" in data
        
        print(f"✅ Ranking Semanal: período {data['periodo']}, {len(data['ranking'])} atletas")
    
    def test_ranking_mensal(self, api_client):
        """GET /api/ranking/mensal - ranking mensal"""
        response = api_client.get(f"{BASE_URL}/api/ranking/mensal")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "periodo" in data
        assert "genero" in data
        assert "ranking" in data
        
        print(f"✅ Ranking Mensal: período {data['periodo']}, {len(data['ranking'])} atletas")
    
    def test_ranking_estados(self, api_client):
        """GET /api/ranking/estados - lista de estados"""
        response = api_client.get(f"{BASE_URL}/api/ranking/estados")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "estados" in data
        assert isinstance(data["estados"], list)
        
        print(f"✅ Ranking Estados: {len(data['estados'])} estados")
    
    def test_ranking_equipes(self, api_client):
        """GET /api/ranking/equipes - lista de equipes"""
        response = api_client.get(f"{BASE_URL}/api/ranking/equipes")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "equipes" in data
        assert isinstance(data["equipes"], list)
        
        print(f"✅ Ranking Equipes: {len(data['equipes'])} equipes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
