"""
Backend API tests for Ranking Run Pró
Testing: Admin Dashboard, Athlete Profile, Rankings, Authentication
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ranking-run-v2.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin123"
ATLETA_EMAIL = "pedrosantos_normal_0@email.com"
ATLETA_PASSWORD = "atleta123"


class TestHealthAndRootEndpoint:
    """Test basic API availability"""
    
    def test_root_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Ranking Run Pro API"
        print("✓ Root endpoint working")


class TestAuthentication:
    """Test authentication flows"""
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"✓ Admin login successful, role: {data['user']['role']}")
    
    def test_atleta_login_success(self):
        """Test athlete login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "atleta"
        print(f"✓ Atleta login successful, role: {data['user']['role']}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")
    
    def test_auth_me_endpoint(self):
        """Test /auth/me returns current user"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_response.json()["token"]
        
        # Then get me
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        assert data["role"] == "admin"
        print("✓ /auth/me endpoint working")


class TestAdminDashboardStats:
    """Test admin dashboard statistics endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    def test_admin_stats_total_atletas(self, admin_token):
        """Test admin stats endpoint returns correct total athletes (90)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected stats
        assert "total_atletas" in data
        assert "total_homens" in data
        assert "total_mulheres" in data
        
        # Expected: 90 athletes (15 per category x 6 categories)
        assert data["total_atletas"] == 90, f"Expected 90 athletes, got {data['total_atletas']}"
        
        # Expected: 45 men, 45 women (15 per category x 3 categories each)
        assert data["total_homens"] == 45, f"Expected 45 men, got {data['total_homens']}"
        assert data["total_mulheres"] == 45, f"Expected 45 women, got {data['total_mulheres']}"
        
        print(f"✓ Admin stats: {data['total_atletas']} total, {data['total_homens']} men, {data['total_mulheres']} women")
    
    def test_admin_stats_estados(self, admin_token):
        """Test athletes by state distribution"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats/estados",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure
        for item in data:
            assert "estado" in item
            assert "total" in item
            assert isinstance(item["total"], int)
        
        total = sum(item["total"] for item in data)
        assert total == 90, f"Total athletes by state should be 90, got {total}"
        
        print(f"✓ Athletes distributed across {len(data)} states")
    
    def test_admin_stats_categorias(self, admin_token):
        """Test athletes by category and gender (15 each)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats/categorias",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Expected structure
        expected_keys = ["normal_m", "normal_f", "pcd_m", "pcd_f", "cadeirante_m", "cadeirante_f"]
        for key in expected_keys:
            assert key in data, f"Missing key: {key}"
            assert data[key] == 15, f"Expected 15 for {key}, got {data[key]}"
        
        print(f"✓ Categories distribution: {data}")
    
    def test_admin_stats_faixa_etaria(self, admin_token):
        """Test athletes by age group"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats/faixa-etaria",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure
        for item in data:
            assert "faixa" in item
            assert "total" in item
        
        total = sum(item["total"] for item in data)
        assert total == 90, f"Total athletes by age group should be 90, got {total}"
        
        print(f"✓ Athletes distributed across {len(data)} age groups")
    
    def test_admin_stats_requires_admin(self):
        """Test that admin stats require admin role"""
        # Login as atleta
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        atleta_token = response.json()["token"]
        
        # Try to access admin stats
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 403
        print("✓ Admin stats correctly restricted to admin users")


