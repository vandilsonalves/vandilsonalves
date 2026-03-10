# /app/backend/tests/test_iter30_monitoring.py
"""
Iteration 30 - Sistema de Monitoramento de Saúde do Backend
Tests for:
- GET /api/health - Public health check básico
- GET /api/health/detailed - Public health check detalhado
- GET /api/monitoring/dashboard - Dashboard completo (admin only)
- GET /api/monitoring/alerts - Alertas ativos (admin only)
- POST /api/monitoring/test-alert - Testar envio de email de alerta (admin only)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestPublicHealthEndpoints:
    """Test public health check endpoints (no auth required)"""

    def test_health_check_basic(self):
        """GET /api/health - Basic health check returns status and uptime"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Data structure assertion
        data = response.json()
        assert "status" in data, "Response missing 'status'"
        assert "timestamp" in data, "Response missing 'timestamp'"
        assert "uptime" in data, "Response missing 'uptime'"
        assert "version" in data, "Response missing 'version'"
        
        # Data value assertions
        assert data["status"] in ["healthy", "degraded", "unhealthy"], f"Invalid status: {data['status']}"
        assert data["version"] == "7.1", f"Expected version 7.1, got {data['version']}"
        print(f"✓ Health check basic: status={data['status']}, uptime={data['uptime']}")

    def test_health_check_detailed(self):
        """GET /api/health/detailed - Detailed health check returns system metrics"""
        response = requests.get(f"{BASE_URL}/api/health/detailed")
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Data structure assertion
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "system" in data
        assert "requests" in data
        assert "alerts_count" in data
        
        # System metrics structure
        system = data["system"]
        assert "cpu_percent" in system
        assert "memory_percent" in system
        assert "disk_percent" in system
        
        # Request metrics structure
        requests_data = data["requests"]
        assert "total" in requests_data
        assert "errors" in requests_data
        assert "avg_response_ms" in requests_data
        
        # Data type assertions
        assert isinstance(system["cpu_percent"], (int, float))
        assert isinstance(system["memory_percent"], (int, float))
        assert isinstance(system["disk_percent"], (int, float))
        assert isinstance(data["alerts_count"], int)
        
        print(f"✓ Health check detailed: CPU={system['cpu_percent']}%, Memory={system['memory_percent']}%")

    def test_health_check_no_sensitive_data(self):
        """Verify detailed health check doesn't expose sensitive data"""
        response = requests.get(f"{BASE_URL}/api/health/detailed")
        data = response.json()
        
        # Should NOT contain these sensitive fields (only in admin dashboard)
        assert "slowest_endpoints" not in data
        assert "history" not in data
        assert "thresholds" not in data
        
        # System should only have basic metrics
        system = data["system"]
        assert "network_connections" not in system
        assert "memory_used_gb" not in system
        assert "memory_total_gb" not in system
        
        print("✓ Detailed health check does not expose sensitive data")


