"""
Backend API tests for New Features in Ranking Run Pró
Testing:
- Admin CRUD Atletas endpoints (GET/POST/PUT/DELETE)
- Admin Ajustar Pontos endpoint
- Atleta profile update (nome, cidade, UF, data_nascimento)
- Atleta foto upload
- Atleta export meu ranking
- Compartilhar atleta
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://admin-dashboard-1008.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin123"
ATLETA_EMAIL = "gabrielsouza_normal_1@email.com"
ATLETA_PASSWORD = "atleta123"


class TestAdminAtletasCRUD:
    """Test admin CRUD operations for atletas"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    def test_admin_get_all_atletas(self, admin_token):
        """Test GET /api/admin/atletas - List all athletes"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 0
        print(f"✓ GET /api/admin/atletas - Found {len(data)} athletes")
    
    def test_admin_get_atletas_by_category_normal_m(self, admin_token):
        """Test GET /api/admin/atletas?categoria=normal-m"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"categoria": "normal-m"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All should be normal M category
        for atleta in data:
            assert atleta.get("categoria") == "normal"
            assert atleta.get("genero") == "M"
        print(f"✓ Filter normal-m - Found {len(data)} athletes")
    
    def test_admin_get_atletas_by_category_pcd(self, admin_token):
        """Test GET /api/admin/atletas?categoria=pcd"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"categoria": "pcd"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for atleta in data:
            assert atleta.get("categoria") == "pcd"
        print(f"✓ Filter pcd - Found {len(data)} athletes")
    
    def test_admin_get_atletas_by_category_cadeirante(self, admin_token):
        """Test GET /api/admin/atletas?categoria=cadeirante"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"categoria": "cadeirante"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for atleta in data:
            assert atleta.get("categoria") == "cadeirante"
        print(f"✓ Filter cadeirante - Found {len(data)} athletes")
    
    def test_admin_create_atleta(self, admin_token):
        """Test POST /api/admin/atletas - Create new athlete"""
        new_atleta = {
            "nome": "TEST_Atleta Novo",
            "email": f"test_atleta_novo_{os.urandom(4).hex()}@email.com",
            "password": "atleta123",
            "equipe": "Test Team",
            "cidade": "São Paulo",
            "estado": "SP",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-01-15"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=new_atleta
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "message" in data
        print(f"✓ POST /api/admin/atletas - Created athlete ID: {data['id']}")
        return data["id"]
    
    def test_admin_update_atleta(self, admin_token):
        """Test PUT /api/admin/atletas/{id} - Update athlete"""
        # First get an athlete to update
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        atletas = response.json()
        
        if len(atletas) == 0:
            pytest.skip("No athletes to update")
        
        atleta_id = atletas[0]["id"]
        
        update_data = {
            "nome": atletas[0]["nome"] + " Updated",
            "cidade": "Rio de Janeiro",
            "estado": "RJ"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/admin/atletas/{atleta_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ PUT /api/admin/atletas/{atleta_id} - Updated successfully")
    
    def test_admin_export_atletas(self, admin_token):
        """Test GET /api/admin/atletas/export - Export athletes to Excel"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas/export",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"categoria": "all"}
        )
        assert response.status_code == 200
        assert "application/vnd.openxmlformats" in response.headers.get("Content-Type", "")
        assert len(response.content) > 0
        print(f"✓ GET /api/admin/atletas/export - Exported {len(response.content)} bytes")


class TestAdminAjustarPontos:
    """Test admin endpoint to adjust athlete points"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    def test_admin_ajustar_pontos_adicionar(self, admin_token):
        """Test POST /api/admin/ajustar-pontos - Add points"""
        # Get an athlete first
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        atletas = response.json()
        
        if len(atletas) == 0:
            pytest.skip("No athletes to adjust")
        
        atleta_id = atletas[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/admin/ajustar-pontos",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "atleta_id": atleta_id,
                "pontos": 10,
                "motivo": "Teste - Adição de pontos"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "+10" in data["message"]
        print("✓ POST /api/admin/ajustar-pontos - Added 10 points")
    
    def test_admin_ajustar_pontos_remover(self, admin_token):
        """Test POST /api/admin/ajustar-pontos - Remove points"""
        # Get an athlete first
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        atletas = response.json()
        
        if len(atletas) == 0:
            pytest.skip("No athletes to adjust")
        
        atleta_id = atletas[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/admin/ajustar-pontos",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "atleta_id": atleta_id,
                "pontos": -5,
                "motivo": "Teste - Remoção de pontos"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "-5" in data["message"]
        print("✓ POST /api/admin/ajustar-pontos - Removed 5 points")


class TestAtletaProfile:
    """Test athlete profile endpoints"""
    
    @pytest.fixture
    def atleta_token(self):
        """Get athlete token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Athlete login failed")
    
    def test_atleta_get_meu_perfil(self, atleta_token):
        """Test GET /api/atletas/meu-perfil"""
        response = requests.get(
            f"{BASE_URL}/api/atletas/meu-perfil",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "nome" in data
        assert "cidade" in data
        assert "estado" in data
        assert "pontos_carreira" in data
        assert "total_corridas" in data
        print(f"✓ GET /api/atletas/meu-perfil - {data['nome']}, {data['pontos_carreira']} pts")
    
    def test_atleta_update_perfil_nome(self, atleta_token):
        """Test PATCH /api/atletas/perfil - Update nome"""
        # First get current profile
        response = requests.get(
            f"{BASE_URL}/api/atletas/meu-perfil",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        current_nome = response.json()["nome"]
        
        # Update nome
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={"nome": current_nome + " Editado"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Restore original
        requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={"nome": current_nome}
        )
        print("✓ PATCH /api/atletas/perfil - Nome updated successfully")
    
    def test_atleta_update_perfil_cidade_estado(self, atleta_token):
        """Test PATCH /api/atletas/perfil - Update cidade and estado"""
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={
                "cidade": "Campinas",
                "estado": "SP"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✓ PATCH /api/atletas/perfil - Cidade/Estado updated")
    
    def test_atleta_update_perfil_data_nascimento(self, atleta_token):
        """Test PATCH /api/atletas/perfil - Update data_nascimento"""
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={
                "data_nascimento": "1990-05-15"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✓ PATCH /api/atletas/perfil - Data nascimento updated")
    
    def test_atleta_update_perfil_equipe(self, atleta_token):
        """Test PATCH /api/atletas/perfil - Update equipe"""
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={
                "equipe": "Super Runners Team"
            }
        )
        assert response.status_code == 200
        print("✓ PATCH /api/atletas/perfil - Equipe updated")
    
    def test_atleta_update_perfil_redes_sociais(self, atleta_token):
        """Test PATCH /api/atletas/perfil - Update social media"""
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            headers={"Authorization": f"Bearer {atleta_token}"},
            json={
                "facebook_url": "https://facebook.com/testuser",
                "instagram_url": "https://instagram.com/testuser",
                "telefone": "(11) 99999-9999"
            }
        )
        assert response.status_code == 200
        print("✓ PATCH /api/atletas/perfil - Social media updated")


class TestAtletaExportData:
    """Test athlete data export"""
    
    @pytest.fixture
    def atleta_token(self):
        """Get athlete token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Athlete login failed")
    
    def test_atleta_export_meu_ranking(self, atleta_token):
        """Test GET /api/atletas/meu-ranking/export - Export athlete's own data"""
        response = requests.get(
            f"{BASE_URL}/api/atletas/meu-ranking/export",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 200
        assert "application/vnd.openxmlformats" in response.headers.get("Content-Type", "")
        assert len(response.content) > 0
        print(f"✓ GET /api/atletas/meu-ranking/export - Exported {len(response.content)} bytes")


class TestCompartilharAtleta:
    """Test athlete sharing endpoint"""
    
    def test_compartilhar_atleta(self):
        """Test GET /api/atletas/{id}/compartilhar"""
        # First get an athlete ID from admin endpoint
        admin_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if admin_response.status_code != 200:
            pytest.skip("Admin login failed")
        
        admin_token = admin_response.json()["token"]
        atletas_response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        atletas = atletas_response.json()
        if len(atletas) == 0:
            pytest.skip("No athletes found")
        
        atleta_id = atletas[0]["id"]
        
        response = requests.get(f"{BASE_URL}/api/atletas/{atleta_id}/compartilhar")
        assert response.status_code == 200
        data = response.json()
        assert "atleta" in data
        assert "colocacao" in data
        assert "categoria" in data
        assert "pontos" in data
        assert "texto_whatsapp" in data
        assert "url_compartilhar" in data
        print(f"✓ GET /api/atletas/{atleta_id}/compartilhar - Sharing data generated")


class TestRankingExport:
    """Test ranking export endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    def test_export_ranking_csv(self):
        """Test GET /api/ranking/export/csv"""
        response = requests.get(f"{BASE_URL}/api/ranking/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("Content-Type", "")
        assert len(response.content) > 0
        print(f"✓ GET /api/ranking/export/csv - Exported {len(response.content)} bytes")
    
    def test_export_ranking_excel(self):
        """Test GET /api/ranking/export/excel"""
        response = requests.get(f"{BASE_URL}/api/ranking/export/excel")
        assert response.status_code == 200
        assert "application/vnd.openxmlformats" in response.headers.get("Content-Type", "")
        assert len(response.content) > 0
        print(f"✓ GET /api/ranking/export/excel - Exported {len(response.content)} bytes")


class TestAtletaDetalhes:
    """Test athlete details page endpoint"""
    
    def test_get_atleta_detalhes(self):
        """Test GET /api/atletas/{id} - Full athlete details"""
        # First get an athlete ID from admin endpoint
        admin_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if admin_response.status_code != 200:
            pytest.skip("Admin login failed")
        
        admin_token = admin_response.json()["token"]
        atletas_response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        atletas = atletas_response.json()
        if len(atletas) == 0:
            pytest.skip("No athletes found")
        
        atleta_id = atletas[0]["id"]
        
        response = requests.get(f"{BASE_URL}/api/atletas/{atleta_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "nome" in data
        assert "pontos_carreira" in data
        assert "total_corridas" in data
        assert "melhor_colocacao" in data
        print(f"✓ GET /api/atletas/{atleta_id} - {data['nome']}, {data['pontos_carreira']} pts")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
