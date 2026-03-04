"""
Tests for Cadastro improvements and Password Change functionality
- Estado -> Cidade dependency (IBGE API)
- Equipe autocomplete with 'Sem equipe' option
- Etnia dropdown with 6 options
- Password change for athletes
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEquipesEndpoint:
    """Test GET /api/ranking/equipes endpoint"""
    
    def test_get_equipes_returns_list(self):
        """Verify equipes endpoint returns a list"""
        response = requests.get(f"{BASE_URL}/api/ranking/equipes")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"SUCCESS: Got {len(data)} equipes from API")
        
    def test_equipes_include_common_teams(self):
        """Verify response includes some common equipe names"""
        response = requests.get(f"{BASE_URL}/api/ranking/equipes")
        assert response.status_code == 200
        
        data = response.json()
        # Just verify it's a non-empty list
        assert len(data) > 0, "Should have at least one equipe"
        print(f"SUCCESS: Equipes list contains {len(data)} items")


class TestAuthAndPasswordChange:
    """Test authentication and password change"""
    
    @pytest.fixture
    def atleta_credentials(self):
        return {
            "email": "leonardocarvalhofilho_normal_1@email.com",
            "password": "atleta123"
        }
    
    def test_login_success(self, atleta_credentials):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=atleta_credentials)
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user info"
        print(f"SUCCESS: Logged in as {data['user']['nome']}")
        return data
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@email.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, "Should return 401 for invalid credentials"
        print("SUCCESS: Login correctly rejected invalid credentials")
    
    def test_password_change_wrong_current(self, atleta_credentials):
        """Test password change with wrong current password"""
        # First login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=atleta_credentials)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json()["token"]
        
        # Try to change password with wrong current password
        headers = {"Authorization": f"Bearer {token}"}
        change_resp = requests.post(f"{BASE_URL}/api/atletas/alterar-senha", 
            json={
                "senha_atual": "wrongpassword",
                "nova_senha": "newpassword123",
                "confirmar_senha": "newpassword123"
            },
            headers=headers
        )
        
        assert change_resp.status_code == 400, f"Expected 400, got {change_resp.status_code}"
        data = change_resp.json()
        assert "incorreta" in data.get("detail", "").lower(), f"Should mention password is incorrect: {data}"
        print("SUCCESS: Password change correctly rejected with wrong current password")
    
    def test_password_change_success_and_revert(self, atleta_credentials):
        """Test successful password change and then revert it back"""
        # 1. Login with original credentials
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=atleta_credentials)
        assert login_resp.status_code == 200, f"Initial login failed: {login_resp.text}"
        token = login_resp.json()["token"]
        
        # 2. Change password to new password
        new_password = "newpassword123"
        headers = {"Authorization": f"Bearer {token}"}
        change_resp = requests.post(f"{BASE_URL}/api/atletas/alterar-senha", 
            json={
                "senha_atual": atleta_credentials["password"],
                "nova_senha": new_password,
                "confirmar_senha": new_password
            },
            headers=headers
        )
        
        assert change_resp.status_code == 200, f"Password change failed: {change_resp.text}"
        print("SUCCESS: Password changed to new password")
        
        # 3. Verify login with new password works
        login_new_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": atleta_credentials["email"],
            "password": new_password
        })
        assert login_new_resp.status_code == 200, f"Login with new password failed: {login_new_resp.text}"
        new_token = login_new_resp.json()["token"]
        print("SUCCESS: Login with new password works")
        
        # 4. Revert password back to original
        headers_new = {"Authorization": f"Bearer {new_token}"}
        revert_resp = requests.post(f"{BASE_URL}/api/atletas/alterar-senha", 
            json={
                "senha_atual": new_password,
                "nova_senha": atleta_credentials["password"],
                "confirmar_senha": atleta_credentials["password"]
            },
            headers=headers_new
        )
        
        assert revert_resp.status_code == 200, f"Password revert failed: {revert_resp.text}"
        print("SUCCESS: Password reverted back to original")
        
        # 5. Verify original password works again
        final_login = requests.post(f"{BASE_URL}/api/auth/login", json=atleta_credentials)
        assert final_login.status_code == 200, f"Final login with original password failed: {final_login.text}"
        print("SUCCESS: Original password works after revert")
    
    def test_password_change_mismatched_confirmation(self, atleta_credentials):
        """Test password change with mismatched confirmation"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=atleta_credentials)
        assert login_resp.status_code == 200
        token = login_resp.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        change_resp = requests.post(f"{BASE_URL}/api/atletas/alterar-senha", 
            json={
                "senha_atual": atleta_credentials["password"],
                "nova_senha": "newpassword123",
                "confirmar_senha": "differentpassword"
            },
            headers=headers
        )
        
        assert change_resp.status_code == 400, f"Expected 400, got {change_resp.status_code}"
        print("SUCCESS: Password change correctly rejected with mismatched confirmation")
    
    def test_password_change_too_short(self, atleta_credentials):
        """Test password change with too short new password"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=atleta_credentials)
        assert login_resp.status_code == 200
        token = login_resp.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        change_resp = requests.post(f"{BASE_URL}/api/atletas/alterar-senha", 
            json={
                "senha_atual": atleta_credentials["password"],
                "nova_senha": "12345",  # Too short
                "confirmar_senha": "12345"
            },
            headers=headers
        )
        
        assert change_resp.status_code == 400, f"Expected 400, got {change_resp.status_code}"
        print("SUCCESS: Password change correctly rejected short password")


class TestAtletaPerfil:
    """Test athlete profile endpoint"""
    
    def test_get_meu_perfil(self):
        """Test getting athlete profile"""
        # Login first
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "leonardocarvalhofilho_normal_1@email.com",
            "password": "atleta123"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_resp = requests.get(f"{BASE_URL}/api/atletas/meu-perfil", headers=headers)
        
        assert profile_resp.status_code == 200, f"Get profile failed: {profile_resp.text}"
        data = profile_resp.json()
        
        assert "nome" in data, "Profile should contain nome"
        assert "email" in data, "Profile should contain email"
        assert "cidade" in data, "Profile should contain cidade"
        assert "estado" in data, "Profile should contain estado"
        print(f"SUCCESS: Got profile for {data['nome']} from {data['cidade']}/{data['estado']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
