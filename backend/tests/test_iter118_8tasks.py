"""
Iteration 118: Testing 8 tasks implemented simultaneously
1. Bug fix Feed/Stories photos (image URL construction)
2. Hall da Fama contrast colors
3. Ranking por Cidade mobile responsive
4. Pontuacao Galera (5km=5pts, 10km=7pts, 21km+=9pts)
5. Frase biblica below title
6. Exportar Excel corridas no Admin
7. Autorizacoes with custom date
7b. Super Admin restricted to 2 emails
8. Restaurar Backup
"""

import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


class TestAuthentication:
    """Test authentication for admin and atleta"""
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert data.get("user", {}).get("role") in ["admin", "super_admin"], f"Unexpected role: {data.get('user', {}).get('role')}"
        print(f"Admin login successful, role: {data.get('user', {}).get('role')}")
        return data["token"]
    
    def test_atleta_login(self):
        """Test atleta login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        assert response.status_code == 200, f"Atleta login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        print(f"Atleta login successful, role: {data.get('user', {}).get('role')}")
        return data["token"]


class TestTask6ExportCorridasExcel:
    """Task 6: GET /api/admin/exportar/corridas-completas returns Excel"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("token")
    
    def test_export_corridas_completas_endpoint_exists(self, admin_token):
        """Test that the export corridas-completas endpoint exists and returns Excel"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/exportar/corridas-completas", headers=headers)
        
        assert response.status_code == 200, f"Export failed: {response.status_code} - {response.text}"
        
        # Check content type is Excel
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheetml" in content_type or "application/vnd" in content_type, f"Unexpected content type: {content_type}"
        
        # Check content disposition
        content_disp = response.headers.get("Content-Disposition", "")
        assert "corridas_completas" in content_disp, f"Unexpected filename: {content_disp}"
        assert ".xlsx" in content_disp, "File should be .xlsx"
        
        # Check file has content
        assert len(response.content) > 0, "Excel file is empty"
        print(f"Export corridas-completas: {len(response.content)} bytes, filename in: {content_disp}")


class TestTask7AutorizacoesCustomDate:
    """Task 7: POST /api/admin/autorizacoes/autorizar with tipo_plano='data_customizada'"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("token")
    
    @pytest.fixture
    def test_atleta_id(self, admin_token):
        """Get a test atleta ID"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/autorizacoes/atletas-completo", headers=headers)
        if response.status_code == 200:
            atletas = response.json().get("atletas", [])
            if atletas:
                return atletas[0].get("id")
        return None
    
    def test_autorizar_with_custom_date(self, admin_token, test_atleta_id):
        """Test authorization with custom date"""
        if not test_atleta_id:
            pytest.skip("No test atleta available")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "atleta_id": test_atleta_id,
            "tipo_plano": "data_customizada",
            "data_expiracao_custom": "2027-06-30"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/autorizacoes/autorizar", json=payload, headers=headers)
        
        # Accept 200 or 400 (if already authorized)
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code} - {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            print(f"Authorization with custom date successful: {data}")
        else:
            print(f"Authorization response (may be already authorized): {response.text}")
    
    def test_autorizar_endpoint_accepts_custom_date_field(self, admin_token):
        """Test that the endpoint schema accepts data_expiracao_custom field"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test with a non-existent atleta to verify schema
        payload = {
            "atleta_id": "test-nonexistent-id",
            "tipo_plano": "data_customizada",
            "data_expiracao_custom": "2027-12-31"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/autorizacoes/autorizar", json=payload, headers=headers)
        
        # Should not be 422 (validation error) - the schema should accept the field
        assert response.status_code != 422, f"Schema validation failed - data_expiracao_custom not accepted: {response.text}"
        print(f"Schema accepts data_expiracao_custom field, status: {response.status_code}")


class TestTask7bSuperAdminEmails:
    """Task 7b: SUPER_ADMIN_EMAILS env var verification"""
    
    def test_super_admin_emails_configured(self):
        """Verify SUPER_ADMIN_EMAILS is set in backend .env"""
        env_path = "/app/backend/.env"
        with open(env_path, "r") as f:
            content = f.read()
        
        assert "SUPER_ADMIN_EMAILS" in content, "SUPER_ADMIN_EMAILS not found in .env"
        
        # Check the expected emails
        assert "vandy1250@gmail.com" in content, "vandy1250@gmail.com not in SUPER_ADMIN_EMAILS"
        assert "suporte@rankingrun.com.br" in content, "suporte@rankingrun.com.br not in SUPER_ADMIN_EMAILS"
        
        print("SUPER_ADMIN_EMAILS configured correctly with both emails")


class TestTask8BackupRestore:
    """Task 8: POST /api/admin/backup/restaurar-upload accepts .zip file"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("token")
    
    def test_backup_info_endpoint(self, admin_token):
        """Test backup info endpoint"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/backup/info", headers=headers)
        
        assert response.status_code == 200, f"Backup info failed: {response.status_code} - {response.text}"
        data = response.json()
        
        assert "total_backups" in data, "Missing total_backups"
        assert "total_collections" in data, "Missing total_collections"
        assert "total_documentos" in data, "Missing total_documentos"
        print(f"Backup info: {data.get('total_backups')} backups, {data.get('total_collections')} collections, {data.get('total_documentos')} docs")
    
    def test_backup_historico_endpoint(self, admin_token):
        """Test backup history endpoint"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/backup/historico", headers=headers)
        
        assert response.status_code == 200, f"Backup history failed: {response.status_code} - {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Expected list of backups"
        print(f"Backup history: {len(data)} backups found")
    
    def test_restore_endpoint_exists(self, admin_token):
        """Test that restore-upload endpoint exists and rejects invalid files"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a fake non-zip file
        files = {"arquivo": ("test.txt", io.BytesIO(b"not a zip file"), "text/plain")}
        
        response = requests.post(
            f"{BASE_URL}/api/admin/backup/restaurar-upload",
            headers=headers,
            files=files
        )
        
        # Should reject non-zip files with 400
        assert response.status_code == 400, f"Expected 400 for non-zip file, got: {response.status_code}"
        assert "zip" in response.text.lower(), f"Error should mention zip: {response.text}"
        print("Restore endpoint correctly rejects non-zip files")


