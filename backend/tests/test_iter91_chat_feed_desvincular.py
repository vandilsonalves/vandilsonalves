"""
Iteration 91: Testing Chat Assessoria, Feed Equipe, and Desvincular Atleta features.

Features tested:
1. POST /api/assessoria/chat/enviar - Send chat message (text + file upload)
2. GET /api/assessoria/chat/historico - Get chat history with pagination
3. POST /api/assessoria/desvincular-atleta - Unlink athlete from team
4. POST /api/equipe/feed/enviar - Post to team feed
5. GET /api/equipe/feed - Get team feed posts
6. POST /api/equipe/feed/{post_id}/curtir - Like/unlike post
7. DELETE /api/equipe/feed/{post_id} - Delete post
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review request
DONO_ASSESSORIA_EMAIL = "gustavo_gomes_2@email.com"
DONO_ASSESSORIA_PASSWORD = "teste123"


class TestAuthLogin:
    """Test login endpoint returns equipe field"""
    
    def test_login_dono_assessoria_returns_equipe(self):
        """Login as dono_assessoria should return equipe in user object"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": DONO_ASSESSORIA_EMAIL,
            "password": DONO_ASSESSORIA_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        assert "token" in data, "Token not in response"
        assert "user" in data, "User not in response"
        assert "equipe" in data["user"], "Equipe not in user object"
        assert data["user"]["role"] == "dono_assessoria", f"Expected role dono_assessoria, got {data['user']['role']}"
        
        print(f"Login successful. User: {data['user']['nome']}, Equipe: {data['user']['equipe']}, Role: {data['user']['role']}")


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for dono_assessoria"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": DONO_ASSESSORIA_EMAIL,
        "password": DONO_ASSESSORIA_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.text}")
    return response.json()["token"]


