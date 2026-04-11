"""
Iteration 111: Multi-Premiação System Tests
Tests for the new multi-premiacao system with CRUD operations, voting, finalization, etc.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


class TestMultiPremiacaoBackend:
    """Tests for multi-premiacao backend endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_admin_token(self):
        """Get admin authentication token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def get_atleta_token(self):
        """Get atleta authentication token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None

    # ==================== PUBLIC ENDPOINTS ====================
    
    def test_get_status_backward_compat(self):
        """GET /api/premiacao/status returns premiacao_id for backward compatibility"""
        response = self.session.get(f"{BASE_URL}/api/premiacao/status")
        assert response.status_code == 200
        data = response.json()
        assert "votacao_aberta" in data
        assert "premiacao_id" in data  # New field for multi-premiacao
        assert "titulo" in data
        print(f"✓ GET /api/premiacao/status returns premiacao_id: {data.get('premiacao_id')}")
    
    def test_get_premiacoes_ativas(self):
        """GET /api/premiacao/ativas returns list of active premiacoes"""
        response = self.session.get(f"{BASE_URL}/api/premiacao/ativas")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/premiacao/ativas returns {len(data)} active premiacoes")
    
    def test_get_todas_premiacoes(self):
        """GET /api/premiacao/todas returns all premiacoes"""
        response = self.session.get(f"{BASE_URL}/api/premiacao/todas")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the migrated premiacao
        print(f"✓ GET /api/premiacao/todas returns {len(data)} premiacoes")
    
    def test_get_single_premiacao(self):
        """GET /api/premiacao/p/{id} returns single premiacao"""
        # First get list to find an ID
        response = self.session.get(f"{BASE_URL}/api/premiacao/todas")
        premiacoes = response.json()
        if len(premiacoes) > 0:
            prem_id = premiacoes[0]["id"]
            response = self.session.get(f"{BASE_URL}/api/premiacao/p/{prem_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == prem_id
            assert "titulo" in data
            assert "modo_votacao" in data
            print(f"✓ GET /api/premiacao/p/{prem_id} returns premiacao: {data.get('titulo')}")
        else:
            pytest.skip("No premiacoes found")
    
    def test_get_premiacao_categorias(self):
        """GET /api/premiacao/p/{id}/categorias returns categories"""
        response = self.session.get(f"{BASE_URL}/api/premiacao/todas")
        premiacoes = response.json()
        if len(premiacoes) > 0:
            prem_id = premiacoes[0]["id"]
            response = self.session.get(f"{BASE_URL}/api/premiacao/p/{prem_id}/categorias")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ GET /api/premiacao/p/{prem_id}/categorias returns {len(data)} categories")
        else:
            pytest.skip("No premiacoes found")
    
    def test_get_regulamento(self):
        """GET /api/premiacao/p/{id}/regulamento returns regulamento"""
        response = self.session.get(f"{BASE_URL}/api/premiacao/todas")
        premiacoes = response.json()
        if len(premiacoes) > 0:
            prem_id = premiacoes[0]["id"]
            response = self.session.get(f"{BASE_URL}/api/premiacao/p/{prem_id}/regulamento")
            assert response.status_code == 200
            data = response.json()
            assert "titulo" in data
            assert "regulamento" in data
            print(f"✓ GET /api/premiacao/p/{prem_id}/regulamento returns regulamento")
        else:
            pytest.skip("No premiacoes found")

    # ==================== ADMIN ENDPOINTS ====================
    
    def test_admin_list_premiacoes(self):
        """GET /api/premiacao/admin/premiacoes returns list with counts"""
        token = self.get_admin_token()
        assert token, "Admin login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "total_categorias" in data[0]
            assert "total_votos" in data[0]
        print(f"✓ GET /api/premiacao/admin/premiacoes returns {len(data)} premiacoes with counts")
    
    def test_admin_create_premiacao(self):
        """POST /api/premiacao/admin/premiacoes creates new premiacao"""
        token = self.get_admin_token()
        assert token, "Admin login failed"
        
        response = self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "titulo": "TEST_Premiacao_Iter111",
                "subtitulo": "Test Subtitle",
                "modo_votacao": "indicar",
                "regulamento": "Test regulamento text"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["titulo"] == "TEST_Premiacao_Iter111"
        assert data["modo_votacao"] == "indicar"
        self.created_prem_id = data["id"]
        print(f"✓ POST /api/premiacao/admin/premiacoes created: {data['id']}")
        return data["id"]
    
    def test_admin_update_premiacao(self):
        """PUT /api/premiacao/admin/premiacoes/{id} updates premiacao"""
        token = self.get_admin_token()
        assert token, "Admin login failed"
        
        # Create a test premiacao first
        create_resp = self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {token}"},
            json={"titulo": "TEST_Update_Iter111", "modo_votacao": "votar"}
        )
        prem_id = create_resp.json()["id"]
        
        # Update it
        response = self.session.put(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "titulo": "TEST_Updated_Title",
                "subtitulo": "Updated Subtitle",
                "modo_votacao": "indicar",
                "regulamento": "Updated regulamento"
            }
        )
        assert response.status_code == 200
        
        # Verify update
        get_resp = self.session.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        data = get_resp.json()
        assert data["titulo"] == "TEST_Updated_Title"
        print(f"✓ PUT /api/premiacao/admin/premiacoes/{prem_id} updated successfully")
        
        # Cleanup
        self.session.delete(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    def test_admin_create_category(self):
        """POST /api/premiacao/admin/premiacoes/{id}/categorias creates category"""
        token = self.get_admin_token()
        assert token, "Admin login failed"
        
        # Create a test premiacao first
        create_resp = self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {token}"},
            json={"titulo": "TEST_Cat_Iter111", "modo_votacao": "indicar"}
        )
        prem_id = create_resp.json()["id"]
        
        # Create category
        response = self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}/categorias",
            headers={"Authorization": f"Bearer {token}"},
            json={"nome": "TEST_Categoria_1", "descricao": "Test description"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["nome"] == "TEST_Categoria_1"
        print(f"✓ POST /api/premiacao/admin/premiacoes/{prem_id}/categorias created category")
        
        # Cleanup
        self.session.delete(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    def test_admin_list_categories(self):
        """GET /api/premiacao/admin/premiacoes/{id}/categorias lists categories"""
        token = self.get_admin_token()
        assert token, "Admin login failed"
        
        # Get existing premiacao
        response = self.session.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        premiacoes = response.json()
        if len(premiacoes) > 0:
            prem_id = premiacoes[0]["id"]
            response = self.session.get(
                f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}/categorias",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                assert "total_votos" in data[0]
            print(f"✓ GET /api/premiacao/admin/premiacoes/{prem_id}/categorias returns {len(data)} categories")
        else:
            pytest.skip("No premiacoes found")
    
    def test_admin_open_close_voting(self):
        """POST /api/premiacao/admin/premiacoes/{id}/abrir and /fechar"""
        token = self.get_admin_token()
        assert token, "Admin login failed"
        
        # Create a test premiacao
        create_resp = self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {token}"},
            json={"titulo": "TEST_OpenClose_Iter111", "modo_votacao": "indicar"}
        )
        prem_id = create_resp.json()["id"]
        
        # Open voting
        response = self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}/abrir",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Verify it's open
        get_resp = self.session.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_resp.json()["votacao_aberta"] == True
        print(f"✓ POST /api/premiacao/admin/premiacoes/{prem_id}/abrir opened voting")
        
        # Close voting
        response = self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}/fechar",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Verify it's closed
        get_resp = self.session.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_resp.json()["votacao_aberta"] == False
        print(f"✓ POST /api/premiacao/admin/premiacoes/{prem_id}/fechar closed voting")
        
        # Cleanup
        self.session.delete(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    def test_admin_delete_premiacao(self):
        """DELETE /api/premiacao/admin/premiacoes/{id} deletes premiacao"""
        token = self.get_admin_token()
        assert token, "Admin login failed"
        
        # Create a test premiacao
        create_resp = self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {token}"},
            json={"titulo": "TEST_Delete_Iter111", "modo_votacao": "indicar"}
        )
        prem_id = create_resp.json()["id"]
        
        # Delete it
        response = self.session.delete(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Verify it's deleted
        get_resp = self.session.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_resp.status_code == 404
        print(f"✓ DELETE /api/premiacao/admin/premiacoes/{prem_id} deleted successfully")
    
    def test_admin_export_excel(self):
        """GET /api/premiacao/admin/premiacoes/{id}/exportar-excel exports excel"""
        token = self.get_admin_token()
        assert token, "Admin login failed"
        
        # Get existing premiacao
        response = self.session.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        premiacoes = response.json()
        if len(premiacoes) > 0:
            prem_id = premiacoes[0]["id"]
            response = self.session.get(
                f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}/exportar-excel",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers.get("content-type", "")
            print(f"✓ GET /api/premiacao/admin/premiacoes/{prem_id}/exportar-excel returns Excel file")
        else:
            pytest.skip("No premiacoes found")

    # ==================== ATLETA VOTING ENDPOINTS ====================
    
    def test_atleta_get_meus_votos(self):
        """GET /api/premiacao/p/{id}/meus-votos returns athlete votes"""
        token = self.get_atleta_token()
        assert token, "Atleta login failed"
        
        # Get existing premiacao
        response = self.session.get(f"{BASE_URL}/api/premiacao/todas")
        premiacoes = response.json()
        if len(premiacoes) > 0:
            prem_id = premiacoes[0]["id"]
            response = self.session.get(
                f"{BASE_URL}/api/premiacao/p/{prem_id}/meus-votos",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ GET /api/premiacao/p/{prem_id}/meus-votos returns {len(data)} votes")
        else:
            pytest.skip("No premiacoes found")
    
    def test_atleta_get_voto_finalizado(self):
        """GET /api/premiacao/p/{id}/voto-finalizado returns finalization status"""
        token = self.get_atleta_token()
        assert token, "Atleta login failed"
        
        # Get existing premiacao
        response = self.session.get(f"{BASE_URL}/api/premiacao/todas")
        premiacoes = response.json()
        if len(premiacoes) > 0:
            prem_id = premiacoes[0]["id"]
            response = self.session.get(
                f"{BASE_URL}/api/premiacao/p/{prem_id}/voto-finalizado",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "finalizado" in data
            print(f"✓ GET /api/premiacao/p/{prem_id}/voto-finalizado returns finalizado: {data['finalizado']}")
        else:
            pytest.skip("No premiacoes found")
    
    def test_atleta_votar_requires_auth(self):
        """POST /api/premiacao/p/{id}/votar requires authentication"""
        response = self.session.get(f"{BASE_URL}/api/premiacao/todas")
        premiacoes = response.json()
        if len(premiacoes) > 0:
            prem_id = premiacoes[0]["id"]
            response = self.session.post(
                f"{BASE_URL}/api/premiacao/p/{prem_id}/votar",
                json={"premiacao_id": prem_id, "categoria_id": "test", "nome_indicado": "Test"}
            )
            assert response.status_code == 401 or response.status_code == 403
            print(f"✓ POST /api/premiacao/p/{prem_id}/votar requires authentication")
        else:
            pytest.skip("No premiacoes found")
    
    def test_atleta_votar_closed_premiacao(self):
        """POST /api/premiacao/p/{id}/votar returns 400 for closed premiacao"""
        token = self.get_atleta_token()
        assert token, "Atleta login failed"
        
        # Find a closed premiacao
        response = self.session.get(f"{BASE_URL}/api/premiacao/todas")
        premiacoes = response.json()
        closed_prem = next((p for p in premiacoes if not p.get("votacao_aberta")), None)
        
        if closed_prem:
            response = self.session.post(
                f"{BASE_URL}/api/premiacao/p/{closed_prem['id']}/votar",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "premiacao_id": closed_prem["id"],
                    "categoria_id": "test",
                    "nome_indicado": "Test"
                }
            )
            assert response.status_code == 400
            print(f"✓ POST /api/premiacao/p/{closed_prem['id']}/votar returns 400 for closed premiacao")
        else:
            pytest.skip("No closed premiacoes found")
    
    def test_atleta_finalizar_requires_all_votes(self):
        """POST /api/premiacao/p/{id}/finalizar requires all categories voted"""
        token = self.get_atleta_token()
        admin_token = self.get_admin_token()
        assert token, "Atleta login failed"
        assert admin_token, "Admin login failed"
        
        # Create a test premiacao with 2 categories
        create_resp = self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"titulo": "TEST_Finalizar_Iter111", "modo_votacao": "votar"}
        )
        prem_id = create_resp.json()["id"]
        
        # Add 2 categories
        self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}/categorias",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"nome": "Cat1"}
        )
        self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}/categorias",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"nome": "Cat2"}
        )
        
        # Open voting
        self.session.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}/abrir",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Try to finalize without voting
        response = self.session.post(
            f"{BASE_URL}/api/premiacao/p/{prem_id}/finalizar",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert "categorias" in response.json().get("detail", "").lower()
        print(f"✓ POST /api/premiacao/p/{prem_id}/finalizar requires all categories voted")
        
        # Cleanup
        self.session.delete(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_premiacoes(self):
        """Delete all TEST_ prefixed premiacoes"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        
        token = response.json().get("token")
        
        # Get all premiacoes
        response = session.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes",
            headers={"Authorization": f"Bearer {token}"}
        )
        premiacoes = response.json()
        
        # Delete TEST_ prefixed ones
        deleted = 0
        for prem in premiacoes:
            if prem.get("titulo", "").startswith("TEST_"):
                session.delete(
                    f"{BASE_URL}/api/premiacao/admin/premiacoes/{prem['id']}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                deleted += 1
        
        print(f"✓ Cleanup: Deleted {deleted} TEST_ premiacoes")
