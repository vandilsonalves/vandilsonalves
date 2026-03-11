# /app/backend/tests/test_iter33_badges_gamification.py
# Iteration 33: Badges/Gamification System & Povao Result Submission Tests

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ATLETA_TOP_ID = "c71a1c91-0cf0-4d3f-a0f8-36863c35b43b"  # Aline Costa - 290 pontos
POVAO_USER_EMAIL = "gustavo_martins_121@email.com"
POVAO_USER_PASSWORD = "atleta123"
ADMIN_EMAIL = "admin@rankingrun.com"
ADMIN_PASSWORD = "admin123"


class TestBadgesListEndpoint:
    """Test /api/badges/lista endpoint - List all 13 badges"""
    
    def test_badges_lista_returns_all_13_badges(self):
        """Should return exactly 13 badges"""
        response = requests.get(f"{BASE_URL}/api/badges/lista")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["total"] == 13, f"Expected 13 badges, got {data['total']}"
        assert len(data["badges"]) == 13, f"Expected 13 badge items, got {len(data['badges'])}"
        print(f"✓ GET /api/badges/lista returns {data['total']} badges")
    
    def test_badges_lista_categories(self):
        """Should return 3 categories: performance, participacao, especial"""
        response = requests.get(f"{BASE_URL}/api/badges/lista")
        assert response.status_code == 200
        
        data = response.json()
        expected_categories = ["performance", "participacao", "especial"]
        assert data["categorias"] == expected_categories, f"Expected {expected_categories}, got {data['categorias']}"
        print(f"✓ Badges categories correct: {data['categorias']}")
    
    def test_badges_lista_structure(self):
        """Each badge should have required fields"""
        response = requests.get(f"{BASE_URL}/api/badges/lista")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["id", "nome", "descricao", "icone", "cor_primaria", "cor_secundaria", "categoria"]
        
        for badge in data["badges"]:
            for field in required_fields:
                assert field in badge, f"Badge missing field: {field}"
        
        print(f"✓ All badges have required fields: {required_fields}")
    
    def test_badges_lista_specific_badges(self):
        """Verify specific badges exist"""
        response = requests.get(f"{BASE_URL}/api/badges/lista")
        assert response.status_code == 200
        
        data = response.json()
        badge_ids = [b["id"] for b in data["badges"]]
        
        expected_badges = [
            "atleta_elite", "corredor_maratona", "top_10_mes", "podio", "rei_velocidade",
            "iniciante", "veterano", "maratonista", "lenda", "consistente",
            "embaixador", "influencer", "estrela_assessoria"
        ]
        
        for expected_id in expected_badges:
            assert expected_id in badge_ids, f"Badge {expected_id} not found"
        
        print(f"✓ All 13 expected badges found")