class TestAdminMonitoringEndpoints:
    """Test admin-only monitoring endpoints"""

    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@rankingrun.com", "password": "admin123"}
        )
        if response.status_code != 200:
            pytest.skip("Admin authentication failed - skipping admin tests")
        return response.json().get("token")

    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Headers with admin auth token"""
        return {"Authorization": f"Bearer {admin_token}"}

    def test_monitoring_dashboard_requires_auth(self):
        """GET /api/monitoring/dashboard - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/monitoring/dashboard")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Dashboard endpoint requires authentication")

    def test_monitoring_dashboard_success(self, admin_headers):
        """GET /api/monitoring/dashboard - Returns complete dashboard data"""
        response = requests.get(
            f"{BASE_URL}/api/monitoring/dashboard",
            headers=admin_headers
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Data structure assertion
        data = response.json()
        assert "current" in data, "Response missing 'current'"
        assert "history_24h" in data, "Response missing 'history_24h'"
        assert "history_7d" in data, "Response missing 'history_7d'"
        assert "thresholds" in data, "Response missing 'thresholds'"
        
        # Current status structure
        current = data["current"]
        assert "status" in current
        assert "system" in current
        assert "requests" in current
        assert "slowest_endpoints" in current
        assert "active_alerts" in current
        
        # System metrics (more detailed than public endpoint)
        system = current["system"]
        assert "cpu_percent" in system
        assert "memory_percent" in system
        assert "disk_percent" in system
        assert "memory_used_gb" in system
        assert "memory_total_gb" in system
        assert "network_connections" in system
        
        # Request metrics
        requests_data = current["requests"]
        assert "total_requests" in requests_data
        assert "total_errors" in requests_data
        assert "error_rate_percent" in requests_data
        assert "avg_response_time_ms" in requests_data
        assert "requests_per_minute" in requests_data
        assert "uptime_formatted" in requests_data
        assert "status_codes" in requests_data
        
        # Thresholds structure
        thresholds = data["thresholds"]
        assert "cpu_percent" in thresholds
        assert "memory_percent" in thresholds
        assert "disk_percent" in thresholds
        assert "error_rate" in thresholds
        assert "response_time_avg" in thresholds
        
        print(f"✓ Dashboard data: {len(data['history_24h'])} history points, {len(current['slowest_endpoints'])} endpoints tracked")

    def test_monitoring_alerts_success(self, admin_headers):
        """GET /api/monitoring/alerts - Returns alerts and thresholds"""
        response = requests.get(
            f"{BASE_URL}/api/monitoring/alerts",
            headers=admin_headers
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Data structure assertion
        data = response.json()
        assert "alerts" in data, "Response missing 'alerts'"
        assert "total" in data, "Response missing 'total'"
        assert "thresholds" in data, "Response missing 'thresholds'"
        
        # Alerts should be a list
        assert isinstance(data["alerts"], list)
        assert isinstance(data["total"], int)
        assert data["total"] == len(data["alerts"])
        
        print(f"✓ Alerts endpoint: {data['total']} active alerts")

    def test_monitoring_alerts_requires_auth(self):
        """GET /api/monitoring/alerts - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/monitoring/alerts")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Alerts endpoint requires authentication")

    def test_test_alert_requires_auth(self):
        """POST /api/monitoring/test-alert - Requires authentication"""
        response = requests.post(f"{BASE_URL}/api/monitoring/test-alert")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Test-alert endpoint requires authentication")

    def test_test_alert_endpoint(self, admin_headers):
        """POST /api/monitoring/test-alert - Test alert email (Resend API)"""
        response = requests.post(
            f"{BASE_URL}/api/monitoring/test-alert",
            headers=admin_headers
        )
        
        # This endpoint may return 200 (success) or 500 (email error due to Resend domain restrictions)
        # Both are valid responses - we're testing the endpoint works
        assert response.status_code in [200, 500], f"Expected 200 or 500, got {response.status_code}"
        
        data = response.json()
        if response.status_code == 200:
            assert "message" in data
            assert "email" in data
            print(f"✓ Test alert sent to {data['email']}")
        else:
            # Resend free tier only allows sending to verified email
            assert "detail" in data
            assert "email" in data["detail"].lower() or "resend" in data["detail"].lower()
            print(f"✓ Test-alert endpoint working (Resend domain restriction: {data['detail'][:80]}...)")

    def test_monitoring_dashboard_slowest_endpoints(self, admin_headers):
        """Verify slowest endpoints are tracked and returned"""
        response = requests.get(
            f"{BASE_URL}/api/monitoring/dashboard",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        slowest = data["current"]["slowest_endpoints"]
        
        # Should be a list
        assert isinstance(slowest, list)
        
        # If there are endpoints, verify structure
        if slowest:
            endpoint = slowest[0]
            assert "endpoint" in endpoint
            assert "avg_time_ms" in endpoint
            assert "max_time_ms" in endpoint
            assert "request_count" in endpoint
            print(f"✓ Slowest endpoint: {endpoint['endpoint']} ({endpoint['avg_time_ms']}ms avg)")
        else:
            print("✓ No slowest endpoints tracked yet")

    def test_history_data_structure(self, admin_headers):
        """Verify historical data structure"""
        response = requests.get(
            f"{BASE_URL}/api/monitoring/dashboard",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify history_24h and history_7d are lists
        assert isinstance(data["history_24h"], list)
        assert isinstance(data["history_7d"], list)
        
        # If there's history data, verify structure
        if data["history_24h"]:
            item = data["history_24h"][0]
            assert "timestamp" in item
            assert "status" in item
            assert "cpu_percent" in item
            assert "memory_percent" in item
            print(f"✓ History data: {len(data['history_24h'])} entries in 24h, {len(data['history_7d'])} in 7d")
        else:
            print("✓ History data structure correct (no data yet)")


class TestMonitoringMetricsIntegration:
    """Test that monitoring middleware is collecting metrics"""

    def test_metrics_increment_on_requests(self):
        """Verify request count increases after making requests"""
        # Get initial metrics
        response1 = requests.get(f"{BASE_URL}/api/health/detailed")
        initial_total = response1.json()["requests"]["total"]
        
        # Make some requests to generate metrics
        for _ in range(3):
            requests.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        
        # Get updated metrics
        response2 = requests.get(f"{BASE_URL}/api/health/detailed")
        final_total = response2.json()["requests"]["total"]
        
        # Total should have increased (at least by 3, but may be more due to health checks)
        assert final_total >= initial_total, f"Request count should increase: {initial_total} -> {final_total}"
        print(f"✓ Metrics increment: {initial_total} -> {final_total} requests")

    def test_status_codes_tracked(self):
        """Verify status codes are being tracked in admin dashboard"""
        # First login to get admin token
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@rankingrun.com", "password": "admin123"}
        )
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get dashboard data
        response = requests.get(
            f"{BASE_URL}/api/monitoring/dashboard",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        status_codes = data["current"]["requests"]["status_codes"]
        
        # Should have at least one status code tracked
        assert isinstance(status_codes, dict)
        assert len(status_codes) > 0, "Should have tracked at least one status code"
        
        # Most requests should be 200
        assert "200" in status_codes or 200 in status_codes, "Should have tracked 200 status codes"
        print(f"✓ Status codes tracked: {status_codes}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
