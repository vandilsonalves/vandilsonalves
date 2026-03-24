"""
Iteration 68: Engajamento Dashboard and AdminDashboard Cleanup Tests
Tests:
1. GET /api/admin/mensagens/engajamento - Dashboard de engajamento
2. GET /api/admin/stats - Admin stats (verify still working after cleanup)
3. GET /api/admin/mensagens/historico - Mensagens historico
4. POST /api/auth/login - Login endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://geo-filtered-admin.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    assert "token" in data
    return data["token"]


@pytest.fixture(scope="module")
def atleta_token():
    """Get atleta authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ATLETA_EMAIL, "password": ATLETA_PASSWORD}
    )
    assert response.status_code == 200, f"Atleta login failed: {response.text}"
    data = response.json()
    assert "token" in data
    return data["token"]


class TestEngajamentoDashboard:
    """Tests for the new Engajamento Dashboard endpoint"""
    
    def test_engajamento_endpoint_returns_200(self, admin_token):
        """Test that engajamento endpoint returns 200 OK"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mensagens/engajamento",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_engajamento_has_resumo(self, admin_token):
        """Test that engajamento response has resumo with required fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mensagens/engajamento",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        assert "resumo" in data, "Response missing 'resumo' field"
        resumo = data["resumo"]
        
        # Check required fields in resumo
        assert "total_mensagens" in resumo, "resumo missing 'total_mensagens'"
        assert "total_enviados" in resumo, "resumo missing 'total_enviados'"
        assert "total_lidas" in resumo, "resumo missing 'total_lidas'"
        assert "taxa_media_leitura" in resumo, "resumo missing 'taxa_media_leitura'"
        
        # Verify types
        assert isinstance(resumo["total_mensagens"], int)
        assert isinstance(resumo["total_enviados"], int)
        assert isinstance(resumo["total_lidas"], int)
        assert isinstance(resumo["taxa_media_leitura"], (int, float))
    
    def test_engajamento_has_melhor_mensagem(self, admin_token):
        """Test that engajamento response has melhor_mensagem field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mensagens/engajamento",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        assert "melhor_mensagem" in data, "Response missing 'melhor_mensagem' field"
        
        # melhor_mensagem can be null if no messages with >= 5 recipients
        if data["melhor_mensagem"] is not None:
            melhor = data["melhor_mensagem"]
            assert "id" in melhor
            assert "titulo" in melhor
            assert "taxa_leitura" in melhor
            assert "total_enviados" in melhor
            assert "total_lidas" in melhor
    
    def test_engajamento_has_timeline(self, admin_token):
        """Test that engajamento response has timeline array"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mensagens/engajamento",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        assert "timeline" in data, "Response missing 'timeline' field"
        assert isinstance(data["timeline"], list), "timeline should be a list"
        
        # If there are messages, check structure
        if len(data["timeline"]) > 0:
            item = data["timeline"][0]
            assert "id" in item
            assert "titulo" in item
            assert "data" in item
            assert "total_enviados" in item
            assert "total_lidas" in item
            assert "total_nao_lidas" in item
            assert "taxa_leitura" in item
            assert "filtro_tipo" in item
    
    def test_engajamento_requires_admin(self):
        """Test that engajamento endpoint requires admin authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/mensagens/engajamento")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
    
    def test_engajamento_rejects_atleta(self, atleta_token):
        """Test that engajamento endpoint rejects non-admin users"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mensagens/engajamento",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 403, f"Expected 403 for atleta, got {response.status_code}"


class TestExistingEndpoints:
    """Tests to verify existing endpoints still work after AdminDashboard cleanup"""
    
    def test_admin_stats_endpoint(self, admin_token):
        """Test that /api/admin/stats still works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected fields
        assert "total_atletas" in data
        assert "total_corridas" in data
        assert "total_assessorias" in data
    
    def test_mensagens_historico_endpoint(self, admin_token):
        """Test that /api/admin/mensagens/historico still works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mensagens/historico",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "mensagens" in data
        assert isinstance(data["mensagens"], list)
    
    def test_login_admin(self):
        """Test admin login still works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
    
    def test_login_atleta(self):
        """Test atleta login still works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ATLETA_EMAIL, "password": ATLETA_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data


class TestEngajamentoDataIntegrity:
    """Tests for data integrity in engajamento endpoint"""
    
    def test_taxa_leitura_calculation(self, admin_token):
        """Test that taxa_leitura is calculated correctly"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mensagens/engajamento",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        for item in data["timeline"]:
            total = item["total_enviados"]
            lidas = item["total_lidas"]
            nao_lidas = item["total_nao_lidas"]
            taxa = item["taxa_leitura"]
            
            # Verify nao_lidas = total - lidas
            assert nao_lidas == total - lidas, f"nao_lidas mismatch: {nao_lidas} != {total} - {lidas}"
            
            # Verify taxa calculation (with tolerance for rounding)
            if total > 0:
                expected_taxa = round((lidas / total) * 100, 1)
                assert abs(taxa - expected_taxa) < 0.2, f"taxa mismatch: {taxa} != {expected_taxa}"
    
    def test_resumo_totals_match_timeline(self, admin_token):
        """Test that resumo totals match sum of timeline"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mensagens/engajamento",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        resumo = data["resumo"]
        timeline = data["timeline"]
        
        # Sum up timeline totals
        sum_enviados = sum(item["total_enviados"] for item in timeline)
        sum_lidas = sum(item["total_lidas"] for item in timeline)
        
        assert resumo["total_enviados"] == sum_enviados, f"total_enviados mismatch: {resumo['total_enviados']} != {sum_enviados}"
        assert resumo["total_lidas"] == sum_lidas, f"total_lidas mismatch: {resumo['total_lidas']} != {sum_lidas}"
        assert resumo["total_mensagens"] == len(timeline), f"total_mensagens mismatch: {resumo['total_mensagens']} != {len(timeline)}"
