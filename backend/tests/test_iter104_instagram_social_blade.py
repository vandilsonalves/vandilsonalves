# /app/backend/tests/test_iter104_instagram_social_blade.py
# Tests for Instagram Ranking Run Inside - Social Blade Manual Analysis
# Features: POST analisar-simplificado, upload-foto, GET/DELETE analises

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestInstagramSocialBlade:
    """Tests for Instagram Ranking Run Inside - Social Blade Manual Analysis"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Get admin token"""
        self.token = None
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
        else:
            pytest.skip("Admin login failed - skipping tests")
        
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_analysis_id = None
    
    def test_01_list_analyses_endpoint(self):
        """Test GET /api/admin/instagram/analises - List all analyses"""
        response = requests.get(f"{BASE_URL}/api/admin/instagram/analises", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASS: List analyses returned {len(data)} items")
    
    def test_02_create_analysis_with_all_fields(self):
        """Test POST /api/admin/instagram/analisar-simplificado - Create analysis with all 15+ manual fields"""
        unique_username = f"test_social_blade_{uuid.uuid4().hex[:8]}"
        payload = {
            "username": unique_username,
            "nome_completo": "Test User Social Blade",
            "data_analise": "2026-01-15",
            # Dados Gerais
            "seguidores": 10000,
            "seguindo": 500,
            "total_posts": 350,
            "nota": "B+",
            "classificacao_sb": "B+",
            "classificacao_seguidores": "Micro-influencer",
            # Crescimento 30d
            "ganho_seguidores_30d": 800,
            "perda_seguidores_30d": 100,
            "media_semanal_ganho": 200,
            "media_semanal_perda": 25,
            # Interações 30d
            "posts_30d": 20,
            "media_semanal_posts": 5,
            "views_reels_6": 60000,
            "curtidas_medias": 350,
            "comentarios_medios": 15
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "analysis" in data, "Response should contain 'analysis'"
        assert "graficos_data" in data, "Response should contain 'graficos_data'"
        
        analysis = data["analysis"]
        graficos = data["graficos_data"]
        
        # Verify analysis fields
        assert analysis["username"] == unique_username
        assert analysis["seguidores"] == 10000
        assert analysis["tipo"] == "social_blade"
        assert "id" in analysis
        
        # Verify all 7 graficos_data sections exist
        required_sections = ["nota_gauge", "views_reels", "engajamento", "curtidas", "comentarios", "crescimento", "posts", "scores"]
        for section in required_sections:
            assert section in graficos, f"graficos_data should contain '{section}'"
        
        # Verify scores section
        scores = graficos["scores"]
        assert "views" in scores
        assert "engajamento" in scores
        assert "curtidas" in scores
        assert "comentarios" in scores
        assert "crescimento" in scores
        assert "posts" in scores
        assert "media" in scores
        
        # Store for later tests
        self.__class__.created_analysis_id = analysis["id"]
        self.__class__.created_username = unique_username
        
        print(f"PASS: Created analysis for @{unique_username} with ID {analysis['id']}")
        print(f"  - Score médio: {scores['media']}/10")
        print(f"  - Engajamento: {graficos['engajamento']['taxa']}%")
        print(f"  - Crescimento: {graficos['crescimento']['taxa']}%")
    
    def test_03_get_single_analysis_with_graficos(self):
        """Test GET /api/admin/instagram/analises/{id} - Get analysis with complete graficos_data"""
        if not hasattr(self.__class__, 'created_analysis_id') or not self.__class__.created_analysis_id:
            pytest.skip("No analysis created in previous test")
        
        analysis_id = self.__class__.created_analysis_id
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "analysis" in data
        assert "graficos_data" in data
        
        graficos = data["graficos_data"]
        
        # Verify all 7 chart sections with their specific data
        # 1. Nota Gauge (Donut)
        assert "nota_gauge" in graficos
        assert "nota" in graficos["nota_gauge"]
        assert "taxa_curtidas_pct" in graficos["nota_gauge"]
        
        # 2. Views Reels (Barras)
        assert "views_reels" in graficos
        assert "media_views" in graficos["views_reels"]
        assert "escala" in graficos["views_reels"]
        
        # 3. Engajamento (Pizza)
        assert "engajamento" in graficos
        assert "taxa" in graficos["engajamento"]
        assert "labels" in graficos["engajamento"]
        assert "values" in graficos["engajamento"]
        
        # 4. Curtidas (Colunas)
        assert "curtidas" in graficos
        assert "valor" in graficos["curtidas"]
        assert "score" in graficos["curtidas"]
        
        # 5. Comentários (Linhas)
        assert "comentarios" in graficos
        assert "valor" in graficos["comentarios"]
        assert "taxa" in graficos["comentarios"]
        
        # 6. Crescimento (Radar)
        assert "crescimento" in graficos
        assert "radar_labels" in graficos["crescimento"]
        assert "radar_values" in graficos["crescimento"]
        
        # 7. Posts (Histograma)
        assert "posts" in graficos
        assert "total" in graficos["posts"]
        assert "escala" in graficos["posts"]
        
        # Scores
        assert "scores" in graficos
        
        print(f"PASS: GET analysis {analysis_id} returned complete graficos_data with all 7 sections")
    
    def test_04_verify_formula_calculations(self):
        """Test that backend correctly calculates all 7 formulas"""
        # Create analysis with known values to verify formulas
        payload = {
            "username": f"test_formulas_{uuid.uuid4().hex[:6]}",
            "seguidores": 10000,
            "seguindo": 500,
            "total_posts": 100,
            "nota": "B",
            "ganho_seguidores_30d": 500,  # 5% growth
            "perda_seguidores_30d": 100,
            "posts_30d": 20,
            "media_semanal_posts": 5,
            "views_reels_6": 60000,  # 10000 avg = 100% of followers
            "curtidas_medias": 300,  # 3% of followers
            "comentarios_medios": 20  # 0.2% of followers
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        analysis = data["analysis"]
        graficos = data["graficos_data"]
        
        # Formula 1: Taxa de Curtidas = (curtidas_medias / seguidores) * 100
        expected_taxa_curtidas = (300 / 10000) * 100  # 3%
        assert abs(analysis["taxa_curtidas_pct"] - expected_taxa_curtidas) < 0.1, f"Taxa curtidas should be ~{expected_taxa_curtidas}%"
        
        # Formula 2: Views Reels = views_reels_6 / 6
        expected_media_views = 60000 / 6  # 10000
        assert abs(graficos["views_reels"]["media_views"] - expected_media_views) < 1
        
        # Formula 3: Engajamento = ((curtidas + comentarios) / seguidores) * 100
        expected_engajamento = ((300 + 20) / 10000) * 100  # 3.2%
        assert abs(analysis["engajamento_pct"] - expected_engajamento) < 0.1
        
        # Formula 6: Crescimento = (ganho_30d / seguidores) * 100
        expected_crescimento = (500 / 10000) * 100  # 5%
        assert abs(analysis["crescimento_pct"] - expected_crescimento) < 0.1
        
        # Verify saldo
        expected_saldo = 500 - 100  # 400
        assert analysis["saldo_seguidores"] == expected_saldo
        
        print("PASS: All formula calculations verified correctly")
        print(f"  - Taxa Curtidas: {analysis['taxa_curtidas_pct']}% (expected ~{expected_taxa_curtidas}%)")
        print(f"  - Engajamento: {analysis['engajamento_pct']}% (expected ~{expected_engajamento}%)")
        print(f"  - Crescimento: {analysis['crescimento_pct']}% (expected ~{expected_crescimento}%)")
    
    def test_05_delete_analysis(self):
        """Test DELETE /api/admin/instagram/analises/{id}"""
        if not hasattr(self.__class__, 'created_analysis_id') or not self.__class__.created_analysis_id:
            pytest.skip("No analysis created in previous test")
        
        analysis_id = self.__class__.created_analysis_id
        response = requests.delete(
            f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify it's deleted
        get_response = requests.get(
            f"{BASE_URL}/api/admin/instagram/analises/{analysis_id}",
            headers=self.headers
        )
        assert get_response.status_code == 404, "Deleted analysis should return 404"
        
        print(f"PASS: Analysis {analysis_id} deleted successfully")
    
    def test_06_upload_foto_endpoint(self):
        """Test POST /api/admin/instagram/upload-foto"""
        # Create a simple test image (1x1 pixel PNG)
        import base64
        # Minimal valid PNG (1x1 transparent pixel)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        
        files = {"foto": ("test_profile.png", png_data, "image/png")}
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/upload-foto",
            files=files,
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "foto_url" in data, "Response should contain 'foto_url'"
        assert data["foto_url"].startswith("/uploads/inside/"), f"foto_url should start with /uploads/inside/, got {data['foto_url']}"
        
        print(f"PASS: Photo uploaded successfully: {data['foto_url']}")
    
    def test_07_create_analysis_with_foto(self):
        """Test creating analysis with uploaded photo URL"""
        # First upload a photo
        import base64
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        
        files = {"foto": ("profile.png", png_data, "image/png")}
        upload_response = requests.post(
            f"{BASE_URL}/api/admin/instagram/upload-foto",
            files=files,
            headers=self.headers
        )
        assert upload_response.status_code == 200
        foto_url = upload_response.json()["foto_url"]
        
        # Create analysis with foto_url
        payload = {
            "username": f"test_with_foto_{uuid.uuid4().hex[:6]}",
            "nome_completo": "User With Photo",
            "seguidores": 5000,
            "seguindo": 300,
            "total_posts": 100,
            "nota": "A",
            "foto_url": foto_url,
            "ganho_seguidores_30d": 200,
            "perda_seguidores_30d": 50,
            "posts_30d": 15,
            "views_reels_6": 30000,
            "curtidas_medias": 200,
            "comentarios_medios": 10
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["analysis"]["foto_url"] == foto_url
        
        print(f"PASS: Analysis created with foto_url: {foto_url}")
    
    def test_08_export_xlsx_endpoint(self):
        """Test GET /api/admin/instagram/export/{id} - XLSX export"""
        # First create an analysis
        payload = {
            "username": f"test_export_{uuid.uuid4().hex[:6]}",
            "seguidores": 8000,
            "seguindo": 400,
            "total_posts": 200,
            "nota": "B+",
            "ganho_seguidores_30d": 300,
            "posts_30d": 18,
            "views_reels_6": 40000,
            "curtidas_medias": 250,
            "comentarios_medios": 12
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers=self.headers
        )
        assert create_response.status_code == 200
        analysis_id = create_response.json()["analysis"]["id"]
        
        # Test XLSX export
        export_response = requests.get(
            f"{BASE_URL}/api/admin/instagram/export/{analysis_id}?token={self.token}",
            headers=self.headers
        )
        assert export_response.status_code == 200, f"Expected 200, got {export_response.status_code}"
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in export_response.headers.get("content-type", "")
        
        print(f"PASS: XLSX export works for analysis {analysis_id}")
    
    def test_09_export_csv_endpoint(self):
        """Test GET /api/admin/instagram/export-csv/{id} - CSV export"""
        # First create an analysis
        payload = {
            "username": f"test_csv_{uuid.uuid4().hex[:6]}",
            "seguidores": 6000,
            "seguindo": 350,
            "total_posts": 150,
            "nota": "C+",
            "ganho_seguidores_30d": 150,
            "posts_30d": 12,
            "views_reels_6": 25000,
            "curtidas_medias": 180,
            "comentarios_medios": 8
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers=self.headers
        )
        assert create_response.status_code == 200
        analysis_id = create_response.json()["analysis"]["id"]
        
        # Test CSV export
        export_response = requests.get(
            f"{BASE_URL}/api/admin/instagram/export-csv/{analysis_id}?token={self.token}",
            headers=self.headers
        )
        assert export_response.status_code == 200, f"Expected 200, got {export_response.status_code}"
        assert "text/csv" in export_response.headers.get("content-type", "")
        
        print(f"PASS: CSV export works for analysis {analysis_id}")
    
    def test_10_score_grades_calculation(self):
        """Test that scores generate correct grades (A++ to F)"""
        # Test with high engagement values (should get high scores)
        payload = {
            "username": f"test_grades_{uuid.uuid4().hex[:6]}",
            "seguidores": 10000,
            "nota": "A++",
            "ganho_seguidores_30d": 1500,  # 15% growth = Excelente
            "posts_30d": 35,  # >30 = Excelente
            "views_reels_6": 150000,  # 250% of followers = Excelente
            "curtidas_medias": 1200,  # 12% = Excelente
            "comentarios_medios": 80  # 0.8% = Excelente
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/instagram/analisar-simplificado",
            json=payload,
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        scores = data["graficos_data"]["scores"]
        
        # All scores should be high (8-10)
        assert scores["views"] >= 8, f"Views score should be >=8, got {scores['views']}"
        assert scores["engajamento"] >= 8, f"Engajamento score should be >=8, got {scores['engajamento']}"
        assert scores["curtidas"] >= 8, f"Curtidas score should be >=8, got {scores['curtidas']}"
        assert scores["crescimento"] >= 8, f"Crescimento score should be >=8, got {scores['crescimento']}"
        assert scores["posts"] >= 8, f"Posts score should be >=8, got {scores['posts']}"
        
        print(f"PASS: High engagement values produce high scores")
        print(f"  - Scores: views={scores['views']}, eng={scores['engajamento']}, curt={scores['curtidas']}, cresc={scores['crescimento']}, posts={scores['posts']}")
        print(f"  - Media: {scores['media']}/10")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
