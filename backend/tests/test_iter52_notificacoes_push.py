# test_iter52_notificacoes_push.py
# Testing Notification System: HTTP endpoints, WebSocket connection, polling fallback
# Features: GET /api/notificacoes, POST /api/notificacoes/{id}/ler, POST /api/notificacoes/ler-todas

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://feed-likes-comments.preview.emergentagent.com"

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"


class TestNotificacoesEndpoints:
    """Test notification HTTP endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("token")
        self.user_id = data.get("user", {}).get("id")
        assert self.token, "No token received"
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_01_get_notificacoes_list(self):
        """Test GET /api/notificacoes returns notification list"""
        response = requests.get(f"{BASE_URL}/api/notificacoes", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "notificacoes" in data, "Response should have 'notificacoes' key"
        assert "nao_lidas" in data, "Response should have 'nao_lidas' key"
        assert isinstance(data["notificacoes"], list), "notificacoes should be a list"
        assert isinstance(data["nao_lidas"], int), "nao_lidas should be an integer"
        
        print(f"✅ GET /api/notificacoes - {len(data['notificacoes'])} notifications, {data['nao_lidas']} unread")
    
    def test_02_notificacoes_structure(self):
        """Test notification object structure"""
        response = requests.get(f"{BASE_URL}/api/notificacoes", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        if len(data["notificacoes"]) > 0:
            notif = data["notificacoes"][0]
            # Check required fields
            assert "id" in notif, "Notification should have 'id'"
            assert "usuario_id" in notif, "Notification should have 'usuario_id'"
            assert "tipo" in notif or "type" in notif, "Notification should have 'tipo' or 'type'"
            assert "titulo" in notif or "title" in notif, "Notification should have 'titulo' or 'title'"
            assert "lida" in notif or "read" in notif, "Notification should have 'lida' or 'read'"
            print(f"✅ Notification structure valid: id={notif['id']}")
        else:
            print("⚠️ No notifications to validate structure")
    
    def test_03_create_test_notification_via_enviar(self):
        """Test POST /api/notificacoes/enviar creates notification (admin only)"""
        # Get a test user ID (use admin's own ID for testing)
        test_payload = {
            "destinatarios": [self.user_id],
            "mensagem": f"TEST_notificacao_{uuid.uuid4().hex[:8]} - Test message at {datetime.now().isoformat()}",
            "tipo": "mensagem_assessoria",
            "titulo": "TEST_Mensagem de Teste"
        }
        
        response = requests.post(f"{BASE_URL}/api/notificacoes/enviar", 
                                 json=test_payload, headers=self.headers)
        
        # Admin should be able to send notifications
        assert response.status_code in [200, 201, 403], f"Unexpected status: {response.status_code}: {response.text}"
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "total_enviados" in data or "message" in data
            print(f"✅ POST /api/notificacoes/enviar - Created notification")
        else:
            print(f"⚠️ POST /api/notificacoes/enviar - Permission denied (admin needs dono_assessoria role)")
    
    def test_04_mark_notification_as_read(self):
        """Test POST /api/notificacoes/{id}/ler marks notification as read"""
        # First get notifications
        response = requests.get(f"{BASE_URL}/api/notificacoes", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        notifications = data.get("notificacoes", [])
        
        # Find unread notification or use first one
        unread = [n for n in notifications if not n.get("lida", True)]
        target = unread[0] if unread else (notifications[0] if notifications else None)
        
        if target:
            notif_id = target["id"]
            response = requests.post(f"{BASE_URL}/api/notificacoes/{notif_id}/ler", headers=self.headers)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            data = response.json()
            assert "message" in data
            print(f"✅ POST /api/notificacoes/{notif_id}/ler - Marked as read")
        else:
            print("⚠️ No notifications available to mark as read")
    
    def test_05_mark_all_notifications_read(self):
        """Test POST /api/notificacoes/ler-todas marks all as read"""
        response = requests.post(f"{BASE_URL}/api/notificacoes/ler-todas", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        
        # Verify all are now read
        verify_response = requests.get(f"{BASE_URL}/api/notificacoes", headers=self.headers)
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["nao_lidas"] == 0, f"Expected 0 unread, got {verify_data['nao_lidas']}"
        
        print("✅ POST /api/notificacoes/ler-todas - All marked as read")
    
    def test_06_get_unread_count(self):
        """Test GET /api/notifications/unread-count endpoint"""
        response = requests.get(f"{BASE_URL}/api/notifications/unread-count", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "unread_count" in data, "Response should have 'unread_count'"
        assert isinstance(data["unread_count"], int)
        
        print(f"✅ GET /api/notifications/unread-count - {data['unread_count']} unread")


class TestWebSocketNotifications:
    """Test WebSocket related HTTP endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        self.token = data.get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_01_ws_status_endpoint(self):
        """Test GET /api/notifications/ws-status (admin only)"""
        response = requests.get(f"{BASE_URL}/api/notifications/ws-status", headers=self.headers)
        
        # Admin should have access
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data, "Response should have 'status'"
        assert data["status"] == "online", f"Expected 'online', got {data['status']}"
        
        # Check for stats fields
        expected_fields = ["active_users", "active_connections", "messages_sent"]
        for field in expected_fields:
            assert field in data, f"Response should have '{field}'"
        
        print(f"✅ GET /api/notifications/ws-status - Status: {data['status']}, Active connections: {data.get('active_connections', 0)}")
    
    def test_02_send_test_notification(self):
        """Test POST /api/notifications/send-test sends test notification"""
        response = requests.post(f"{BASE_URL}/api/notifications/send-test", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        assert "notification" in data
        assert "user_online" in data
        
        print(f"✅ POST /api/notifications/send-test - User online: {data['user_online']}")
    
    def test_03_mark_notification_read_via_notifications(self):
        """Test POST /api/notifications/{id}/read endpoint"""
        # First get notifications
        response = requests.get(f"{BASE_URL}/api/notificacoes", headers=self.headers)
        assert response.status_code == 200
        
        notifications = response.json().get("notificacoes", [])
        if notifications:
            notif_id = notifications[0]["id"]
            response = requests.post(f"{BASE_URL}/api/notifications/{notif_id}/read", headers=self.headers)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            print(f"✅ POST /api/notifications/{notif_id}/read - Marked as read")
        else:
            print("⚠️ No notifications available to test")
    
    def test_04_read_all_via_notifications(self):
        """Test POST /api/notifications/read-all endpoint"""
        response = requests.post(f"{BASE_URL}/api/notifications/read-all", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        print(f"✅ POST /api/notifications/read-all - {data['message']}")


class TestNotificacaoDetails:
    """Test notification detail and delete endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        self.token = data.get("token")
        self.user_id = data.get("user", {}).get("id")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_01_get_notification_details(self):
        """Test GET /api/notificacoes/{id} returns notification details"""
        # First get notifications
        response = requests.get(f"{BASE_URL}/api/notificacoes", headers=self.headers)
        assert response.status_code == 200
        
        notifications = response.json().get("notificacoes", [])
        if notifications:
            notif_id = notifications[0]["id"]
            response = requests.get(f"{BASE_URL}/api/notificacoes/{notif_id}", headers=self.headers)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            data = response.json()
            assert data.get("id") == notif_id, "ID should match"
            print(f"✅ GET /api/notificacoes/{notif_id} - Details retrieved")
        else:
            print("⚠️ No notifications to test details")
    
    def test_02_delete_notification(self):
        """Test DELETE /api/notificacoes/{id} deletes notification"""
        # First create a test notification if we have permission
        test_payload = {
            "destinatarios": [self.user_id],
            "mensagem": f"TEST_DELETE_{uuid.uuid4().hex[:8]}",
            "tipo": "mensagem_assessoria",
            "titulo": "TEST_Para Exclusão"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/notificacoes/enviar", 
                                        json=test_payload, headers=self.headers)
        
        # Get notifications to find one to delete
        response = requests.get(f"{BASE_URL}/api/notificacoes", headers=self.headers)
        assert response.status_code == 200
        
        notifications = response.json().get("notificacoes", [])
        # Find a test notification to delete
        test_notifs = [n for n in notifications if "TEST_" in n.get("titulo", "") or "TEST_" in n.get("mensagem", "")]
        
        if test_notifs:
            notif_id = test_notifs[0]["id"]
            response = requests.delete(f"{BASE_URL}/api/notificacoes/{notif_id}", headers=self.headers)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            # Verify deletion
            verify_response = requests.get(f"{BASE_URL}/api/notificacoes/{notif_id}", headers=self.headers)
            assert verify_response.status_code == 404, "Deleted notification should return 404"
            print(f"✅ DELETE /api/notificacoes/{notif_id} - Deleted successfully")
        else:
            print("⚠️ No test notifications available to delete")
    
    def test_03_nonexistent_notification(self):
        """Test 404 for non-existent notification"""
        fake_id = f"fake-{uuid.uuid4()}"
        response = requests.get(f"{BASE_URL}/api/notificacoes/{fake_id}", headers=self.headers)
        assert response.status_code == 404, f"Expected 404 for non-existent notification, got {response.status_code}"
        print(f"✅ GET /api/notificacoes/{fake_id} - 404 as expected")


class TestNotificacoesAuth:
    """Test authentication for notification endpoints"""
    
    def test_01_notificacoes_requires_auth(self):
        """Test GET /api/notificacoes requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notificacoes")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✅ GET /api/notificacoes - Requires authentication")
    
    def test_02_mark_read_requires_auth(self):
        """Test POST /api/notificacoes/{id}/ler requires authentication"""
        response = requests.post(f"{BASE_URL}/api/notificacoes/test-id/ler")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✅ POST /api/notificacoes/{id}/ler - Requires authentication")
    
    def test_03_mark_all_requires_auth(self):
        """Test POST /api/notificacoes/ler-todas requires authentication"""
        response = requests.post(f"{BASE_URL}/api/notificacoes/ler-todas")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✅ POST /api/notificacoes/ler-todas - Requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