class TestAtletaPerfil:
    """Test athlete profile endpoints"""
    
    @pytest.fixture
    def atleta_session(self):
        """Get athlete token and user info"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return {"token": data["token"], "user": data["user"]}
        pytest.skip("Atleta login failed")
    
    def test_atleta_detalhes(self, atleta_session):
        """Test getting athlete details"""
        user_id = atleta_session["user"]["id"]
        token = atleta_session["token"]
        
        response = requests.get(
            f"{BASE_URL}/api/atletas/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "id" in data
        assert "nome" in data
        assert "categoria" in data
        assert "pontos_carreira" in data
        assert "total_corridas" in data
        
        print(f"✓ Athlete details: {data['nome']}, {data['total_corridas']} races, {data['pontos_carreira']} points")
    
    def test_update_perfil(self, atleta_session):
        """Test updating athlete profile"""
        token = atleta_session["token"]
        
        # Update profile
        update_data = {
            "equipe": "TEST_Team",
            "facebook_url": "https://facebook.com/test",
            "instagram_url": "https://instagram.com/test",
            "telefone": "(11) 99999-9999",
            "bio": "Test bio for athlete"
        }
        
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        print(f"✓ Profile update successful: {data['message']}")
        
        # Cleanup - reset to original values
        requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            json={"equipe": "Runners BR"},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    def test_update_perfil_no_data(self, atleta_session):
        """Test updating profile with no data"""
        token = atleta_session["token"]
        
        response = requests.patch(
            f"{BASE_URL}/api/atletas/perfil",
            json={},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        print("✓ Empty profile update correctly rejected")


class TestRanking:
    """Test ranking endpoints"""
    
    def test_ranking_masculino(self):
        """Test ranking for masculino category"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2025")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 15, f"Expected 15 athletes in masculino, got {len(data)}"
        
        # Check structure
        if len(data) > 0:
            athlete = data[0]
            assert "id" in athlete
            assert "colocacao" in athlete
            assert "nome" in athlete
            assert "pontos" in athlete
            assert "is_pendente" in athlete
        
        print(f"✓ Masculino ranking: {len(data)} athletes")
    
    def test_ranking_feminino(self):
        """Test ranking for feminino category"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/feminino/M?ano=2025")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 15, f"Expected 15 athletes in feminino, got {len(data)}"
        
        print(f"✓ Feminino ranking: {len(data)} athletes")
    
    def test_ranking_pcd_m(self):
        """Test ranking for PCD masculino"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/pcd-m/M?ano=2025")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 15, f"Expected 15 athletes in PCD-M, got {len(data)}"
        
        print(f"✓ PCD-M ranking: {len(data)} athletes")
    
    def test_ranking_pcd_f(self):
        """Test ranking for PCD feminino"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/pcd-f/M?ano=2025")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 15, f"Expected 15 athletes in PCD-F, got {len(data)}"
        
        print(f"✓ PCD-F ranking: {len(data)} athletes")
    
    def test_ranking_cadeirante_m(self):
        """Test ranking for cadeirante masculino"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/cadeirante-m/M?ano=2025")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 15, f"Expected 15 athletes in Cadeirante-M, got {len(data)}"
        
        print(f"✓ Cadeirante-M ranking: {len(data)} athletes")
    
    def test_ranking_cadeirante_f(self):
        """Test ranking for cadeirante feminino"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/cadeirante-f/M?ano=2025")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 15, f"Expected 15 athletes in Cadeirante-F, got {len(data)}"
        
        print(f"✓ Cadeirante-F ranking: {len(data)} athletes")
    
    def test_ranking_points_validation(self):
        """Test that ranking points are calculated correctly"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2025")
        assert response.status_code == 200
        data = response.json()
        
        # Check that athletes are sorted by points (descending)
        points = [a["pontos"] for a in data]
        assert points == sorted(points, reverse=True), "Ranking should be sorted by points descending"
        
        # Check colocacao matches position
        for idx, athlete in enumerate(data, 1):
            assert athlete["colocacao"] == idx, f"Colocacao should match position: expected {idx}, got {athlete['colocacao']}"
        
        print("✓ Ranking correctly sorted by points")
    
    def test_ranking_nacional(self):
        """Test national ranking endpoint"""
        response = requests.get(f"{BASE_URL}/api/ranking/nacional?ano=2025")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Should have all 90 athletes
        assert len(data) == 90, f"Expected 90 athletes in national ranking, got {len(data)}"
        
        print(f"✓ National ranking: {len(data)} athletes")


class TestAdminPendentes:
    """Test admin pending results management"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin login failed")
    
    def test_get_pendentes(self, admin_token):
        """Test getting pending results list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/pendentes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Pending results: {len(data)} items")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
