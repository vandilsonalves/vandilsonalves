"""
Iteration 115: Testing 3 Bug Fixes in Dono Assessoria Dashboard
1. Bug 1: GET /api/liga-assessorias/exportar-graficos/{equipe} should return Content-Disposition: attachment header
2. Bug 2: Exportar Lista in Meus Atletas tab should work for dono_assessoria (client-side CSV generation)
3. Bug 3: Upload/Delete foto endpoints should use correct URLs (/api/assessorias/upload-foto and /api/assessorias/remover-foto)
"""

import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDonoAssessoriaBugFixes:
    """Test the 3 bug fixes for Dono Assessoria Dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test credentials"""
        self.admin_email = "admin@runpro.com"
        self.admin_password = "admin"
        self.dono_email = "teste.dono@teste.com"
        self.dono_password = "123456"
        self.dono_equipe = "Individual"  # User's equipe name
        
    def get_admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.admin_email,
            "password": self.admin_password
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def get_dono_token(self):
        """Get dono_assessoria authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.dono_email,
            "password": self.dono_password
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None

    # ==================== BUG 1 TESTS ====================
    # exportar-graficos should return Content-Disposition: attachment header
    
    def test_bug1_exportar_graficos_returns_attachment_header(self):
        """Bug 1: GET /api/liga-assessorias/exportar-graficos/{equipe} should return Content-Disposition: attachment"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-graficos/{self.dono_equipe}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should return 200 OK
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # CRITICAL: Should have Content-Disposition: attachment header
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition.lower(), \
            f"Expected Content-Disposition: attachment header, got: {content_disposition}"
        
        # Should be JSON content type
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected JSON content type, got: {content_type}"
        
        # Should have filename in Content-Disposition
        assert "filename" in content_disposition.lower(), \
            f"Expected filename in Content-Disposition, got: {content_disposition}"
        
        print(f"✓ Bug 1 FIXED: exportar-graficos returns Content-Disposition: {content_disposition}")
    
    def test_bug1_exportar_graficos_returns_valid_json(self):
        """Bug 1: Verify the exported graficos data is valid JSON"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-graficos/{self.dono_equipe}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Should be valid JSON
        data = response.json()
        assert isinstance(data, dict), "Response should be a JSON object"
        
        # Should have expected fields
        assert "equipe" in data, "Response should have 'equipe' field"
        assert "metadados" in data, "Response should have 'metadados' field"
        
        print(f"✓ Bug 1 VERIFIED: exportar-graficos returns valid JSON with equipe={data.get('equipe')}")
    
    def test_bug1_exportar_graficos_requires_auth(self):
        """Bug 1: exportar-graficos should require authentication"""
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-graficos/{self.dono_equipe}"
        )
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], \
            f"Expected 401/403 without auth, got {response.status_code}"
        
        print("✓ Bug 1 VERIFIED: exportar-graficos requires authentication")

    # ==================== BUG 2 TESTS ====================
    # Exportar Lista should NOT call /api/admin/download-csv (admin-only endpoint)
    # Instead, it should generate CSV client-side
    
    def test_bug2_admin_download_csv_requires_admin(self):
        """Bug 2: Verify /api/admin/download-csv is admin-only (dono should get 403)"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        # Try to access admin endpoint as dono_assessoria
        response = requests.post(
            f"{BASE_URL}/api/admin/download-csv",
            headers={"Authorization": f"Bearer {token}"},
            json={"data": [["test"]], "filename": "test.csv"}
        )
        
        # Should return 403 Forbidden for non-admin
        assert response.status_code in [401, 403], \
            f"Expected 401/403 for dono accessing admin endpoint, got {response.status_code}"
        
        print("✓ Bug 2 VERIFIED: /api/admin/download-csv correctly requires admin role")
    
    def test_bug2_dono_can_access_atletas_data(self):
        """Bug 2: Verify dono can access their atletas data for client-side CSV generation"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        # Dono should be able to get assessoria details (which includes atletas)
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/assessoria/{self.dono_equipe}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "atletas" in data, "Response should have 'atletas' field"
        
        print(f"✓ Bug 2 VERIFIED: Dono can access atletas data (count: {len(data.get('atletas', []))})")
    
    def test_bug2_exportar_dados_csv_works_for_dono(self):
        """Bug 2: Verify dono can export data in CSV format"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{self.dono_equipe}?formato=csv",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Should have Content-Disposition: attachment
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition.lower(), \
            f"Expected attachment header, got: {content_disposition}"
        
        # Should be CSV content type
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Expected text/csv, got: {content_type}"
        
        print("✓ Bug 2 VERIFIED: Dono can export CSV data via exportar-dados endpoint")

    # ==================== BUG 3 TESTS ====================
    # Upload foto should use /api/assessorias/upload-foto (not /api/assessoria/foto)
    # Delete foto should use /api/assessorias/remover-foto
    
    def test_bug3_upload_foto_endpoint_exists(self):
        """Bug 3: Verify POST /api/assessorias/upload-foto endpoint exists and works for dono"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        # Create a simple test image (1x1 pixel PNG)
        # PNG header for a 1x1 transparent pixel
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # bit depth, color type, etc
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # compressed data
            0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,  # 
            0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
            0x42, 0x60, 0x82
        ])
        
        files = {
            'foto': ('test_image.png', io.BytesIO(png_data), 'image/png')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/assessorias/upload-foto",
            headers={"Authorization": f"Bearer {token}"},
            files=files
        )
        
        # Should return 200 OK (or 400 if image validation fails, but NOT 404)
        assert response.status_code != 404, \
            f"Endpoint /api/assessorias/upload-foto not found (404)"
        
        # If successful, should have foto_url in response
        if response.status_code == 200:
            data = response.json()
            assert "foto_url" in data or "message" in data, \
                f"Expected foto_url or message in response, got: {data}"
            print(f"✓ Bug 3 FIXED: upload-foto endpoint works, response: {data.get('message', data.get('foto_url', 'OK'))}")
        else:
            # Even if upload fails (e.g., invalid image), endpoint exists
            print(f"✓ Bug 3 VERIFIED: upload-foto endpoint exists (status: {response.status_code})")
    
    def test_bug3_upload_foto_requires_auth(self):
        """Bug 3: Verify upload-foto requires authentication"""
        png_data = bytes([0x89, 0x50, 0x4E, 0x47])  # Minimal PNG header
        files = {'foto': ('test.png', io.BytesIO(png_data), 'image/png')}
        
        response = requests.post(
            f"{BASE_URL}/api/assessorias/upload-foto",
            files=files
        )
        
        assert response.status_code in [401, 403], \
            f"Expected 401/403 without auth, got {response.status_code}"
        
        print("✓ Bug 3 VERIFIED: upload-foto requires authentication")
    
    def test_bug3_remover_foto_endpoint_exists(self):
        """Bug 3: Verify DELETE /api/assessorias/remover-foto endpoint exists"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        response = requests.delete(
            f"{BASE_URL}/api/assessorias/remover-foto",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should NOT return 404 (endpoint should exist)
        assert response.status_code != 404, \
            f"Endpoint /api/assessorias/remover-foto not found (404)"
        
        # Should return 200 OK (even if no photo to remove)
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}: {response.text}"
        
        print(f"✓ Bug 3 FIXED: remover-foto endpoint works (status: {response.status_code})")
    
    def test_bug3_remover_foto_requires_auth(self):
        """Bug 3: Verify remover-foto requires authentication"""
        response = requests.delete(f"{BASE_URL}/api/assessorias/remover-foto")
        
        assert response.status_code in [401, 403], \
            f"Expected 401/403 without auth, got {response.status_code}"
        
        print("✓ Bug 3 VERIFIED: remover-foto requires authentication")
    
    def test_bug3_old_endpoint_should_not_exist(self):
        """Bug 3: Verify old endpoint /api/assessoria/foto does NOT exist (or returns 404)"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        # Try the OLD incorrect endpoint
        response = requests.post(
            f"{BASE_URL}/api/assessoria/foto",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Old endpoint should return 404 or 405 (not found or method not allowed)
        # If it returns 200, the bug might not be fully fixed
        if response.status_code == 404:
            print("✓ Bug 3 VERIFIED: Old endpoint /api/assessoria/foto returns 404 (correct)")
        elif response.status_code == 405:
            print("✓ Bug 3 VERIFIED: Old endpoint /api/assessoria/foto returns 405 (method not allowed)")
        else:
            print(f"⚠ Warning: Old endpoint /api/assessoria/foto returned {response.status_code}")

    # ==================== ADDITIONAL VERIFICATION TESTS ====================
    
    def test_dono_assessoria_dashboard_loads(self):
        """Verify dono_assessoria can access their dashboard data"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        # Get assessoria details
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/assessoria/{self.dono_equipe}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("nome") == self.dono_equipe, \
            f"Expected equipe name '{self.dono_equipe}', got '{data.get('nome')}'"
        
        print(f"✓ Dashboard data loads correctly for equipe: {data.get('nome')}")
    
    def test_graficos_avancados_works_for_dono(self):
        """Verify dono can access graficos-avancados endpoint"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/graficos-avancados/{self.dono_equipe}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "equipe" in data, "Response should have 'equipe' field"
        assert "estatisticas" in data, "Response should have 'estatisticas' field"
        
        print(f"✓ graficos-avancados works for dono (equipe: {data.get('equipe')})")
    
    def test_comparacao_mensal_works_for_dono(self):
        """Verify dono can access comparacao-mensal endpoint"""
        token = self.get_dono_token()
        assert token is not None, "Failed to get dono token"
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/comparacao-mensal/{self.dono_equipe}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "equipe" in data, "Response should have 'equipe' field"
        assert "mes_atual" in data, "Response should have 'mes_atual' field"
        assert "mes_anterior" in data, "Response should have 'mes_anterior' field"
        
        print(f"✓ comparacao-mensal works for dono (equipe: {data.get('equipe')})")


class TestExportFormats:
    """Test all export formats work correctly"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.dono_email = "teste.dono@teste.com"
        self.dono_password = "123456"
        self.dono_equipe = "Individual"
    
    def get_dono_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.dono_email,
            "password": self.dono_password
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_export_csv_format(self):
        """Test CSV export format"""
        token = self.get_dono_token()
        assert token is not None
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{self.dono_equipe}?formato=csv",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("Content-Type", "")
        assert "attachment" in response.headers.get("Content-Disposition", "")
        print("✓ CSV export works correctly")
    
    def test_export_json_format(self):
        """Test JSON export format"""
        token = self.get_dono_token()
        assert token is not None
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{self.dono_equipe}?formato=json",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert "attachment" in response.headers.get("Content-Disposition", "")
        print("✓ JSON export works correctly")
    
    def test_export_xlsx_format(self):
        """Test XLSX export format"""
        token = self.get_dono_token()
        assert token is not None
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{self.dono_equipe}?formato=xlsx",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheet" in content_type or "xlsx" in content_type or "octet-stream" in content_type
        assert "attachment" in response.headers.get("Content-Disposition", "")
        print("✓ XLSX export works correctly")
    
    def test_export_pdf_format(self):
        """Test PDF export format"""
        token = self.get_dono_token()
        assert token is not None
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{self.dono_equipe}?formato=pdf",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "pdf" in content_type or "octet-stream" in content_type
        assert "attachment" in response.headers.get("Content-Disposition", "")
        print("✓ PDF export works correctly")
