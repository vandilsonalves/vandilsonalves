# /app/backend/tests/test_iter105_foto_pdf_politica.py
# Iteration 105: Testing foto_url fix, PDF export, and Privacy Policy page
# Tests: foto_url prefix /api/uploads/inside/, PDF export, XLSX export, graficos_data with scores

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Test admin authentication"""
    
    def test_admin_login(self):
        """Test admin login returns valid token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert len(data["token"]) > 0, "Token is empty"
        print(f"✓ Admin login successful, token received")
        return data["token"]


class TestFotoUpload:
    """Test foto upload returns correct URL prefix"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    def test_upload_foto_returns_api_prefix(self, admin_token):
        """POST /api/admin/instagram/upload-foto should return foto_url with /api/uploads/inside/ prefix"""
        # Create a simple test image (1x1 pixel PNG)
        import base64
        # Minimal valid PNG (1x1 transparent pixel)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        
        files = {'foto': ('test_image.png', png_data, 'image/png')}
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/upload-foto",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        assert "foto_url" in data, "No foto_url in response"
        
        # CRITICAL: foto_url must start with /api/uploads/inside/
        foto_url = data["foto_url"]
        assert foto_url.startswith("/api/uploads/inside/"), f"foto_url should start with /api/uploads/inside/, got: {foto_url}"
        print(f"✓ foto_url has correct prefix: {foto_url}")
        
        # Verify the file is accessible
        full_url = f"{BASE_URL}{foto_url}"
        img_response = requests.get(full_url)
        assert img_response.status_code == 200, f"Uploaded image not accessible at {full_url}"
        print(f"✓ Uploaded image accessible at {full_url}")


class TestPDFExport:
    """Test PDF export functionality"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    @pytest.fixture
    def test_analysis_id(self, admin_token):
        """Create a test analysis for export testing"""
        payload = {
            "username": f"test_pdf_export_{uuid.uuid4().hex[:8]}",
            "nome_completo": "Test PDF Export User",
            "seguidores": 10000,
            "seguindo": 500,
            "total_posts": 200,
            "nota": "B+",
            "classificacao_sb": "B+",
            "classificacao_seguidores": "Micro-influencer",
            "ganho_seguidores_30d": 500,
            "perda_seguidores_30d": 50,
            "media_semanal_ganho": 125,
            "media_semanal_perda": 12.5,
            "posts_30d": 20,
            "media_semanal_posts": 5,
            "views_reels_6": 60000,
            "curtidas_medias": 350,
            "comentarios_medios": 15
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed to create test analysis: {response.text}"
        return response.json()["analysis"]["id"]
    
    def test_export_pdf_returns_valid_pdf(self, admin_token, test_analysis_id):
        """GET /api/admin/instagram/export-pdf/{id} should return valid PDF"""
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/export-pdf/{test_analysis_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"PDF export failed: {response.status_code} - {response.text}"
        
        # Check Content-Type
        content_type = response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected application/pdf, got: {content_type}"
        print(f"✓ PDF export returned correct Content-Type: {content_type}")
        
        # Check Content-Disposition
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, f"Expected attachment disposition, got: {content_disp}"
        assert ".pdf" in content_disp, f"Expected .pdf in filename, got: {content_disp}"
        print(f"✓ PDF export has correct Content-Disposition: {content_disp}")
        
        # Check PDF magic bytes
        pdf_content = response.content
        assert pdf_content[:4] == b'%PDF', f"Response does not start with PDF magic bytes"
        print(f"✓ PDF content starts with valid PDF header")
        
        # Check PDF has reasonable size
        assert len(pdf_content) > 1000, f"PDF seems too small: {len(pdf_content)} bytes"
        print(f"✓ PDF size: {len(pdf_content)} bytes")
    
    def test_export_pdf_404_for_invalid_id(self, admin_token):
        """GET /api/admin/instagram/export-pdf/{invalid_id} should return 404"""
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/export-pdf/invalid-id-12345",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
        print(f"✓ PDF export returns 404 for invalid ID")


class TestXLSXExport:
    """Test XLSX export still works"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    @pytest.fixture
    def test_analysis_id(self, admin_token):
        """Create a test analysis for export testing"""
        payload = {
            "username": f"test_xlsx_export_{uuid.uuid4().hex[:8]}",
            "seguidores": 5000,
            "seguindo": 300,
            "total_posts": 100,
            "nota": "C+",
            "ganho_seguidores_30d": 200,
            "perda_seguidores_30d": 30,
            "posts_30d": 15,
            "views_reels_6": 30000,
            "curtidas_medias": 200,
            "comentarios_medios": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        return response.json()["analysis"]["id"]
    
    def test_export_xlsx_returns_valid_xlsx(self, admin_token, test_analysis_id):
        """GET /api/admin/instagram/export/{id} should return valid XLSX"""
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/export/{test_analysis_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"XLSX export failed: {response.status_code}"
        
        # Check Content-Type
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheet" in content_type or "xlsx" in content_type, f"Expected spreadsheet content-type, got: {content_type}"
        print(f"✓ XLSX export returned correct Content-Type: {content_type}")
        
        # Check XLSX magic bytes (PK for ZIP format)
        xlsx_content = response.content
        assert xlsx_content[:2] == b'PK', f"Response does not start with XLSX/ZIP magic bytes"
        print(f"✓ XLSX content starts with valid ZIP header (PK)")


class TestGraficosDataWithScores:
    """Test that graficos_data includes all 7 sections with scores"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    @pytest.fixture
    def test_analysis_id(self, admin_token):
        """Create a test analysis"""
        payload = {
            "username": f"test_graficos_{uuid.uuid4().hex[:8]}",
            "seguidores": 15000,
            "seguindo": 800,
            "total_posts": 300,
            "nota": "A",
            "ganho_seguidores_30d": 1000,
            "perda_seguidores_30d": 100,
            "posts_30d": 25,
            "views_reels_6": 90000,
            "curtidas_medias": 500,
            "comentarios_medios": 25
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        return response.json()["analysis"]["id"]
    
    def test_graficos_data_has_all_sections(self, admin_token, test_analysis_id):
        """GET /api/admin/instagram/analises/{id} should return graficos_data with 7 sections including scores"""
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/analises/{test_analysis_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Failed to get analysis: {response.text}"
        data = response.json()
        
        assert "graficos_data" in data, "No graficos_data in response"
        gd = data["graficos_data"]
        
        # Check all 7 sections exist
        required_sections = ["nota_gauge", "views_reels", "engajamento", "curtidas", "comentarios", "crescimento", "posts", "scores"]
        for section in required_sections:
            assert section in gd, f"Missing section: {section}"
            print(f"✓ Section '{section}' present in graficos_data")
        
        # Check scores section has all required fields
        scores = gd["scores"]
        score_fields = ["views", "engajamento", "curtidas", "comentarios", "crescimento", "posts", "media"]
        for field in score_fields:
            assert field in scores, f"Missing score field: {field}"
            assert isinstance(scores[field], (int, float)), f"Score '{field}' should be numeric"
        print(f"✓ Scores section has all required fields: {list(scores.keys())}")
        print(f"✓ Score values: {scores}")


class TestAnalysisWithFoto:
    """Test that analyses with foto display correctly"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    def test_analysis_with_foto_url(self, admin_token):
        """Create analysis with foto_url and verify it's stored correctly"""
        # First upload a photo
        import base64
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        
        files = {'foto': ('test_image.png', png_data, 'image/png')}
        upload_response = requests.post(
            f"{BASE_URL}/api/admin/instagram/upload-foto",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        foto_url = upload_response.json()["foto_url"]
        
        # Create analysis with foto_url
        payload = {
            "username": f"test_with_foto_{uuid.uuid4().hex[:8]}",
            "seguidores": 8000,
            "seguindo": 400,
            "total_posts": 150,
            "nota": "B",
            "ganho_seguidores_30d": 300,
            "perda_seguidores_30d": 40,
            "posts_30d": 18,
            "views_reels_6": 45000,
            "curtidas_medias": 280,
            "comentarios_medios": 12,
            "foto_url": foto_url
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Failed to create analysis: {response.text}"
        analysis = response.json()["analysis"]
        
        # Verify foto_url is stored
        assert "foto_url" in analysis, "foto_url not in analysis"
        assert analysis["foto_url"] == foto_url, f"foto_url mismatch: expected {foto_url}, got {analysis['foto_url']}"
        assert analysis["foto_url"].startswith("/api/uploads/inside/"), f"foto_url should have /api/uploads/inside/ prefix"
        print(f"✓ Analysis created with foto_url: {analysis['foto_url']}")
        
        # Verify foto is accessible
        full_url = f"{BASE_URL}{analysis['foto_url']}"
        img_response = requests.get(full_url)
        assert img_response.status_code == 200, f"Foto not accessible at {full_url}"
        print(f"✓ Foto accessible at {full_url}")


class TestPrivacyPolicyPage:
    """Test Privacy Policy page is accessible without login"""
    
    def test_privacy_policy_page_accessible(self):
        """GET /politica-de-privacidade should be accessible without authentication"""
        response = requests.get(f"{BASE_URL}/politica-de-privacidade")
        
        # Should return 200 (page loads)
        assert response.status_code == 200, f"Privacy policy page not accessible: {response.status_code}"
        print(f"✓ Privacy policy page accessible (status: {response.status_code})")
        
        # Check that it returns HTML
        content_type = response.headers.get("Content-Type", "")
        assert "text/html" in content_type, f"Expected HTML, got: {content_type}"
        print(f"✓ Privacy policy returns HTML content")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    def test_cleanup_test_analyses(self, admin_token):
        """Delete test analyses created during testing"""
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/analises",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            analyses = response.json()
            deleted = 0
            for a in analyses:
                if a.get("username", "").startswith("test_"):
                    del_response = requests.delete(
                        f"{BASE_URL}/api/admin/instagram/analises/{a['id']}",
                        headers={"Authorization": f"Bearer {admin_token}"}
                    )
                    if del_response.status_code == 200:
                        deleted += 1
            print(f"✓ Cleaned up {deleted} test analyses")