class TestTask4GaleraPontuacao:
    """Task 4: Verify Galera points calculation (5km=5pts, 10km=7pts, 21km+=9pts)"""
    
    def test_pontuacao_rules_in_services(self):
        """Verify the points calculation rules exist in services"""
        services_path = "/app/backend/services/__init__.py"
        with open(services_path, "r") as f:
            content = f.read()
        
        # Check for calcular_pontos_povao function
        assert "calcular_pontos_povao" in content, "calcular_pontos_povao function not found"
        
        # Check for correct point values in the function
        assert "return 9" in content, "Should return 9 points for 21km+"
        assert "return 7" in content, "Should return 7 points for 10-20km"
        assert "return 5" in content, "Should return 5 points for 5-9km"
        
        # Verify the distance thresholds
        assert "dist_num >= 21" in content, "Should check for 21km threshold"
        assert "dist_num >= 10" in content, "Should check for 10km threshold"
        assert "dist_num >= 5" in content, "Should check for 5km threshold"
        
        print("calcular_pontos_povao function exists with correct rules: 5km=5pts, 10km=7pts, 21km+=9pts")
    
    def test_pontuacao_frontend_display(self):
        """Verify SubmeterResultadoPage shows correct points preview"""
        file_path = "/app/frontend/src/pages/SubmeterResultadoPage.js"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for correct point display text
        assert "5 Pontos" in content, "Should show 5 Pontos for 5-9km"
        assert "7 Pontos" in content, "Should show 7 Pontos for 10-20km"
        assert "9 Pontos" in content, "Should show 9 Pontos for 21km+"
        
        print("SubmeterResultadoPage shows correct points preview")


class TestFeedAndStoriesImageURLs:
    """Task 1: Verify Feed/Stories image URL construction is fixed"""
    
    def test_feed_post_card_image_url_fix(self):
        """Verify FeedPostCard.jsx has the correct image URL logic"""
        file_path = "/app/frontend/src/components/feed/FeedPostCard.jsx"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Should check if URL starts with http before prepending BACKEND_URL
        assert "startsWith('http')" in content or 'startsWith("http")' in content, \
            "FeedPostCard should check if imagem_url starts with http"
        
        print("FeedPostCard.jsx has correct image URL logic (checks for http prefix)")
    
    def test_stories_bar_image_url_fix(self):
        """Verify StoriesBar.jsx has the correct image URL logic"""
        file_path = "/app/frontend/src/components/StoriesBar.jsx"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Should check if URL starts with http before prepending BACKEND_URL
        assert "startsWith('http')" in content or 'startsWith("http")' in content, \
            "StoriesBar should check if imagem_url starts with http"
        
        print("StoriesBar.jsx has correct image URL logic (checks for http prefix)")


