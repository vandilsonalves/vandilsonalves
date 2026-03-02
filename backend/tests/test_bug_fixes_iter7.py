"""
Test suite for Bug Fixes Iteration 7:
1. Bug Fix: /api/ranking/semanal should not return Povão athletes
2. Bug Fix: /api/ranking/mensal should not return Povão athletes  
3. Feature: Admin Dashboard new charts and stats
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

# Read from .env file directly
def get_base_url():
    env_path = '/app/frontend/.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip().rstrip('/')
    return os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

BASE_URL = get_base_url()
API = f"{BASE_URL}/api"

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin123"


class TestAuth:
    """Authentication tests"""
    
    def test_admin_login(self):
        """Admin should be able to login"""
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful")
        return data["token"]


class TestRankingSemanalBugFix:
    """Bug Fix: /api/ranking/semanal should not return Povão athletes"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_ranking_semanal_endpoint_works(self, admin_token):
        """Ranking semanal endpoint should return 200"""
        response = requests.get(f"{API}/ranking/semanal?categoria=masculino")
        assert response.status_code == 200
        data = response.json()
        assert "periodo" in data
        assert "categoria" in data
        assert "ranking" in data
        print(f"✓ Ranking semanal endpoint works - Periodo: {data['periodo']}")
    
    def test_ranking_semanal_filters_by_categoria(self, admin_token):
        """Ranking semanal should filter by categoria parameter"""
        for categoria in ["masculino", "feminino", "pcd-m", "pcd-f", "cadeirante-m", "cadeirante-f"]:
            response = requests.get(f"{API}/ranking/semanal?categoria={categoria}")
            assert response.status_code == 200
            data = response.json()
            assert data["categoria"] == categoria
            print(f"✓ Ranking semanal works for categoria: {categoria}")
    
    def test_ranking_semanal_structure(self, admin_token):
        """Ranking semanal should have correct response structure"""
        response = requests.get(f"{API}/ranking/semanal?categoria=masculino")
        data = response.json()
        
        # Verify structure
        assert "periodo" in data
        assert "categoria" in data
        assert "ranking" in data
        assert isinstance(data["ranking"], list)
        
        # If there are results, verify ranking item structure
        if len(data["ranking"]) > 0:
            item = data["ranking"][0]
            expected_fields = ["posicao", "atleta_id", "nome", "equipe", "cidade", "estado", "foto_url", "pontos_semana", "corridas_semana"]
            for field in expected_fields:
                assert field in item, f"Missing field: {field}"
        
        print(f"✓ Ranking semanal has correct structure")


