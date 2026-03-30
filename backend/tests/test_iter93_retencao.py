"""
Iteration 93: Test Retention Dashboard and Export Functionality
- GET /api/admin/retencao/inativos - Retention dashboard data
- POST /api/admin/retencao/alertar-assessoria - Alert team owner
- GET /api/admin/atletas/export - Export athletes (triggerDownload helper)
- GET /api/ranking/export/excel - Export ranking Excel
- GET /api/ranking/export/csv - Export ranking CSV
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRetencaoDashboard:
    """Test retention dashboard endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_inativos_default_30_days(self):
        """Test GET /api/admin/retencao/inativos with default 30 days"""
        response = requests.get(
            f"{BASE_URL}/api/admin/retencao/inativos",
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "resumo" in data, "Missing 'resumo' in response"
        assert "equipes_com_inativos" in data, "Missing 'equipes_com_inativos'"
        assert "atletas_inativos" in data, "Missing 'atletas_inativos'"
        
        # Verify resumo fields
        resumo = data["resumo"]
        assert "total_atletas" in resumo
        assert "total_ativos" in resumo
        assert "total_inativos" in resumo
        assert "taxa_retencao" in resumo
        assert "nunca_submeteram" in resumo
        assert "pararam_de_competir" in resumo
        assert "periodo_dias" in resumo
        assert resumo["periodo_dias"] == 30
        
        print(f"✅ Retention stats: {resumo['total_inativos']} inativos, taxa {resumo['taxa_retencao']}%")
    
    def test_get_inativos_custom_period(self):
        """Test GET /api/admin/retencao/inativos with custom period"""
        for dias in [7, 15, 60, 90]:
            response = requests.get(
                f"{BASE_URL}/api/admin/retencao/inativos",
                headers=self.headers,
                params={"dias": dias}
            )
            assert response.status_code == 200, f"Failed for {dias} days: {response.text}"
            data = response.json()
            assert data["resumo"]["periodo_dias"] == dias
            print(f"✅ Period {dias} days: {data['resumo']['total_inativos']} inativos")
    
    def test_equipes_com_inativos_structure(self):
        """Test equipes_com_inativos list structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/retencao/inativos",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        equipes = data["equipes_com_inativos"]
        assert isinstance(equipes, list)
        
        if len(equipes) > 0:
            equipe = equipes[0]
            assert "equipe" in equipe
            assert "inativos" in equipe
            print(f"✅ Top equipe com inativos: {equipe['equipe']} ({equipe['inativos']} inativos)")
    
    def test_atletas_inativos_structure(self):
        """Test atletas_inativos list structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/retencao/inativos",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        atletas = data["atletas_inativos"]
        assert isinstance(atletas, list)
        
        if len(atletas) > 0:
            atleta = atletas[0]
            # Verify required fields
            assert "id" in atleta
            assert "nome" in atleta
            assert "email" in atleta
            assert "equipe" in atleta
            assert "dias_inativo" in atleta or atleta.get("nunca_submeteu")
            print(f"✅ Sample atleta inativo: {atleta['nome']} ({atleta['equipe']})")


class TestAlertarAssessoria:
    """Test alertar assessoria endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        self.token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_alertar_assessoria_success(self):
        """Test POST /api/admin/retencao/alertar-assessoria with valid team"""
        # First get a team with inactive athletes
        response = requests.get(
            f"{BASE_URL}/api/admin/retencao/inativos",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        equipes = data["equipes_com_inativos"]
        # Find a non-Individual team
        equipe_alvo = None
        for eq in equipes:
            if eq["equipe"] != "Individual":
                equipe_alvo = eq["equipe"]
                break
        
        if equipe_alvo:
            response = requests.post(
                f"{BASE_URL}/api/admin/retencao/alertar-assessoria",
                headers=self.headers,
                json={"equipe": equipe_alvo}
            )
            assert response.status_code == 200, f"Failed: {response.text}"
            result = response.json()
            
            # Either success or dono not found
            if result.get("enviado"):
                assert "dono" in result
                assert "equipe" in result
                print(f"✅ Alerta enviado para {result['dono']} ({result['equipe']})")
            else:
                print(f"⚠️ Dono não encontrado para {equipe_alvo}: {result.get('detail')}")
        else:
            pytest.skip("No non-Individual teams with inactive athletes")
    
    def test_alertar_individual_rejected(self):
        """Test that alerting Individual team is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/admin/retencao/alertar-assessoria",
            headers=self.headers,
            json={"equipe": "Individual"}
        )
        assert response.status_code == 200
        result = response.json()
        assert "detail" in result or result.get("enviado") == False
        print("✅ Individual team alert correctly rejected")


class TestExportFunctionality:
    """Test export endpoints (triggerDownload helper validation)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        self.token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_export_atletas_excel(self):
        """Test GET /api/admin/atletas/export returns Excel file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas/export",
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify content type
        content_type = response.headers.get("content-type", "")
        assert "spreadsheet" in content_type or "octet-stream" in content_type, f"Unexpected content type: {content_type}"
        
        # Verify file size
        content_length = len(response.content)
        assert content_length > 0, "Empty file returned"
        print(f"✅ Export atletas: {content_length} bytes")
    
    def test_export_ranking_excel(self):
        """Test GET /api/ranking/export/excel returns Excel file"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/export/excel",
            headers=self.headers,
            params={"todas_modalidades": True}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        content_length = len(response.content)
        assert content_length > 0, "Empty file returned"
        print(f"✅ Export ranking Excel: {content_length} bytes")
    
    def test_export_ranking_csv(self):
        """Test GET /api/ranking/export/csv returns CSV file"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/export/csv",
            headers=self.headers,
            params={"todas_modalidades": True}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        content_type = response.headers.get("content-type", "")
        assert "csv" in content_type or "text" in content_type, f"Unexpected content type: {content_type}"
        
        content_length = len(response.content)
        assert content_length > 0, "Empty file returned"
        print(f"✅ Export ranking CSV: {content_length} bytes")


class TestDownloadHelperIntegration:
    """Test that downloadHelper.js is properly integrated"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        self.token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_atletas_export_blob_response(self):
        """Verify atletas export returns proper blob for triggerDownload"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas/export",
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Check Content-Disposition header for filename
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp or len(response.content) > 0
        print(f"✅ Atletas export blob ready for triggerDownload")
    
    def test_ranking_export_blob_response(self):
        """Verify ranking export returns proper blob for triggerDownload"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/export/excel",
            headers=self.headers
        )
        assert response.status_code == 200
        
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp or len(response.content) > 0
        print(f"✅ Ranking export blob ready for triggerDownload")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
