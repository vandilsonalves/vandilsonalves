"""
Iteration 109: Premiação / Votação System Tests
Tests for the voting system "Prêmio Nacional Ranking Run"

Features tested:
- GET /api/premiacao/status - Public voting status
- GET /api/premiacao/categorias - Public categories list
- POST /api/premiacao/votar - Submit vote (authenticated)
- GET /api/premiacao/meus-votos - Get athlete's votes
- GET /api/premiacao/admin/config - Admin config
- POST /api/premiacao/admin/categorias - Create category (admin)
- POST /api/premiacao/admin/abrir - Open voting (admin)
- POST /api/premiacao/admin/fechar - Close voting (admin)
- GET /api/premiacao/admin/resultados - Admin results with details
- GET /api/premiacao/resultados-publicos - Public results (403 if voting open)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


class TestPremiacaoPublicEndpoints:
    """Tests for public premiação endpoints (no auth required)"""
    
    def test_get_status_votacao(self):
        """GET /api/premiacao/status returns voting status"""
        response = requests.get(f"{BASE_URL}/api/premiacao/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "votacao_aberta" in data, "Response should contain votacao_aberta"
        assert isinstance(data["votacao_aberta"], bool), "votacao_aberta should be boolean"
        
        # Should also have title info
        if data.get("titulo"):
            assert isinstance(data["titulo"], str)
        print(f"✓ Voting status: {'OPEN' if data['votacao_aberta'] else 'CLOSED'}")
    
    def test_get_categorias_publico(self):
        """GET /api/premiacao/categorias returns public categories"""
        response = requests.get(f"{BASE_URL}/api/premiacao/categorias")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        if len(data) > 0:
            cat = data[0]
            assert "id" in cat, "Category should have id"
            assert "nome" in cat, "Category should have nome"
            print(f"✓ Found {len(data)} categories")
        else:
            print("✓ No categories found (empty list)")
    
    def test_resultados_publicos_returns_403_when_voting_open(self):
        """GET /api/premiacao/resultados-publicos returns 403 if voting is open"""
        # First check if voting is open
        status_res = requests.get(f"{BASE_URL}/api/premiacao/status")
        status = status_res.json()
        
        response = requests.get(f"{BASE_URL}/api/premiacao/resultados-publicos")
        
        if status.get("votacao_aberta"):
            # If voting is open, should return 403
            assert response.status_code == 403, f"Expected 403 when voting open, got {response.status_code}"
            print("✓ Public results correctly blocked while voting is open")
        else:
            # If voting is closed, might return 200 or 403 (if never closed properly)
            assert response.status_code in [200, 403], f"Expected 200 or 403, got {response.status_code}"
            print(f"✓ Public results endpoint returned {response.status_code} (voting closed)")


class TestPremiacaoAtletaEndpoints:
    """Tests for athlete voting endpoints (requires auth)"""
    
    @pytest.fixture
    def atleta_token(self):
        """Get athlete authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Could not authenticate athlete: {response.text}")
        return response.json().get("token")
    
    def test_get_meus_votos_authenticated(self, atleta_token):
        """GET /api/premiacao/meus-votos returns athlete's votes"""
        response = requests.get(
            f"{BASE_URL}/api/premiacao/meus-votos",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Athlete has {len(data)} votes")
    
    def test_get_meus_votos_unauthenticated(self):
        """GET /api/premiacao/meus-votos returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/premiacao/meus-votos")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Meus votos correctly requires authentication")
    
    def test_votar_unauthenticated(self):
        """POST /api/premiacao/votar returns 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/premiacao/votar", json={
            "categoria_id": "test",
            "nome_indicado": "Test Nominee"
        })
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Voting correctly requires authentication")
    
    def test_votar_authenticated(self, atleta_token):
        """POST /api/premiacao/votar submits a vote when voting is open"""
        # First check if voting is open
        status_res = requests.get(f"{BASE_URL}/api/premiacao/status")
        status = status_res.json()
        
        if not status.get("votacao_aberta"):
            pytest.skip("Voting is closed, cannot test vote submission")
        
        # Get a category to vote on
        cats_res = requests.get(f"{BASE_URL}/api/premiacao/categorias")
        cats = cats_res.json()
        
        if not cats:
            pytest.skip("No categories available for voting")
        
        cat_id = cats[0]["id"]
        test_nominee = f"Test Nominee {uuid.uuid4().hex[:6]}"
        
        response = requests.post(
            f"{BASE_URL}/api/premiacao/votar",
            json={
                "categoria_id": cat_id,
                "nome_indicado": test_nominee,
                "link_indicado": "@testnominee"
            },
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data, "Response should contain message"
        print(f"✓ Vote submitted successfully: {data['message']}")
    
    def test_votar_invalid_category(self, atleta_token):
        """POST /api/premiacao/votar returns 404 for invalid category"""
        # First check if voting is open
        status_res = requests.get(f"{BASE_URL}/api/premiacao/status")
        status = status_res.json()
        
        if not status.get("votacao_aberta"):
            pytest.skip("Voting is closed, cannot test invalid category")
        
        response = requests.post(
            f"{BASE_URL}/api/premiacao/votar",
            json={
                "categoria_id": "invalid_category_id_12345",
                "nome_indicado": "Test Nominee"
            },
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print("✓ Invalid category correctly returns 404")
    
    def test_votar_empty_nominee(self, atleta_token):
        """POST /api/premiacao/votar returns 400 for empty nominee name"""
        # First check if voting is open
        status_res = requests.get(f"{BASE_URL}/api/premiacao/status")
        status = status_res.json()
        
        if not status.get("votacao_aberta"):
            pytest.skip("Voting is closed, cannot test empty nominee")
        
        # Get a category
        cats_res = requests.get(f"{BASE_URL}/api/premiacao/categorias")
        cats = cats_res.json()
        
        if not cats:
            pytest.skip("No categories available")
        
        response = requests.post(
            f"{BASE_URL}/api/premiacao/votar",
            json={
                "categoria_id": cats[0]["id"],
                "nome_indicado": "   "  # Empty/whitespace
            },
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("✓ Empty nominee correctly returns 400")


class TestPremiacaoAdminEndpoints:
    """Tests for admin premiação endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Could not authenticate admin: {response.text}")
        return response.json().get("token")
    
    def test_get_admin_config(self, admin_token):
        """GET /api/premiacao/admin/config returns config (admin only)"""
        response = requests.get(
            f"{BASE_URL}/api/premiacao/admin/config",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "votacao_aberta" in data, "Config should have votacao_aberta"
        assert "titulo" in data or "id" in data, "Config should have titulo or id"
        print(f"✓ Admin config retrieved: votacao_aberta={data.get('votacao_aberta')}")
    
    def test_get_admin_config_unauthenticated(self):
        """GET /api/premiacao/admin/config returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/premiacao/admin/config")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Admin config correctly requires authentication")
    
    def test_get_admin_categorias(self, admin_token):
        """GET /api/premiacao/admin/categorias returns categories with vote counts"""
        response = requests.get(
            f"{BASE_URL}/api/premiacao/admin/categorias",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        if len(data) > 0:
            cat = data[0]
            assert "id" in cat, "Category should have id"
            assert "nome" in cat, "Category should have nome"
            assert "total_votos" in cat, "Admin categories should include total_votos"
            print(f"✓ Found {len(data)} categories with vote counts")
        else:
            print("✓ No categories found")
    
    def test_create_categoria(self, admin_token):
        """POST /api/premiacao/admin/categorias creates a new category"""
        test_name = f"TEST_Categoria_{uuid.uuid4().hex[:6]}"
        
        response = requests.post(
            f"{BASE_URL}/api/premiacao/admin/categorias",
            json={
                "nome": test_name,
                "descricao": "Test category for automated testing",
                "icone": "trophy"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain category id"
        assert data["nome"] == test_name, "Category name should match"
        print(f"✓ Category created: {data['id']}")
        
        # Cleanup: delete the test category
        delete_res = requests.delete(
            f"{BASE_URL}/api/premiacao/admin/categorias/{data['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if delete_res.status_code == 200:
            print(f"✓ Test category cleaned up")
    
    def test_get_admin_resultados(self, admin_token):
        """GET /api/premiacao/admin/resultados returns detailed results"""
        response = requests.get(
            f"{BASE_URL}/api/premiacao/admin/resultados",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        if len(data) > 0:
            result = data[0]
            assert "categoria" in result, "Result should have categoria"
            assert "total_votos" in result, "Result should have total_votos"
            assert "indicados" in result, "Result should have indicados list"
            print(f"✓ Admin results retrieved: {len(data)} categories")
        else:
            print("✓ No results yet (no categories)")
    
    def test_abrir_fechar_votacao(self, admin_token):
        """POST /api/premiacao/admin/abrir and /fechar toggle voting"""
        # Get current status
        config_res = requests.get(
            f"{BASE_URL}/api/premiacao/admin/config",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        current_status = config_res.json().get("votacao_aberta", False)
        
        if current_status:
            # If open, test closing
            response = requests.post(
                f"{BASE_URL}/api/premiacao/admin/fechar",
                json={},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            print("✓ Voting closed successfully")
            
            # Re-open for other tests
            reopen_res = requests.post(
                f"{BASE_URL}/api/premiacao/admin/abrir",
                json={},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert reopen_res.status_code == 200
            print("✓ Voting re-opened")
        else:
            # If closed, test opening
            response = requests.post(
                f"{BASE_URL}/api/premiacao/admin/abrir",
                json={},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            print("✓ Voting opened successfully")


class TestPremiacaoIntegration:
    """Integration tests for the full voting flow"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Could not authenticate admin: {response.text}")
        return response.json().get("token")
    
    @pytest.fixture
    def atleta_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Could not authenticate athlete: {response.text}")
        return response.json().get("token")
    
    def test_full_voting_flow(self, admin_token, atleta_token):
        """Test complete voting flow: create category -> vote -> check results"""
        # 1. Ensure voting is open
        requests.post(
            f"{BASE_URL}/api/premiacao/admin/abrir",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # 2. Create a test category
        test_cat_name = f"TEST_Integration_{uuid.uuid4().hex[:6]}"
        cat_res = requests.post(
            f"{BASE_URL}/api/premiacao/admin/categorias",
            json={"nome": test_cat_name, "descricao": "Integration test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert cat_res.status_code == 200
        cat_id = cat_res.json()["id"]
        print(f"✓ Created test category: {cat_id}")
        
        try:
            # 3. Vote as athlete
            test_nominee = f"Integration Nominee {uuid.uuid4().hex[:4]}"
            vote_res = requests.post(
                f"{BASE_URL}/api/premiacao/votar",
                json={
                    "categoria_id": cat_id,
                    "nome_indicado": test_nominee,
                    "link_indicado": "@integrationtest"
                },
                headers={"Authorization": f"Bearer {atleta_token}"}
            )
            assert vote_res.status_code == 200
            print(f"✓ Vote submitted for: {test_nominee}")
            
            # 4. Verify vote appears in meus-votos
            meus_votos_res = requests.get(
                f"{BASE_URL}/api/premiacao/meus-votos",
                headers={"Authorization": f"Bearer {atleta_token}"}
            )
            assert meus_votos_res.status_code == 200
            votos = meus_votos_res.json()
            vote_found = any(v["categoria_id"] == cat_id for v in votos)
            assert vote_found, "Vote should appear in meus-votos"
            print("✓ Vote verified in meus-votos")
            
            # 5. Verify vote appears in admin results
            results_res = requests.get(
                f"{BASE_URL}/api/premiacao/admin/resultados",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert results_res.status_code == 200
            results = results_res.json()
            cat_result = next((r for r in results if r["categoria"]["id"] == cat_id), None)
            assert cat_result is not None, "Category should appear in results"
            assert cat_result["total_votos"] >= 1, "Category should have at least 1 vote"
            print(f"✓ Admin results show {cat_result['total_votos']} vote(s)")
            
        finally:
            # Cleanup: delete test category
            delete_res = requests.delete(
                f"{BASE_URL}/api/premiacao/admin/categorias/{cat_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            if delete_res.status_code == 200:
                print("✓ Test category cleaned up")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
