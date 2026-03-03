"""
Test: Instagram Analytics (Ranking Run Inside) Feature
Testing: POST /api/admin/instagram/analisar - criar nova análise com cálculo de score
         GET /api/admin/instagram/analises - listar todas as análises
         GET /api/admin/instagram/analises/{id} - obter detalhes com dados de gráficos
         DELETE /api/admin/instagram/analises/{id} - excluir análise
         GET /api/admin/instagram/export/{id} - exportar XLSX
         GET /api/admin/instagram/export-csv/{id} - exportar CSV
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestInstagramAnalytics:
    """Instagram Analytics (Ranking Run Inside) endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as admin to get token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json()["token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_01_list_instagram_analyses(self):
        """GET /api/admin/instagram/analises - List all Instagram analyses"""
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/analises",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Failed with {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Listed {len(data)} Instagram analyses")
    
    def test_02_create_instagram_analysis(self):
        """POST /api/admin/instagram/analisar - Create new analysis with score calculation"""
        # Test data with valid Instagram profile metrics
        test_profile = {
            "username": "test_influencer_pytest",
            "nome_completo": "Test Influencer Pytest",
            "nicho": "corrida",
            "seguidores": 25000,
            "seguindo": 800,
            "total_posts": 150,
            "media_likes": 1200.0,
            "media_comentarios": 45.0,
            "media_views_reels": 15000.0,
            "posts_por_semana": 4.0,
            "dias_ultimo_post": 2,
            "crescimento_30_dias": 5.5,
            "desvio_intervalo_posts": 1.5,
            "desvio_engajamento": 0.8,
            "bio_descricao": True,
            "bio_keywords": True,
            "bio_cta": True,
            "bio_link": True,
            "bio_clareza": "excelente",
            "percentual_reels": 60,
            "percentual_carrossel": 25,
            "percentual_foto": 15,
            "picos_anormais": 0,
            "comentarios_repetitivos": 0,
            "horarios_artificiais": 0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar",
            json=test_profile,
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Failed with {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "analysis" in data, "Response should contain 'analysis'"
        assert "graficos_data" in data, "Response should contain 'graficos_data'"
        assert "recomendacoes" in data, "Response should contain 'recomendacoes'"
        
        analysis = data["analysis"]
        
        # Verify analysis fields
        assert analysis["username"] == test_profile["username"]
        assert "score_final" in analysis
        assert "classificacao" in analysis
        assert 0 <= analysis["score_final"] <= 100, "Score should be between 0-100"
        
        # Verify score metrics (all should be 0-10)
        metrics = ["nota_bio", "nota_frequencia", "nota_engajamento", "nota_crescimento",
                   "nota_consistencia", "nota_padroes", "nota_reels", "nota_formatos"]
        for metric in metrics:
            assert metric in analysis, f"Missing metric: {metric}"
            assert 0 <= analysis[metric] <= 10, f"{metric} should be between 0-10"
        
        # Verify classification is valid
        valid_classifications = ["Elite Platinum", "Elite Gold", "Premium", "Profissional", "Regular", "Alto Risco"]
        assert analysis["classificacao"] in valid_classifications, f"Invalid classification: {analysis['classificacao']}"
        
        # Verify graphs data
        graficos = data["graficos_data"]
        assert "radar" in graficos
        assert "gauge" in graficos
        assert "comparativo" in graficos
        assert "formatos" in graficos
        assert "metricas" in graficos
        
        # Store analysis ID for subsequent tests
        self.__class__.created_analysis_id = analysis["id"]
        print(f"✓ Created analysis for @{analysis['username']} with score {analysis['score_final']}/100 ({analysis['classificacao']})")
    
    def test_03_get_analysis_details(self):
        """GET /api/admin/instagram/analises/{id} - Get analysis details with chart data"""
        # Use the previously created analysis
        analysis_id = getattr(self.__class__, 'created_analysis_id', None)
        if not analysis_id:
            # Fallback: List and get first analysis
            list_response = requests.get(
                f"{BASE_URL}/api/admin/instagram/analises",
                headers=self.headers
            )
            assert list_response.status_code == 200
            analyses = list_response.json()
            if not analyses:
                pytest.skip("No analyses available to test")
            analysis_id = analyses[0]["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Failed with {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "analysis" in data, "Response should contain 'analysis'"
        assert "graficos_data" in data, "Response should contain 'graficos_data'"
        assert "recomendacoes" in data, "Response should contain 'recomendacoes'"
        
        # Verify graphs data for charts
        graficos = data["graficos_data"]
        
        # Radar chart data
        assert "labels" in graficos["radar"], "Radar should have labels"
        assert "values" in graficos["radar"], "Radar should have values"
        assert len(graficos["radar"]["labels"]) == 8, "Should have 8 metrics for radar"
        
        # Gauge chart data
        assert "value" in graficos["gauge"], "Gauge should have value"
        assert "ranges" in graficos["gauge"], "Gauge should have ranges"
        
        print(f"✓ Got analysis details for ID {analysis_id}")
    
    def test_04_get_nonexistent_analysis(self):
        """GET /api/admin/instagram/analises/{id} - 404 for non-existent analysis"""
        fake_id = "non-existent-analysis-id"
        
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/analises/{fake_id}",
            headers=self.headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Correctly returns 404 for non-existent analysis")
    
    def test_05_export_xlsx(self):
        """GET /api/admin/instagram/export/{id} - Export analysis as XLSX"""
        analysis_id = getattr(self.__class__, 'created_analysis_id', None)
        if not analysis_id:
            # Fallback: Get existing analysis
            list_response = requests.get(
                f"{BASE_URL}/api/admin/instagram/analises",
                headers=self.headers
            )
            analyses = list_response.json()
            if not analyses:
                pytest.skip("No analyses available to test export")
            analysis_id = analyses[0]["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/export/{analysis_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Export XLSX failed: {response.status_code}"
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers.get("content-type", "")
        assert len(response.content) > 0, "XLSX file should not be empty"
        print(f"✓ Exported XLSX ({len(response.content)} bytes)")
    
    def test_06_export_csv(self):
        """GET /api/admin/instagram/export-csv/{id} - Export analysis as CSV"""
        analysis_id = getattr(self.__class__, 'created_analysis_id', None)
        if not analysis_id:
            # Fallback: Get existing analysis
            list_response = requests.get(
                f"{BASE_URL}/api/admin/instagram/analises",
                headers=self.headers
            )
            analyses = list_response.json()
            if not analyses:
                pytest.skip("No analyses available to test export")
            analysis_id = analyses[0]["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/export-csv/{analysis_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Export CSV failed: {response.status_code}"
        assert "text/csv" in response.headers.get("content-type", "")
        
        # Verify CSV content
        csv_content = response.text
        assert "Ranking Run Inside" in csv_content, "CSV should contain header"
        assert "Score Final" in csv_content, "CSV should contain Score Final"
        print(f"✓ Exported CSV ({len(csv_content)} chars)")
    
    def test_07_score_calculation_validation(self):
        """Verify score calculation logic with different profile types"""
        
        # Test with high-quality profile (should get high score)
        high_quality_profile = {
            "username": "high_quality_test",
            "nicho": "corrida",
            "seguidores": 100000,
            "seguindo": 500,
            "total_posts": 300,
            "media_likes": 8000.0,
            "media_comentarios": 500.0,
            "media_views_reels": 80000.0,
            "posts_por_semana": 5.0,
            "dias_ultimo_post": 1,
            "crescimento_30_dias": 8.0,
            "desvio_intervalo_posts": 0.5,
            "desvio_engajamento": 0.3,
            "bio_descricao": True,
            "bio_keywords": True,
            "bio_cta": True,
            "bio_link": True,
            "bio_clareza": "excelente",
            "percentual_reels": 50,
            "percentual_carrossel": 30,
            "percentual_foto": 20,
            "picos_anormais": 0,
            "comentarios_repetitivos": 0,
            "horarios_artificiais": 0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar",
            json=high_quality_profile,
            headers=self.headers
        )
        
        assert response.status_code == 200
        high_score = response.json()["analysis"]["score_final"]
        self.__class__.high_quality_id = response.json()["analysis"]["id"]
        
        # Test with low-quality profile (should get lower score)
        low_quality_profile = {
            "username": "low_quality_test",
            "nicho": "corrida",
            "seguidores": 5000,
            "seguindo": 3000,  # High following ratio
            "total_posts": 50,
            "media_likes": 50.0,  # Low engagement
            "media_comentarios": 2.0,
            "media_views_reels": 100.0,
            "posts_por_semana": 0.5,  # Low frequency
            "dias_ultimo_post": 30,  # Inactive
            "crescimento_30_dias": 0.5,  # Low growth
            "desvio_intervalo_posts": 5.0,  # Inconsistent
            "desvio_engajamento": 3.0,
            "bio_descricao": False,
            "bio_keywords": False,
            "bio_cta": False,
            "bio_link": False,
            "bio_clareza": "ruim",
            "percentual_reels": 10,
            "percentual_carrossel": 10,
            "percentual_foto": 80,
            "picos_anormais": 5,  # Suspicious
            "comentarios_repetitivos": 10,
            "horarios_artificiais": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar",
            json=low_quality_profile,
            headers=self.headers
        )
        
        assert response.status_code == 200
        low_score = response.json()["analysis"]["score_final"]
        self.__class__.low_quality_id = response.json()["analysis"]["id"]
        
        # High quality should have higher score
        assert high_score > low_score, f"High quality score ({high_score}) should be > low quality ({low_score})"
        print(f"✓ Score validation passed: High={high_score}, Low={low_score}")
    
    def test_08_delete_analysis(self):
        """DELETE /api/admin/instagram/analises/{id} - Delete an analysis"""
        analysis_id = getattr(self.__class__, 'created_analysis_id', None)
        if not analysis_id:
            pytest.skip("No analysis to delete")
        
        response = requests.delete(
            f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Delete failed: {response.status_code}"
        
        # Verify deletion
        get_response = requests.get(
            f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}",
            headers=self.headers
        )
        assert get_response.status_code == 404, "Deleted analysis should return 404"
        print(f"✓ Successfully deleted analysis {analysis_id}")
    
    def test_09_delete_nonexistent_analysis(self):
        """DELETE /api/admin/instagram/analises/{id} - 404 for non-existent"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/instagram/analises/non-existent-id",
            headers=self.headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Correctly returns 404 when deleting non-existent analysis")
    
    def test_10_unauthorized_access(self):
        """Verify endpoints require authentication"""
        endpoints = [
            ("GET", f"{BASE_URL}/api/admin/instagram/analises"),
            ("POST", f"{BASE_URL}/api/admin/instagram/analisar"),
        ]
        
        for method, url in endpoints:
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url, json={})
            
            assert response.status_code in [401, 403, 422], f"{method} {url} should require auth"
        
        print("✓ All endpoints correctly require authentication")
    
    def test_cleanup(self):
        """Cleanup test data"""
        # Delete test analyses created during tests
        for attr in ['high_quality_id', 'low_quality_id']:
            analysis_id = getattr(self.__class__, attr, None)
            if analysis_id:
                requests.delete(
                    f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}",
                    headers=self.headers
                )
        print("✓ Cleanup completed")


class TestInstagramAnalyticsValidation:
    """Additional validation tests for Instagram Analytics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as admin"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        self.token = login_response.json()["token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_classification_ranges(self):
        """Verify classification is assigned correctly based on score"""
        # Test profile that should get score ~70-80 (Profissional)
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar",
            json={
                "username": "classification_test",
                "nicho": "corrida",
                "seguidores": 20000,
                "seguindo": 500,
                "total_posts": 100,
                "media_likes": 800.0,
                "media_comentarios": 30.0,
                "media_views_reels": 8000.0,
                "posts_por_semana": 3.0,
                "dias_ultimo_post": 3,
                "crescimento_30_dias": 3.0,
                "desvio_intervalo_posts": 2.0,
                "desvio_engajamento": 1.0,
                "bio_descricao": True,
                "bio_keywords": True,
                "bio_cta": False,
                "bio_link": True,
                "bio_clareza": "boa",
                "percentual_reels": 40,
                "percentual_carrossel": 30,
                "percentual_foto": 30,
                "picos_anormais": 0,
                "comentarios_repetitivos": 0,
                "horarios_artificiais": 0
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        analysis = response.json()["analysis"]
        score = analysis["score_final"]
        classificacao = analysis["classificacao"]
        
        # Verify classification matches score range
        if score >= 95:
            assert classificacao == "Elite Platinum"
        elif score >= 90:
            assert classificacao == "Elite Gold"
        elif score >= 80:
            assert classificacao == "Premium"
        elif score >= 70:
            assert classificacao == "Profissional"
        elif score >= 60:
            assert classificacao == "Regular"
        else:
            assert classificacao == "Alto Risco"
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/admin/instagram/analises/{analysis['id']}",
            headers=self.headers
        )
        print(f"✓ Classification correct: score={score}, class={classificacao}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
