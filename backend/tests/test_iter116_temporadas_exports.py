"""
Iteration 116: Test Temporadas (Season Management) and Ranking Export Endpoints
Features:
1. 4 new ranking export Excel endpoints
2. Complete Season Management System (temporadas_routes.py)
3. Frontend: DashboardTemporadas in admin sidebar, HistoricoTemporadasPage
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
MASTER_PASSWORD = "d7ff103ad1250@#$"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {admin_token}"}


# ==================== PUBLIC TEMPORADAS ENDPOINTS ====================

class TestTemporadasPublic:
    """Test public temporadas endpoints (no auth required)"""

    def test_get_temporada_ativa(self):
        """GET /api/temporadas/ativa - Returns current active season"""
        response = requests.get(f"{BASE_URL}/api/temporadas/ativa")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "season_id" in data, "Response should contain season_id"
        assert "status" in data, "Response should contain status"
        assert data["status"] == "ativa", f"Expected status 'ativa', got {data['status']}"
        
        # Verify season_id is current year (2026)
        current_year = datetime.now().year
        assert data["season_id"] == current_year, f"Expected season_id {current_year}, got {data['season_id']}"
        
        print(f"✓ Active season: {data['season_id']} ({data['status']})")

    def test_get_historico_temporadas(self):
        """GET /api/temporadas/historico - Returns list of all seasons"""
        response = requests.get(f"{BASE_URL}/api/temporadas/historico")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "temporadas" in data, "Response should contain 'temporadas' list"
        assert isinstance(data["temporadas"], list), "temporadas should be a list"
        
        # Should have at least the current active season
        assert len(data["temporadas"]) >= 1, "Should have at least one season"
        
        # Verify structure of first season
        if data["temporadas"]:
            season = data["temporadas"][0]
            assert "season_id" in season, "Season should have season_id"
            assert "status" in season, "Season should have status"
            
        print(f"✓ Found {len(data['temporadas'])} temporadas in history")


# ==================== ADMIN TEMPORADAS ENDPOINTS ====================

class TestTemporadasAdmin:
    """Test admin temporadas endpoints (auth required)"""

    def test_get_admin_temporadas(self, admin_headers):
        """GET /api/admin/temporadas - Returns seasons list with pode_encerrar flag"""
        response = requests.get(f"{BASE_URL}/api/admin/temporadas", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "temporadas" in data, "Response should contain 'temporadas'"
        assert "temporada_ativa" in data, "Response should contain 'temporada_ativa'"
        assert "pode_encerrar" in data, "Response should contain 'pode_encerrar' flag"
        assert "data_atual" in data, "Response should contain 'data_atual'"
        
        # pode_encerrar should be boolean
        assert isinstance(data["pode_encerrar"], bool), "pode_encerrar should be boolean"
        
        # Verify temporada_ativa structure
        ativa = data["temporada_ativa"]
        assert "season_id" in ativa, "temporada_ativa should have season_id"
        assert ativa["status"] == "ativa", "temporada_ativa status should be 'ativa'"
        
        print(f"✓ Admin temporadas: {len(data['temporadas'])} seasons, pode_encerrar={data['pode_encerrar']}")

    def test_encerrar_temporada_blocked_by_date(self, admin_headers):
        """POST /api/admin/temporadas/encerrar - Should be blocked outside Jan 1-2"""
        current_date = datetime.now()
        
        # This test expects 403 because we're not in Jan 1-2 window
        response = requests.post(
            f"{BASE_URL}/api/admin/temporadas/encerrar",
            headers=admin_headers,
            json={
                "confirmacao": f"ENCERRAR {current_date.year}",
                "senha_master": MASTER_PASSWORD
            }
        )
        
        # Should be blocked by date window (403) unless we're in Jan 1-2
        if current_date.month == 1 and current_date.day <= 2:
            # If we're in the window, it might succeed or fail for other reasons
            assert response.status_code in [200, 400, 403], f"Unexpected status: {response.status_code}"
        else:
            assert response.status_code == 403, f"Expected 403 (date blocked), got {response.status_code}: {response.text}"
            data = response.json()
            assert "detail" in data, "Error response should have detail"
            assert "janeiro" in data["detail"].lower() or "jan" in data["detail"].lower(), \
                f"Error should mention January restriction: {data['detail']}"
        
        print(f"✓ Encerrar temporada correctly blocked by date (current: {current_date.strftime('%d/%m/%Y')})")

    def test_encerrar_temporada_wrong_confirmation(self, admin_headers):
        """POST /api/admin/temporadas/encerrar - Should fail with wrong confirmation text"""
        response = requests.post(
            f"{BASE_URL}/api/admin/temporadas/encerrar",
            headers=admin_headers,
            json={
                "confirmacao": "WRONG TEXT",
                "senha_master": MASTER_PASSWORD
            }
        )
        
        # Should fail - either 400 (wrong confirmation) or 403 (date blocked first)
        assert response.status_code in [400, 403], f"Expected 400 or 403, got {response.status_code}: {response.text}"
        print(f"✓ Encerrar temporada correctly rejects wrong confirmation")

    def test_encerrar_temporada_wrong_password(self, admin_headers):
        """POST /api/admin/temporadas/encerrar - Should fail with wrong master password"""
        current_year = datetime.now().year
        response = requests.post(
            f"{BASE_URL}/api/admin/temporadas/encerrar",
            headers=admin_headers,
            json={
                "confirmacao": f"ENCERRAR {current_year}",
                "senha_master": "wrong_password"
            }
        )
        
        # Should fail - either 403 (wrong password or date blocked)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print(f"✓ Encerrar temporada correctly rejects wrong master password")


# ==================== RANKING EXPORT ENDPOINTS ====================

class TestRankingExports:
    """Test the 4 new ranking export Excel endpoints"""

    def test_export_ranking_profissional(self, admin_headers):
        """GET /api/admin/exportar/ranking-profissional - Returns Excel file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/exportar/ranking-profissional",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify Content-Type is Excel
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheetml" in content_type or "excel" in content_type.lower(), \
            f"Expected Excel content type, got: {content_type}"
        
        # Verify Content-Disposition header for download
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, f"Expected attachment disposition, got: {content_disp}"
        assert "ranking_profissional" in content_disp, f"Filename should contain 'ranking_profissional': {content_disp}"
        assert ".xlsx" in content_disp, f"Filename should be .xlsx: {content_disp}"
        
        # Verify content is not empty
        assert len(response.content) > 0, "Excel file should not be empty"
        
        print(f"✓ Ranking Profissional export: {len(response.content)} bytes, {content_disp}")

    def test_export_ranking_galera(self, admin_headers):
        """GET /api/admin/exportar/ranking-galera - Returns Excel file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/exportar/ranking-galera",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify Content-Type is Excel
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheetml" in content_type or "excel" in content_type.lower(), \
            f"Expected Excel content type, got: {content_type}"
        
        # Verify Content-Disposition header
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, f"Expected attachment disposition, got: {content_disp}"
        assert "ranking_galera" in content_disp, f"Filename should contain 'ranking_galera': {content_disp}"
        
        print(f"✓ Ranking Galera export: {len(response.content)} bytes")

    def test_export_ranking_assessorias(self, admin_headers):
        """GET /api/admin/exportar/ranking-assessorias - Returns Excel file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/exportar/ranking-assessorias",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify Content-Type is Excel
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheetml" in content_type or "excel" in content_type.lower(), \
            f"Expected Excel content type, got: {content_type}"
        
        # Verify Content-Disposition header
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, f"Expected attachment disposition, got: {content_disp}"
        assert "ranking_assessorias" in content_disp, f"Filename should contain 'ranking_assessorias': {content_disp}"
        
        print(f"✓ Ranking Assessorias export: {len(response.content)} bytes")

    def test_export_ranking_corridas_avaliadas(self, admin_headers):
        """GET /api/admin/exportar/ranking-corridas-avaliadas - Returns Excel file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/exportar/ranking-corridas-avaliadas",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify Content-Type is Excel
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheetml" in content_type or "excel" in content_type.lower(), \
            f"Expected Excel content type, got: {content_type}"
        
        # Verify Content-Disposition header
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, f"Expected attachment disposition, got: {content_disp}"
        assert "ranking_corridas_avaliadas" in content_disp, f"Filename should contain 'ranking_corridas_avaliadas': {content_disp}"
        
        print(f"✓ Ranking Corridas Avaliadas export: {len(response.content)} bytes")


# ==================== AUTH VALIDATION ====================

class TestAuthValidation:
    """Test that endpoints require proper authentication"""

    def test_admin_temporadas_requires_auth(self):
        """GET /api/admin/temporadas - Should require auth"""
        response = requests.get(f"{BASE_URL}/api/admin/temporadas")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Admin temporadas requires authentication")

    def test_encerrar_temporada_requires_auth(self):
        """POST /api/admin/temporadas/encerrar - Should require auth"""
        response = requests.post(
            f"{BASE_URL}/api/admin/temporadas/encerrar",
            json={"confirmacao": "test", "senha_master": "test"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Encerrar temporada requires authentication")

    def test_export_ranking_requires_auth(self):
        """Export endpoints should require admin auth"""
        endpoints = [
            "/api/admin/exportar/ranking-profissional",
            "/api/admin/exportar/ranking-galera",
            "/api/admin/exportar/ranking-assessorias",
            "/api/admin/exportar/ranking-corridas-avaliadas"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code in [401, 403], \
                f"{endpoint} should require auth, got {response.status_code}"
        
        print(f"✓ All {len(endpoints)} export endpoints require authentication")


# ==================== RANKING FINAL ENDPOINT ====================

class TestRankingFinal:
    """Test ranking final endpoint for finished seasons"""

    def test_ranking_final_not_found_for_active_season(self):
        """GET /api/temporadas/{season_id}/ranking-final - Should return 404 for active season without snapshot"""
        current_year = datetime.now().year
        response = requests.get(f"{BASE_URL}/api/temporadas/{current_year}/ranking-final")
        
        # Active season won't have a snapshot yet, so expect 404
        # Unless a snapshot was manually created
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}: {response.text}"
        
        if response.status_code == 404:
            print(f"✓ Ranking final for active season {current_year} correctly returns 404 (no snapshot)")
        else:
            data = response.json()
            assert "season_id" in data, "Response should contain season_id"
            print(f"✓ Ranking final for season {current_year} found (snapshot exists)")

    def test_ranking_final_nonexistent_season(self):
        """GET /api/temporadas/{season_id}/ranking-final - Should return 404 for nonexistent season"""
        response = requests.get(f"{BASE_URL}/api/temporadas/1900/ranking-final")
        assert response.status_code == 404, f"Expected 404 for nonexistent season, got {response.status_code}"
        print("✓ Ranking final correctly returns 404 for nonexistent season")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
