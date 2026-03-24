"""
Iteration 70: Geographic Filters and Distance Fix Tests
Tests for:
1. GET /api/admin/atletas?limit=1000 returns atletas with estado and cidade fields
2. GET /api/raio-x/completo returns evolucao.totais.distancia_total_km > 0 for atletas with corridas
3. extrair_distancia function in raio_x_routes.py
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminAtletasGeoFields:
    """Test admin atletas endpoint returns estado and cidade fields"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.admin_token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_admin_atletas_returns_estado_field(self):
        """Test that atletas have estado field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas?limit=10",
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed to get atletas: {response.text}"
        
        data = response.json()
        assert "atletas" in data, "Response should have 'atletas' key"
        
        atletas = data["atletas"]
        assert len(atletas) > 0, "Should have at least one atleta"
        
        # Check that atletas have estado field
        for atleta in atletas[:5]:
            assert "estado" in atleta, f"Atleta {atleta.get('nome')} missing 'estado' field"
    
    def test_admin_atletas_returns_cidade_field(self):
        """Test that atletas have cidade field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas?limit=10",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        atletas = data["atletas"]
        
        # Check that atletas have cidade field
        for atleta in atletas[:5]:
            assert "cidade" in atleta, f"Atleta {atleta.get('nome')} missing 'cidade' field"
    
    def test_admin_atletas_limit_1000(self):
        """Test that limit=1000 works correctly"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas?limit=1000",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "atletas" in data
        assert "total" in data
        
        # Should return atletas up to limit
        atletas = data["atletas"]
        assert len(atletas) <= 1000, "Should not exceed limit"
        print(f"Total atletas returned: {len(atletas)}, Total in DB: {data['total']}")
    
    def test_atletas_have_valid_estado_values(self):
        """Test that estado values are valid Brazilian states"""
        valid_estados = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO', '', None
        ]
        
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas?limit=100",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        atletas = data["atletas"]
        
        for atleta in atletas:
            estado = atleta.get("estado")
            assert estado in valid_estados or estado is None, f"Invalid estado: {estado}"
    
    def test_atletas_from_sp_exist(self):
        """Test that there are atletas from SP (São Paulo)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/atletas?limit=1000",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        atletas = data["atletas"]
        
        sp_atletas = [a for a in atletas if a.get("estado") == "SP"]
        assert len(sp_atletas) > 0, "Should have atletas from SP"
        print(f"Found {len(sp_atletas)} atletas from SP")


class TestRaioXDistanciaFix:
    """Test raio-x/completo returns correct distancia_total_km"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as atleta and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teste.dono@teste.com",
            "password": "123456"
        })
        assert response.status_code == 200, f"Atleta login failed: {response.text}"
        self.atleta_token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.atleta_token}"}
    
    def test_raio_x_completo_returns_distancia_total(self):
        """Test that raio-x/completo returns distancia_total_km > 0"""
        response = requests.get(
            f"{BASE_URL}/api/raio-x/completo",
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed to get raio-x: {response.text}"
        
        data = response.json()
        assert "evolucao" in data, "Response should have 'evolucao' key"
        
        evolucao = data["evolucao"]
        assert evolucao.get("tem_dados") == True, "Should have data"
        
        totais = evolucao.get("totais", {})
        distancia_total = totais.get("distancia_total_km", 0)
        
        assert distancia_total > 0, f"distancia_total_km should be > 0, got {distancia_total}"
        print(f"distancia_total_km: {distancia_total}")
    
    def test_raio_x_evolucao_endpoint(self):
        """Test raio-x/evolucao endpoint directly"""
        response = requests.get(
            f"{BASE_URL}/api/raio-x/evolucao?periodo=12_meses",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("tem_dados") == True
        
        totais = data.get("totais", {})
        distancia_total = totais.get("distancia_total_km", 0)
        
        assert distancia_total > 0, f"distancia_total_km should be > 0"
        print(f"Evolucao distancia_total_km: {distancia_total}")
    
    def test_raio_x_records_endpoint(self):
        """Test raio-x/records endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/raio-x/records",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "records" in data
    
    def test_raio_x_score_endpoint(self):
        """Test raio-x/score endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/raio-x/score",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "score_mes_atual" in data
    
    def test_raio_x_comparativo_endpoint(self):
        """Test raio-x/comparativo endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/raio-x/comparativo",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "mes_atual" in data
        assert "mes_anterior" in data


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] == "admin"
    
    def test_atleta_login(self):
        """Test atleta login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teste.dono@teste.com",
            "password": "123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
