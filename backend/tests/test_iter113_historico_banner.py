"""
Iteration 113: Testing Histórico de Votações and Banner Visibility
Features:
1. GET /api/premiacao/status with auth returns todas_finalizadas field
2. GET /api/premiacao/status without auth does NOT include todas_finalizadas
3. GET /api/premiacao/p/{id}/resultados-publicos returns results for CLOSED premiacao
4. GET /api/premiacao/p/{id}/resultados-publicos returns 403 for OPEN premiacao
5. GET /api/premiacao/todas returns all premiacoes (open + closed)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"

# Known premiacao IDs from context
OPEN_PREMIACAO_ID = "310d78e2"  # PRÊMIO NACIONAL, open
CLOSED_PREMIACAO_ID = "b347cb7a"  # Trofreu Brasil, CLOSED with data_encerramento


class TestPremiacaoStatusEndpoint:
    """Tests for GET /api/premiacao/status endpoint"""
    
    @pytest.fixture
    def atleta_token(self):
        """Get authentication token for atleta"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    
    def test_status_without_auth_no_todas_finalizadas(self):
        """GET /api/premiacao/status without auth should NOT include todas_finalizadas"""
        response = requests.get(f"{BASE_URL}/api/premiacao/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"Response without auth: {data}")
        
        # Should NOT have todas_finalizadas field when not authenticated
        assert "todas_finalizadas" not in data, "todas_finalizadas should NOT be present without auth"
        
        # Should have basic fields
        assert "votacao_aberta" in data, "votacao_aberta field should be present"
        print("PASS: Status without auth does not include todas_finalizadas")
    
    def test_status_with_auth_includes_todas_finalizadas(self, atleta_token):
        """GET /api/premiacao/status with auth should include todas_finalizadas field"""
        headers = {"Authorization": f"Bearer {atleta_token}"}
        response = requests.get(f"{BASE_URL}/api/premiacao/status", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"Response with auth: {data}")
        
        # Should have todas_finalizadas field when authenticated
        assert "todas_finalizadas" in data, "todas_finalizadas should be present with auth"
        
        # Atleta hasn't finalized any premiacao, so should be False
        assert data["todas_finalizadas"] == False, f"Expected todas_finalizadas=False, got {data['todas_finalizadas']}"
        
        # Should have basic fields
        assert "votacao_aberta" in data, "votacao_aberta field should be present"
        assert "titulo" in data, "titulo field should be present"
        print(f"PASS: Status with auth includes todas_finalizadas={data['todas_finalizadas']}")
    
    def test_status_returns_premiacao_id(self, atleta_token):
        """GET /api/premiacao/status should return premiacao_id"""
        headers = {"Authorization": f"Bearer {atleta_token}"}
        response = requests.get(f"{BASE_URL}/api/premiacao/status", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "premiacao_id" in data, "premiacao_id should be present"
        print(f"PASS: Status returns premiacao_id={data.get('premiacao_id')}")


class TestResultadosPublicosEndpoint:
    """Tests for GET /api/premiacao/p/{id}/resultados-publicos endpoint"""
    
    def test_resultados_publicos_open_premiacao_returns_403(self):
        """GET /api/premiacao/p/{id}/resultados-publicos for OPEN premiacao should return 403"""
        response = requests.get(f"{BASE_URL}/api/premiacao/p/{OPEN_PREMIACAO_ID}/resultados-publicos")
        
        # Should return 403 because votacao is still open
        assert response.status_code == 403, f"Expected 403 for open premiacao, got {response.status_code}"
        
        data = response.json()
        print(f"Response for open premiacao: {data}")
        assert "detail" in data, "Should have error detail"
        print(f"PASS: Open premiacao returns 403 with message: {data.get('detail')}")
    
    def test_resultados_publicos_closed_premiacao_returns_results(self):
        """GET /api/premiacao/p/{id}/resultados-publicos for CLOSED premiacao should return results"""
        response = requests.get(f"{BASE_URL}/api/premiacao/p/{CLOSED_PREMIACAO_ID}/resultados-publicos")
        
        # Should return 200 because votacao is closed with data_encerramento
        assert response.status_code == 200, f"Expected 200 for closed premiacao, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Response for closed premiacao: {data}")
        
        # Should have titulo and resultados
        assert "titulo" in data, "Should have titulo field"
        assert "resultados" in data, "Should have resultados field"
        assert isinstance(data["resultados"], list), "resultados should be a list"
        
        print(f"PASS: Closed premiacao returns results with titulo={data.get('titulo')}, {len(data.get('resultados', []))} categories")
    
    def test_resultados_publicos_nonexistent_premiacao_returns_404(self):
        """GET /api/premiacao/p/{id}/resultados-publicos for nonexistent premiacao should return 404"""
        response = requests.get(f"{BASE_URL}/api/premiacao/p/nonexistent123/resultados-publicos")
        
        assert response.status_code == 404, f"Expected 404 for nonexistent premiacao, got {response.status_code}"
        print("PASS: Nonexistent premiacao returns 404")


class TestTodasPremiacoesEndpoint:
    """Tests for GET /api/premiacao/todas endpoint"""
    
    def test_todas_returns_all_premiacoes(self):
        """GET /api/premiacao/todas should return all premiacoes (open + closed)"""
        response = requests.get(f"{BASE_URL}/api/premiacao/todas")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list"
        
        print(f"Total premiacoes returned: {len(data)}")
        
        # Check we have both open and closed premiacoes
        open_count = sum(1 for p in data if p.get("votacao_aberta", False))
        closed_count = sum(1 for p in data if not p.get("votacao_aberta", False))
        
        print(f"Open premiacoes: {open_count}, Closed premiacoes: {closed_count}")
        
        # Should have at least one of each based on context
        assert len(data) >= 2, f"Expected at least 2 premiacoes, got {len(data)}"
        
        # Verify structure of each premiacao
        for p in data:
            assert "id" in p, "Each premiacao should have id"
            assert "titulo" in p, "Each premiacao should have titulo"
            assert "votacao_aberta" in p, "Each premiacao should have votacao_aberta"
            print(f"  - {p.get('titulo')} (id={p.get('id')}, aberta={p.get('votacao_aberta')}, encerramento={p.get('data_encerramento')})")
        
        print("PASS: /todas returns all premiacoes with correct structure")
    
    def test_todas_includes_closed_with_data_encerramento(self):
        """GET /api/premiacao/todas should include closed premiacoes with data_encerramento"""
        response = requests.get(f"{BASE_URL}/api/premiacao/todas")
        assert response.status_code == 200
        
        data = response.json()
        
        # Find the closed premiacao (Trofreu Brasil)
        closed_prem = next((p for p in data if p.get("id") == CLOSED_PREMIACAO_ID), None)
        
        assert closed_prem is not None, f"Closed premiacao {CLOSED_PREMIACAO_ID} should be in the list"
        assert closed_prem.get("votacao_aberta") == False, "Closed premiacao should have votacao_aberta=False"
        assert closed_prem.get("data_encerramento") is not None, "Closed premiacao should have data_encerramento"
        
        print(f"PASS: Closed premiacao found: {closed_prem.get('titulo')} with data_encerramento={closed_prem.get('data_encerramento')}")


class TestAtivasEndpoint:
    """Tests for GET /api/premiacao/ativas endpoint (for comparison)"""
    
    def test_ativas_returns_only_open_premiacoes(self):
        """GET /api/premiacao/ativas should return only open premiacoes"""
        response = requests.get(f"{BASE_URL}/api/premiacao/ativas")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list"
        
        print(f"Active premiacoes returned: {len(data)}")
        
        # All should be open
        for p in data:
            assert p.get("votacao_aberta") == True, f"Premiacao {p.get('id')} should be open"
            print(f"  - {p.get('titulo')} (id={p.get('id')})")
        
        print("PASS: /ativas returns only open premiacoes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
