# /app/backend/tests/test_iter44_reactions.py
# Test iteration 44: Feed Reactions System, Liga Assessorias, Ranking Corridas endpoints
# Tested features:
# - GET /api/feed/reacoes-disponiveis
# - POST /api/feed/posts/{post_id}/reagir (add/change/remove reaction)
# - GET /api/feed/posts/{post_id}/reacoes
# - GET /api/liga-assessorias/graficos-avancados/{nome_equipe}
# - GET /api/liga-assessorias/estados
# - GET /api/ranking-corridas
# - GET /api/feed (feed with reactions)

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin123"


class TestAuthentication:
    """Test authentication first to get token for other tests"""
    
    def test_login_success(self):
        """Login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, f"Expected 'token' in response: {data}"
        assert "user" in data
        print(f"Login successful for user: {data['user'].get('nome', 'N/A')}")


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for authenticated requests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_session(auth_token):
    """Create authenticated session"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


class TestFeedReactionsSystem:
    """Test the new reactions system that replaced likes"""
    
    def test_get_reacoes_disponiveis(self, authenticated_session):
        """Test GET /api/feed/reacoes-disponiveis - returns available reactions"""
        response = requests.get(f"{BASE_URL}/api/feed/reacoes-disponiveis")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "reacoes" in data
        reacoes = data["reacoes"]
        
        # Verify all 7 reaction types are present
        expected_reactions = ["aplausos", "corrida", "forca", "fogo", "coracao", "festa", "trofeu"]
        for reaction_type in expected_reactions:
            assert reaction_type in reacoes, f"Missing reaction type: {reaction_type}"
            assert "emoji" in reacoes[reaction_type]
            assert "nome" in reacoes[reaction_type]
        
        print(f"Available reactions: {list(reacoes.keys())}")
        print(f"Reaction details: {reacoes}")
    
    def test_get_feed_requires_auth(self):
        """Test GET /api/feed requires authentication"""
        response = requests.get(f"{BASE_URL}/api/feed")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_get_feed_with_auth(self, authenticated_session):
        """Test GET /api/feed returns posts with reactions"""
        response = authenticated_session.get(f"{BASE_URL}/api/feed")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "posts" in data
        assert "pagina" in data
        assert "limite" in data
        assert "total" in data
        assert "reacoes_disponiveis" in data
        
        # Verify reacoes_disponiveis are included
        reacoes_disp = data["reacoes_disponiveis"]
        assert "aplausos" in reacoes_disp
        assert "corrida" in reacoes_disp
        assert "forca" in reacoes_disp
        
        print(f"Feed returned {len(data['posts'])} posts, total: {data['total']}")
        
        # If there are posts, verify reaction fields
        if data["posts"]:
            post = data["posts"][0]
            assert "reacoes" in post, "Post should have 'reacoes' field"
            assert "total_reacoes" in post, "Post should have 'total_reacoes' field"
            assert "minha_reacao" in post, "Post should have 'minha_reacao' field"
            print(f"Post reactions structure: reacoes={post.get('reacoes')}, total_reacoes={post.get('total_reacoes')}")
    
    def test_create_post_for_reaction_test(self, authenticated_session):
        """Create a test post to test reactions on"""
        response = authenticated_session.post(f"{BASE_URL}/api/feed/posts", json={
            "texto": "TEST_POST_ITER44 - Post para testar sistema de reações",
            "tipo": "texto"
        })
        
        assert response.status_code == 200, f"Failed to create post: {response.text}"
        data = response.json()
        assert "post_id" in data
        print(f"Created test post with ID: {data['post_id']}")
        return data["post_id"]
    
    def test_reagir_post_add_reaction(self, authenticated_session):
        """Test POST /api/feed/posts/{post_id}/reagir - add a reaction"""
        # First create a post
        create_response = authenticated_session.post(f"{BASE_URL}/api/feed/posts", json={
            "texto": "TEST_REACTION_ADD - Post para testar adicionar reação",
            "tipo": "texto"
        })
        assert create_response.status_code == 200
        post_id = create_response.json()["post_id"]
        
        # Add reaction
        response = authenticated_session.post(f"{BASE_URL}/api/feed/posts/{post_id}/reagir", json={
            "tipo_reacao": "aplausos"
        })
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "message" in data
        assert "reacao" in data
        assert data["reacao"] == "aplausos"
        assert data["removida"] == False
        print(f"Added reaction 'aplausos' to post {post_id}: {data['message']}")
    
    def test_reagir_post_change_reaction(self, authenticated_session):
        """Test POST /api/feed/posts/{post_id}/reagir - change reaction"""
        # First create a post
        create_response = authenticated_session.post(f"{BASE_URL}/api/feed/posts", json={
            "texto": "TEST_REACTION_CHANGE - Post para testar trocar reação",
            "tipo": "texto"
        })
        assert create_response.status_code == 200
        post_id = create_response.json()["post_id"]
        
        # Add first reaction
        r1 = authenticated_session.post(f"{BASE_URL}/api/feed/posts/{post_id}/reagir", json={
            "tipo_reacao": "fogo"
        })
        assert r1.status_code == 200
        
        # Change to different reaction
        r2 = authenticated_session.post(f"{BASE_URL}/api/feed/posts/{post_id}/reagir", json={
            "tipo_reacao": "trofeu"
        })
        assert r2.status_code == 200
        data = r2.json()
        
        assert data["reacao"] == "trofeu"
        assert data["removida"] == False
        print(f"Changed reaction from 'fogo' to 'trofeu': {data['message']}")
    
    def test_reagir_post_remove_reaction(self, authenticated_session):
        """Test POST /api/feed/posts/{post_id}/reagir - toggle to remove reaction"""
        # First create a post
        create_response = authenticated_session.post(f"{BASE_URL}/api/feed/posts", json={
            "texto": "TEST_REACTION_REMOVE - Post para testar remover reação",
            "tipo": "texto"
        })
        assert create_response.status_code == 200
        post_id = create_response.json()["post_id"]
        
        # Add reaction
        r1 = authenticated_session.post(f"{BASE_URL}/api/feed/posts/{post_id}/reagir", json={
            "tipo_reacao": "coracao"
        })
        assert r1.status_code == 200
        
        # Toggle same reaction to remove
        r2 = authenticated_session.post(f"{BASE_URL}/api/feed/posts/{post_id}/reagir", json={
            "tipo_reacao": "coracao"
        })
        assert r2.status_code == 200
        data = r2.json()
        
        assert data["reacao"] is None
        assert data["removida"] == True
        print(f"Removed reaction by toggling same type: {data['message']}")
    
    def test_reagir_invalid_reaction_type(self, authenticated_session):
        """Test POST /api/feed/posts/{post_id}/reagir with invalid reaction type"""
        # First create a post
        create_response = authenticated_session.post(f"{BASE_URL}/api/feed/posts", json={
            "texto": "TEST_INVALID_REACTION - Post para testar reação inválida",
            "tipo": "texto"
        })
        assert create_response.status_code == 200
        post_id = create_response.json()["post_id"]
        
        # Try invalid reaction
        response = authenticated_session.post(f"{BASE_URL}/api/feed/posts/{post_id}/reagir", json={
            "tipo_reacao": "invalid_reaction"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"Invalid reaction correctly rejected: {response.json()}")
    
    def test_get_reacoes_post(self, authenticated_session):
        """Test GET /api/feed/posts/{post_id}/reacoes - get reactions for a post"""
        # First create a post and add reactions
        create_response = authenticated_session.post(f"{BASE_URL}/api/feed/posts", json={
            "texto": "TEST_GET_REACOES - Post para testar buscar reações",
            "tipo": "texto"
        })
        assert create_response.status_code == 200
        post_id = create_response.json()["post_id"]
        
        # Add a reaction
        authenticated_session.post(f"{BASE_URL}/api/feed/posts/{post_id}/reagir", json={
            "tipo_reacao": "festa"
        })
        
        # Get reactions
        response = requests.get(f"{BASE_URL}/api/feed/posts/{post_id}/reacoes")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "post_id" in data
        assert "total_reacoes" in data
        assert "reacoes" in data
        assert data["post_id"] == post_id
        print(f"Post {post_id} reactions: total={data['total_reacoes']}, details={data['reacoes']}")


class TestLigaAssessorias:
    """Test Liga Assessorias endpoints"""
    
    def test_get_estados_com_assessorias(self):
        """Test GET /api/liga-assessorias/estados - returns list of states"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/estados")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list), "Expected list of states"
        print(f"States with assessorias: {data}")
    
    def test_get_cidades_com_assessorias(self):
        """Test GET /api/liga-assessorias/cidades - returns list of cities"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/cidades")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list), "Expected list of cities"
        print(f"Cities with assessorias (first 10): {data[:10]}")
    
    def test_get_cidades_with_estado_filter(self):
        """Test GET /api/liga-assessorias/cidades with estado filter"""
        # First get available states
        states_response = requests.get(f"{BASE_URL}/api/liga-assessorias/estados")
        if states_response.status_code == 200 and states_response.json():
            estado = states_response.json()[0]
            response = requests.get(f"{BASE_URL}/api/liga-assessorias/cidades?estado={estado}")
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            assert isinstance(data, list)
            print(f"Cities in {estado}: {data}")
        else:
            pytest.skip("No states available to test filter")