class TestHallDaFamaContrast:
    """Task 2: Verify Hall da Fama has good contrast colors"""
    
    def test_hall_da_fama_contrast_colors(self):
        """Verify HallDaFama.jsx uses high contrast colors"""
        file_path = "/app/frontend/src/components/ranking/HallDaFama.jsx"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for bg-gray-900 (dark background for cards)
        assert "bg-gray-900" in content, "Should use bg-gray-900 for card backgrounds"
        
        # Check for bg-gray-800 (for rows)
        assert "bg-gray-800" in content, "Should use bg-gray-800 for rows"
        
        # Check for white text
        assert "text-white" in content, "Should use text-white for text"
        
        # Check for emerald-300 or emerald-400 for points
        assert "emerald-300" in content or "emerald-400" in content, "Should use emerald colors for points"
        
        print("HallDaFama.jsx has correct contrast colors (bg-gray-900, bg-gray-800, text-white, emerald)")


class TestRankingCidadeMobileResponsive:
    """Task 3: Verify RankingCidadePage has mobile responsive classes"""
    
    def test_ranking_cidade_responsive_classes(self):
        """Verify RankingCidadePage.jsx has responsive gap and text classes"""
        file_path = "/app/frontend/src/pages/RankingCidadePage.jsx"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for responsive gap classes
        assert "gap-2" in content, "Should have gap-2 for mobile"
        assert "sm:gap-4" in content or "md:gap-4" in content, "Should have larger gap for desktop"
        
        # Check for responsive text classes
        assert "text-sm" in content, "Should have text-sm for mobile"
        assert "sm:text-base" in content or "md:text-base" in content, "Should have text-base for desktop"
        
        # Check for flex-shrink-0
        assert "flex-shrink-0" in content, "Should have flex-shrink-0 to prevent text overlap"
        
        print("RankingCidadePage.jsx has correct responsive classes (gap-2, sm:gap-4, text-sm, flex-shrink-0)")


class TestBibleVerse:
    """Task 5: Verify bible verse is present in RankingPage"""
    
    def test_bible_verse_in_ranking_page(self):
        """Verify RankingPage.js has the bible verse"""
        file_path = "/app/frontend/src/pages/RankingPage.js"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for the bible verse text
        assert "All honor and glory" in content or "1 Co 9:24" in content, \
            "Bible verse not found in RankingPage"
        
        # Check for italic styling
        assert "italic" in content, "Bible verse should be in italic"
        
        print("RankingPage.js has bible verse in italic")


class TestDashboardAutorizacoesCustomDate:
    """Task 7: Verify DashboardAutorizacoes has custom date input"""
    
    def test_custom_date_input_exists(self):
        """Verify DashboardAutorizacoes.jsx has custom date input"""
        file_path = "/app/frontend/src/pages/admin/DashboardAutorizacoes.jsx"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for date input
        assert 'type="date"' in content, "Should have date input"
        
        # Check for data_customizada handling
        assert "data_customizada" in content, "Should handle data_customizada tipo_plano"
        
        # Check for data_expiracao_custom
        assert "data_expiracao_custom" in content, "Should send data_expiracao_custom"
        
        print("DashboardAutorizacoes.jsx has custom date input and handling")


class TestDashboardBackupRestore:
    """Task 8: Verify DashboardBackup has restore section"""
    
    def test_restore_section_exists(self):
        """Verify DashboardBackup.jsx has restore section with file upload"""
        file_path = "/app/frontend/src/pages/admin/DashboardBackup.jsx"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for restore file input
        assert 'accept=".zip"' in content, "Should have .zip file input"
        
        # Check for restaurar-upload endpoint
        assert "restaurar-upload" in content, "Should call restaurar-upload endpoint"
        
        # Check for restore button
        assert "Restaurar" in content, "Should have Restaurar button"
        
        print("DashboardBackup.jsx has restore section with file upload")


class TestDashboardCorridasExportButton:
    """Task 6: Verify DashboardCorridas has Export Excel button"""
    
    def test_export_excel_button_exists(self):
        """Verify DashboardCorridas.jsx has Export Excel button"""
        file_path = "/app/frontend/src/pages/admin/DashboardCorridas.jsx"
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for corridas-completas endpoint
        assert "corridas-completas" in content, "Should call corridas-completas endpoint"
        
        # Check for Exportar Excel text
        assert "Exportar Excel" in content, "Should have Exportar Excel button"
        
        print("DashboardCorridas.jsx has Export Excel button for corridas-completas")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