class TestBadgesAtletaEndpoint:
    """Test /api/badges/atleta/{atleta_id} endpoint"""
    
    def test_badges_atleta_for_top_athlete(self):
        """Atleta with 290+ points should have Atleta Elite badge"""
        response = requests.get(f"{BASE_URL}/api/badges/atleta/{ATLETA_TOP_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["atleta_id"] == ATLETA_TOP_ID
        assert data["atleta_nome"] == "Aline Costa"
        assert data["pontos_totais"] >= 100, f"Expected 100+ points, got {data['pontos_totais']}"
        print(f"✓ GET /api/badges/atleta/{ATLETA_TOP_ID[:8]}... returned athlete with {data['pontos_totais']} points")
    
    def test_atleta_elite_badge_conquistado(self):
        """Athlete with 100+ points should have Atleta Elite badge earned"""
        response = requests.get(f"{BASE_URL}/api/badges/atleta/{ATLETA_TOP_ID}")
        assert response.status_code == 200
        
        data = response.json()
        badges = data["badges"]
        
        atleta_elite = next((b for b in badges if b["id"] == "atleta_elite"), None)
        assert atleta_elite is not None, "Atleta Elite badge not found"
        assert atleta_elite["conquistado"] == True, "Atleta Elite should be earned (100+ points)"
        print(f"✓ Atleta Elite badge correctly marked as conquistado")
    
    def test_podio_badge_conquistado(self):
        """Athlete with top 3 placement should have Pódio badge"""
        response = requests.get(f"{BASE_URL}/api/badges/atleta/{ATLETA_TOP_ID}")
        assert response.status_code == 200
        
        data = response.json()
        badges = data["badges"]
        
        podio = next((b for b in badges if b["id"] == "podio"), None)
        assert podio is not None, "Pódio badge not found"
        assert podio["conquistado"] == True, "Pódio badge should be earned (top 3 placement)"
        print(f"✓ Pódio badge correctly marked as conquistado")
    
    def test_iniciante_badge_conquistado(self):
        """Athlete with 1+ races should have Iniciante badge"""
        response = requests.get(f"{BASE_URL}/api/badges/atleta/{ATLETA_TOP_ID}")
        assert response.status_code == 200
        
        data = response.json()
        badges = data["badges"]
        
        iniciante = next((b for b in badges if b["id"] == "iniciante"), None)
        assert iniciante is not None, "Iniciante badge not found"
        assert iniciante["conquistado"] == True, "Iniciante badge should be earned (1+ races)"
        print(f"✓ Iniciante badge correctly marked as conquistado")
    
    def test_badges_not_conquistado_correctly_marked(self):
        """Badges not earned should be marked as not conquistado"""
        response = requests.get(f"{BASE_URL}/api/badges/atleta/{ATLETA_TOP_ID}")
        assert response.status_code == 200
        
        data = response.json()
        badges = data["badges"]
        
        # Athlete with 8 corridas should NOT have veterano (10+) badge
        veterano = next((b for b in badges if b["id"] == "veterano"), None)
        assert veterano is not None, "Veterano badge not found"
        
        if data["total_corridas"] < 10:
            assert veterano["conquistado"] == False, "Veterano badge should NOT be earned (less than 10 races)"
            print(f"✓ Veterano badge correctly marked as NOT conquistado (only {data['total_corridas']} corridas)")
        else:
            print(f"⚠ Athlete has {data['total_corridas']} races, veterano check skipped")
    
    def test_badges_atleta_404_for_invalid_id(self):
        """Invalid atleta_id should return 404"""
        response = requests.get(f"{BASE_URL}/api/badges/atleta/invalid-id-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Invalid atleta_id returns 404")


class TestBadgesCardCompartilhamento:
    """Test /api/badges/atleta/{atleta_id}/card-compartilhamento endpoint"""
    
    def test_card_compartilhamento_success(self):
        """Should return card data for sharing"""
        response = requests.get(f"{BASE_URL}/api/badges/atleta/{ATLETA_TOP_ID}/card-compartilhamento")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "atleta" in data
        assert "stats" in data
        assert "badges" in data
        assert "texto_compartilhamento" in data
        assert "url_perfil" in data
        print(f"✓ Card compartilhamento endpoint returns all required fields")
    
    def test_card_compartilhamento_atleta_data(self):
        """Card should include atleta information"""
        response = requests.get(f"{BASE_URL}/api/badges/atleta/{ATLETA_TOP_ID}/card-compartilhamento")
        assert response.status_code == 200
        
        data = response.json()
        atleta = data["atleta"]
        assert atleta["nome"] == "Aline Costa"
        assert atleta["id"] == ATLETA_TOP_ID
        print(f"✓ Card compartilhamento includes correct atleta data")
    
    def test_card_compartilhamento_stats(self):
        """Card should include stats"""
        response = requests.get(f"{BASE_URL}/api/badges/atleta/{ATLETA_TOP_ID}/card-compartilhamento")
        assert response.status_code == 200
        
        data = response.json()
        stats = data["stats"]
        assert "pontos" in stats
        assert "total_corridas" in stats
        assert "total_badges" in stats
        assert stats["pontos"] >= 100  # Atleta Elite requirement
        print(f"✓ Card compartilhamento stats: {stats['pontos']} pontos, {stats['total_badges']} badges")


class TestPovaoResultSubmission:
    """Test result submission for Povão athletes (optional colocacao)"""
    
    @pytest.fixture
    def povao_token(self):
        """Login as Povão user and return token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": POVAO_USER_EMAIL,
            "password": POVAO_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not login as Povão user")
    
    def test_povao_user_login(self):
        """Povão user should be able to login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": POVAO_USER_EMAIL,
            "password": POVAO_USER_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "token" in data
        print(f"✓ Povão user login successful")
    
    def test_povao_user_modalidade(self, povao_token):
        """Povão user should have modalidade_usuario = povao_pace_livre"""
        headers = {"Authorization": f"Bearer {povao_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["modalidade_usuario"] == "povao_pace_livre", f"Expected povao_pace_livre, got {data.get('modalidade_usuario')}"
        print(f"✓ User modalidade correctly set to povao_pace_livre")
    
    def test_povao_result_submission_without_colocacao(self, povao_token):
        """Povão user should be able to submit result without colocacao"""
        headers = {"Authorization": f"Bearer {povao_token}"}
        
        response = requests.post(f"{BASE_URL}/api/resultados/submeter",
            headers=headers,
            data={
                "nome_competicao": "Teste Corrida Povão pytest",
                "cidade_competicao": "São Paulo",
                "estado_competicao": "SP",
                "data_competicao": "2026-03-09",
                "link_resultado": "https://example.com/resultado-teste",
                "distancia": "10KM"
                # NO colocacao or tempo - should use defaults
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data
        assert "id" in data
        print(f"✓ Povão result submission without colocacao successful")


class TestBadgesRanking:
    """Test /api/badges/ranking-badges endpoint"""
    
    def test_ranking_badges_endpoint(self):
        """Should return ranking of athletes by badge count"""
        response = requests.get(f"{BASE_URL}/api/badges/ranking-badges")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "ranking" in data
        assert "total_participantes" in data
        print(f"✓ Badges ranking endpoint working, {data['total_participantes']} participants")


class TestHealthAndBasicEndpoints:
    """Basic health checks"""
    
    def test_health_endpoint(self):
        """Health endpoint should return healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health endpoint: {data['status']}")
    
    def test_ranking_categoria_masculino(self):
        """Should return ranking for masculino category"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/masculino/M")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Ranking masculino returns {len(data)} athletes")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
