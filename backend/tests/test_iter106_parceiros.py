# /app/backend/tests/test_iter106_parceiros.py
# Tests for Parceiros (Partners) CRUD and Export functionality

import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestParceirosPublic:
    """Public endpoint tests - no auth required"""
    
    def test_listar_parceiros_publico(self):
        """GET /api/parceiros - list partners (public)"""
        response = requests.get(f"{BASE_URL}/api/parceiros")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Public parceiros endpoint returned {len(data)} parceiros")
        
        # If there are parceiros, validate structure
        if len(data) > 0:
            parceiro = data[0]
            assert "id" in parceiro, "Parceiro should have 'id'"
            assert "nome" in parceiro, "Parceiro should have 'nome'"
            print(f"✓ First parceiro: {parceiro.get('nome', 'N/A')}")


class TestParceirosAdmin:
    """Admin endpoint tests - requires authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin and get token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin login failed - skipping admin tests")
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        print(f"✓ Admin login successful")
    
    def test_admin_listar_parceiros(self):
        """GET /api/admin/parceiros - list partners (admin)"""
        response = requests.get(f"{BASE_URL}/api/admin/parceiros", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Admin parceiros endpoint returned {len(data)} parceiros")
    
    def test_criar_parceiro_sem_imagem(self):
        """POST /api/admin/parceiros - create partner without image"""
        form_data = {
            "nome": "TEST_Parceiro_Sem_Imagem",
            "instagram": "https://instagram.com/test_parceiro",
            "site": "https://www.testparceiro.com.br"
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/parceiros",
            data=form_data,
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should have 'id'"
        assert data["nome"] == "TEST_Parceiro_Sem_Imagem"
        assert data["instagram"] == "https://instagram.com/test_parceiro"
        assert data["site"] == "https://www.testparceiro.com.br"
        print(f"✓ Created parceiro: {data['id']}")
        
        # Cleanup
        self._cleanup_parceiro(data["id"])
    
    def test_criar_parceiro_com_imagem(self):
        """POST /api/admin/parceiros - create partner with image"""
        # Create a simple test image (1x1 PNG)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            "imagem": ("test_image.png", io.BytesIO(png_data), "image/png")
        }
        form_data = {
            "nome": "TEST_Parceiro_Com_Imagem",
            "instagram": "https://instagram.com/test_img",
            "site": "https://www.testimg.com.br"
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/parceiros",
            data=form_data,
            files=files,
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert "imagem_url" in data
        assert data["imagem_url"].startswith("/api/uploads/parceiros/")
        print(f"✓ Created parceiro with image: {data['id']}, imagem_url: {data['imagem_url']}")
        
        # Verify image is accessible
        img_response = requests.get(f"{BASE_URL}{data['imagem_url']}")
        assert img_response.status_code == 200, f"Image not accessible: {img_response.status_code}"
        print(f"✓ Image accessible at {data['imagem_url']}")
        
        # Cleanup
        self._cleanup_parceiro(data["id"])
    
    def test_editar_parceiro(self):
        """PUT /api/admin/parceiros/{id} - edit partner"""
        # First create a parceiro
        create_response = requests.post(
            f"{BASE_URL}/api/admin/parceiros",
            data={"nome": "TEST_Parceiro_Edit", "instagram": "", "site": ""},
            headers=self.headers
        )
        assert create_response.status_code == 200
        parceiro_id = create_response.json()["id"]
        
        # Edit the parceiro
        edit_response = requests.put(
            f"{BASE_URL}/api/admin/parceiros/{parceiro_id}",
            data={
                "nome": "TEST_Parceiro_Editado",
                "instagram": "https://instagram.com/editado",
                "site": "https://www.editado.com.br"
            },
            headers=self.headers
        )
        assert edit_response.status_code == 200, f"Expected 200, got {edit_response.status_code}: {edit_response.text}"
        print(f"✓ Edited parceiro: {parceiro_id}")
        
        # Verify edit by listing
        list_response = requests.get(f"{BASE_URL}/api/admin/parceiros", headers=self.headers)
        parceiros = list_response.json()
        edited = next((p for p in parceiros if p["id"] == parceiro_id), None)
        assert edited is not None, "Edited parceiro not found"
        assert edited["nome"] == "TEST_Parceiro_Editado"
        print(f"✓ Verified edit: nome={edited['nome']}")
        
        # Cleanup
        self._cleanup_parceiro(parceiro_id)
    
    def test_deletar_parceiro(self):
        """DELETE /api/admin/parceiros/{id} - delete partner"""
        # First create a parceiro
        create_response = requests.post(
            f"{BASE_URL}/api/admin/parceiros",
            data={"nome": "TEST_Parceiro_Delete", "instagram": "", "site": ""},
            headers=self.headers
        )
        assert create_response.status_code == 200
        parceiro_id = create_response.json()["id"]
        
        # Delete the parceiro
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/parceiros/{parceiro_id}",
            headers=self.headers
        )
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        print(f"✓ Deleted parceiro: {parceiro_id}")
        
        # Verify deletion
        list_response = requests.get(f"{BASE_URL}/api/admin/parceiros", headers=self.headers)
        parceiros = list_response.json()
        deleted = next((p for p in parceiros if p["id"] == parceiro_id), None)
        assert deleted is None, "Parceiro should be deleted"
        print(f"✓ Verified deletion")
    
    def test_deletar_parceiro_inexistente(self):
        """DELETE /api/admin/parceiros/{id} - delete non-existent partner"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/parceiros/nonexistent123",
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Correctly returned 404 for non-existent parceiro")
    
    def test_upload_imagem_avulso(self):
        """POST /api/admin/parceiros/upload-imagem - standalone image upload"""
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            "imagem": ("test_upload.png", io.BytesIO(png_data), "image/png")
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/parceiros/upload-imagem",
            files=files,
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "imagem_url" in data
        assert data["imagem_url"].startswith("/api/uploads/parceiros/")
        print(f"✓ Uploaded image: {data['imagem_url']}")
        
        # Verify image is accessible
        img_response = requests.get(f"{BASE_URL}{data['imagem_url']}")
        assert img_response.status_code == 200
        print(f"✓ Uploaded image accessible")
    
    def test_export_excel(self):
        """GET /api/admin/parceiros/export-excel - export to Excel"""
        # Test with Bearer token
        response = requests.get(
            f"{BASE_URL}/api/admin/parceiros/export-excel",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers.get("Content-Type", "")
        assert len(response.content) > 0, "Excel file should not be empty"
        print(f"✓ Export Excel returned {len(response.content)} bytes")
        
        # Test with query param token
        response_query = requests.get(
            f"{BASE_URL}/api/admin/parceiros/export-excel?token={self.token}"
        )
        assert response_query.status_code == 200, f"Expected 200 with query token, got {response_query.status_code}"
        print(f"✓ Export Excel with query token also works")
    
    def test_export_excel_sem_auth(self):
        """GET /api/admin/parceiros/export-excel - should fail without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/parceiros/export-excel")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Export Excel correctly requires authentication")
    
    def _cleanup_parceiro(self, parceiro_id):
        """Helper to cleanup test parceiros"""
        try:
            requests.delete(
                f"{BASE_URL}/api/admin/parceiros/{parceiro_id}",
                headers=self.headers
            )
        except:
            pass


class TestParceirosDataPersistence:
    """Test data persistence - Create → GET verification"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin login failed")
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_and_verify_in_public_list(self):
        """Create parceiro and verify it appears in public list"""
        # Create
        create_response = requests.post(
            f"{BASE_URL}/api/admin/parceiros",
            data={
                "nome": "TEST_Parceiro_Persistence",
                "instagram": "https://instagram.com/persistence",
                "site": "https://www.persistence.com"
            },
            headers=self.headers
        )
        assert create_response.status_code == 200
        parceiro_id = create_response.json()["id"]
        
        # Verify in public list (ativo=True by default)
        public_response = requests.get(f"{BASE_URL}/api/parceiros")
        assert public_response.status_code == 200
        parceiros = public_response.json()
        found = next((p for p in parceiros if p["id"] == parceiro_id), None)
        assert found is not None, "Created parceiro should appear in public list"
        assert found["nome"] == "TEST_Parceiro_Persistence"
        print(f"✓ Created parceiro appears in public list")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/parceiros/{parceiro_id}", headers=self.headers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
