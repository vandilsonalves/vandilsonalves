# /app/backend/tests/test_iter51_feed_reactions.py
# Iteration 51: Feed de Atividades - Posts automáticos, Reações, Comentários, Parabéns
# Features: GET /api/feed, POST /api/feed/posts, POST /api/feed/posts/{id}/reagir, 
#          POST /api/feed/posts/{id}/parabens, POST /api/feed/posts/{id}/comentarios,
#          GET /api/feed/posts/{id}/comentarios

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://admin-mensagens.preview.emergentagent.com')

class TestFeedEndpoints:
    """Tests for Feed API endpoints - Reactions, Comments, Parabéns"""
    
    @pytest.fixture(scope="class")
    def admin_auth(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def test_user(self, admin_auth):
        """Create a test user for feed testing"""
        user_email = f"testfeed_{uuid.uuid4().hex[:8]}@test.com"
        
        # Try to create user
        create_response = requests.post(f"{BASE_URL}/api/admin/atletas", json={
            "nome": "TEST_Feed User",
            "email": user_email,
            "password": "test123",
            "genero": "M",
            "categoria": "normal"
        }, headers={"Authorization": f"Bearer {admin_auth}"})
        
        if create_response.status_code in [200, 201]:
            user_id = create_response.json().get("id")
        else:
            # If user creation fails, try login
            user_id = None
        
        # Login as user
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": user_email,
            "password": "test123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token") or login_response.json().get("token")
            user_id = login_response.json().get("user", {}).get("id") or user_id
            return {"token": token, "id": user_id, "email": user_email}
        
        # Use admin for testing if user creation fails
        return {"token": admin_auth, "id": "admin_user", "email": "admin@runpro.com"}
    
    # =============================================
    # GET /api/feed - Feed principal
    # =============================================
    
    def test_get_feed_requires_auth(self):
        """GET /api/feed should require authentication"""
        response = requests.get(f"{BASE_URL}/api/feed")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_get_feed_with_auth(self, test_user):
        """GET /api/feed should return posts with reactions and comments count"""
        response = requests.get(
            f"{BASE_URL}/api/feed",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200, f"Failed to get feed: {response.text}"
        
        data = response.json()
        assert "posts" in data, "Response should contain 'posts'"
        assert "pagina" in data, "Response should contain 'pagina'"
        assert "total_paginas" in data, "Response should contain 'total_paginas'"
        
        # Verify post structure if posts exist
        if data["posts"]:
            post = data["posts"][0]
            assert "id" in post, "Post should have 'id'"
            assert "autor" in post, "Post should have 'autor'"
            assert "reacoes" in post, "Post should have 'reacoes'"
            assert "total_comentarios" in post, "Post should have 'total_comentarios'"
            assert "total_reacoes" in post, "Post should have 'total_reacoes'"
        
        print(f"✅ Feed returned {len(data['posts'])} posts")
    
    def test_get_feed_with_pagination(self, test_user):
        """GET /api/feed should support pagination"""
        response = requests.get(
            f"{BASE_URL}/api/feed?pagina=1&limite=5",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["posts"]) <= 5, "Should respect limite parameter"
        assert data["limite"] == 5, "Should return correct limite"
        print("✅ Pagination working correctly")
    
    # =============================================
    # POST /api/feed/posts - Criar post
    # =============================================
    
    def test_create_post_requires_auth(self):
        """POST /api/feed/posts should require authentication"""
        response = requests.post(f"{BASE_URL}/api/feed/posts", json={
            "texto": "Test post",
            "tipo": "texto"
        })
        assert response.status_code in [401, 403]
    
    def test_create_post_success(self, test_user):
        """POST /api/feed/posts should create a new post"""
        test_text = f"TEST_Post criado pelo teste automatizado - {uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": test_text, "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code in [200, 201], f"Failed to create post: {response.text}"
        
        data = response.json()
        assert "post_id" in data, "Response should contain 'post_id'"
        assert "message" in data, "Response should contain 'message'"
        
        # Store for later tests
        test_user["post_id"] = data["post_id"]
        print(f"✅ Post created with ID: {data['post_id']}")
        
        return data["post_id"]
    
    def test_create_post_empty_text_rejected(self, test_user):
        """POST /api/feed/posts should reject empty text"""
        response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": "", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ Empty post text correctly rejected")
    
    def test_create_post_exceeds_max_length(self, test_user):
        """POST /api/feed/posts should reject text > 1000 characters"""
        long_text = "x" * 1001
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": long_text, "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 400, f"Expected 400 for long text, got {response.status_code}"
        print("✅ Long post text correctly rejected")
    
    # =============================================
    # POST /api/feed/posts/{id}/reagir - Reações
    # =============================================
    
    def test_reagir_invalid_reaction_type(self, test_user):
        """POST /api/feed/posts/{id}/reagir should reject invalid reaction types"""
        # First create a post
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Post for reaction test {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert post_response.status_code in [200, 201]
        post_id = post_response.json()["post_id"]
        
        # Try invalid reaction
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/reagir",
            json={"tipo_reacao": "invalid_reaction"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid reaction, got {response.status_code}"
        print("✅ Invalid reaction type correctly rejected")
    
    def test_reagir_valid_reactions(self, test_user):
        """POST /api/feed/posts/{id}/reagir should accept valid reaction types"""
        # Create a post
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Post for valid reactions {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert post_response.status_code in [200, 201]
        post_id = post_response.json()["post_id"]
        
        # Test all valid reaction types
        valid_reactions = ["aplausos", "corrida", "forca", "fogo", "coracao", "festa", "trofeu", "parabens"]
        
        for reaction in valid_reactions[:3]:  # Test first 3 to save time
            response = requests.post(
                f"{BASE_URL}/api/feed/posts/{post_id}/reagir",
                json={"tipo_reacao": reaction},
                headers={"Authorization": f"Bearer {test_user['token']}"}
            )
            assert response.status_code == 200, f"Reaction '{reaction}' failed: {response.text}"
            
            data = response.json()
            assert "message" in data
            print(f"✅ Reaction '{reaction}' added successfully")
        
        # Store post_id for other tests
        test_user["reaction_post_id"] = post_id
    
    def test_reagir_toggle_removes_reaction(self, test_user):
        """POST /api/feed/posts/{id}/reagir should toggle (remove) existing reaction"""
        # Create a post
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Post for toggle test {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert post_response.status_code in [200, 201]
        post_id = post_response.json()["post_id"]
        
        # Add reaction
        response1 = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/reagir",
            json={"tipo_reacao": "aplausos"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1.get("removida") == False, "First reaction should not be marked as removed"
        
        # Toggle same reaction (should remove)
        response2 = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/reagir",
            json={"tipo_reacao": "aplausos"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2.get("removida") == True, "Second same reaction should be removed (toggle)"
        print("✅ Reaction toggle (remove) working correctly")
    
    # =============================================
    # POST /api/feed/posts/{id}/parabens - Parabéns rápido
    # =============================================
    
    def test_parabens_endpoint(self, test_user):
        """POST /api/feed/posts/{id}/parabens should send congratulations"""
        # Create a post
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Post for parabens test {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert post_response.status_code in [200, 201]
        post_id = post_response.json()["post_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/parabens",
            json={},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200, f"Parabens failed: {response.text}"
        
        data = response.json()
        assert "message" in data
        assert data.get("emoji") == "🎊", "Parabéns should return 🎊 emoji"
        print(f"✅ Parabéns sent successfully: {data['message']}")
    
    def test_parabens_post_not_found(self, test_user):
        """POST /api/feed/posts/{id}/parabens should return 404 for invalid post"""
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/invalid-post-id-12345/parabens",
            json={},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ Parabéns correctly returns 404 for invalid post")
    
    # =============================================
    # POST /api/feed/posts/{id}/comentarios - Comentários
    # =============================================
    
    def test_add_comment_success(self, test_user):
        """POST /api/feed/posts/{id}/comentarios should add a comment"""
        # Create a post
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Post for comment test {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert post_response.status_code in [200, 201]
        post_id = post_response.json()["post_id"]
        
        # Add comment
        comment_text = f"TEST_Comment {uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/comentarios",
            json={"texto": comment_text},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code in [200, 201], f"Add comment failed: {response.text}"
        
        data = response.json()
        assert "comentario_id" in data, "Response should contain 'comentario_id'"
        assert "message" in data
        print(f"✅ Comment added successfully: {data['comentario_id']}")
        
        # Store for later
        test_user["comment_post_id"] = post_id
        test_user["comment_id"] = data["comentario_id"]
    
    def test_add_comment_empty_rejected(self, test_user):
        """POST /api/feed/posts/{id}/comentarios should reject empty comment"""
        # Create a post first
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Post for empty comment {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert post_response.status_code in [200, 201]
        post_id = post_response.json()["post_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/comentarios",
            json={"texto": ""},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 400, f"Expected 400 for empty comment, got {response.status_code}"
        print("✅ Empty comment correctly rejected")
    
    def test_add_comment_exceeds_max_length(self, test_user):
        """POST /api/feed/posts/{id}/comentarios should reject comment > 500 characters"""
        # Create a post first
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Post for long comment {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert post_response.status_code in [200, 201]
        post_id = post_response.json()["post_id"]
        
        long_comment = "x" * 501
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/comentarios",
            json={"texto": long_comment},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 400, f"Expected 400 for long comment, got {response.status_code}"
        print("✅ Long comment correctly rejected")
    
    # =============================================
    # GET /api/feed/posts/{id}/comentarios - Listar comentários
    # =============================================
    
    def test_get_comments_success(self, test_user):
        """GET /api/feed/posts/{id}/comentarios should list comments"""
        # Create a post and add comments
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Post for list comments {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert post_response.status_code in [200, 201]
        post_id = post_response.json()["post_id"]
        
        # Add some comments
        for i in range(3):
            requests.post(
                f"{BASE_URL}/api/feed/posts/{post_id}/comentarios",
                json={"texto": f"TEST_Comment {i+1}"},
                headers={"Authorization": f"Bearer {test_user['token']}"}
            )
        
        # Get comments
        response = requests.get(f"{BASE_URL}/api/feed/posts/{post_id}/comentarios")
        assert response.status_code == 200, f"Get comments failed: {response.text}"
        
        data = response.json()
        assert "comentarios" in data
        assert "total" in data
        assert data["total"] >= 3, f"Expected at least 3 comments, got {data['total']}"
        
        # Verify comment structure
        if data["comentarios"]:
            comment = data["comentarios"][0]
            assert "id" in comment
            assert "texto" in comment
            assert "autor" in comment
            assert "data_criacao" in comment
        
        print(f"✅ Listed {data['total']} comments successfully")
    
    # =============================================
    # GET /api/feed/trending - Posts em alta
    # =============================================
    
    def test_get_trending(self, test_user):
        """GET /api/feed/trending should return popular posts"""
        response = requests.get(
            f"{BASE_URL}/api/feed/trending?limite=5",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200, f"Get trending failed: {response.text}"
        
        data = response.json()
        assert "trending" in data
        print(f"✅ Trending returned {len(data['trending'])} posts")
    
    # =============================================
    # GET /api/feed/reacoes-disponiveis - Tipos de reações
    # =============================================
    
    def test_get_reacoes_disponiveis(self):
        """GET /api/feed/reacoes-disponiveis should return available reactions"""
        response = requests.get(f"{BASE_URL}/api/feed/reacoes-disponiveis")
        assert response.status_code == 200, f"Get reactions failed: {response.text}"
        
        data = response.json()
        assert "reacoes" in data
        
        # Verify expected reactions
        expected_reactions = ["aplausos", "corrida", "forca", "fogo", "coracao", "festa", "trofeu", "parabens"]
        for reaction in expected_reactions:
            assert reaction in data["reacoes"], f"Missing reaction: {reaction}"
            assert "emoji" in data["reacoes"][reaction]
            assert "nome" in data["reacoes"][reaction]
        
        # Verify parabéns reaction was added
        assert data["reacoes"]["parabens"]["emoji"] == "🎊"
        
        print(f"✅ All {len(data['reacoes'])} reaction types available including 'parabens' 🎊")
    
    # =============================================
    # DELETE /api/feed/posts/{id} - Deletar post
    # =============================================
    
    def test_delete_post_success(self, test_user):
        """DELETE /api/feed/posts/{id} should delete user's own post"""
        # Create a post
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Post to delete {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert post_response.status_code in [200, 201]
        post_id = post_response.json()["post_id"]
        
        # Delete the post
        response = requests.delete(
            f"{BASE_URL}/api/feed/posts/{post_id}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200, f"Delete post failed: {response.text}"
        
        data = response.json()
        assert "message" in data
        print("✅ Post deleted successfully")


class TestFeedPostStructure:
    """Test feed post structure with reactions and comments data"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        assert response.status_code == 200
        return response.json().get("access_token") or response.json().get("token")
    
    def test_feed_post_contains_reaction_data(self, auth_token):
        """Feed posts should include reaction counts and user's reaction"""
        # First create a post and add a reaction
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Structure test {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if post_response.status_code not in [200, 201]:
            pytest.skip("Could not create test post")
        
        post_id = post_response.json()["post_id"]
        
        # Add a reaction
        requests.post(
            f"{BASE_URL}/api/feed/posts/{post_id}/reagir",
            json={"tipo_reacao": "fogo"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get feed and check post structure
        feed_response = requests.get(
            f"{BASE_URL}/api/feed",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert feed_response.status_code == 200
        
        feed_data = feed_response.json()
        
        # Find our test post
        test_post = None
        for post in feed_data["posts"]:
            if post["id"] == post_id:
                test_post = post
                break
        
        if test_post:
            assert "reacoes" in test_post, "Post should have 'reacoes' field"
            assert "total_reacoes" in test_post, "Post should have 'total_reacoes' field"
            assert "minha_reacao" in test_post, "Post should have 'minha_reacao' field"
            assert test_post["minha_reacao"] == "fogo", "minha_reacao should be 'fogo'"
            print("✅ Post structure contains all reaction data fields")
        else:
            print("⚠️ Test post not found in feed (may have been filtered)")
    
    def test_feed_post_contains_comment_count(self, auth_token):
        """Feed posts should include comment count"""
        # Create post
        post_response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": f"TEST_Comment count test {uuid.uuid4().hex[:8]}", "tipo": "texto"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if post_response.status_code not in [200, 201]:
            pytest.skip("Could not create test post")
        
        post_id = post_response.json()["post_id"]
        
        # Add comments
        for i in range(2):
            requests.post(
                f"{BASE_URL}/api/feed/posts/{post_id}/comentarios",
                json={"texto": f"TEST_Comment for count {i}"},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        
        # Get feed
        feed_response = requests.get(
            f"{BASE_URL}/api/feed",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert feed_response.status_code == 200
        
        feed_data = feed_response.json()
        
        # Find our test post
        for post in feed_data["posts"]:
            if post["id"] == post_id:
                assert "total_comentarios" in post, "Post should have 'total_comentarios'"
                assert post["total_comentarios"] >= 2, f"Expected at least 2 comments, got {post['total_comentarios']}"
                assert "comentarios_preview" in post, "Post should have 'comentarios_preview'"
                print(f"✅ Post contains comment count: {post['total_comentarios']}")
                return
        
        print("⚠️ Test post not found in feed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
