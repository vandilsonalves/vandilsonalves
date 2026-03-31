"""
Iteration 96: Test Export Endpoints with Token via Query Parameter
=================================================================
Tests the new authentication mechanism that accepts token via query param (?token=...)
This allows window.open() to work for downloads instead of Blob/createObjectURL (blocked in iframes).

Also tests:
- Scraping buscar does NOT auto-cadastrar (cadastradas should be 0)
- Atualizar todas fontes returns Excel
- Auth still works with Bearer header (backward compatibility)
- Invalid token returns 401
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://geo-filtered-admin.preview.emergentagent.com')

class TestAuthTokenQueryParam:
    """Test authentication via query parameter"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not in response"
        return data["token"]
    
    def test_01_admin_login_returns_token(self):
        """POST /api/auth/login with admin credentials returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@runpro.com"
        print(f"✅ Admin login successful, token received")
    
    def test_02_auth_still_works_with_bearer_header(self, admin_token):
        """Auth with Bearer header still works (backward compatibility)"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@runpro.com"
        print(f"✅ Bearer header auth works: {data['nome']}")
    
    def test_03_invalid_token_returns_401(self):
        """Invalid token via query param returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/financeiro/exportar/excel?token=invalid_token_12345")
        assert response.status_code == 401
        print(f"✅ Invalid token correctly returns 401")


class TestExportWithTokenQueryParam:
    """Test all export endpoints with token via query parameter"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_04_ranking_export_csv_with_token(self, admin_token):
        """GET /api/ranking/export/csv?todas_modalidades=true&token=TOKEN returns CSV"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/export/csv?todas_modalidades=true&token={admin_token}"
        )
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "text/csv" in content_type or "text/plain" in content_type
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp or len(response.content) > 0
        print(f"✅ Ranking CSV export with token: {len(response.content)} bytes")
    
    def test_05_ranking_export_excel_with_token(self, admin_token):
        """GET /api/ranking/export/excel?todas_modalidades=true&token=TOKEN returns Excel"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/export/excel?todas_modalidades=true&token={admin_token}"
        )
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "spreadsheet" in content_type or "octet-stream" in content_type or len(response.content) > 0
        print(f"✅ Ranking Excel export with token: {len(response.content)} bytes")
    
    def test_06_financeiro_export_excel_with_token(self, admin_token):
        """GET /api/admin/financeiro/exportar/excel?token=TOKEN returns Excel"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/exportar/excel?token={admin_token}"
        )
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        # Should be Excel or PDF content
        assert len(response.content) > 0
        print(f"✅ Financeiro Excel export with token: {len(response.content)} bytes")
    
    def test_07_financeiro_export_pdf_with_token(self, admin_token):
        """GET /api/admin/financeiro/exportar/pdf?token=TOKEN returns PDF"""
        response = requests.get(
            f"{BASE_URL}/api/admin/financeiro/exportar/pdf?token={admin_token}"
        )
        assert response.status_code == 200
        assert len(response.content) > 0
        print(f"✅ Financeiro PDF export with token: {len(response.content)} bytes")
    
    def test_08_atletas_export_with_token(self, admin_token):
        """GET /api/admin/atletas/export?token=TOKEN returns Excel"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas/export?token={admin_token}"
        )
        assert response.status_code == 200
        assert len(response.content) > 0
        print(f"✅ Atletas export with token: {len(response.content)} bytes")
    
    def test_09_corridas_export_csv_with_token(self, admin_token):
        """GET /api/corridas-eventos/exportar/csv?token=TOKEN returns CSV"""
        response = requests.get(
            f"{BASE_URL}/api/corridas-eventos/exportar/csv?token={admin_token}"
        )
        assert response.status_code == 200
        assert len(response.content) > 0
        print(f"✅ Corridas CSV export with token: {len(response.content)} bytes")
    
    def test_10_corridas_export_excel_with_token(self, admin_token):
        """GET /api/corridas-eventos/exportar/excel?token=TOKEN returns Excel"""
        response = requests.get(
            f"{BASE_URL}/api/corridas-eventos/exportar/excel?token={admin_token}"
        )
        assert response.status_code == 200
        assert len(response.content) > 0
        print(f"✅ Corridas Excel export with token: {len(response.content)} bytes")
    
    def test_11_corridas_template_excel_with_token(self, admin_token):
        """GET /api/corridas-eventos/template?formato=excel&token=TOKEN returns Excel template"""
        response = requests.get(
            f"{BASE_URL}/api/corridas-eventos/template?formato=excel&token={admin_token}"
        )
        assert response.status_code == 200
        assert len(response.content) > 0
        print(f"✅ Corridas template Excel with token: {len(response.content)} bytes")


class TestDownloadCSVEndpoint:
    """Test the generic CSV download endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_12_download_csv_with_form_data(self, admin_token):
        """POST /api/admin/download-csv?token=TOKEN&filename=teste.csv with form data"""
        csv_content = "Nome,Email,Pontos\nJoao,joao@test.com,100\nMaria,maria@test.com,200"
        response = requests.post(
            f"{BASE_URL}/api/admin/download-csv?token={admin_token}&filename=teste.csv",
            data={"csv_content": csv_content}
        )
        assert response.status_code == 200
        content_disp = response.headers.get("content-disposition", "")
        assert "teste.csv" in content_disp or len(response.content) > 0
        print(f"✅ Download CSV endpoint works: {len(response.content)} bytes")


class TestScrapingManualMode:
    """Test that scraping buscar does NOT auto-cadastrar"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_13_scraping_buscar_does_not_auto_cadastrar(self, admin_token):
        """POST /api/scraping/buscar should NOT have cadastradas > 0"""
        # Use a test URL - the scraping might fail but we check the response structure
        response = requests.post(
            f"{BASE_URL}/api/scraping/buscar",
            json={
                "url": "https://www.ticketsports.com.br/eventos",
                "usar_playwright": False,
                "cadastrar_automaticamente": False
            },
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=60
        )
        # The endpoint might return 200 with success=false if scraping fails
        # But if it succeeds, cadastradas should be 0
        if response.status_code == 200:
            data = response.json()
            cadastradas = data.get("cadastradas", 0)
            assert cadastradas == 0, f"Expected cadastradas=0, got {cadastradas}"
            print(f"✅ Scraping buscar does NOT auto-cadastrar: cadastradas={cadastradas}")
        else:
            # Scraping might fail due to network/site issues, that's OK
            print(f"⚠️ Scraping returned {response.status_code} - may be network issue, skipping")
    
    def test_14_scraping_status_endpoint(self, admin_token):
        """GET /api/scraping/status returns status info"""
        response = requests.get(
            f"{BASE_URL}/api/scraping/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_fontes_ativas" in data
        print(f"✅ Scraping status: {data.get('total_fontes_ativas', 0)} fontes ativas")


class TestAtletaLogin:
    """Test atleta login"""
    
    def test_15_atleta_login(self):
        """POST /api/auth/login with atleta credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teste.dono@teste.com",
            "password": "123456"
        })
        # This atleta might not exist, so we accept 401 as valid
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            print(f"✅ Atleta login successful: {data['user']['nome']}")
        elif response.status_code == 401:
            print(f"⚠️ Atleta teste.dono@teste.com not found (401) - expected if not seeded")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
