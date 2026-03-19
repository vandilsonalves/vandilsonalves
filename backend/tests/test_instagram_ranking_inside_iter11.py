"""
Tests for Ranking Run Inside feature - Iteration 11
Bug fixes and new features:
1. Bug fix: Pydantic validation errors now handled properly in frontend (no more 'Objects are not valid as React child')
2. GET /api/admin/instagram/buscar/{username} - Search via Social Blade (may return success: false if blocked - EXPECTED)
3. Interface: Search bar with @username field and 'Buscar Dados' button
4. Interface: Link 'Ou preencha os dados manualmente' opens manual form
5. bio_clareza field is now a select with options: excelente, boa, regular, ruim
6. POST /api/admin/instagram/analisar works with bio_clareza as string
7. Analysis view shows complete dashboard with charts
8. Analysis history shows list correctly
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://assess-photo-fix.preview.emergentagent.com').rstrip('/')

class TestInstagramRankingInside:
    """Tests for Instagram Analytics (Ranking Run Inside) feature"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    def test_instagram_search_endpoint_returns_proper_structure(self, auth_token):
        """
        Test GET /api/admin/instagram/buscar/{username}
        Should return success: true/false with proper structure
        Note: Social Blade may block (403) which is expected behavior
        """
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/instagram/buscar/rankingrun", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Response should always have these fields
        assert "success" in data, "Response should have 'success' field"
        assert "error" in data, "Response should have 'error' field"
        assert "data" in data, "Response should have 'data' field"
        
        # If blocked by Social Blade, success should be false (expected behavior)
        if not data["success"]:
            assert data["error"] is not None, "If not successful, error should have message"
            print(f"Social Blade blocked (expected): {data['error']}")
    
    def test_instagram_search_nonexistent_username(self, auth_token):
        """Test search with a non-existent username"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/instagram/buscar/nonexistent_user_12345678", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        # Either not found or blocked - both are valid responses
    
    def test_instagram_analyze_with_bio_clareza_string(self, auth_token):
        """
        Test POST /api/admin/instagram/analisar with bio_clareza as string
        This tests the bug fix where bio_clareza was changed from boolean to string
        """
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Test with bio_clareza as "excelente"
        payload = {
            "username": "test_iter11_excellent",
            "nome_completo": "Test User Excellent",
            "nicho": "corrida",
            "seguidores": 10000,
            "seguindo": 500,
            "total_posts": 200,
            "media_likes": 500,
            "media_comentarios": 30,
            "media_views_reels": 2000,
            "posts_por_semana": 4,
            "dias_ultimo_post": 1,
            "crescimento_30_dias": 8,
            "desvio_intervalo_posts": 1.5,
            "desvio_engajamento": 1.0,
            "bio_descricao": True,
            "bio_keywords": True,
            "bio_cta": True,
            "bio_link": True,
            "bio_clareza": "excelente",  # String value: excelente, boa, regular, ruim
            "percentual_reels": 60,
            "percentual_carrossel": 25,
            "percentual_foto": 15,
            "picos_anormais": 0,
            "comentarios_repetitivos": 0,
            "horarios_artificiais": 0
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/instagram/analisar", json=payload, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "analysis" in data, "Response should have 'analysis'"
        assert "graficos_data" in data, "Response should have 'graficos_data'"
        assert "recomendacoes" in data, "Response should have 'recomendacoes'"
        
        # Verify analysis fields
        analysis = data["analysis"]
        assert analysis["username"] == "test_iter11_excellent"
        assert analysis["score_final"] > 0, "Score should be calculated"
        assert analysis["classificacao"] in ["Elite Platinum", "Elite Gold", "Premium", "Profissional", "Regular", "Alto Risco"]
        
        # Bio score should be high (10) for excelente clareza with all bio fields true
        assert analysis["nota_bio"] == 10.0, f"Expected nota_bio=10.0 for perfect bio, got {analysis['nota_bio']}"
        
        print(f"Analysis created: score={analysis['score_final']}, classificacao={analysis['classificacao']}")
        
        # Return analysis ID for cleanup
        return analysis["id"]
    
    def test_instagram_analyze_with_bio_clareza_ruim(self, auth_token):
        """Test analysis with bio_clareza='ruim' (poor quality bio)"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        payload = {
            "username": "test_iter11_poor_bio",
            "nicho": "corrida",
            "seguidores": 5000,
            "seguindo": 1000,
            "total_posts": 50,
            "media_likes": 100,
            "media_comentarios": 5,
            "posts_por_semana": 1,
            "bio_descricao": False,
            "bio_keywords": False,
            "bio_cta": False,
            "bio_link": False,
            "bio_clareza": "ruim",  # Poor quality bio
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/instagram/analisar", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        analysis = data["analysis"]
        
        # Bio score should be 0 for ruim clareza with no bio fields
        assert analysis["nota_bio"] == 0.0, f"Expected nota_bio=0.0 for poor bio, got {analysis['nota_bio']}"
    
    def test_instagram_analyze_with_bio_clareza_boa(self, auth_token):
        """Test analysis with bio_clareza='boa' (good quality bio)"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        payload = {
            "username": "test_iter11_good_bio",
            "nicho": "fitness",
            "seguidores": 8000,
            "seguindo": 400,
            "total_posts": 150,
            "media_likes": 300,
            "media_comentarios": 20,
            "posts_por_semana": 3,
            "bio_descricao": True,
            "bio_keywords": True,
            "bio_cta": False,
            "bio_link": True,
            "bio_clareza": "boa",  # Good quality bio
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/instagram/analisar", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        analysis = data["analysis"]
        
        # Bio score should be moderate (1.5+3.0+1.5+1.5 = 7.5 for desc+keywords+link+clareza_boa)
        assert 6.0 <= analysis["nota_bio"] <= 8.0, f"Expected nota_bio between 6-8 for good bio, got {analysis['nota_bio']}"
    
    def test_list_instagram_analyses(self, auth_token):
        """Test GET /api/admin/instagram/analises returns list of analyses"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/instagram/analises", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        
        # Check that existing analyses have required fields
        if len(data) > 0:
            analysis = data[0]
            required_fields = ["id", "username", "score_final", "classificacao", "seguidores"]
            for field in required_fields:
                assert field in analysis, f"Analysis should have '{field}' field"
        
        print(f"Found {len(data)} analyses")
    
    def test_get_single_analysis_with_graphs(self, auth_token):
        """Test GET /api/admin/instagram/analises/{id} returns analysis with graph data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First get list to find an existing analysis
        list_response = requests.get(f"{BASE_URL}/api/admin/instagram/analises", headers=headers)
        assert list_response.status_code == 200
        analyses = list_response.json()
        
        if len(analyses) == 0:
            pytest.skip("No analyses available to test")
        
        analysis_id = analyses[0]["id"]
        
        # Get single analysis
        response = requests.get(f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have analysis and graficos_data
        assert "analysis" in data or "id" in data, "Response should have analysis data"
        
        # If it returns full structure with graphs
        if "graficos_data" in data:
            graphs = data["graficos_data"]
            assert "radar" in graphs, "Should have radar chart data"
            assert "gauge" in graphs, "Should have gauge chart data"
            assert "comparativo" in graphs, "Should have comparativo chart data"
            assert "formatos" in graphs, "Should have formatos chart data"
    
    def test_delete_analysis(self, auth_token):
        """Test DELETE /api/admin/instagram/analises/{id}"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a test analysis to delete
        create_payload = {
            "username": "test_to_delete_iter11",
            "nicho": "corrida",
            "seguidores": 1000,
            "seguindo": 100,
            "total_posts": 50,
            "media_likes": 50,
            "media_comentarios": 5,
            "posts_por_semana": 2,
            "bio_clareza": "regular"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/admin/instagram/analisar", 
                                        json=create_payload, headers=headers)
        assert create_response.status_code == 200
        analysis_id = create_response.json()["analysis"]["id"]
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}", 
                                          headers=headers)
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        # Verify it's deleted
        get_response = requests.get(f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}", 
                                    headers=headers)
        assert get_response.status_code == 404, "Deleted analysis should return 404"
    
    def test_validation_error_handling(self, auth_token):
        """
        Test that Pydantic validation errors are returned properly
        This tests the bug fix for 'Objects are not valid as React child'
        """
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Send invalid data (missing required fields)
        invalid_payload = {
            "username": "",  # Empty username
            "seguidores": -100,  # Negative followers
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/instagram/analisar", 
                                 json=invalid_payload, headers=headers)
        
        # Should return 422 for validation error OR 200 with defaults
        # The important thing is it doesn't crash the frontend
        assert response.status_code in [200, 422], f"Unexpected status: {response.status_code}"
        
        # If 422, check error structure
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data, "Validation error should have 'detail'"


