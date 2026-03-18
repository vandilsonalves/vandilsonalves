"""
Test Suite for Iteration 38 Bug Fixes:
1. Ranking Estadual filter - should return only assessorias from specified estado
2. POST /api/notificacoes/enviar - should allow dono_assessoria to send messages
3. is_dono field in atletas - assessoria details should include is_dono flag
4. whatsapp_link field - should be returned in assessoria details
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


# ==================== FIXTURES ====================

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@rankingrun.com",
        "password": "admin123"
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    # API returns 'token' instead of 'access_token'
    token = data.get("access_token") or data.get("token")
    assert token, f"No token in response. Keys: {list(data.keys())}"
    return token


@pytest.fixture(scope="module")
def authenticated_client(api_client, admin_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


# ==================== TEST: RANKING ESTADUAL FILTER ====================

class TestRankingEstadualFilter:
    """Tests for ranking estadual filter - should filter by estado AFTER aggregation"""

    def test_ranking_estadual_returns_only_specified_estado(self, api_client):
        """Test that ranking estadual returns only assessorias from the specified estado"""
        # Test with ES (Espírito Santo)
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual&estado=ES")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "ranking" in data, "Response should contain 'ranking' field"
        assert "tipo" in data, "Response should contain 'tipo' field"
        assert data["tipo"] == "estadual", f"Expected tipo 'estadual', got '{data['tipo']}'"
        
        # Verify all assessorias in ranking are from ES
        ranking = data.get("ranking", [])
        for assessoria in ranking:
            assert assessoria.get("estado") == "ES", \
                f"Assessoria '{assessoria.get('nome')}' has estado '{assessoria.get('estado')}', expected 'ES'"
        
        print(f"✓ Ranking estadual ES returned {len(ranking)} assessorias, all from ES")

    def test_ranking_estadual_with_different_estado(self, api_client):
        """Test ranking estadual with a different estado (SP)"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual&estado=SP")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        ranking = data.get("ranking", [])
        
        # Verify all assessorias in ranking are from SP
        for assessoria in ranking:
            assert assessoria.get("estado") == "SP", \
                f"Assessoria '{assessoria.get('nome')}' has estado '{assessoria.get('estado')}', expected 'SP'"
        
        print(f"✓ Ranking estadual SP returned {len(ranking)} assessorias, all from SP")

    def test_ranking_estadual_structure(self, api_client):
        """Test that ranking estadual has correct response structure"""
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual&estado=ES")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        assert "tipo" in data
        assert "periodo" in data
        assert "total_assessorias" in data
        assert "ranking" in data
        
        # If there are assessorias, check their structure
        if data["ranking"]:
            assessoria = data["ranking"][0]
            required_fields = ["nome", "estado", "cidade", "total_atletas", "pontos_total", "posicao", "selo"]
            for field in required_fields:
                assert field in assessoria, f"Missing field '{field}' in assessoria response"
        
        print(f"✓ Ranking estadual response structure is correct")


# ==================== TEST: NOTIFICACOES/ENVIAR ENDPOINT ====================

class TestNotificacoesEnviar:
    """Tests for POST /api/notificacoes/enviar endpoint"""

    def test_enviar_notificacao_without_auth_fails(self, api_client):
        """Test that sending notification without auth returns 401/403"""
        # Create a new session without auth headers
        clean_session = requests.Session()
        clean_session.headers.update({"Content-Type": "application/json"})
        
        response = clean_session.post(f"{BASE_URL}/api/notificacoes/enviar", json={
            "destinatarios": ["user123"],
            "mensagem": "Test message",
            "tipo": "mensagem_assessoria"
        })
        
        assert response.status_code in [401, 403], \
            f"Expected 401 or 403 without auth, got {response.status_code}"
        
        print(f"✓ Notification endpoint correctly requires authentication")

    def test_enviar_notificacao_endpoint_exists(self, api_client):
        """Test that the endpoint exists (even if auth fails)"""
        response = api_client.post(f"{BASE_URL}/api/notificacoes/enviar", json={
            "destinatarios": [],
            "mensagem": "Test",
            "tipo": "test"
        })
        
        # Should not be 404 - endpoint must exist
        assert response.status_code != 404, "Endpoint /api/notificacoes/enviar does not exist"
        
        print(f"✓ Endpoint /api/notificacoes/enviar exists (status: {response.status_code})")

    def test_enviar_notificacao_validates_empty_destinatarios(self, authenticated_client):
        """Test that endpoint validates empty destinatarios list"""
        response = authenticated_client.post(f"{BASE_URL}/api/notificacoes/enviar", json={
            "destinatarios": [],
            "mensagem": "Test message",
            "tipo": "mensagem_assessoria"
        })
        
        # Should return 400 for empty destinatarios
        assert response.status_code == 400, \
            f"Expected 400 for empty destinatarios, got {response.status_code}: {response.text}"
        
        print(f"✓ Endpoint correctly validates empty destinatarios")

    def test_enviar_notificacao_validates_empty_mensagem(self, authenticated_client):
        """Test that endpoint validates empty message"""
        response = authenticated_client.post(f"{BASE_URL}/api/notificacoes/enviar", json={
            "destinatarios": ["user123"],
            "mensagem": "   ",  # Empty/whitespace message
            "tipo": "mensagem_assessoria"
        })
        
        # Should return 400 for empty message
        assert response.status_code == 400, \
            f"Expected 400 for empty message, got {response.status_code}: {response.text}"
        
        print(f"✓ Endpoint correctly validates empty message")


