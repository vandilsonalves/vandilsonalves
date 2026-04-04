"""
Iteration 100: Premium Badge Feature Tests
Tests for verified badge (premium) display in ranking table
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://geo-filtered-admin.preview.emergentagent.com')

class TestPremiumBadgeBackend:
    """Backend tests for premium badge feature"""
    
    def test_ranking_endpoint_returns_is_premium_field(self):
        """Test that ranking endpoint returns is_premium field for each athlete"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2026&page=1&limit=20")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "ranking" in data, "Response should contain 'ranking' key"
        assert len(data["ranking"]) > 0, "Ranking should have at least one athlete"
        
        # Check that all athletes have is_premium field
        for athlete in data["ranking"]:
            assert "is_premium" in athlete, f"Athlete {athlete.get('nome')} missing is_premium field"
            assert isinstance(athlete["is_premium"], bool), f"is_premium should be boolean for {athlete.get('nome')}"
        
        print(f"✅ All {len(data['ranking'])} athletes have is_premium field")
    
    def test_premium_athletes_exist_in_ranking(self):
        """Test that there are premium athletes in the ranking"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/masculino/M?ano=2026&page=1&limit=50")
        assert response.status_code == 200
        
        data = response.json()
        premium_athletes = [a for a in data["ranking"] if a.get("is_premium") == True]
        non_premium_athletes = [a for a in data["ranking"] if a.get("is_premium") == False]
        
        print(f"Total athletes: {len(data['ranking'])}")
        print(f"Premium athletes: {len(premium_athletes)}")
        print(f"Non-premium athletes: {len(non_premium_athletes)}")
        
        # There should be some premium athletes
        assert len(premium_athletes) > 0, "There should be at least one premium athlete"
        
        # Print first 5 premium athletes
        print("\nFirst 5 premium athletes:")
        for a in premium_athletes[:5]:
            print(f"  - {a['nome']} (pos {a['colocacao']})")
    
    def test_ranking_nacional_returns_is_premium(self):
        """Test that /ranking/nacional endpoint also returns is_premium"""
        response = requests.get(f"{BASE_URL}/api/ranking/nacional?ano=2026")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0, "Nacional ranking should have athletes"
        
        # Check first athlete has is_premium
        first_athlete = data[0]
        assert "is_premium" in first_athlete, "Nacional ranking should include is_premium field"
        print(f"✅ Nacional ranking includes is_premium field")
    
    def test_feminino_ranking_has_is_premium(self):
        """Test that feminino ranking also has is_premium field"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/feminino/F?ano=2026&page=1&limit=20")
        assert response.status_code == 200
        
        data = response.json()
        if len(data.get("ranking", [])) > 0:
            for athlete in data["ranking"]:
                assert "is_premium" in athlete, f"Feminino athlete {athlete.get('nome')} missing is_premium"
            print(f"✅ Feminino ranking ({len(data['ranking'])} athletes) has is_premium field")
        else:
            pytest.skip("No feminino athletes in ranking")
    
    def test_pcd_ranking_has_is_premium(self):
        """Test that PCD ranking also has is_premium field"""
        response = requests.get(f"{BASE_URL}/api/ranking/categoria/pcd-m/M?ano=2026&page=1&limit=20")
        assert response.status_code == 200
        
        data = response.json()
        if len(data.get("ranking", [])) > 0:
            for athlete in data["ranking"]:
                assert "is_premium" in athlete, f"PCD athlete {athlete.get('nome')} missing is_premium"
            print(f"✅ PCD ranking ({len(data['ranking'])} athletes) has is_premium field")
        else:
            pytest.skip("No PCD athletes in ranking")


class TestAutorizacoesCollection:
    """Tests for autorizacoes collection that determines premium status"""
    
    def test_autorizacoes_endpoint_exists(self):
        """Test that autorizacoes endpoints exist"""
        # This endpoint requires admin auth, so we just check it doesn't 404
        response = requests.get(f"{BASE_URL}/api/autorizacoes/stats")
        # Should return 401 (unauthorized) or 200, not 404
        assert response.status_code != 404, "Autorizacoes endpoint should exist"
        print(f"✅ Autorizacoes endpoint exists (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
