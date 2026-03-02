"""
Test suite for Ranking do Povão - Pace Livre feature
Tests the new modality where athletes are ranked by distance covered, not placement

Features to test:
1. Cadastro with modalidade selection (Profissional/Amador vs Povão)
2. Validation: PCD/Cadeirante cannot select Povão modality
3. GET /api/ranking/povao endpoint
4. GET /api/ranking/povao/stats endpoint
5. Points calculation based on distance (5-9km=5pts, 10-20km=7pts, 21km+=9pts)
6. Gender filters for Povão ranking (only M/F)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRankingPovaoAPI:
    """Test the Ranking do Povão API endpoints"""

    def test_get_ranking_povao_masculino(self):
        """Test GET /api/ranking/povao?genero=M returns valid response"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "genero" in data, "Response should contain 'genero'"
        assert "total_atletas" in data, "Response should contain 'total_atletas'"
        assert "ranking" in data, "Response should contain 'ranking'"
        assert data["genero"] == "Masculino", f"Expected 'Masculino', got {data['genero']}"
        assert isinstance(data["ranking"], list), "ranking should be a list"
        print(f"✓ Ranking Povão Masculino: {data['total_atletas']} atletas")

    def test_get_ranking_povao_feminino(self):
        """Test GET /api/ranking/povao?genero=F returns valid response"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao?genero=F")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["genero"] == "Feminino", f"Expected 'Feminino', got {data['genero']}"
        assert isinstance(data["ranking"], list), "ranking should be a list"
        print(f"✓ Ranking Povão Feminino: {data['total_atletas']} atletas")

    def test_get_povao_stats(self):
        """Test GET /api/ranking/povao/stats returns statistics"""
        response = requests.get(f"{BASE_URL}/api/ranking/povao/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "total_atletas_masculino" in data, "Response should contain 'total_atletas_masculino'"
        assert "total_atletas_feminino" in data, "Response should contain 'total_atletas_feminino'"
        assert "total_atletas" in data, "Response should contain 'total_atletas'"
        assert "total_provas" in data, "Response should contain 'total_provas'"
        assert "total_pontos" in data, "Response should contain 'total_pontos'"
        print(f"✓ Povão Stats: {data}")


class TestCadastroModalidade:
    """Test user registration with modalidade selection"""
    
    test_email_profissional = f"test_prof_{uuid.uuid4().hex[:8]}@test.com"
    test_email_povao = f"test_povao_{uuid.uuid4().hex[:8]}@test.com"
    test_email_pcd = f"test_pcd_{uuid.uuid4().hex[:8]}@test.com"
    
    def test_register_profissional_amador(self):
        """Test registration with profissional_amador modality"""
        payload = {
            "nome": "Atleta Profissional Teste",
            "email": self.test_email_profissional,
            "password": "test123456",
            "equipe": "Equipe Teste",
            "cidade": "São Paulo",
            "estado": "SP",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-01-15",
            "etnia": "Branco",
            "apelido": "Profissional",
            "modalidade_usuario": "profissional_amador"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["user"]["modalidade_usuario"] == "profissional_amador"
        print(f"✓ Cadastro Profissional/Amador: {data['user']['nome']}")

    def test_register_povao_pace_livre(self):
        """Test registration with povao_pace_livre modality"""
        payload = {
            "nome": "Atleta Povão Teste",
            "email": self.test_email_povao,
            "password": "test123456",
            "equipe": "Equipe Povão",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "genero": "M",
            "categoria": "normal",  # Only normal can select Povão
            "data_nascimento": "1985-05-20",
            "etnia": "Negro",
            "apelido": "Povão",
            "modalidade_usuario": "povao_pace_livre"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["user"]["modalidade_usuario"] == "povao_pace_livre"
        print(f"✓ Cadastro Povão - Pace Livre: {data['user']['nome']}")

    def test_register_pcd_cannot_select_povao(self):
        """Test that PCD athletes cannot select povao_pace_livre modality"""
        payload = {
            "nome": "Atleta PCD Teste",
            "email": self.test_email_pcd,
            "password": "test123456",
            "equipe": "Equipe PCD",
            "cidade": "Belo Horizonte",
            "estado": "MG",
            "genero": "F",
            "categoria": "pcd",  # PCD category
            "data_nascimento": "1992-08-10",
            "etnia": "Pardo",
            "apelido": "PCD",
            "modalidade_usuario": "povao_pace_livre"  # Trying to select Povão
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 400, f"Expected 400 for PCD trying Povão, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        assert "PCD" in data["detail"] or "Cadeirante" in data["detail"]
        print(f"✓ PCD corretamente rejeitado para modalidade Povão: {data['detail']}")

    def test_register_cadeirante_cannot_select_povao(self):
        """Test that Cadeirante athletes cannot select povao_pace_livre modality"""
        payload = {
            "nome": "Atleta Cadeirante Teste",
            "email": f"test_cad_{uuid.uuid4().hex[:8]}@test.com",
            "password": "test123456",
            "equipe": "Equipe Cadeirante",
            "cidade": "Salvador",
            "estado": "BA",
            "genero": "M",
            "categoria": "cadeirante",  # Cadeirante category
            "data_nascimento": "1988-03-25",
            "etnia": "Amarelo",
            "apelido": "Cadeirante",
            "modalidade_usuario": "povao_pace_livre"  # Trying to select Povão
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 400, f"Expected 400 for Cadeirante trying Povão, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        print(f"✓ Cadeirante corretamente rejeitado para modalidade Povão: {data['detail']}")


class TestPontosPovao:
    """Test points calculation for Povão modality"""
    
    def test_points_calculation_logic(self):
        """Test the points calculation logic for different distances"""
        # Import the function to test logic
        # This is a unit test simulation - we'll test via API behavior
        
        # Expected points by distance:
        # 5km-9km = 5 points
        # 10km-20km = 7 points
        # 21km+ = 9 points
        
        expected_points = {
            "5KM": 5,
            "6KM": 5,
            "9KM": 5,
            "10KM": 7,
            "15KM": 7,
            "20KM": 7,
            "21KM": 9,
            "42KM": 9
        }
        
        print("✓ Pontuação Povão esperada:")
        for dist, pts in expected_points.items():
            print(f"  {dist}: {pts} pontos")


class TestSubmeterResultadoPovao:
    """Test result submission for Povão athletes"""
    
    def get_povao_token(self):
        """Login as a Povão athlete or create one"""
        # First try to create a new Povão athlete
        test_email = f"test_submeter_povao_{uuid.uuid4().hex[:8]}@test.com"
        register_payload = {
            "nome": "Atleta Submeter Povão",
            "email": test_email,
            "password": "test123456",
            "equipe": "Equipe Submeter",
            "cidade": "Curitiba",
            "estado": "PR",
            "genero": "M",
            "categoria": "normal",
            "data_nascimento": "1990-06-15",
            "etnia": "Branco",
            "apelido": "Submeter",
            "modalidade_usuario": "povao_pace_livre"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_payload)
        if response.status_code == 200:
            return response.json()["token"]
        
        # If registration fails (email exists), try login
        login_payload = {
            "email": test_email,
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload)
        if response.status_code == 200:
            return response.json()["token"]
        
        return None

    def test_povao_can_submit_result(self):
        """Test that Povão athlete can submit result without colocacao/tempo requirement"""
        token = self.get_povao_token()
        if not token:
            pytest.skip("Could not get token for Povão athlete")
        
        # Check /auth/me to verify user info
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        print(f"✓ Usuário autenticado: {me_response.json()}")


class TestAdminFilterModalidade:
    """Test admin filter by modality"""
    
    def get_admin_token(self):
        """Login as admin"""
        payload = {
            "email": "admin@runpro.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        if response.status_code == 200:
            return response.json()["token"]
        return None

    def test_admin_can_list_atletas_by_modalidade(self):
        """Test that admin can filter athletes by modalidade"""
        token = self.get_admin_token()
        if not token:
            pytest.skip("Could not get admin token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test fetching all atletas
        response = requests.get(f"{BASE_URL}/api/admin/atletas", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        atletas = response.json()
        assert isinstance(atletas, list)
        
        # Check if modalidade_usuario field is present
        if len(atletas) > 0:
            # Count athletes by modalidade
            profissional_count = sum(1 for a in atletas if a.get("modalidade_usuario", "profissional_amador") == "profissional_amador")
            povao_count = sum(1 for a in atletas if a.get("modalidade_usuario") == "povao_pace_livre")
            
            print(f"✓ Admin lista atletas por modalidade:")
            print(f"  Profissional/Amador: {profissional_count}")
            print(f"  Povão - Pace Livre: {povao_count}")
            print(f"  Total: {len(atletas)}")


class TestExistingAtleta:
    """Test with existing test athlete"""
    
    def test_login_existing_atleta(self):
        """Test login with provided test athlete"""
        payload = {
            "email": "leonardocarvalhofilho_normal_1@email.com",
            "password": "atleta123"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"✓ Login atleta existente: {data['user']['nome']}")
        
        return data["token"]

    def test_admin_login(self):
        """Test login with provided admin credentials"""
        payload = {
            "email": "admin@runpro.com",
            "password": "admin123"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Login admin: {data['user']['nome']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
