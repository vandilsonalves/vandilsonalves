# /app/backend/tests/test_iter32_celery_modules.py
"""
Iteration 32: Celery Queue System & Refactored Modules Testing
- Celery Status, Tasks, Task Status
- Corridas Eventos Routes
- Aniversariantes Routes
- Instagram Routes
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Test admin authentication for accessing protected endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in login response"
        return data["token"]

    def test_admin_login(self):
        """Test admin can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data


class TestCeleryStatus:
    """Test Celery status and worker monitoring endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_celery_status_endpoint(self, admin_token):
        """GET /api/celery/status - Check Celery worker status"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/celery/status", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Celery status should have expected fields
        assert "status" in data
        assert "workers" in data
        
        # Log status for debugging
        print(f"Celery Status: {data.get('status')}")
        print(f"Workers: {data.get('workers')}")
    
    def test_celery_status_requires_auth(self):
        """Test Celery status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/celery/status")
        assert response.status_code in [401, 403]


class TestCeleryTasks:
    """Test Celery task dispatching and monitoring"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_dispatch_recalcular_ranking_task(self, admin_token):
        """POST /api/celery/tasks/recalcular-ranking - Dispatch ranking recalculation task"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(
            f"{BASE_URL}/api/celery/tasks/recalcular-ranking",
            headers=headers,
            params={"tipo": "geral"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return task_id
        assert "task_id" in data
        assert "status" in data
        assert "message" in data
        
        # Task should be PENDING or started
        assert data["status"] in ["PENDING", "STARTED", "SUCCESS"]
        print(f"Task ID: {data['task_id']}")
        print(f"Status: {data['status']}")
        
        return data["task_id"]
    
    def test_get_task_status(self, admin_token):
        """GET /api/celery/tasks/{task_id} - Check task status"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First dispatch a task
        response = requests.post(
            f"{BASE_URL}/api/celery/tasks/recalcular-ranking",
            headers=headers,
            params={"tipo": "geral"}
        )
        
        if response.status_code == 200:
            task_id = response.json().get("task_id")
            
            # Check task status
            status_response = requests.get(
                f"{BASE_URL}/api/celery/tasks/{task_id}",
                headers=headers
            )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            assert "task_id" in status_data
            assert "status" in status_data
            assert "ready" in status_data
            
            print(f"Task Status: {status_data}")
    
    def test_list_active_tasks(self, admin_token):
        """GET /api/celery/tasks - List active Celery tasks"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/celery/tasks", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert "tasks" in data
        print(f"Active tasks: {data['total']}")


class TestCorridasEventos:
    """Test Corridas e Eventos (Race Ranking) endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_get_corridas_eventos_list(self):
        """GET /api/corridas-eventos - List corridas (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/corridas-eventos")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)
        print(f"Total corridas eventos: {len(data)}")
    
    def test_get_corridas_eventos_with_filters(self):
        """GET /api/corridas-eventos with estado filter"""
        response = requests.get(
            f"{BASE_URL}/api/corridas-eventos",
            params={"estado": "SP"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_ranking_corridas(self):
        """GET /api/ranking-corridas - Get race ranking"""
        response = requests.get(f"{BASE_URL}/api/ranking-corridas")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have ranking structure
        assert "tipo" in data
        assert "total_corridas" in data
        assert "ranking" in data
        
        print(f"Ranking type: {data['tipo']}")
        print(f"Total corridas: {data['total_corridas']}")
    
    def test_get_ranking_corridas_estadual(self):
        """GET /api/ranking-corridas with tipo=estadual"""
        response = requests.get(
            f"{BASE_URL}/api/ranking-corridas",
            params={"tipo": "estadual", "estado": "SP"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data


class TestAniversariantes:
    """Test Aniversariantes (Birthday) management endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_get_aniversariantes_hoje(self, admin_token):
        """GET /api/admin/aniversariantes/hoje - Get today's birthdays"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/aniversariantes/hoje",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have expected fields
        assert "aniversariantes" in data
        assert "data" in data
        
        print(f"Aniversariantes hoje: {len(data['aniversariantes'])}")
    
    def test_get_aniversariantes_mes(self, admin_token):
        """GET /api/admin/aniversariantes - Get month birthdays"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/aniversariantes",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have calendar structure
        assert "mes" in data
        assert "ano" in data
        assert "calendario" in data
        assert "total_aniversariantes" in data
        
        print(f"Mês: {data['mes']}")
        print(f"Total aniversariantes: {data['total_aniversariantes']}")
    
    def test_get_aniversariantes_mes_with_params(self, admin_token):
        """GET /api/admin/aniversariantes with specific month"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/aniversariantes",
            headers=headers,
            params={"mes": 3, "ano": 2026}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == "Março"
    
    def test_aniversariantes_requires_auth(self):
        """Test aniversariantes endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/aniversariantes/hoje")
        assert response.status_code in [401, 403]


class TestInstagramStats:
    """Test Instagram analytics endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_get_instagram_stats(self, admin_token):
        """GET /api/admin/instagram/stats - Get Instagram analytics stats"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/stats",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have expected fields
        assert "total_analises" in data
        assert "media_score" in data
        assert "media_engagement" in data
        
        print(f"Total análises: {data['total_analises']}")
        print(f"Média score: {data['media_score']}")
    
    def test_get_instagram_ranking(self, admin_token):
        """GET /api/admin/instagram/ranking - Get Instagram profiles ranking"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/instagram/ranking",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data
        assert "total" in data
        print(f"Total profiles in ranking: {data['total']}")
    
    def test_instagram_stats_requires_auth(self):
        """Test Instagram stats requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/instagram/stats")
        assert response.status_code in [401, 403]


class TestRefactoredModulesIntegration:
    """Integration tests for refactored route modules"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rankingrun.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_admin_stats_endpoint(self, admin_token):
        """GET /api/admin/stats - Test admin dashboard stats"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_atletas" in data
        assert "resultados_pendentes" in data
        print(f"Total atletas: {data['total_atletas']}")
    
    def test_admin_pendentes_endpoint(self, admin_token):
        """GET /api/admin/pendentes - Test pending results"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/pendentes", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Pending results: {len(data)}")
    
    def test_monitoring_health(self):
        """GET /api/health - Test health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_cache_stats(self, admin_token):
        """GET /api/monitoring/cache - Test cache statistics"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/api/monitoring/cache",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "available" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
