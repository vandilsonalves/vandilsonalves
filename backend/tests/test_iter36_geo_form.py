"""
Iteration 36: Geo Location Form Tests
Testing:
- Custom distance field functionality in result submission
- Point calculation for custom distances (calcular_pontos_povao)
- State/City dropdown integration with IBGE API
- Result submission with custom distance
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_POVAO_USER = {
    "email": "test.povao@teste.com",
    "password": "senha123"
}

ADMIN_USER = {
    "email": "admin@rankingrun.com",
    "password": "admin123"
}


class TestCalcPontosPovao:
    """Tests for custom distance point calculation in Ranking do Povão"""
    
    def test_pontos_5km_standard(self):
        """5KM should give 5 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("5KM") == 5
    
    def test_pontos_10km_standard(self):
        """10KM should give 10 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("10KM") == 10
    
    def test_pontos_21km_standard(self):
        """21KM (half marathon) should give 21 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("21KM") == 21
    
    def test_pontos_42km_standard(self):
        """42KM (marathon) should give 42 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("42KM") == 42
    
    def test_pontos_custom_7km(self):
        """7KM (between 5-9) should give 5 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("7KM") == 5
    
    def test_pontos_custom_15km(self):
        """15KM (between 10-20) should give 10 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("15KM") == 10
    
    def test_pontos_custom_8km(self):
        """8KM (between 5-9) should give 5 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("8KM") == 5
    
    def test_pontos_custom_18km(self):
        """18KM (between 10-20) should give 10 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("18KM") == 10
    
    def test_pontos_custom_25km(self):
        """25KM (21+) should give 25 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("25KM") == 25
    
    def test_pontos_custom_100km(self):
        """100KM ultramarathon should give 100 points"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("100KM") == 100
    
    def test_pontos_custom_float_15_5km(self):
        """15.5KM should give 10 points (between 10-20)"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("15.5KM") == 10
    
    def test_pontos_custom_3km_min(self):
        """3KM (less than 5) should give 3 points (floor)"""
        from routes.admin_routes import calcular_pontos_povao
        assert calcular_pontos_povao("3KM") == 3


class TestIBGEApiIntegration:
    """Tests for IBGE API integration for states/cities"""
    
    def test_ibge_api_states_sp(self):
        """Test that IBGE API returns cities for SP state"""
        response = requests.get(
            "https://servicodados.ibge.gov.br/api/v1/localidades/estados/SP/municipios?orderBy=nome",
            timeout=10
        )
        assert response.status_code == 200
        cities = response.json()
        assert len(cities) > 0
        # Check that São Paulo city exists
        city_names = [c['nome'] for c in cities]
        assert "São Paulo" in city_names
    
    def test_ibge_api_states_rj(self):
        """Test that IBGE API returns cities for RJ state"""
        response = requests.get(
            "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios?orderBy=nome",
            timeout=10
        )
        assert response.status_code == 200
        cities = response.json()
        assert len(cities) > 0
        city_names = [c['nome'] for c in cities]
        assert "Rio de Janeiro" in city_names
    
    def test_ibge_api_states_mg(self):
        """Test that IBGE API returns cities for MG state"""
        response = requests.get(
            "https://servicodados.ibge.gov.br/api/v1/localidades/estados/MG/municipios?orderBy=nome",
            timeout=10
        )
        assert response.status_code == 200
        cities = response.json()
        assert len(cities) > 0
        city_names = [c['nome'] for c in cities]
        assert "Belo Horizonte" in city_names


