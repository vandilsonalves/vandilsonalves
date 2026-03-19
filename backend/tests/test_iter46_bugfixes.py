"""
Iteration 46 - Backend Testing for Bug Fixes and Feed Comments
Tests:
1. Ranking Estadual bug fix - posicao_estadual should be correct (not None)
2. Feed Comments endpoints (POST/GET/DELETE comentarios)
3. Image upload endpoint removal verification
4. Feed response includes comentarios_preview and total_comentarios
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER = {"email": "admin@runpro.com", "password": "admin123"}
TEST_ASSESSORIA = "Assessoria CAFAV"  # Estado ES, posicao estadual 1


class TestAuthentication:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["token"]
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data  # API returns 'user' not 'usuario'
        print(f"Login successful for {TEST_USER['email']}")


class TestRankingEstadualBugFix:
    """Tests for ranking estadual bug fix - posicao_estadual should show correctly"""
    
    @pytest.fixture(scope="class")
    def token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    def test_assessoria_posicao_estadual_not_none(self, token):
        """Test that posicao_estadual is not None for assessorias with estado"""
        import urllib.parse
        nome_encoded = urllib.parse.quote(TEST_ASSESSORIA)
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/assessoria/{nome_encoded}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Failed to get assessoria: {response.text}"
        data = response.json()
        
        print(f"Assessoria: {data.get('nome')}")
        print(f"Estado: {data.get('estado')}")
        print(f"posicao_estadual: {data.get('posicao_estadual')}")
        print(f"posicao_nacional: {data.get('posicao_nacional')}")
        
        # Verify estado is not empty
        assert data.get("estado"), f"Estado should not be empty, got: {data.get('estado')}"
        
        # Verify posicao_estadual is not None and is a valid integer
        posicao_estadual = data.get("posicao_estadual")
        assert posicao_estadual is not None, f"posicao_estadual should not be None, got: {posicao_estadual}"
        assert isinstance(posicao_estadual, int), f"posicao_estadual should be int, got: {type(posicao_estadual)}"
        assert posicao_estadual >= 1, f"posicao_estadual should be >= 1, got: {posicao_estadual}"
        
        print(f"SUCCESS: posicao_estadual = {posicao_estadual} (not None)")
    
    def test_assessoria_cafav_posicao_estadual_is_1(self, token):
        """Test that Assessoria CAFAV has posicao_estadual = 1 in ES"""
        import urllib.parse
        nome_encoded = urllib.parse.quote(TEST_ASSESSORIA)
        
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/assessoria/{nome_encoded}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # According to the test request, CAFAV should be position 1 in ES
        assert data.get("estado") == "ES", f"Expected estado ES, got: {data.get('estado')}"
        assert data.get("posicao_estadual") == 1, f"Expected posicao_estadual 1, got: {data.get('posicao_estadual')}"
        
        print(f"SUCCESS: {TEST_ASSESSORIA} has posicao_estadual = 1 in ES")
    
    def test_ranking_estadual_endpoint(self, token):
        """Test ranking estadual returns positions correctly"""
        response = requests.get(
            f"{BASE_URL}/api/liga-assessorias/ranking?tipo=estadual&estado=ES",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("tipo") == "estadual"
        assert "ranking" in data
        
        # Check first assessoria has posicao = 1
        if data["ranking"]:
            first = data["ranking"][0]
            assert first.get("posicao") == 1, f"First position should be 1, got: {first.get('posicao')}"
            print(f"First in ES ranking: {first.get('nome')} with posicao {first.get('posicao')}")
        
        print(f"SUCCESS: Estadual ranking has {len(data['ranking'])} assessorias in ES")


class TestFeedCommentsEndpoints:
    """Tests for feed comments functionality"""
    
    @pytest.fixture(scope="class")
    def token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def test_post_id(self, token):
        """Create a test post and return its ID"""
        response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": "TEST_Post para teste de comentarios iter46", "tipo": "texto"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Failed to create post: {response.text}"
        return response.json()["post_id"]
    
    def test_add_comentario(self, token, test_post_id):
        """Test POST /api/feed/posts/{post_id}/comentarios"""
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{test_post_id}/comentarios",
            json={"texto": "Este e um comentario de teste iter46"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Failed to add comment: {response.text}"
        data = response.json()
        
        assert "comentario_id" in data, f"Response should contain comentario_id"
        assert data.get("message") == "Comentário adicionado!"
        
        print(f"SUCCESS: Comment added with ID: {data['comentario_id']}")
        return data["comentario_id"]
    
    def test_add_comentario_empty_text(self, token, test_post_id):
        """Test that empty comment text is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{test_post_id}/comentarios",
            json={"texto": "   "},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400, f"Empty comment should be rejected, got: {response.status_code}"
        print("SUCCESS: Empty comment rejected with 400")
    
    def test_add_comentario_too_long(self, token, test_post_id):
        """Test that comment over 500 chars is rejected"""
        long_text = "x" * 501
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{test_post_id}/comentarios",
            json={"texto": long_text},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400, f"Long comment should be rejected, got: {response.status_code}"
        print("SUCCESS: Comment > 500 chars rejected with 400")
    
    def test_get_comentarios(self, token, test_post_id):
        """Test GET /api/feed/posts/{post_id}/comentarios"""
        # First add a comment
        requests.post(
            f"{BASE_URL}/api/feed/posts/{test_post_id}/comentarios",
            json={"texto": "Comentario para listar"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Then get comments
        response = requests.get(
            f"{BASE_URL}/api/feed/posts/{test_post_id}/comentarios",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Failed to get comments: {response.text}"
        data = response.json()
        
        assert "comentarios" in data, "Response should contain comentarios"
        assert "total" in data, "Response should contain total"
        assert "pagina" in data, "Response should contain pagina"
        assert data["total"] >= 1, f"Should have at least 1 comment, got: {data['total']}"
        
        # Verify comment structure
        if data["comentarios"]:
            com = data["comentarios"][0]
            assert "id" in com, "Comment should have id"
            assert "texto" in com, "Comment should have texto"
            assert "autor_id" in com, "Comment should have autor_id"
            assert "autor" in com, "Comment should have autor (enriched)"
        
        print(f"SUCCESS: GET comentarios returned {data['total']} comments")
    
    def test_delete_comentario(self, token, test_post_id):
        """Test DELETE /api/feed/comentarios/{comentario_id}"""
        # First add a comment
        add_response = requests.post(
            f"{BASE_URL}/api/feed/posts/{test_post_id}/comentarios",
            json={"texto": "TEST_Comentario para deletar"},
            headers={"Authorization": f"Bearer {token}"}
        )
        comentario_id = add_response.json()["comentario_id"]
        
        # Then delete it
        response = requests.delete(
            f"{BASE_URL}/api/feed/comentarios/{comentario_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Failed to delete comment: {response.text}"
        data = response.json()
        assert data.get("message") == "Comentário deletado"
        
        print(f"SUCCESS: Comment {comentario_id} deleted")
    
    def test_delete_comentario_not_found(self, token):
        """Test DELETE non-existent comment returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/feed/comentarios/nonexistent-id-12345",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404, f"Should return 404, got: {response.status_code}"
        print("SUCCESS: Delete non-existent comment returns 404")


class TestFeedResponseStructure:
    """Tests for feed response structure with comments"""
    
    @pytest.fixture(scope="class")
    def token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    def test_feed_includes_comentarios_fields(self, token):
        """Test GET /api/feed includes comentarios_preview and total_comentarios"""
        response = requests.get(
            f"{BASE_URL}/api/feed",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Failed to get feed: {response.text}"
        data = response.json()
        
        assert "posts" in data, "Response should contain posts"
        
        if data["posts"]:
            post = data["posts"][0]
            
            # Check for comentarios_preview field
            assert "comentarios_preview" in post, f"Post should have comentarios_preview field"
            assert isinstance(post["comentarios_preview"], list), "comentarios_preview should be a list"
            
            # Check for total_comentarios field
            assert "total_comentarios" in post, f"Post should have total_comentarios field"
            assert isinstance(post["total_comentarios"], int), "total_comentarios should be int"
            
            print(f"Post has total_comentarios: {post['total_comentarios']}")
            print(f"Post has comentarios_preview with {len(post['comentarios_preview'])} items")
            
            # Check comentarios_preview structure if any
            if post["comentarios_preview"]:
                com = post["comentarios_preview"][0]
                assert "id" in com, "Comment preview should have id"
                assert "texto" in com, "Comment preview should have texto"
                assert "autor" in com, "Comment preview should have autor"
        
        print(f"SUCCESS: Feed includes comentarios_preview and total_comentarios")


class TestImageUploadRemoved:
    """Tests to verify image upload endpoint was removed"""
    
    @pytest.fixture(scope="class")
    def token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def test_post_id(self, token):
        """Create a test post for image upload test"""
        response = requests.post(
            f"{BASE_URL}/api/feed/posts",
            json={"texto": "TEST_Post para teste de imagem", "tipo": "texto"},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()["post_id"]
    
    def test_image_upload_endpoint_removed(self, token, test_post_id):
        """Test POST /api/feed/posts/{post_id}/imagem returns 404 or error"""
        # Try to upload an image (endpoint should not exist)
        files = {"imagem": ("test.jpg", b"fake image content", "image/jpeg")}
        
        response = requests.post(
            f"{BASE_URL}/api/feed/posts/{test_post_id}/imagem",
            headers={"Authorization": f"Bearer {token}"},
            files=files
        )
        
        # Endpoint should return 404 (Not Found) or 405 (Method Not Allowed)
        assert response.status_code in [404, 405, 422], \
            f"Image upload endpoint should be removed, expected 404/405/422, got: {response.status_code}"
        
        print(f"SUCCESS: Image upload endpoint returns {response.status_code} (removed/not found)")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    def test_cleanup_test_posts(self, token):
        """Delete test posts created during testing"""
        # Get all posts
        response = requests.get(
            f"{BASE_URL}/api/feed/meus-posts?limite=50",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            deleted = 0
            for post in data.get("posts", []):
                if "TEST_" in post.get("texto", ""):
                    del_response = requests.delete(
                        f"{BASE_URL}/api/feed/posts/{post['id']}",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if del_response.status_code == 200:
                        deleted += 1
            
            print(f"Cleanup: Deleted {deleted} test posts")
        
        # Always pass cleanup
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