class TestInstagramExport:
    """Tests for Instagram analysis export functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        return response.json().get("token")
    
    def test_export_xlsx(self, auth_token):
        """Test XLSX export endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get an existing analysis ID
        list_response = requests.get(f"{BASE_URL}/api/admin/instagram/analises", headers=headers)
        if list_response.status_code != 200 or len(list_response.json()) == 0:
            pytest.skip("No analyses available")
        
        analysis_id = list_response.json()[0]["id"]
        
        # Export to XLSX
        response = requests.get(f"{BASE_URL}/api/admin/instagram/export/{analysis_id}", 
                                headers=headers)
        
        assert response.status_code == 200
        assert "application/vnd.openxmlformats" in response.headers.get("content-type", "")
    
    def test_export_csv(self, auth_token):
        """Test CSV export endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get an existing analysis ID
        list_response = requests.get(f"{BASE_URL}/api/admin/instagram/analises", headers=headers)
        if list_response.status_code != 200 or len(list_response.json()) == 0:
            pytest.skip("No analyses available")
        
        analysis_id = list_response.json()[0]["id"]
        
        # Export to CSV
        response = requests.get(f"{BASE_URL}/api/admin/instagram/export-csv/{analysis_id}", 
                                headers=headers)
        
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")


# Cleanup test data after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Cleanup test-created analyses after all tests"""
    yield
    
    # Get token
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@runpro.com",
        "password": "admin123"
    })
    if response.status_code != 200:
        return
    
    token = response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all analyses
    list_response = requests.get(f"{BASE_URL}/api/admin/instagram/analises", headers=headers)
    if list_response.status_code != 200:
        return
    
    analyses = list_response.json()
    
    # Delete test analyses (those starting with test_iter11)
    for analysis in analyses:
        if analysis.get("username", "").startswith("test_iter11") or \
           analysis.get("username", "").startswith("test_to_delete"):
            requests.delete(f"{BASE_URL}/api/admin/instagram/analises/{analysis['id']}", 
                            headers=headers)
            print(f"Cleaned up test analysis: {analysis['username']}")
