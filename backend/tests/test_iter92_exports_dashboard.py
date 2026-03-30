"""
Iteration 92: Testing Export functionality and Dashboard Estratégico
- Export Atletas (Excel)
- Export Ranking (Excel/CSV)
- Dashboard Estratégico endpoints
- Brazil Map data
- Pie charts (Tipo de Corredor, Terreno Preferido)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://geo-filtered-admin.preview.emergentagent.com')

class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        return data["token"]
    
    def test_admin_login(self, admin_token):
        """Test admin login returns valid token"""
        assert admin_token is not None
        assert len(admin_token) > 0
        print(f"Admin token obtained successfully")


class TestExportAtletas:
    """Test Export Atletas functionality"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    def test_export_atletas_excel(self, admin_token):
        """Test Export Atletas returns Excel file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas/export",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Export failed: {response.status_code}"
        assert len(response.content) > 1000, "Export file too small"
        # Check content type
        content_type = response.headers.get('content-type', '')
        assert 'spreadsheet' in content_type or 'octet-stream' in content_type, f"Wrong content type: {content_type}"
        print(f"Export Atletas: {len(response.content)} bytes")


class TestExportRanking:
    """Test Export Ranking functionality"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    def test_export_ranking_excel(self, admin_token):
        """Test Export Ranking Excel returns valid file"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/export/excel",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"todas_modalidades": True}
        )
        assert response.status_code == 200, f"Export failed: {response.status_code}"
        assert len(response.content) > 1000, "Export file too small"
        print(f"Export Ranking Excel: {len(response.content)} bytes")
    
    def test_export_ranking_csv(self, admin_token):
        """Test Export Ranking CSV returns valid file"""
        response = requests.get(
            f"{BASE_URL}/api/ranking/export/csv",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"todas_modalidades": True}
        )
        assert response.status_code == 200, f"Export failed: {response.status_code}"
        assert len(response.content) > 1000, "Export file too small"
        print(f"Export Ranking CSV: {len(response.content)} bytes")


class TestDashboardEstrategico:
    """Test Dashboard Estratégico endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    def test_visao_geral(self, admin_token):
        """Test Dashboard Visao Geral returns stats"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/visao-geral",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_atletas" in data
        assert "total_corridas" in data
        assert data["total_atletas"] > 0
        print(f"Visao Geral: {data['total_atletas']} atletas, {data['total_corridas']} corridas")
    
    def test_distribuicao_estados_brazil_map(self, admin_token):
        """Test Brazil Map data (Distribuição por Estado)"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/grafico/distribuicao-estados",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "dados" in data
        assert len(data["dados"]) > 0
        # Check state data structure
        first_state = data["dados"][0]
        assert "estado" in first_state
        assert "count" in first_state
        print(f"Brazil Map: {len(data['dados'])} states with data")
    
    def test_tipo_corredor_pie_chart(self, admin_token):
        """Test Tipo de Corredor pie chart data"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/grafico/distribuicao-tipo-corredor",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "dados" in data
        assert "titulo" in data
        assert data["titulo"] == "Tipo de Corredor"
        print(f"Tipo de Corredor: {len(data['dados'])} types")
    
    def test_terreno_preferido_pie_chart(self, admin_token):
        """Test Terreno Preferido pie chart data"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/grafico/distribuicao-terreno-preferido",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "dados" in data
        assert "titulo" in data
        assert data["titulo"] == "Terreno Preferido"
        print(f"Terreno Preferido: {len(data['dados'])} terrains")
    
    def test_crescimento_atletas(self, admin_token):
        """Test Crescimento de Atletas chart data"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/grafico/crescimento-atletas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "dados" in data
        assert len(data["dados"]) > 0
        print(f"Crescimento Atletas: {len(data['dados'])} months of data")


class TestAdminStats:
    """Test Admin Stats endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    def test_admin_stats(self, admin_token):
        """Test Admin Stats returns correct data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_atletas" in data or "atletas" in data
        print(f"Admin Stats: {data}")
    
    def test_admin_atletas_list(self, admin_token):
        """Test Admin Atletas list with search"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        # Check if atletas are returned
        atletas = data.get("atletas", data)
        assert len(atletas) > 0
        # Check atleta has email field for search
        first_atleta = atletas[0]
        assert "email" in first_atleta
        print(f"Admin Atletas: {len(atletas)} returned")


class TestInstagramDashboard:
    """Test Instagram Dashboard (Ranking Run Inside) - KeyError fix"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        return response.json()["token"]
    
    def test_instagram_historico(self, admin_token):
        """Test Instagram historico endpoint doesn't return 500"""
        response = requests.get(
            f"{BASE_URL}/api/instagram/historico",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should not be 500
        assert response.status_code != 500, f"Got 500 error: {response.text}"
        # Should be 200 or 404 (if no data)
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print(f"Instagram Historico: Status {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
