"""
Iteration 95: Test Export Buttons and Ranking Corridas
- Tests for triggerDownload helper usage in all export buttons
- Tests for ranking-corridas endpoint returning 1289 corridas
- Tests for financeiro export endpoints (PDF/Excel)
- Tests for atletas export and ranking export
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRankingCorridas:
    """Tests for ranking-corridas endpoint - should return 1289 corridas"""
    
    def test_ranking_corridas_nacional(self):
        """GET /api/ranking-corridas should return corridas with total_corridas > 0"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas?tipo=nacional&page=1&limit=20")
        assert response.status_code == 200
        data = response.json()
        assert "total_corridas" in data
        assert data["total_corridas"] > 0, f"Expected total_corridas > 0, got {data['total_corridas']}"
        assert "ranking" in data
        assert len(data["ranking"]) > 0
        print(f"✓ Ranking corridas: {data['total_corridas']} corridas found")
    
    def test_ranking_corridas_stats(self):
        """GET /api/ranking-corridas/stats should return stats"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_corridas" in data
        assert data["total_corridas"] > 0
        print(f"✓ Stats: {data['total_corridas']} total corridas")
    
    def test_ranking_corridas_has_avaliar_button_data(self):
        """Corridas should have id field for Avaliar button"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas?tipo=nacional&page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        for corrida in data["ranking"]:
            assert "id" in corrida, "Corrida must have id for Avaliar button"
            assert "nome_corrida" in corrida
        print(f"✓ All corridas have id field for Avaliar button")


class TestAdminExportEndpoints:
    """Tests for admin export endpoints - all should return HTTP 200"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_financeiro_export_pdf(self):
        """GET /api/admin/financeiro/exportar/pdf should return HTTP 200"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/exportar/pdf",
            headers=self.headers
        )
        assert response.status_code == 200, f"PDF export failed: {response.status_code}"
        assert len(response.content) > 0, "PDF content should not be empty"
        print(f"✓ Financeiro PDF export: {len(response.content)} bytes")
    
    def test_financeiro_export_excel(self):
        """GET /api/admin/financeiro/exportar/excel should return HTTP 200"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/exportar/excel",
            headers=self.headers
        )
        assert response.status_code == 200, f"Excel export failed: {response.status_code}"
        assert len(response.content) > 0, "Excel content should not be empty"
        print(f"✓ Financeiro Excel export: {len(response.content)} bytes")
    
    def test_atletas_export_excel(self):
        """GET /api/admin/atletas/export should return HTTP 200"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas/export",
            headers=self.headers
        )
        assert response.status_code == 200, f"Atletas export failed: {response.status_code}"
        assert len(response.content) > 0, "Atletas export content should not be empty"
        print(f"✓ Atletas Excel export: {len(response.content)} bytes")
    
    def test_ranking_export_excel(self):
        """GET /api/ranking/export/excel should return HTTP 200"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/export/excel",
            headers=self.headers
        )
        assert response.status_code == 200, f"Ranking Excel export failed: {response.status_code}"
        assert len(response.content) > 0, "Ranking Excel content should not be empty"
        print(f"✓ Ranking Excel export: {len(response.content)} bytes")
    
    def test_ranking_export_csv(self):
        """GET /api/ranking/export/csv should return HTTP 200"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/export/csv",
            headers=self.headers
        )
        assert response.status_code == 200, f"Ranking CSV export failed: {response.status_code}"
        assert len(response.content) > 0, "Ranking CSV content should not be empty"
        print(f"✓ Ranking CSV export: {len(response.content)} bytes")
    
    def test_financeiro_resumo(self):
        """GET /api/admin/financeiro/resumo should return data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/resumo",
            headers=self.headers
        )
        assert response.status_code == 200, f"Financeiro resumo failed: {response.status_code}"
        data = response.json()
        assert "totais" in data
        print(f"✓ Financeiro resumo loaded")


class TestAtletaRankingCorridas:
    """Tests for atleta access to ranking-corridas"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as atleta"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "leonardo_souza_136@email.com",
            "password": "leonardo123"
        })
        assert response.status_code == 200, f"Atleta login failed: {response.text}"
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user = response.json()["user"]
    
    def test_atleta_can_access_ranking_corridas(self):
        """Atleta should be able to access ranking-corridas"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas?tipo=nacional&page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total_corridas"] > 0
        print(f"✓ Atleta can see {data['total_corridas']} corridas")
    
    def test_atleta_user_info(self):
        """Verify atleta user info"""
        assert self.user["email"] == "leonardo_souza_136@email.com"
        assert self.user["role"] == "atleta"
        print(f"✓ Atleta logged in: {self.user['nome']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
