"""
Iteration 66: Test new Estado and Cidade filters for Admin Mensagens
Tests:
1. GET /api/admin/mensagens/estados-disponiveis - Returns list of states
2. GET /api/admin/mensagens/cidades-disponiveis?estado=PE - Returns cities for PE
3. GET /api/admin/mensagens/contagem-destinatarios with filtro_estados
4. GET /api/admin/mensagens/contagem-destinatarios with filtro_cidades
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEstadoCidadeFilters:
    """Test new Estado and Cidade filter endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        data = login_response.json()
        self.token = data.get("token")
        assert self.token, "No token received"
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        print(f"✅ Admin login successful")
    
    def test_01_estados_disponiveis_endpoint(self):
        """Test GET /api/admin/mensagens/estados-disponiveis returns list of states"""
        response = self.session.get(f"{BASE_URL}/api/admin/mensagens/estados-disponiveis")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "estados" in data, "Response should have 'estados' key"
        assert isinstance(data["estados"], list), "estados should be a list"
        
        estados = data["estados"]
        print(f"✅ Found {len(estados)} estados: {estados}")
        
        # Check if PE is in the list (as mentioned in test requirements)
        if "PE" in estados:
            print("✅ PE (Pernambuco) is in the list")
        else:
            print("⚠️ PE not found in estados list")
        
        return estados
    
    def test_02_cidades_disponiveis_sem_estado(self):
        """Test GET /api/admin/mensagens/cidades-disponiveis without estado param"""
        response = self.session.get(f"{BASE_URL}/api/admin/mensagens/cidades-disponiveis")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "cidades" in data, "Response should have 'cidades' key"
        assert isinstance(data["cidades"], list), "cidades should be a list"
        
        print(f"✅ Found {len(data['cidades'])} cidades (all states)")
    
    def test_03_cidades_disponiveis_para_PE(self):
        """Test GET /api/admin/mensagens/cidades-disponiveis?estado=PE returns PE cities"""
        response = self.session.get(f"{BASE_URL}/api/admin/mensagens/cidades-disponiveis?estado=PE")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "cidades" in data, "Response should have 'cidades' key"
        assert isinstance(data["cidades"], list), "cidades should be a list"
        
        cidades = data["cidades"]
        print(f"✅ Found {len(cidades)} cidades in PE: {cidades}")
        
        # Check for expected cities mentioned in requirements
        expected_cities = ["Caruaru", "Jaboatão", "Olinda", "Recife"]
        for city in expected_cities:
            if city in cidades:
                print(f"  ✅ {city} found")
            else:
                print(f"  ⚠️ {city} not found in PE cities")
        
        return cidades
    
    def test_04_contagem_todos(self):
        """Test contagem with filtro_tipo=todos"""
        params = {
            "filtro_tipo": "todos",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": "[]",
            "filtro_estados": "[]",
            "filtro_cidades": "[]"
        }
        response = self.session.get(f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total" in data, "Response should have 'total' key"
        total_todos = data["total"]
        print(f"✅ Total atletas (todos): {total_todos}")
        
        return total_todos
    
    def test_05_contagem_por_estado_PE(self):
        """Test contagem with filtro_tipo=estado and filtro_estados=["PE"]"""
        params = {
            "filtro_tipo": "estado",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": "[]",
            "filtro_estados": json.dumps(["PE"]),
            "filtro_cidades": "[]"
        }
        response = self.session.get(f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total" in data, "Response should have 'total' key"
        total_pe = data["total"]
        print(f"✅ Total atletas in PE: {total_pe}")
        
        # Should be less than total
        return total_pe
    
    def test_06_contagem_por_cidade_Recife(self):
        """Test contagem with filtro_tipo=cidade and filtro_cidades=["Recife"]"""
        params = {
            "filtro_tipo": "cidade",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": "[]",
            "filtro_estados": "[]",
            "filtro_cidades": json.dumps(["Recife"])
        }
        response = self.session.get(f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total" in data, "Response should have 'total' key"
        total_recife = data["total"]
        print(f"✅ Total atletas in Recife: {total_recife}")
        
        return total_recife
    
    def test_07_contagem_comparison(self):
        """Verify that contagem decreases: todos > PE > Recife"""
        # Get todos
        params_todos = {
            "filtro_tipo": "todos",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": "[]",
            "filtro_estados": "[]",
            "filtro_cidades": "[]"
        }
        resp_todos = self.session.get(f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios", params=params_todos)
        total_todos = resp_todos.json()["total"]
        
        # Get PE
        params_pe = {
            "filtro_tipo": "estado",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": "[]",
            "filtro_estados": json.dumps(["PE"]),
            "filtro_cidades": "[]"
        }
        resp_pe = self.session.get(f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios", params=params_pe)
        total_pe = resp_pe.json()["total"]
        
        # Get Recife
        params_recife = {
            "filtro_tipo": "cidade",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": "[]",
            "filtro_estados": "[]",
            "filtro_cidades": json.dumps(["Recife"])
        }
        resp_recife = self.session.get(f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios", params=params_recife)
        total_recife = resp_recife.json()["total"]
        
        print(f"✅ Contagem comparison:")
        print(f"   Todos: {total_todos}")
        print(f"   PE: {total_pe}")
        print(f"   Recife: {total_recife}")
        
        # Verify hierarchy
        assert total_todos >= total_pe, f"Total todos ({total_todos}) should be >= PE ({total_pe})"
        assert total_pe >= total_recife, f"Total PE ({total_pe}) should be >= Recife ({total_recife})"
        print(f"✅ Hierarchy verified: {total_todos} >= {total_pe} >= {total_recife}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
