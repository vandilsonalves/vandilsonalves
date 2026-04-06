"""
Test cases for the 30-day rule bypass for 2026 races
Tests the POST /api/resultados/submeter endpoint with various date scenarios
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://geo-filtered-admin.preview.emergentagent.com')

class Test30DaysRuleBypass:
    """Tests for the 30-day submission rule with 2026 bypass"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token before each test"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "teste.dono@teste.com", "password": "123456"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def _create_submission_data(self, data_competicao: str):
        """Helper to create form data for submission"""
        return {
            "nome_competicao": "TEST_Corrida de Teste",
            "colocacao": "1",
            "cidade_competicao": "São Paulo",
            "estado_competicao": "SP",
            "data_competicao": data_competicao,
            "link_resultado": "https://example.com/resultado",
            "tempo": "01:30:00",
            "distancia": "10KM"
        }
    
    def test_2026_race_over_30_days_should_be_accepted(self):
        """
        Test: A 2026 race with more than 30 days should be ACCEPTED
        The 30-day rule is bypassed for 2026 races
        """
        # Use a date in 2026 that is more than 30 days ago (e.g., Jan 1, 2026)
        data_competicao = "2026-01-01"
        data = self._create_submission_data(data_competicao)
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=self.headers
        )
        
        # Should be accepted (200 or 201) - NOT rejected with 400
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
        # The request should NOT fail due to 30-day rule
        # It may fail for other reasons (e.g., authorization period) but NOT for 30-day rule
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            assert "30 dias" not in error_detail, f"2026 race should bypass 30-day rule, but got: {error_detail}"
        
        # If we get 200/201, the test passes
        # If we get 403 (authorization period), that's a different validation - test still passes for 30-day rule
        assert response.status_code in [200, 201, 403], f"Unexpected status: {response.status_code}"
    
    def test_2025_race_over_30_days_should_be_rejected(self):
        """
        Test: A 2025 race with more than 30 days should be REJECTED
        The 30-day rule applies to non-2026 years
        """
        # Use a date in 2025 that is more than 30 days ago
        data_competicao = "2025-01-15"
        data = self._create_submission_data(data_competicao)
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=self.headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
        # Should be rejected with 400 due to 30-day rule
        assert response.status_code == 400, f"Expected 400 for 2025 race >30 days, got {response.status_code}"
        
        error_detail = response.json().get("detail", "")
        assert "30 dias" in error_detail, f"Expected 30-day error message, got: {error_detail}"
    
    def test_2027_race_over_30_days_should_be_rejected(self):
        """
        Test: A 2027 race with more than 30 days should be REJECTED
        The bypass only applies to 2026, not 2027+
        """
        # Use a date in 2027 that would be more than 30 days ago (hypothetically)
        # Since we're in Jan 2026, a 2027 date would be in the future
        # So we test with a date that would be >30 days if it were in the past
        # Actually, 2027 dates are future dates from Jan 2026, so they should fail as "future date"
        data_competicao = "2027-01-15"
        data = self._create_submission_data(data_competicao)
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=self.headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
        # Should be rejected - either as future date or (if somehow in past) as >30 days
        assert response.status_code == 400, f"Expected 400 for 2027 date, got {response.status_code}"
    
    def test_future_date_should_be_rejected(self):
        """
        Test: A future date should always be REJECTED
        """
        # Use tomorrow's date
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        data = self._create_submission_data(future_date)
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=self.headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
        # Should be rejected with 400 due to future date
        assert response.status_code == 400, f"Expected 400 for future date, got {response.status_code}"
        
        error_detail = response.json().get("detail", "")
        assert "futura" in error_detail.lower(), f"Expected future date error, got: {error_detail}"
    
    def test_2026_race_within_30_days_should_be_accepted(self):
        """
        Test: A 2026 race within 30 days should be ACCEPTED (normal case)
        """
        # Use a recent date in 2026 (within 30 days)
        recent_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        
        # Only test if we're in 2026
        if datetime.now().year != 2026:
            pytest.skip("This test is only valid when running in 2026")
        
        data = self._create_submission_data(recent_date)
        
        response = requests.post(
            f"{BASE_URL}/api/resultados/submeter",
            data=data,
            headers=self.headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
        # Should be accepted (or fail for other reasons, not 30-day rule)
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            assert "30 dias" not in error_detail, f"Recent 2026 race should be accepted, but got: {error_detail}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
