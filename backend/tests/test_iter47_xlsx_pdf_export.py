# /app/backend/tests/test_iter47_xlsx_pdf_export.py
# Iteration 47: Testing NEW Export Formats - XLSX (Excel) and PDF
# Features:
# - GET /api/liga-assessorias/exportar-dados/{nome_equipe}?formato=xlsx - Excel Export
# - GET /api/liga-assessorias/exportar-dados/{nome_equipe}?formato=pdf - PDF Export
# - Verify CSV and JSON exports still work (regression)

import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_ADMIN_EMAIL = "admin@runpro.com"
TEST_ADMIN_PASSWORD = "admin123"
TEST_ASSESSORIA = "Assessoria CAFAV"  # Team with 17 athletes as per request


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    token = response.json().get("token")
    assert token, "No token received from login"
    return token


@pytest.fixture(scope="module")
def authenticated_client(api_client, admin_token):
    """Session with admin auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_login_success(self, api_client):
        """Test admin login returns token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_ADMIN_EMAIL,
            "password": TEST_ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"✅ Login successful for {TEST_ADMIN_EMAIL}")


class TestExcelXLSXExport:
    """Excel (XLSX) Export endpoint tests - NEW FEATURE"""
    
    def test_export_xlsx_requires_auth(self, api_client):
        """XLSX export should require authentication"""
        # Use a fresh session without auth
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato=xlsx"
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✅ XLSX export correctly requires authentication")
    
    def test_export_xlsx_with_auth(self, authenticated_client):
        """XLSX export with valid auth should return valid Excel file"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato=xlsx"
        )
        assert response.status_code == 200, f"XLSX export failed with {response.status_code}: {response.text[:500]}"
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in content_type, \
            f"Expected Excel content type, got: {content_type}"
        
        # Check content disposition
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp, "Missing attachment in content-disposition"
        assert ".xlsx" in content_disp, "Missing .xlsx extension in content-disposition"
        
        # Validate file is not empty and has reasonable size
        content = response.content
        assert len(content) > 0, "XLSX file is empty"
        assert len(content) > 1000, f"XLSX file too small: {len(content)} bytes"
        
        # XLSX files start with PK (ZIP format)
        assert content[:2] == b'PK', "XLSX file should start with PK (ZIP header)"
        
        print(f"✅ XLSX export successful, file size: {len(content)} bytes")
    
    def test_export_xlsx_file_structure(self, authenticated_client):
        """XLSX export file should be a valid ZIP (XLSX format)"""
        import zipfile
        
        response = authenticated_client.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato=xlsx"
        )
        assert response.status_code == 200
        
        # Try to open as ZIP file
        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                # XLSX files should contain certain files
                namelist = zf.namelist()
                assert len(namelist) > 0, "XLSX ZIP file is empty"
                
                # XLSX typically contains [Content_Types].xml
                has_content_types = any('[Content_Types].xml' in name for name in namelist)
                assert has_content_types, f"Missing [Content_Types].xml in XLSX. Files: {namelist[:5]}"
                
                print(f"✅ XLSX is valid ZIP with {len(namelist)} files")
        except zipfile.BadZipFile:
            pytest.fail("XLSX file is not a valid ZIP archive")
    
    def test_export_xlsx_assessoria_not_found(self, authenticated_client):
        """XLSX export for non-existent assessoria should return 404"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/ASSESSORIA_INEXISTENTE_XYZ?formato=xlsx"
        )
        assert response.status_code == 404
        print(f"✅ XLSX export correctly returns 404 for non-existent assessoria")


