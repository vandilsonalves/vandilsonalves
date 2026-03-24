# /app/backend/tests/test_iter69_websocket_testid.py
# Tests for Iteration 69: WebSocket 403 fix and data-testid verification

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWebSocketFix:
    """Tests for WebSocket 403 fix - SECRET_KEY now imported from auth_routes"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin login failed")
    
    @pytest.fixture
    def atleta_token(self):
        """Get atleta token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teste.dono@teste.com",
            "password": "123456"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Atleta login failed")
    
    def test_admin_login_success(self):
        """Test admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data.get("user", {}).get("role") == "admin"
        print(f"✅ Admin login successful, role: {data.get('user', {}).get('role')}")
    
    def test_atleta_login_success(self):
        """Test atleta login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teste.dono@teste.com",
            "password": "123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"✅ Atleta login successful, user: {data.get('user', {}).get('nome')}")
    
    def test_websocket_status_endpoint(self, admin_token):
        """Test WebSocket status endpoint (admin only)"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/ws-status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should return 200 for admin
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "online"
        print(f"✅ WebSocket status: {data}")
    
    def test_websocket_unread_count(self, admin_token):
        """Test unread notifications count endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/unread-count",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        print(f"✅ Unread count: {data['unread_count']}")
    
    def test_websocket_test_notification(self, admin_token):
        """Test sending test notification"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/send-test",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ Test notification sent: {data}")


class TestRaioXEndpoint:
    """Tests for Raio-X page endpoints"""
    
    @pytest.fixture
    def atleta_token(self):
        """Get atleta token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teste.dono@teste.com",
            "password": "123456"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Atleta login failed")
    
    def test_raio_x_completo_endpoint(self, atleta_token):
        """Test Raio-X completo endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/raio-x/completo",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        # May return 200 with data or 200 with tem_dados=false
        assert response.status_code == 200
        data = response.json()
        # Should have structure even if no data
        print(f"✅ Raio-X endpoint returned: {list(data.keys()) if isinstance(data, dict) else 'list'}")


class TestStravaEndpoints:
    """Tests for Strava atividades endpoints"""
    
    def test_strava_classificacao(self):
        """Test Strava classificacao endpoint"""
        response = requests.get(f"{BASE_URL}/api/strava-atividades/classificacao?periodo=esta_semana")
        assert response.status_code == 200
        data = response.json()
        assert "classificacao" in data
        print(f"✅ Strava classificacao: {len(data.get('classificacao', []))} atletas")
    
    def test_strava_lideres(self):
        """Test Strava lideres endpoint"""
        response = requests.get(f"{BASE_URL}/api/strava-atividades/lideres?periodo=semana_passada")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Strava lideres: {list(data.keys()) if isinstance(data, dict) else 'ok'}")
    
    def test_strava_membros(self):
        """Test Strava membros endpoint"""
        response = requests.get(f"{BASE_URL}/api/strava-atividades/membros")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        print(f"✅ Strava membros: {data.get('total', 0)} total")


class TestAdminDashboard:
    """Tests for Admin Dashboard endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin login failed")
    
    def test_admin_stats(self, admin_token):
        """Test admin stats endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Admin stats: {list(data.keys()) if isinstance(data, dict) else 'ok'}")
    
    def test_engajamento_endpoint(self, admin_token):
        """Test engajamento dashboard endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/mensagens/engajamento",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "resumo" in data
        print(f"✅ Engajamento: {data.get('resumo', {})}")