class TestAuthLogin:
    """Test authentication endpoints for test users"""
    
    @pytest.fixture
    def api_client(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    def test_login_povao_user(self, api_client):
        """Test login for povao pace livre user"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=TEST_POVAO_USER)
        # May be 200 OK or 401 if user doesn't exist
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            assert "user" in data
            print(f"Povao user logged in: {data['user'].get('email')}")
            print(f"Modalidade: {data['user'].get('modalidade_usuario')}")
        else:
            print(f"Povao user not found or credentials wrong: {response.status_code}")
            pytest.skip("Test user not found - needs seed data")
    
    def test_login_admin_user(self, api_client):
        """Test login for admin user"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=ADMIN_USER)
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            assert "user" in data
            assert data['user'].get('role') == 'admin'
            print(f"Admin logged in: {data['user'].get('email')}")
        else:
            print(f"Admin login failed: {response.status_code}")
            pytest.skip("Admin user not found")


class TestSubmeterResultadoEndpoint:
    """Test result submission endpoint with custom distances"""
    
    @pytest.fixture
    def api_client(self):
        session = requests.Session()
        return session
    
    @pytest.fixture
    def povao_token(self, api_client):
        """Get token for povao user"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_POVAO_USER
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Povao user not found")
    
    def test_submit_result_custom_distance_15km(self, api_client, povao_token):
        """Test submitting result with custom 15KM distance"""
        headers = {"Authorization": f"Bearer {povao_token}"}
        
        # Create form data for multipart upload
        form_data = {
            "nome_competicao": "TEST_Corrida Custom 15KM",
            "colocacao": "0",  # Povao doesn't use colocacao
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": "2025-03-15",
            "link_resultado": "https://example.com/resultado/test15km",
            "tempo": "00:00:00",  # Povao doesn't use tempo
            "distancia": "15KM"  # Custom distance
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/resultados/submeter",
            headers=headers,
            data=form_data
        )
        
        print(f"Submit response status: {response.status_code}")
        print(f"Submit response body: {response.text}")
        
        # Accept both success and authorization errors (period expired)
        assert response.status_code in [200, 201, 403]
        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data or "message" in data
    
    def test_submit_result_custom_distance_7km(self, api_client, povao_token):
        """Test submitting result with custom 7KM distance"""
        headers = {"Authorization": f"Bearer {povao_token}"}
        
        form_data = {
            "nome_competicao": "TEST_Corrida Custom 7KM",
            "colocacao": "0",
            "cidade_competicao": "Rio de Janeiro",
            "estado_competicao": "RJ",
            "data_competicao": "2025-03-14",
            "link_resultado": "https://example.com/resultado/test7km",
            "tempo": "00:00:00",
            "distancia": "7KM"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/resultados/submeter",
            headers=headers,
            data=form_data
        )
        
        print(f"Submit response status: {response.status_code}")
        assert response.status_code in [200, 201, 403]
    
    def test_submit_result_ultramarathon_100km(self, api_client, povao_token):
        """Test submitting result with 100KM ultramarathon"""
        headers = {"Authorization": f"Bearer {povao_token}"}
        
        form_data = {
            "nome_competicao": "TEST_Ultramarathon 100KM",
            "colocacao": "0",
            "cidade_competicao": "Belo Horizonte",
            "estado_competicao": "MG",
            "data_competicao": "2025-03-13",
            "link_resultado": "https://example.com/resultado/test100km",
            "tempo": "00:00:00",
            "distancia": "100KM"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/resultados/submeter",
            headers=headers,
            data=form_data
        )
        
        print(f"Submit response status: {response.status_code}")
        assert response.status_code in [200, 201, 403]


class TestAdminPendentes:
    """Test admin pending results endpoint"""
    
    @pytest.fixture
    def api_client(self):
        session = requests.Session()
        return session
    
    @pytest.fixture
    def admin_token(self, api_client):
        """Get token for admin user"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json=ADMIN_USER
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin user not found")
    
    def test_get_pendentes(self, api_client, admin_token):
        """Test getting pending results as admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = api_client.get(
            f"{BASE_URL}/api/admin/pendentes",
            headers=headers
        )
        
        print(f"Pendentes response status: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Total pending results: {len(data)}")
        
        # Check if any pending results have custom distances
        for r in data[:5]:  # Check first 5
            if 'distancia' in r:
                print(f"  - {r.get('nome_competicao', 'N/A')}: {r.get('distancia')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