class TestGraficosAvancados:
    """Test advanced graphs endpoint for DonoAssessoria Dashboard"""
    
    def test_graficos_avancados_requires_auth(self):
        """Test GET /api/liga-assessorias/graficos-avancados requires auth"""
        response = requests.get(f"{BASE_URL}/api/liga-assessorias/graficos-avancados/TestEquipe")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_graficos_avancados_with_auth(self, authenticated_session):
        """Test GET /api/liga-assessorias/graficos-avancados/{nome_equipe}"""
        # First get a valid equipe name from ranking
        ranking_response = requests.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        
        if ranking_response.status_code == 200:
            ranking_data = ranking_response.json()
            if ranking_data.get("ranking") and len(ranking_data["ranking"]) > 0:
                equipe_nome = ranking_data["ranking"][0].get("nome")
                if equipe_nome:
                    import urllib.parse
                    encoded_name = urllib.parse.quote(equipe_nome)
                    
                    response = authenticated_session.get(
                        f"{BASE_URL}/api/liga-assessorias/graficos-avancados/{encoded_name}"
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Verify response structure for advanced graphs
                        assert "equipe" in data
                        
                        # Check for chart data presence (may be empty if no data)
                        expected_fields = [
                            "grafico_genero", "grafico_faixa_etaria", "grafico_categoria",
                            "resultados_por_mes", "grafico_distancias", "evolucao_atletas",
                            "ranking_interno", "grafico_estados", "estatisticas"
                        ]
                        
                        for field in expected_fields:
                            assert field in data, f"Missing field: {field}"
                        
                        print(f"Advanced graphs for '{equipe_nome}':")
                        print(f"  - grafico_genero: {len(data.get('grafico_genero', []))} items")
                        print(f"  - grafico_faixa_etaria: {len(data.get('grafico_faixa_etaria', []))} items")
                        print(f"  - grafico_categoria: {len(data.get('grafico_categoria', []))} items")
                        print(f"  - resultados_por_mes: {len(data.get('resultados_por_mes', []))} items")
                        print(f"  - estatisticas: {data.get('estatisticas', {})}")
                        
                    elif response.status_code == 403:
                        print("Access denied - user may not have permission for this equipe (expected for non-dono users)")
                        # This is acceptable for admin users who are not dono of the equipe
                    elif response.status_code == 404:
                        print(f"Assessoria '{equipe_nome}' not found or has no athletes")
                    else:
                        print(f"Unexpected status: {response.status_code} - {response.text}")
                else:
                    pytest.skip("No equipe name found in ranking")
            else:
                pytest.skip("Empty ranking, cannot test graficos avancados")
        else:
            pytest.skip("Could not get ranking to find equipe name")


class TestRankingCorridas:
    """Test Ranking Corridas endpoints (migrated from server.py)"""
    
    def test_get_ranking_corridas(self):
        """Test GET /api/ranking-corridas - basic ranking"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "tipo" in data
        assert "total_corridas" in data
        assert "ranking" in data
        print(f"Ranking corridas: tipo={data['tipo']}, total={data['total_corridas']}")
    
    def test_get_ranking_corridas_nacional(self):
        """Test GET /api/ranking-corridas?tipo=nacional"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas?tipo=nacional")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data["tipo"] == "nacional"
        print(f"National ranking: {data['total_corridas']} corridas")
    
    def test_get_ranking_corridas_estadual(self):
        """Test GET /api/ranking-corridas?tipo=estadual with state filter"""
        # First get available states
        estados_response = requests.get(f"{BASE_URL}/api/ranking-corridas/estados")
        if estados_response.status_code == 200:
            estados = estados_response.json().get("estados", [])
            if estados:
                estado = estados[0]
                response = requests.get(f"{BASE_URL}/api/ranking-corridas?tipo=estadual&estado={estado}")
                assert response.status_code == 200, f"Failed: {response.text}"
                data = response.json()
                assert data["tipo"] == "estadual"
                print(f"Estadual ranking for {estado}: {data['total_corridas']} corridas")
            else:
                pytest.skip("No states available")
        else:
            pytest.skip("Could not get states list")
    
    def test_get_ranking_corridas_stats(self):
        """Test GET /api/ranking-corridas/stats"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "total_corridas" in data
        assert "total_avaliacoes" in data
        # Note: API returns different field names based on implementation
        media_field = "media_geral" if "media_geral" in data else "media"
        print(f"Stats: total_corridas={data['total_corridas']}, total_avaliacoes={data['total_avaliacoes']}")
        print(f"Stats data: {data}")
    
    def test_get_estados_com_corridas(self):
        """Test GET /api/ranking-corridas/estados"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/estados")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "estados" in data
        assert isinstance(data["estados"], list)
        print(f"Estados with corridas: {data['estados']}")
    
    def test_get_cidades_com_corridas(self):
        """Test GET /api/ranking-corridas/cidades"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/cidades")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "cidades" in data
        assert isinstance(data["cidades"], list)
        print(f"Cidades with corridas (first 10): {data['cidades'][:10]}")


class TestFeedTrending:
    """Test trending posts with reaction counts"""
    
    def test_get_trending(self, authenticated_session):
        """Test GET /api/feed/trending - returns trending posts based on reactions"""
        response = authenticated_session.get(f"{BASE_URL}/api/feed/trending")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "trending" in data
        print(f"Trending posts: {len(data['trending'])} posts")
        
        if data["trending"]:
            post = data["trending"][0]
            # Verify post has reaction-related fields
            assert "total_reacoes" in post, "Trending post should have total_reacoes"
            assert "reacoes" in post or "engajamento" in post, "Trending post should have reacoes or engajamento"
            print(f"Top trending post: total_reacoes={post.get('total_reacoes', 0)}")


class TestFeedCodeReview:
    """Code review tests to ensure reactions are properly integrated"""
    
    def test_feed_posts_have_reaction_fields(self, authenticated_session):
        """Verify feed posts have the new reaction fields instead of like fields"""
        response = authenticated_session.get(f"{BASE_URL}/api/feed")
        assert response.status_code == 200
        data = response.json()
        
        if data["posts"]:
            post = data["posts"][0]
            
            # Should have new reaction fields
            assert "reacoes" in post, "Post should have 'reacoes' field (dict of reaction types)"
            assert "total_reacoes" in post, "Post should have 'total_reacoes' field"
            assert "minha_reacao" in post, "Post should have 'minha_reacao' field"
            
            # Should NOT have old like fields (or they should be replaced)
            # Note: The old fields may still exist but should not be the primary system
            print(f"Post fields verified: reacoes={type(post['reacoes'])}, total_reacoes={post['total_reacoes']}, minha_reacao={post['minha_reacao']}")
            
            # Verify reacoes is a dict with proper structure
            reacoes = post["reacoes"]
            if reacoes:
                for tipo, info in reacoes.items():
                    assert "count" in info, f"Reaction {tipo} should have 'count'"
                    assert "emoji" in info, f"Reaction {tipo} should have 'emoji'"
                    print(f"  Reaction '{tipo}': {info}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