# ==================== TEST: IS_DONO FIELD IN ATLETAS ====================

class TestIsDono:
    """Tests for is_dono field in assessoria atletas"""

    def test_assessoria_details_endpoint_works(self, api_client):
        """Test that assessoria details endpoint works"""
        # First get a list of assessorias to find one to test
        ranking_response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        
        assert ranking_response.status_code == 200, f"Failed to get ranking: {ranking_response.text}"
        
        ranking_data = ranking_response.json()
        if not ranking_data.get("ranking"):
            pytest.skip("No assessorias available for testing")
        
        # Get first assessoria name
        assessoria_nome = ranking_data["ranking"][0]["nome"]
        
        # Get details
        import urllib.parse
        encoded_nome = urllib.parse.quote(assessoria_nome)
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{encoded_nome}")
        
        assert response.status_code == 200, f"Failed to get assessoria details: {response.text}"
        
        data = response.json()
        assert "atletas" in data, "Response should contain 'atletas' field"
        
        print(f"✓ Assessoria details endpoint works for '{assessoria_nome}'")

    def test_atletas_contain_is_dono_field(self, api_client):
        """Test that atletas in assessoria details contain is_dono field"""
        # Get a list of assessorias
        ranking_response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        
        if ranking_response.status_code != 200:
            pytest.skip("Cannot get ranking list")
        
        ranking_data = ranking_response.json()
        if not ranking_data.get("ranking"):
            pytest.skip("No assessorias available")
        
        # Test multiple assessorias if available
        tested = 0
        for assessoria in ranking_data["ranking"][:5]:  # Test up to 5
            import urllib.parse
            encoded_nome = urllib.parse.quote(assessoria["nome"])
            response = api_client.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{encoded_nome}")
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            atletas = data.get("atletas", [])
            
            if atletas:
                for atleta in atletas:
                    assert "is_dono" in atleta, \
                        f"Atleta '{atleta.get('nome')}' missing 'is_dono' field in assessoria '{assessoria['nome']}'"
                tested += 1
                
                # Check if any atleta is marked as dono
                donos = [a for a in atletas if a.get("is_dono") == True]
                print(f"  - Assessoria '{assessoria['nome']}': {len(atletas)} atletas, {len(donos)} marked as dono")
        
        assert tested > 0, "No assessorias with atletas found to test"
        print(f"✓ is_dono field present in atletas for {tested} assessorias")


# ==================== TEST: WHATSAPP_LINK FIELD ====================