@pytest.fixture(scope="module")
def user_info():
    """Get user info from login"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": DONO_ASSESSORIA_EMAIL,
        "password": DONO_ASSESSORIA_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.text}")
    return response.json()["user"]


class TestChatAssessoria:
    """Test Chat Assessoria endpoints"""
    
    def test_enviar_mensagem_texto(self, auth_token):
        """POST /api/assessoria/chat/enviar - Send text message"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Use multipart/form-data as expected by the endpoint
        data = {
            "mensagem": f"TEST_Mensagem de teste {uuid.uuid4().hex[:8]}",
            "destinatarios": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/assessoria/chat/enviar",
            headers=headers,
            data=data
        )
        
        assert response.status_code == 200, f"Failed to send message: {response.text}"
        result = response.json()
        
        assert "message" in result, "No message in response"
        assert "msg" in result, "No msg object in response"
        assert result["msg"]["mensagem"] == data["mensagem"], "Message content mismatch"
        assert "id" in result["msg"], "No id in message"
        assert "data_envio" in result["msg"], "No data_envio in message"
        
        print(f"Message sent successfully: {result['msg']['id']}")
        return result["msg"]["id"]
    
    def test_enviar_mensagem_vazia_falha(self, auth_token):
        """POST /api/assessoria/chat/enviar - Empty message should fail"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        data = {
            "mensagem": "",
            "destinatarios": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/assessoria/chat/enviar",
            headers=headers,
            data=data
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "Envie uma mensagem ou arquivo" in response.text
        print("Empty message correctly rejected")
    
    def test_historico_chat(self, auth_token):
        """GET /api/assessoria/chat/historico - Get chat history"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/assessoria/chat/historico?page=1&limit=30",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to get history: {response.text}"
        data = response.json()
        
        assert "mensagens" in data, "No mensagens in response"
        assert "total" in data, "No total in response"
        assert "page" in data, "No page in response"
        assert "has_more" in data, "No has_more in response"
        assert isinstance(data["mensagens"], list), "mensagens should be a list"
        
        print(f"Chat history: {len(data['mensagens'])} messages, total: {data['total']}, has_more: {data['has_more']}")
    
    def test_historico_chat_pagination(self, auth_token):
        """GET /api/assessoria/chat/historico - Test pagination"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get page 1 with limit 5
        response = requests.get(
            f"{BASE_URL}/api/assessoria/chat/historico?page=1&limit=5",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert len(data["mensagens"]) <= 5
        
        print(f"Pagination test: page 1, got {len(data['mensagens'])} messages")


class TestFeedEquipe:
    """Test Feed Equipe endpoints"""
    
    created_post_id = None
    
    def test_enviar_post_feed(self, auth_token):
        """POST /api/equipe/feed/enviar - Post to team feed"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        data = {
            "mensagem": f"TEST_Post no feed da equipe {uuid.uuid4().hex[:8]}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/equipe/feed/enviar",
            headers=headers,
            data=data
        )
        
        assert response.status_code == 200, f"Failed to post: {response.text}"
        result = response.json()
        
        assert "message" in result, "No message in response"
        assert "post" in result, "No post object in response"
        assert result["post"]["mensagem"] == data["mensagem"], "Message content mismatch"
        assert "id" in result["post"], "No id in post"
        assert "autor_nome" in result["post"], "No autor_nome in post"
        assert "curtidas" in result["post"], "No curtidas in post"
        
        TestFeedEquipe.created_post_id = result["post"]["id"]
        print(f"Post created successfully: {result['post']['id']}")
    
    def test_enviar_post_vazio_falha(self, auth_token):
        """POST /api/equipe/feed/enviar - Empty post should fail"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        data = {"mensagem": ""}
        
        response = requests.post(
            f"{BASE_URL}/api/equipe/feed/enviar",
            headers=headers,
            data=data
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("Empty post correctly rejected")
    
    def test_get_feed(self, auth_token):
        """GET /api/equipe/feed - Get team feed"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/equipe/feed?page=1&limit=20",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to get feed: {response.text}"
        data = response.json()
        
        assert "posts" in data, "No posts in response"
        assert "total" in data, "No total in response"
        assert "page" in data, "No page in response"
        assert "has_more" in data, "No has_more in response"
        assert "equipe" in data, "No equipe in response"
        assert isinstance(data["posts"], list), "posts should be a list"
        
        print(f"Feed: {len(data['posts'])} posts, total: {data['total']}, equipe: {data['equipe']}")
    
    def test_curtir_post(self, auth_token):
        """POST /api/equipe/feed/{post_id}/curtir - Like post"""
        if not TestFeedEquipe.created_post_id:
            pytest.skip("No post created to like")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        post_id = TestFeedEquipe.created_post_id
        
        # Like the post
        response = requests.post(
            f"{BASE_URL}/api/equipe/feed/{post_id}/curtir",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to like: {response.text}"
        data = response.json()
        
        assert "curtiu" in data, "No curtiu in response"
        print(f"Like action: curtiu = {data['curtiu']}")
        
        # Unlike the post (toggle)
        response2 = requests.post(
            f"{BASE_URL}/api/equipe/feed/{post_id}/curtir",
            headers=headers
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["curtiu"] != data["curtiu"], "Toggle should change curtiu value"
        print(f"Unlike action: curtiu = {data2['curtiu']}")
    
    def test_curtir_post_inexistente(self, auth_token):
        """POST /api/equipe/feed/{post_id}/curtir - Like non-existent post"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/equipe/feed/nonexistent-post-id/curtir",
            headers=headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Non-existent post correctly returns 404")
    
    def test_deletar_post(self, auth_token):
        """DELETE /api/equipe/feed/{post_id} - Delete post"""
        if not TestFeedEquipe.created_post_id:
            pytest.skip("No post created to delete")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        post_id = TestFeedEquipe.created_post_id
        
        response = requests.delete(
            f"{BASE_URL}/api/equipe/feed/{post_id}",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to delete: {response.text}"
        data = response.json()
        
        assert "message" in data, "No message in response"
        print(f"Post deleted: {data['message']}")
        
        # Verify post is gone
        response2 = requests.post(
            f"{BASE_URL}/api/equipe/feed/{post_id}/curtir",
            headers=headers
        )
        assert response2.status_code == 404, "Deleted post should return 404"
    
    def test_deletar_post_inexistente(self, auth_token):
        """DELETE /api/equipe/feed/{post_id} - Delete non-existent post"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.delete(
            f"{BASE_URL}/api/equipe/feed/nonexistent-post-id",
            headers=headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Non-existent post delete correctly returns 404")


class TestDesvincularAtleta:
    """Test Desvincular Atleta endpoint"""
    
    def test_desvincular_atleta_inexistente(self, auth_token):
        """POST /api/assessoria/desvincular-atleta - Non-existent athlete"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/assessoria/desvincular-atleta",
            headers=headers,
            json={
                "atleta_id": "nonexistent-athlete-id",
                "motivo": "Teste"
            }
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Non-existent athlete correctly returns 404")
    
    def test_desvincular_atleta_outra_equipe(self, auth_token, user_info):
        """POST /api/assessoria/desvincular-atleta - Athlete from another team"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Try to unlink self (should fail with different error)
        response = requests.post(
            f"{BASE_URL}/api/assessoria/desvincular-atleta",
            headers=headers,
            json={
                "atleta_id": user_info["id"],
                "motivo": "Teste auto-desvinculacao"
            }
        )
        
        # Should fail because can't unlink yourself
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "não pode desvincular a si mesmo" in response.text.lower() or "si mesmo" in response.text.lower()
        print("Self-unlink correctly rejected")


class TestAccessControl:
    """Test access control for endpoints"""
    
    def test_chat_requires_auth(self):
        """Chat endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/assessoria/chat/historico")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Chat history requires auth - OK")
    
    def test_feed_requires_auth(self):
        """Feed endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/equipe/feed")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Feed requires auth - OK")
    
    def test_desvincular_requires_auth(self):
        """Desvincular endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/assessoria/desvincular-atleta",
            json={"atleta_id": "test", "motivo": "test"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Desvincular requires auth - OK")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