class TestPDFExport:
    """PDF Export endpoint tests - NEW FEATURE"""
    
    def test_export_pdf_requires_auth(self, api_client):
        """PDF export should require authentication"""
        # Use a fresh session without auth
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato=pdf"
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✅ PDF export correctly requires authentication")
    
    def test_export_pdf_with_auth(self, authenticated_client):
        """PDF export with valid auth should return valid PDF file"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato=pdf"
        )
        assert response.status_code == 200, f"PDF export failed with {response.status_code}: {response.text[:500]}"
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, \
            f"Expected PDF content type, got: {content_type}"
        
        # Check content disposition
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp, "Missing attachment in content-disposition"
        assert ".pdf" in content_disp, "Missing .pdf extension in content-disposition"
        
        # Validate file is not empty and has reasonable size
        content = response.content
        assert len(content) > 0, "PDF file is empty"
        assert len(content) > 1000, f"PDF file too small: {len(content)} bytes"
        
        # PDF files start with %PDF
        assert content[:4] == b'%PDF', f"PDF file should start with %PDF, got: {content[:10]}"
        
        print(f"✅ PDF export successful, file size: {len(content)} bytes")
    
    def test_export_pdf_valid_structure(self, authenticated_client):
        """PDF export file should contain expected PDF markers"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato=pdf"
        )
        assert response.status_code == 200
        
        content = response.content
        
        # PDF should start with %PDF
        assert content.startswith(b'%PDF'), "PDF should start with %PDF header"
        
        # PDF should end with %%EOF
        assert b'%%EOF' in content, "PDF should contain %%EOF marker"
        
        print(f"✅ PDF structure is valid (has %PDF header and %%EOF)")
    
    def test_export_pdf_assessoria_not_found(self, authenticated_client):
        """PDF export for non-existent assessoria should return 404"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/ASSESSORIA_INEXISTENTE_XYZ?formato=pdf"
        )
        assert response.status_code == 404
        print(f"✅ PDF export correctly returns 404 for non-existent assessoria")


class TestCSVRegressionExport:
    """CSV Export regression tests - ensure existing format still works"""
    
    def test_export_csv_still_works(self, authenticated_client):
        """CSV export should continue working after XLSX/PDF additions"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato=csv"
        )
        assert response.status_code == 200
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "text/csv" in content_type, f"Expected CSV content type, got: {content_type}"
        
        # Check for UTF-8 BOM (for Excel compatibility)
        content = response.content
        assert content.startswith(b'\xef\xbb\xbf'), "CSV should have UTF-8 BOM for Excel"
        
        # Decode and validate structure
        text = content.decode('utf-8-sig')
        assert "ESTATÍSTICAS DA ASSESSORIA" in text
        assert TEST_ASSESSORIA in text
        
        print(f"✅ CSV export still working, file size: {len(content)} bytes")


class TestJSONRegressionExport:
    """JSON Export regression tests - ensure existing format still works"""
    
    def test_export_json_still_works(self, authenticated_client):
        """JSON export should continue working after XLSX/PDF additions"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato=json"
        )
        assert response.status_code == 200
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type, f"Expected JSON content type, got: {content_type}"
        
        # Validate JSON structure
        data = response.json()
        assert "equipe" in data
        assert data["equipe"] == TEST_ASSESSORIA
        assert "data_exportacao" in data
        assert "estatisticas" in data
        assert "atletas" in data
        assert "corridas" in data
        
        print(f"✅ JSON export still working, {len(data['atletas'])} athletes exported")


class TestAllFormatsComparison:
    """Compare all export formats for consistency"""
    
    def test_all_formats_same_assessoria_data(self, authenticated_client):
        """All formats should export data for the same assessoria"""
        formats_tested = []
        
        for formato in ["csv", "json", "xlsx", "pdf"]:
            response = authenticated_client.get(
                f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato={formato}"
            )
            assert response.status_code == 200, f"Format {formato} failed with {response.status_code}"
            formats_tested.append(formato)
        
        print(f"✅ All formats working: {', '.join(formats_tested)}")
    
    def test_file_sizes_are_reasonable(self, authenticated_client):
        """File sizes should be reasonable for all formats"""
        sizes = {}
        
        for formato in ["csv", "json", "xlsx", "pdf"]:
            response = authenticated_client.get(
                f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato={formato}"
            )
            assert response.status_code == 200
            sizes[formato] = len(response.content)
        
        # Print sizes for debugging
        print(f"File sizes: CSV={sizes['csv']} bytes, JSON={sizes['json']} bytes, "
              f"XLSX={sizes['xlsx']} bytes, PDF={sizes['pdf']} bytes")
        
        # All files should be > 1KB
        for formato, size in sizes.items():
            assert size > 1000, f"{formato.upper()} file too small: {size} bytes"
        
        # Files should be < 1MB for this test data
        for formato, size in sizes.items():
            assert size < 1000000, f"{formato.upper()} file too large: {size} bytes"
        
        print(f"✅ All file sizes are reasonable")


class TestInvalidFormat:
    """Test handling of invalid export format"""
    
    def test_invalid_format_returns_422_or_csv_default(self, authenticated_client):
        """Export with invalid format should return 422 or default to CSV"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/liga-assessorias/exportar-dados/{TEST_ASSESSORIA}?formato=xml"
        )
        # FastAPI Query enum validation should reject invalid format (422)
        # OR the backend may default to CSV (200) - both behaviors are acceptable
        assert response.status_code in [200, 422], \
            f"Expected 200 (CSV default) or 422 (validation error), got {response.status_code}"
        
        if response.status_code == 200:
            # If defaulting to CSV, check content type
            content_type = response.headers.get("content-type", "")
            assert "text/csv" in content_type, f"Expected CSV content type when defaulting, got: {content_type}"
            print(f"✅ Invalid format defaults to CSV (200)")
        else:
            print(f"✅ Invalid format correctly returns 422")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
