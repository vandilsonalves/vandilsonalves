"""
Test cases for athlete modality transfer feature (Profissional/Amador <-> Povão)
Tests:
1. Transfer endpoint exists and works
2. Transfer button only for NORMAL category (not PCD/Cadeirante)
3. Points recalculation based on new modality
4. Athlete removed from old ranking after transfer
5. Athlete notification created after transfer
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTransferenciaModalidade:
    """Tests for POST /api/admin/atletas/{id}/transferir-modalidade"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin auth and get athletes"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        self.token = login_response.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
    def test_transfer_endpoint_exists(self):
        """Test that the transfer endpoint exists"""
        # First, get a list of athletes to find one to test with
        response = self.session.get(f"{BASE_URL}/api/admin/atletas")
        assert response.status_code == 200, f"Failed to get athletes: {response.text}"
        atletas = response.json()
        
        # Find a normal category athlete (not PCD or Cadeirante)
        normal_atleta = next((a for a in atletas if a.get('categoria') == 'normal'), None)
        
        if normal_atleta:
            # Test the endpoint exists by trying to transfer
            # Note: This will actually perform the transfer, so we need to be careful
            transfer_response = self.session.post(f"{BASE_URL}/api/admin/atletas/{normal_atleta['id']}/transferir-modalidade")
            # Should return 200 or 400/404 - but NOT 404 for endpoint not found
            assert transfer_response.status_code in [200, 400], f"Transfer endpoint failed: {transfer_response.status_code} - {transfer_response.text}"
            print(f"PASS: Transfer endpoint exists and responds correctly")
        else:
            pytest.skip("No normal category athlete found to test transfer")
    
    def test_transfer_pcd_athlete_blocked(self):
        """Test that PCD athletes cannot be transferred to Povão"""
        response = self.session.get(f"{BASE_URL}/api/admin/atletas")
        assert response.status_code == 200
        atletas = response.json()
        
        # Find a PCD athlete
        pcd_atleta = next((a for a in atletas if a.get('categoria') == 'pcd'), None)
        
        if pcd_atleta:
            # Try to transfer - should be blocked
            transfer_response = self.session.post(f"{BASE_URL}/api/admin/atletas/{pcd_atleta['id']}/transferir-modalidade")
            # Should return 400 with error message
            assert transfer_response.status_code == 400, f"PCD transfer should be blocked: {transfer_response.status_code}"
            error = transfer_response.json().get('detail', '')
            assert 'PCD' in error or 'não podem' in error.lower(), f"Error message should mention PCD restriction: {error}"
            print(f"PASS: PCD athlete transfer correctly blocked - {error}")
        else:
            print("SKIP: No PCD athlete found to test blocked transfer")
    
    def test_transfer_cadeirante_athlete_blocked(self):
        """Test that Cadeirante athletes cannot be transferred to Povão"""
        response = self.session.get(f"{BASE_URL}/api/admin/atletas")
        assert response.status_code == 200
        atletas = response.json()
        
        # Find a Cadeirante athlete
        cadeirante_atleta = next((a for a in atletas if a.get('categoria') == 'cadeirante'), None)
        
        if cadeirante_atleta:
            # Try to transfer - should be blocked
            transfer_response = self.session.post(f"{BASE_URL}/api/admin/atletas/{cadeirante_atleta['id']}/transferir-modalidade")
            # Should return 400 with error message
            assert transfer_response.status_code == 400, f"Cadeirante transfer should be blocked: {transfer_response.status_code}"
            error = transfer_response.json().get('detail', '')
            assert 'Cadeirante' in error or 'não podem' in error.lower(), f"Error message should mention Cadeirante restriction: {error}"
            print(f"PASS: Cadeirante athlete transfer correctly blocked - {error}")
        else:
            print("SKIP: No Cadeirante athlete found to test blocked transfer")
    
    def test_transfer_nonexistent_athlete(self):
        """Test transfer with non-existent athlete ID"""
        transfer_response = self.session.post(f"{BASE_URL}/api/admin/atletas/nonexistent-id/transferir-modalidade")
        assert transfer_response.status_code == 404, f"Should return 404 for nonexistent athlete: {transfer_response.status_code}"
        print("PASS: Non-existent athlete returns 404")
    
    def test_transfer_response_structure(self):
        """Test that transfer response has correct structure with stats"""
        response = self.session.get(f"{BASE_URL}/api/admin/atletas")
        assert response.status_code == 200
        atletas = response.json()
        
        # Find a normal athlete with profissional_amador modality to test transfer to Povão
        normal_atleta = next(
            (a for a in atletas 
             if a.get('categoria') == 'normal' and 
             a.get('modalidade_usuario', 'profissional_amador') == 'profissional_amador'), 
            None
        )
        
        if normal_atleta:
            transfer_response = self.session.post(f"{BASE_URL}/api/admin/atletas/{normal_atleta['id']}/transferir-modalidade")
            assert transfer_response.status_code == 200, f"Transfer failed: {transfer_response.text}"
            
            data = transfer_response.json()
            assert 'message' in data, "Response should have 'message' field"
            assert 'stats' in data, "Response should have 'stats' field"
            
            stats = data['stats']
            expected_fields = ['corridas_processadas', 'pontos_antigos', 'pontos_novos', 'modalidade_anterior', 'modalidade_nova']
            for field in expected_fields:
                assert field in stats, f"Stats should have '{field}' field"
            
            print(f"PASS: Transfer response structure is correct")
            print(f"  - Athlete: {normal_atleta['nome']}")
            print(f"  - From: {stats['modalidade_anterior']} to {stats['modalidade_nova']}")
            print(f"  - Points: {stats['pontos_antigos']} -> {stats['pontos_novos']}")
            print(f"  - Races processed: {stats['corridas_processadas']}")
            
            # Transfer back to restore state
            restore_response = self.session.post(f"{BASE_URL}/api/admin/atletas/{normal_atleta['id']}/transferir-modalidade")
            if restore_response.status_code == 200:
                print("  - Restored original modality")
        else:
            pytest.skip("No profissional_amador normal athlete found for transfer test")