class TestWhatsappLink:
    """Tests for whatsapp_link field in assessoria details"""

    def test_whatsapp_link_field_returned(self, api_client):
        """Test that whatsapp_link field is returned in assessoria details"""
        # Get a list of assessorias
        ranking_response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        
        if ranking_response.status_code != 200:
            pytest.skip("Cannot get ranking list")
        
        ranking_data = ranking_response.json()
        if not ranking_data.get("ranking"):
            pytest.skip("No assessorias available")
        
        # Test first assessoria
        assessoria_nome = ranking_data["ranking"][0]["nome"]
        
        import urllib.parse
        encoded_nome = urllib.parse.quote(assessoria_nome)
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{encoded_nome}")
        
        assert response.status_code == 200, f"Failed to get assessoria details: {response.text}"
        
        data = response.json()
        
        # whatsapp_link should be present in the response (even if empty string)
        assert "whatsapp_link" in data, \
            f"Field 'whatsapp_link' not found in assessoria details response. Keys: {list(data.keys())}"
        
        print(f"✓ whatsapp_link field is present in assessoria details (value: '{data.get('whatsapp_link', '')}')")

    def test_assessoria_details_has_all_required_fields(self, api_client):
        """Test that assessoria details has all the expected fields"""
        # Get a list of assessorias
        ranking_response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        
        if ranking_response.status_code != 200:
            pytest.skip("Cannot get ranking list")
        
        ranking_data = ranking_response.json()
        if not ranking_data.get("ranking"):
            pytest.skip("No assessorias available")
        
        assessoria_nome = ranking_data["ranking"][0]["nome"]
        
        import urllib.parse
        encoded_nome = urllib.parse.quote(assessoria_nome)
        response = api_client.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{encoded_nome}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields for assessoria details
        required_fields = [
            "nome", "estado", "cidade", "total_atletas",
            "pontos_cadastro", "pontos_resultados", "pontos_total",
            "total_resultados", "total_primeiros", "total_podios",
            "posicao_nacional", "posicao_estadual", "selo", "atletas",
            "responsavel_nome", "responsavel_id", "mensagem_bio", 
            "foto_url", "whatsapp_link"  # New field
        ]
        
        missing_fields = [f for f in required_fields if f not in data]
        assert not missing_fields, f"Missing fields in assessoria details: {missing_fields}"
        
        print(f"✓ All required fields present in assessoria details including whatsapp_link")


# ==================== TEST: RELATORIOS ENDPOINT ====================

class TestRelatoriosAssessoria:
    """Tests for relatórios endpoint used by DonoAssessoriaDashboard"""

    def test_relatorios_endpoint_exists(self, authenticated_client):
        """Test that relatórios endpoint exists"""
        # Get a known equipe name first
        ranking_response = authenticated_client.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        
        if ranking_response.status_code != 200:
            pytest.skip("Cannot get ranking list")
        
        ranking_data = ranking_response.json()
        if not ranking_data.get("ranking"):
            pytest.skip("No assessorias available")
        
        assessoria_nome = ranking_data["ranking"][0]["nome"]
        
        import urllib.parse
        encoded_nome = urllib.parse.quote(assessoria_nome)
        
        response = authenticated_client.get(f"{BASE_URL}/api/dono-assessoria/relatorios/{encoded_nome}")
        
        # Should not be 404
        assert response.status_code != 404, \
            f"Relatórios endpoint does not exist. Status: {response.status_code}"
        
        print(f"✓ Relatórios endpoint exists (status: {response.status_code})")


# ==================== TEST: POSICAO ESTADUAL ====================

class TestPosicaoEstadual:
    """Tests for posição estadual calculation"""

    def test_posicao_estadual_in_assessoria_details(self, api_client):
        """Test that posicao_estadual is correctly calculated in assessoria details"""
        # Get a list of assessorias
        ranking_response = api_client.get(f"{BASE_URL}/api/liga-assessorias/ranking?tipo=nacional")
        
        if ranking_response.status_code != 200:
            pytest.skip("Cannot get ranking list")
        
        ranking_data = ranking_response.json()
        if not ranking_data.get("ranking"):
            pytest.skip("No assessorias available")
        
        # Find an assessoria with a known estado
        for assessoria in ranking_data["ranking"]:
            if assessoria.get("estado"):
                import urllib.parse
                encoded_nome = urllib.parse.quote(assessoria["nome"])
                estado = assessoria.get("estado")
                
                # Get assessoria details
                response = api_client.get(f"{BASE_URL}/api/liga-assessorias/assessoria/{encoded_nome}")
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                
                # posicao_estadual should be present and be a number or None
                assert "posicao_estadual" in data, "posicao_estadual field not in response"
                
                posicao_estadual = data.get("posicao_estadual")
                
                # If there's a posicao_estadual, verify it's correct by checking the estadual ranking
                if posicao_estadual is not None:
                    estadual_response = api_client.get(
                        f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual&estado={estado}"
                    )
                    
                    if estadual_response.status_code == 200:
                        estadual_data = estadual_response.json()
                        
                        # Find the assessoria in estadual ranking
                        found = None
                        for eq in estadual_data.get("ranking", []):
                            if eq["nome"] == assessoria["nome"]:
                                found = eq
                                break
                        
                        if found:
                            assert found["posicao"] == posicao_estadual, \
                                f"posicao_estadual mismatch: details says {posicao_estadual}, ranking says {found['posicao']}"
                            print(f"✓ Assessoria '{assessoria['nome']}' ({estado}): posição estadual {posicao_estadual} is correct")
                            return
        
        print("✓ posicao_estadual field test completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
