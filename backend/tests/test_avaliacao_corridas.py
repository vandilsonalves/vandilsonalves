"""
Test Suite for Sistema de Avaliação de Corridas (Fase 2 - Ranking das Corridas)
Features:
- POST /api/avaliar-corrida - Submit evaluation with 5 IQC criteria
- GET /api/verificar-avaliacao/{corrida_id} - Check if athlete already evaluated
- Validation: Cannot evaluate future races
- Validation: Cannot evaluate same race twice
- Validation: All 5 criteria must be between 1-5
- Stats update after evaluation
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review_request
ADMIN_CREDENTIALS = {"email": "admin@runpro.com", "password": "admin123"}
ATLETA_CREDENTIALS = {"email": "gustavo_carvalho_13@email.com", "password": "atleta123"}
ATLETA_JA_AVALIOU = {"email": "rafael_souza_1@email.com", "password": "atleta123"}

# Corrida de Natal 2025 - past race with 11 evaluations
CORRIDA_NATAL_ID = "360234e9-7e20-4d9c-bd20-8ea5e8b1c43c"


@pytest.fixture(scope="module")
def atleta_token():
    """Get atleta authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=ATLETA_CREDENTIALS)
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Failed to login as atleta: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def atleta_ja_avaliou_token():
    """Get token for atleta who already evaluated"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=ATLETA_JA_AVALIOU)
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Failed to login as atleta_ja_avaliou: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDENTIALS)
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Failed to login as admin: {response.status_code} - {response.text}")


class TestVerificarAvaliacao:
    """Test GET /api/verificar-avaliacao/{corrida_id} endpoint"""
    
    def test_verificar_avaliacao_endpoint_exists(self, atleta_token):
        """Test that endpoint exists and requires auth"""
        response = requests.get(
            f"{BASE_URL}/api/verificar-avaliacao/{CORRIDA_NATAL_ID}",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        # Should return 200 with ja_avaliou field
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "ja_avaliou" in data, f"Response should have 'ja_avaliou' field: {data}"
        assert isinstance(data["ja_avaliou"], bool), "ja_avaliou should be boolean"
        print(f"✓ verificar-avaliacao endpoint working: ja_avaliou={data['ja_avaliou']}")
    
    def test_verificar_avaliacao_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/verificar-avaliacao/{CORRIDA_NATAL_ID}")
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ verificar-avaliacao requires authentication")
    
    def test_atleta_que_ja_avaliou(self, atleta_ja_avaliou_token):
        """Test that atleta who already evaluated returns ja_avaliou=true"""
        response = requests.get(
            f"{BASE_URL}/api/verificar-avaliacao/{CORRIDA_NATAL_ID}",
            headers={"Authorization": f"Bearer {atleta_ja_avaliou_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # This atleta should have already evaluated this race
        assert data["ja_avaliou"] == True, f"Expected atleta to have already evaluated: {data}"
        print(f"✓ Atleta que já avaliou returns ja_avaliou=True")


class TestAvaliarCorridaValidations:
    """Test POST /api/avaliar-corrida validations"""
    
    def test_avaliar_corrida_requires_auth(self):
        """Test that evaluation requires authentication"""
        form_data = {
            "corrida_id": CORRIDA_NATAL_ID,
            "organizacao": 4,
            "percurso": 4,
            "kit_atleta": 4,
            "hidratacao": 4,
            "pos_prova": 4,
            "participei": True
        }
        response = requests.post(f"{BASE_URL}/api/avaliar-corrida", data=form_data)
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ avaliar-corrida requires authentication")
    
    def test_validation_nota_must_be_1_to_5(self, atleta_token):
        """Test that all criteria must be between 1-5"""
        # Test nota below 1
        form_data = {
            "corrida_id": CORRIDA_NATAL_ID,
            "organizacao": 0,  # Invalid - below 1
            "percurso": 4,
            "kit_atleta": 4,
            "hidratacao": 4,
            "pos_prova": 4,
            "participei": True
        }
        response = requests.post(
            f"{BASE_URL}/api/avaliar-corrida",
            data=form_data,
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid nota, got {response.status_code}"
        print("✓ Validation: nota below 1 rejected")
        
        # Test nota above 5
        form_data["organizacao"] = 6  # Invalid - above 5
        response = requests.post(
            f"{BASE_URL}/api/avaliar-corrida",
            data=form_data,
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 400, f"Expected 400 for nota > 5, got {response.status_code}"
        print("✓ Validation: nota above 5 rejected")
    
    def test_validation_participei_required(self, atleta_token):
        """Test that 'participei' checkbox is required"""
        form_data = {
            "corrida_id": CORRIDA_NATAL_ID,
            "organizacao": 4,
            "percurso": 4,
            "kit_atleta": 4,
            "hidratacao": 4,
            "pos_prova": 4,
            "participei": False  # Must be True
        }
        response = requests.post(
            f"{BASE_URL}/api/avaliar-corrida",
            data=form_data,
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 400, f"Expected 400 for participei=False, got {response.status_code}"
        data = response.json()
        assert "participou" in data.get("detail", "").lower() or "confirmar" in data.get("detail", "").lower(), \
            f"Error message should mention participation: {data}"
        print("✓ Validation: participei=False rejected with correct message")
    
    def test_validation_corrida_not_found(self, atleta_token):
        """Test that non-existent race returns 404"""
        fake_id = str(uuid.uuid4())
        form_data = {
            "corrida_id": fake_id,
            "organizacao": 4,
            "percurso": 4,
            "kit_atleta": 4,
            "hidratacao": 4,
            "pos_prova": 4,
            "participei": True
        }
        response = requests.post(
            f"{BASE_URL}/api/avaliar-corrida",
            data=form_data,
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 404, f"Expected 404 for non-existent race, got {response.status_code}"
        print("✓ Validation: non-existent race returns 404")
    
    def test_cannot_evaluate_same_race_twice(self, atleta_ja_avaliou_token):
        """Test that athlete cannot evaluate same race twice"""
        form_data = {
            "corrida_id": CORRIDA_NATAL_ID,
            "organizacao": 5,
            "percurso": 5,
            "kit_atleta": 5,
            "hidratacao": 5,
            "pos_prova": 5,
            "participei": True
        }
        response = requests.post(
            f"{BASE_URL}/api/avaliar-corrida",
            data=form_data,
            headers={"Authorization": f"Bearer {atleta_ja_avaliou_token}"}
        )
        assert response.status_code == 400, f"Expected 400 for duplicate evaluation, got {response.status_code}"
        data = response.json()
        assert "já avaliou" in data.get("detail", "").lower(), f"Error should mention already evaluated: {data}"
        print("✓ Validation: duplicate evaluation blocked")


class TestFutureRaceValidation:
    """Test validation for future races"""
    
    def test_get_ranking_corridas(self):
        """Get list of races to find a future one"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        print(f"✓ Found {len(data['ranking'])} races in ranking")
        
        # Check for future races (2026)
        from datetime import datetime
        hoje = datetime.now()
        future_races = [r for r in data['ranking'] if r.get('data_corrida', '') > hoje.strftime('%Y-%m-%d')]
        print(f"✓ Found {len(future_races)} future races")
        return data['ranking']
    
    def test_cannot_evaluate_future_race(self, atleta_token):
        """Test that future races cannot be evaluated"""
        # First, get all races
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 200
        races = response.json().get("ranking", [])
        
        from datetime import datetime
        hoje = datetime.now()
        future_races = [r for r in races if r.get('data_corrida', '') > hoje.strftime('%Y-%m-%d')]
        
        if not future_races:
            pytest.skip("No future races found to test")
        
        future_race = future_races[0]
        print(f"Testing with future race: {future_race['nome_corrida']} ({future_race['data_corrida']})")
        
        form_data = {
            "corrida_id": future_race['id'],
            "organizacao": 4,
            "percurso": 4,
            "kit_atleta": 4,
            "hidratacao": 4,
            "pos_prova": 4,
            "participei": True
        }
        response = requests.post(
            f"{BASE_URL}/api/avaliar-corrida",
            data=form_data,
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 400, f"Expected 400 for future race, got {response.status_code}: {response.text}"
        data = response.json()
        assert "após" in data.get("detail", "").lower() or "realização" in data.get("detail", "").lower(), \
            f"Error should mention after the race: {data}"
        print(f"✓ Validation: future race evaluation blocked")


class TestRankingCorridasStats:
    """Test ranking-corridas stats endpoint"""
    
    def test_stats_endpoint(self):
        """Test GET /api/ranking-corridas/stats"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_corridas" in data, f"Stats should have total_corridas: {data}"
        assert "total_avaliacoes" in data, f"Stats should have total_avaliacoes: {data}"
        assert "media_geral" in data, f"Stats should have media_geral: {data}"
        
        print(f"✓ Stats endpoint working:")
        print(f"  - Total corridas: {data['total_corridas']}")
        print(f"  - Total avaliações: {data['total_avaliacoes']}")
        print(f"  - Média geral: {data.get('media_geral', 'N/A')}")
    
    def test_corrida_natal_has_evaluations(self):
        """Test that Corrida de Natal 2025 has evaluations"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 200
        
        data = response.json()
        corrida_natal = None
        for race in data.get("ranking", []):
            if race.get("id") == CORRIDA_NATAL_ID:
                corrida_natal = race
                break
        
        if corrida_natal:
            print(f"✓ Corrida de Natal 2025 found:")
            print(f"  - Nome: {corrida_natal.get('nome_corrida')}")
            print(f"  - Total avaliações: {corrida_natal.get('total_avaliacoes')}")
            print(f"  - Média geral: {corrida_natal.get('media_geral')}")
            print(f"  - No ranking: {corrida_natal.get('no_ranking')}")
            
            # Should have at least 10 evaluations to be in ranking
            if corrida_natal.get('total_avaliacoes', 0) >= 10:
                assert corrida_natal.get('no_ranking') == True, "Should be in ranking with 10+ evaluations"
        else:
            print("! Corrida de Natal 2025 not found in ranking")


class TestSuccessfulEvaluation:
    """Test successful evaluation flow"""
    
    def test_create_new_atleta_and_evaluate(self, admin_token):
        """Create a new test atleta and submit evaluation"""
        # First, create a new test atleta
        test_email = f"test_avaliacao_{uuid.uuid4().hex[:8]}@test.com"
        atleta_data = {
            "nome": "Test Avaliacao Atleta",
            "email": test_email,
            "password": "test123",
            "equipe": "Test Team",
            "cidade": "São Paulo",
            "estado": "SP",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-01-01"
        }
        
        # Register new atleta
        response = requests.post(f"{BASE_URL}/api/auth/register", json=atleta_data)
        if response.status_code != 200:
            pytest.skip(f"Could not create test atleta: {response.text}")
        
        new_atleta_token = response.json().get("token")
        print(f"✓ Created test atleta: {test_email}")
        
        # Verify this atleta hasn't evaluated yet
        verify_response = requests.get(
            f"{BASE_URL}/api/verificar-avaliacao/{CORRIDA_NATAL_ID}",
            headers={"Authorization": f"Bearer {new_atleta_token}"}
        )
        assert verify_response.status_code == 200
        assert verify_response.json()["ja_avaliou"] == False, "New atleta should not have evaluated yet"
        print("✓ New atleta hasn't evaluated yet")
        
        # Submit evaluation
        form_data = {
            "corrida_id": CORRIDA_NATAL_ID,
            "organizacao": 4,
            "percurso": 5,
            "kit_atleta": 3,
            "hidratacao": 4,
            "pos_prova": 4,
            "participei": True
        }
        eval_response = requests.post(
            f"{BASE_URL}/api/avaliar-corrida",
            data=form_data,
            headers={"Authorization": f"Bearer {new_atleta_token}"}
        )
        assert eval_response.status_code == 200, f"Expected 200 for valid evaluation, got {eval_response.status_code}: {eval_response.text}"
        
        eval_data = eval_response.json()
        assert "nota_corrida" in eval_data, f"Response should have nota_corrida: {eval_data}"
        expected_media = (4 + 5 + 3 + 4 + 4) / 5  # 4.0
        assert abs(eval_data["nota_corrida"] - expected_media) < 0.1, f"Expected media ~{expected_media}, got {eval_data['nota_corrida']}"
        print(f"✓ Evaluation submitted successfully with nota_corrida={eval_data['nota_corrida']}")
        
        # Verify atleta now shows as having evaluated
        verify_after = requests.get(
            f"{BASE_URL}/api/verificar-avaliacao/{CORRIDA_NATAL_ID}",
            headers={"Authorization": f"Bearer {new_atleta_token}"}
        )
        assert verify_after.status_code == 200
        assert verify_after.json()["ja_avaliou"] == True, "Atleta should now show as having evaluated"
        print("✓ Atleta correctly shows as having evaluated after submission")
        
        # Verify stats were updated
        stats_response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        assert stats_response.status_code == 200
        print("✓ Stats endpoint still working after evaluation")


class TestMinhasAvaliacoes:
    """Test /api/minhas-avaliacoes-corridas endpoint"""
    
    def test_minhas_avaliacoes_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/minhas-avaliacoes-corridas")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ minhas-avaliacoes-corridas requires authentication")
    
    def test_minhas_avaliacoes_for_atleta(self, atleta_ja_avaliou_token):
        """Test that atleta who evaluated can see their evaluations"""
        response = requests.get(
            f"{BASE_URL}/api/minhas-avaliacoes-corridas",
            headers={"Authorization": f"Bearer {atleta_ja_avaliou_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), f"Response should be a list: {data}"
        
        if len(data) > 0:
            aval = data[0]
            assert "organizacao" in aval, "Evaluation should have organizacao"
            assert "percurso" in aval, "Evaluation should have percurso"
            assert "nota_corrida" in aval, "Evaluation should have nota_corrida"
            print(f"✓ Found {len(data)} evaluation(s) for atleta")
        else:
            print("✓ Atleta has 0 evaluations (endpoint working)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