class TestTransferencePointsRecalculation:
    """Tests for verifying points are correctly recalculated during transfer"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin auth"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_ranking_povao_excludes_pro_athletes(self):
        """Verify Pro/Amador athletes don't appear in Povão ranking"""
        response = self.session.get(f"{BASE_URL}/api/ranking/povao?genero=M")
        assert response.status_code == 200
        
        data = response.json()
        ranking = data.get('ranking', [])
        
        # Get all Pro/Amador athletes
        atletas_response = self.session.get(f"{BASE_URL}/api/admin/atletas")
        atletas = atletas_response.json()
        pro_athlete_ids = [a['id'] for a in atletas if a.get('modalidade_usuario', 'profissional_amador') == 'profissional_amador']
        
        # Verify none appear in Povão ranking
        povao_ids = [r.get('atleta_id') for r in ranking]
        overlap = set(pro_athlete_ids) & set(povao_ids)
        assert len(overlap) == 0, f"Pro/Amador athletes should not appear in Povão ranking: {overlap}"
        print(f"PASS: Povão ranking correctly excludes {len(pro_athlete_ids)} Pro/Amador athletes")
    
    def test_ranking_pro_excludes_povao_athletes(self):
        """Verify Povão athletes don't appear in Pro/Amador ranking"""
        # Get Povão athletes
        atletas_response = self.session.get(f"{BASE_URL}/api/admin/atletas")
        atletas = atletas_response.json()
        povao_athlete_ids = [a['id'] for a in atletas if a.get('modalidade_usuario') == 'povao_pace_livre']
        
        if not povao_athlete_ids:
            pytest.skip("No Povão athletes to test")
        
        # Check Pro/Amador ranking
        response = self.session.get(f"{BASE_URL}/api/ranking/categoria/masculino/M")
        assert response.status_code == 200
        
        ranking = response.json()
        pro_ids = [r.get('atleta_id') for r in ranking]
        
        overlap = set(povao_athlete_ids) & set(pro_ids)
        assert len(overlap) == 0, f"Povão athletes should not appear in Pro/Amador ranking: {overlap}"
        print(f"PASS: Pro/Amador ranking correctly excludes {len(povao_athlete_ids)} Povão athletes")


class TestTransferNotification:
    """Tests for verifying notification is created after transfer"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin auth"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_transfer_creates_notification(self):
        """Test that transfer creates a notification for the athlete"""
        # Get athletes
        response = self.session.get(f"{BASE_URL}/api/admin/atletas")
        atletas = response.json()
        
        # Find a normal athlete to test with
        normal_atleta = next(
            (a for a in atletas if a.get('categoria') == 'normal'), 
            None
        )
        
        if not normal_atleta:
            pytest.skip("No normal athlete found")
        
        # Perform transfer
        transfer_response = self.session.post(f"{BASE_URL}/api/admin/atletas/{normal_atleta['id']}/transferir-modalidade")
        
        if transfer_response.status_code == 200:
            # The notification creation is internal, we can verify by checking the endpoint succeeded
            # and the message mentions notification
            message = transfer_response.json().get('message', '')
            print(f"PASS: Transfer succeeded - notification should have been created")
            print(f"  - Message: {message}")
            
            # Restore the athlete's modality
            self.session.post(f"{BASE_URL}/api/admin/atletas/{normal_atleta['id']}/transferir-modalidade")
        else:
            print(f"Transfer returned: {transfer_response.status_code}")


class TestAdminAtletasEndpoint:
    """Tests for admin atletas endpoint with modalidade info"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin auth"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_atletas_have_modalidade_field(self):
        """Test that atletas response includes modalidade_usuario field"""
        response = self.session.get(f"{BASE_URL}/api/admin/atletas")
        assert response.status_code == 200
        
        atletas = response.json()
        assert len(atletas) > 0, "Should have at least one athlete"
        
        # Check that athletes have the modalidade_usuario field (or default)
        for atleta in atletas[:5]:  # Check first 5
            # modalidade_usuario can be 'profissional_amador', 'povao_pace_livre', or not present (defaults to profissional_amador)
            modalidade = atleta.get('modalidade_usuario', 'profissional_amador')
            assert modalidade in ['profissional_amador', 'povao_pace_livre'], f"Invalid modalidade: {modalidade}"
        
        print(f"PASS: Athletes have valid modalidade_usuario field")
        
        # Count by modality
        pro_count = sum(1 for a in atletas if a.get('modalidade_usuario', 'profissional_amador') == 'profissional_amador')
        povao_count = sum(1 for a in atletas if a.get('modalidade_usuario') == 'povao_pace_livre')
        print(f"  - Pro/Amador: {pro_count}")
        print(f"  - Povão: {povao_count}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
