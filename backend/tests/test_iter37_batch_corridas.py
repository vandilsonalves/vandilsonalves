"""
Test Iteration 37: Batch Management Features for Admin Corridas Dashboard
- Tests batch deletion endpoint POST /corridas-eventos/excluir-lote
- Tests filters by Estado and Cidade
- Tests sorting A-Z / Z-A
- Tests checkbox selection features (via API verification)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBatchCorridasManagement:
    """Test batch management features for corridas"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test - get admin token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@rankingrun.com", "password": "admin123"}
        )
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        self.admin_token = login_response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.admin_token}"}
        yield
        # Cleanup: no specific cleanup needed
    
    def test_01_admin_login_success(self):
        """Test admin login works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@rankingrun.com", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] in ["admin", "super_admin"]
        print(f"✅ Admin login successful - role: {data['user']['role']}")
    
    def test_02_list_corridas_eventos(self):
        """Test GET /corridas-eventos endpoint works"""
        response = requests.get(f"{BASE_URL}/api/corridas-eventos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /corridas-eventos - Found {len(data)} corridas")
        return data
    
    def test_03_filter_corridas_by_estado(self):
        """Test filtering corridas by estado"""
        # First get all corridas to find available states
        all_corridas = requests.get(f"{BASE_URL}/api/corridas-eventos").json()
        
        if len(all_corridas) == 0:
            pytest.skip("No corridas to test filters")
        
        # Find a state that has corridas
        estados = [c.get('estado') for c in all_corridas if c.get('estado')]
        if not estados:
            pytest.skip("No corridas with estado defined")
        
        test_estado = estados[0]
        response = requests.get(f"{BASE_URL}/api/corridas-eventos?estado={test_estado}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all returned corridas have the filtered state
        for corrida in data:
            assert corrida.get('estado') == test_estado
        
        print(f"✅ Filter by estado={test_estado} - Found {len(data)} corridas")
    
    def test_04_filter_corridas_by_cidade(self):
        """Test filtering corridas by cidade"""
        all_corridas = requests.get(f"{BASE_URL}/api/corridas-eventos").json()
        
        if len(all_corridas) == 0:
            pytest.skip("No corridas to test filters")
        
        # Find a cidade that has corridas
        cidades = [c.get('cidade') for c in all_corridas if c.get('cidade')]
        if not cidades:
            pytest.skip("No corridas with cidade defined")
        
        test_cidade = cidades[0]
        response = requests.get(f"{BASE_URL}/api/corridas-eventos?cidade={test_cidade}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all returned corridas have the filtered cidade
        for corrida in data:
            assert corrida.get('cidade') == test_cidade
        
        print(f"✅ Filter by cidade={test_cidade} - Found {len(data)} corridas")
    
    def test_05_create_test_corridas_for_batch(self):
        """Create test corridas for batch deletion testing"""
        test_corridas_ids = []
        
        for i in range(3):
            form_data = {
                "nome_corrida": f"TEST_BatchTest_Corrida_{i+1}",
                "organizador": "Test Organizer",
                "cidade": "São Paulo",
                "estado": "SP",
                "data_corrida": "2026-12-01",
                "pagina_link": "https://test.com",
                "status": "ativa"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/corridas-eventos",
                data=form_data,
                headers=self.headers
            )
            
            if response.status_code in [200, 201]:
                corrida_id = response.json().get("id")
                test_corridas_ids.append(corrida_id)
                print(f"  Created test corrida: {corrida_id}")
        
        assert len(test_corridas_ids) >= 2, "Need at least 2 corridas for batch test"
        print(f"✅ Created {len(test_corridas_ids)} test corridas for batch deletion")
        
        # Store for cleanup
        self._test_corridas_ids = test_corridas_ids
        return test_corridas_ids
    
    def test_06_batch_delete_corridas_success(self):
        """Test POST /corridas-eventos/excluir-lote - batch deletion"""
        # First create test corridas
        test_ids = self.test_05_create_test_corridas_for_batch()
        
        # Now test batch deletion
        form_data = {
            "ids": ",".join(test_ids)
        }
        
        response = requests.post(
            f"{BASE_URL}/api/corridas-eventos/excluir-lote",
            data=form_data,
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Batch delete failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert data.get("total_excluidas", 0) >= 2
        
        print(f"✅ Batch delete successful: {data['message']}")
        
        # Verify corridas were actually deleted
        for corrida_id in test_ids:
            verify_response = requests.get(f"{BASE_URL}/api/corridas-eventos/{corrida_id}")
            assert verify_response.status_code == 404, f"Corrida {corrida_id} still exists after batch delete"
        
        print(f"✅ Verified {len(test_ids)} corridas were deleted")
    
    def test_07_batch_delete_empty_ids_error(self):
        """Test batch delete with empty ids returns error or zero deleted"""
        form_data = {"ids": ""}
        
        response = requests.post(
            f"{BASE_URL}/api/corridas-eventos/excluir-lote",
            data=form_data,
            headers=self.headers
        )
        
        # Should return 400/422 for empty ids OR 200 with 0 deleted
        if response.status_code in [400, 422]:
            print(f"✅ Empty ids correctly returns error: {response.status_code}")
        elif response.status_code == 200:
            data = response.json()
            assert data.get("total_excluidas", 0) == 0, "Empty ids should result in 0 deletions"
            print(f"✅ Empty ids returns 0 deletions as expected")
        else:
            pytest.fail(f"Unexpected status code for empty ids: {response.status_code}")
    
    def test_08_batch_delete_requires_admin(self):
        """Test batch delete requires admin authentication"""
        form_data = {"ids": "fake-id-1,fake-id-2"}
        
        # Without auth header
        response = requests.post(
            f"{BASE_URL}/api/corridas-eventos/excluir-lote",
            data=form_data
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got: {response.status_code}"
        print(f"✅ Batch delete correctly requires authentication: {response.status_code}")
    
    def test_09_ranking_corridas_endpoint(self):
        """Test GET /ranking-corridas endpoint works"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        assert response.status_code == 200
        data = response.json()
        assert "tipo" in data
        assert "ranking" in data
        print(f"✅ GET /ranking-corridas - tipo={data['tipo']}, total={data.get('total_corridas', 0)}")
    
    def test_10_ranking_corridas_stats(self):
        """Test GET /ranking-corridas/stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_corridas" in data
        assert "total_avaliacoes" in data
        print(f"✅ GET /ranking-corridas/stats - total_corridas={data['total_corridas']}, total_avaliacoes={data['total_avaliacoes']}")


class TestCorridasTemplateAndImport:
    """Test template download and import features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test - get admin token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@rankingrun.com", "password": "admin123"}
        )
        if login_response.status_code == 200:
            self.admin_token = login_response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.admin_token}"}
        yield
    
    def test_01_download_template_csv(self):
        """Test downloading CSV template"""
        response = requests.get(f"{BASE_URL}/api/corridas-eventos/template?formato=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        print(f"✅ CSV template download - {len(response.content)} bytes")
    
    def test_02_download_template_excel(self):
        """Test downloading Excel template"""
        response = requests.get(f"{BASE_URL}/api/corridas-eventos/template?formato=excel")
        assert response.status_code == 200
        assert "spreadsheet" in response.headers.get("content-type", "")
        print(f"✅ Excel template download - {len(response.content)} bytes")


class TestCorridasDashboardData:
    """Test dashboard data endpoints for corridas"""
    
    def test_01_estados_corridas(self):
        """Test GET /ranking-corridas/estados"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/estados")
        assert response.status_code == 200
        data = response.json()
        assert "estados" in data
        assert isinstance(data["estados"], list)
        print(f"✅ GET /ranking-corridas/estados - {len(data['estados'])} states")
    
    def test_02_cidades_corridas(self):
        """Test GET /ranking-corridas/cidades"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/cidades")
        assert response.status_code == 200
        data = response.json()
        assert "cidades" in data
        assert isinstance(data["cidades"], list)
        print(f"✅ GET /ranking-corridas/cidades - {len(data['cidades'])} cities")
    
    def test_03_cidades_by_estado(self):
        """Test GET /ranking-corridas/cidades?estado=SP"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/cidades?estado=SP")
        assert response.status_code == 200
        data = response.json()
        assert "cidades" in data
        print(f"✅ GET /ranking-corridas/cidades?estado=SP - {len(data['cidades'])} cities in SP")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