class TestRankingMensalBugFix:
    """Bug Fix: /api/ranking/mensal should not return Povão athletes"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_ranking_mensal_endpoint_works(self, admin_token):
        """Ranking mensal endpoint should return 200"""
        response = requests.get(f"{API}/ranking/mensal?categoria=masculino")
        assert response.status_code == 200
        data = response.json()
        assert "mes" in data
        assert "ano" in data
        assert "categoria" in data
        assert "ranking" in data
        print(f"✓ Ranking mensal endpoint works - Mes: {data['mes']} {data['ano']}")
    
    def test_ranking_mensal_filters_by_categoria(self, admin_token):
        """Ranking mensal should filter by categoria parameter"""
        for categoria in ["masculino", "feminino", "pcd-m", "pcd-f", "cadeirante-m", "cadeirante-f"]:
            response = requests.get(f"{API}/ranking/mensal?categoria={categoria}")
            assert response.status_code == 200
            data = response.json()
            assert data["categoria"] == categoria
            print(f"✓ Ranking mensal works for categoria: {categoria}")
    
    def test_ranking_mensal_accepts_mes_ano_params(self, admin_token):
        """Ranking mensal should accept mes and ano parameters"""
        response = requests.get(f"{API}/ranking/mensal?categoria=masculino&mes=1&ano=2025")
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == "Janeiro"
        assert data["ano"] == 2025
        print(f"✓ Ranking mensal accepts mes and ano params")
    
    def test_ranking_mensal_structure(self, admin_token):
        """Ranking mensal should have correct response structure"""
        response = requests.get(f"{API}/ranking/mensal?categoria=masculino")
        data = response.json()
        
        # Verify structure
        assert "mes" in data
        assert "ano" in data
        assert "categoria" in data
        assert "ranking" in data
        assert isinstance(data["ranking"], list)
        
        # If there are results, verify ranking item structure
        if len(data["ranking"]) > 0:
            item = data["ranking"][0]
            expected_fields = ["posicao", "atleta_id", "nome", "equipe", "cidade", "estado", "foto_url", "pontos_mes", "corridas_mes"]
            for field in expected_fields:
                assert field in item, f"Missing field: {field}"
        
        print(f"✓ Ranking mensal has correct structure")


class TestAdminDashboardStats:
    """Feature: Admin Dashboard new charts and stats"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_admin_stats_endpoint(self, admin_token):
        """Admin stats endpoint should return data"""
        response = requests.get(f"{API}/admin/stats", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_atletas" in data
        assert "resultados_pendentes" in data
        assert "total_corridas" in data
        assert "total_homens" in data
        assert "total_mulheres" in data
        print(f"✓ Admin stats: {data['total_atletas']} atletas, {data['total_corridas']} corridas")
    
    def test_admin_stats_estados(self, admin_token):
        """Admin should be able to get athletes by state"""
        response = requests.get(f"{API}/admin/stats/estados", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin stats estados: {len(data)} states with athletes")
    
    def test_admin_stats_categorias(self, admin_token):
        """Admin should be able to get athletes by category"""
        response = requests.get(f"{API}/admin/stats/categorias", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Check category fields exist
        expected_fields = ["normal_m", "normal_f", "pcd_m", "pcd_f", "cadeirante_m", "cadeirante_f"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        print(f"✓ Admin stats categorias: Normal M={data['normal_m']}, Normal F={data['normal_f']}")
    
    def test_admin_stats_faixa_etaria(self, admin_token):
        """Admin should be able to get athletes by age range"""
        response = requests.get(f"{API}/admin/stats/faixa-etaria", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin stats faixa etaria: {len(data)} age ranges")
    
    def test_admin_stats_corridas_por_mes(self, admin_token):
        """Admin should be able to get races by month"""
        response = requests.get(f"{API}/admin/stats/corridas-por-mes", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin stats corridas por mes: {len(data)} months with data")
    
    def test_povao_stats_endpoint(self, admin_token):
        """Povão stats endpoint should return data for dashboard"""
        response = requests.get(f"{API}/ranking/povao/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields for Povão stats
        assert "total_atletas" in data
        assert "total_atletas_masculino" in data
        assert "total_atletas_feminino" in data
        assert "total_provas" in data
        assert "total_pontos" in data
        print(f"✓ Povão stats: {data['total_atletas']} atletas, {data['total_provas']} provas")


class TestPovaoAthleteFiltering:
    """Verify that Povão athletes are not mixed with Profissional/Amador rankings"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_povao_ranking_separate_from_semanal(self, admin_token):
        """Povão ranking should be completely separate from semanal ranking"""
        # Get Povão ranking
        povao_response = requests.get(f"{API}/ranking/povao?genero=M")
        assert povao_response.status_code == 200
        povao_data = povao_response.json()
        povao_ids = [a["atleta_id"] for a in povao_data.get("ranking", [])]
        
        # Get Semanal ranking
        semanal_response = requests.get(f"{API}/ranking/semanal?categoria=masculino")
        assert semanal_response.status_code == 200
        semanal_data = semanal_response.json()
        semanal_ids = [a["atleta_id"] for a in semanal_data.get("ranking", [])]
        
        # Verify no overlap
        overlap = set(povao_ids) & set(semanal_ids)
        assert len(overlap) == 0, f"Found overlap between Povão and Semanal rankings: {overlap}"
        print(f"✓ No overlap between Povão ({len(povao_ids)} athletes) and Semanal ({len(semanal_ids)} athletes)")
    
    def test_povao_ranking_separate_from_mensal(self, admin_token):
        """Povão ranking should be completely separate from mensal ranking"""
        # Get Povão ranking
        povao_response = requests.get(f"{API}/ranking/povao?genero=M")
        assert povao_response.status_code == 200
        povao_data = povao_response.json()
        povao_ids = [a["atleta_id"] for a in povao_data.get("ranking", [])]
        
        # Get Mensal ranking
        mensal_response = requests.get(f"{API}/ranking/mensal?categoria=masculino")
        assert mensal_response.status_code == 200
        mensal_data = mensal_response.json()
        mensal_ids = [a["atleta_id"] for a in mensal_data.get("ranking", [])]
        
        # Verify no overlap
        overlap = set(povao_ids) & set(mensal_ids)
        assert len(overlap) == 0, f"Found overlap between Povão and Mensal rankings: {overlap}"
        print(f"✓ No overlap between Povão ({len(povao_ids)} athletes) and Mensal ({len(mensal_ids)} athletes)")


class TestAdminPendentes:
    """Test Admin Pendentes (Approvals) functionality"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["token"]
    
    def test_admin_can_list_pendentes(self, admin_token):
        """Admin should be able to list pending results"""
        response = requests.get(f"{API}/admin/pendentes", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin can list pendentes: {len(data)} pending results")
        
        # If there are pending results, verify structure
        if len(data) > 0:
            item = data[0]
            # Check if foto_podio_url field exists (for photo viewing feature)
            assert "id" in item
            assert "nome_competicao" in item
            if "foto_podio_url" in item:
                print(f"  - Pending result has foto_podio_url field: {item.get('foto_podio_url', 'N/A')[:50]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
