"""
Test suite for Backup System - Iteration 98
Tests: Admin backup endpoints (criar, historico, download, excluir, info)
Security: Verifies super admin only access
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


class TestBackupAuth:
    """Authentication tests for backup endpoints"""
    
    def test_admin_login_success(self):
        """Test admin login returns valid token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not in response"
        assert "user" in data, "User not in response"
        print(f"✓ Admin login successful - user: {data['user']['email']}")
    
    def test_atleta_login_success(self):
        """Test atleta login returns valid token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        assert response.status_code == 200, f"Atleta login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not in response"
        print(f"✓ Atleta login successful - user: {data['user']['email']}")


class TestBackupSecurity:
    """Security tests - verify atleta cannot access backup endpoints"""
    
    @pytest.fixture
    def atleta_token(self):
        """Get atleta token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Atleta login failed")
        return response.json()["token"]
    
    def test_atleta_cannot_access_backup_info(self, atleta_token):
        """Atleta should get 403 when accessing backup info"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/info",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Atleta correctly blocked from backup info (403)")
    
    def test_atleta_cannot_access_backup_historico(self, atleta_token):
        """Atleta should get 403 when accessing backup history"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/historico",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Atleta correctly blocked from backup historico (403)")
    
    def test_atleta_cannot_create_backup(self, atleta_token):
        """Atleta should get 403 when trying to create backup"""
        response = requests.post(
            f"{BASE_URL}/api/admin/backup/criar",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Atleta correctly blocked from creating backup (403)")


class TestBackupEndpoints:
    """Test backup CRUD operations for super admin"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_get_backup_info(self, admin_token):
        """GET /api/admin/backup/info returns system info"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/info",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "total_backups" in data, "Missing total_backups"
        assert "total_collections" in data, "Missing total_collections"
        assert "total_documentos" in data, "Missing total_documentos"
        assert "agendamento" in data, "Missing agendamento"
        assert "tamanho_uploads_mb" in data, "Missing tamanho_uploads_mb"
        
        print(f"✓ Backup info: {data['total_collections']} collections, {data['total_documentos']} docs")
        print(f"  Agendamento: {data['agendamento']}")
    
    def test_get_backup_historico(self, admin_token):
        """GET /api/admin/backup/historico returns list of backups"""
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/historico",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Backup historico: {len(data)} backups found")
        
        # If there are backups, validate structure
        if len(data) > 0:
            backup = data[0]
            assert "id" in backup, "Missing id"
            assert "nome_arquivo" in backup, "Missing nome_arquivo"
            assert "data_criacao" in backup, "Missing data_criacao"
            assert "arquivo_disponivel" in backup, "Missing arquivo_disponivel"
            assert "tamanho_mb" in backup, "Missing tamanho_mb"
            print(f"  Latest backup: {backup['nome_arquivo']} ({backup['tamanho_mb']} MB)")
    
    def test_create_backup_manual(self, admin_token):
        """POST /api/admin/backup/criar creates a new backup"""
        response = requests.post(
            f"{BASE_URL}/api/admin/backup/criar",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=300  # Backup can take time
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert data.get("sucesso") == True, "sucesso should be True"
        assert "backup" in data, "Missing backup object"
        
        backup = data["backup"]
        assert "id" in backup, "Missing backup id"
        assert "nome_arquivo" in backup, "Missing nome_arquivo"
        assert "tamanho_mb" in backup, "Missing tamanho_mb"
        assert "total_documentos" in backup, "Missing total_documentos"
        assert "total_collections" in backup, "Missing total_collections"
        
        print(f"✓ Backup created: {backup['nome_arquivo']}")
        print(f"  Size: {backup['tamanho_mb']} MB, {backup['total_collections']} collections, {backup['total_documentos']} docs")
        
        # Store backup id for later tests
        return backup["id"]
    
    def test_download_backup(self, admin_token):
        """GET /api/admin/backup/download/{id} returns zip file"""
        # First get the list of backups
        hist_response = requests.get(
            f"{BASE_URL}/api/admin/backup/historico",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert hist_response.status_code == 200
        backups = hist_response.json()
        
        if len(backups) == 0:
            pytest.skip("No backups available to download")
        
        # Find a backup with arquivo_disponivel=True
        available_backup = None
        for b in backups:
            if b.get("arquivo_disponivel"):
                available_backup = b
                break
        
        if not available_backup:
            pytest.skip("No available backup files to download")
        
        backup_id = available_backup["id"]
        
        # Test download with token in query param (as used by frontend)
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/download/{backup_id}?token={admin_token}",
            stream=True
        )
        assert response.status_code == 200, f"Download failed: {response.status_code}"
        
        # Check Content-Disposition header
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, "Missing attachment in Content-Disposition"
        assert ".zip" in content_disp, "Missing .zip in Content-Disposition"
        
        # Check Content-Type
        content_type = response.headers.get("Content-Type", "")
        assert "application/zip" in content_type or "application/octet-stream" in content_type
        
        print(f"✓ Backup download works: {content_disp}")
    
    def test_delete_backup(self, admin_token):
        """DELETE /api/admin/backup/{id} removes backup"""
        # First create a backup to delete
        create_response = requests.post(
            f"{BASE_URL}/api/admin/backup/criar",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=300
        )
        
        if create_response.status_code != 200:
            pytest.skip("Could not create backup to delete")
        
        backup_id = create_response.json()["backup"]["id"]
        print(f"  Created backup {backup_id} for deletion test")
        
        # Now delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/backup/{backup_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        data = delete_response.json()
        assert data.get("sucesso") == True, "sucesso should be True"
        
        print(f"✓ Backup {backup_id} deleted successfully")
        
        # Verify it's gone from historico
        hist_response = requests.get(
            f"{BASE_URL}/api/admin/backup/historico",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        backups = hist_response.json()
        backup_ids = [b["id"] for b in backups]
        assert backup_id not in backup_ids, "Deleted backup still in historico"
        print("✓ Verified backup removed from historico")


class TestBackupDownloadWithQueryToken:
    """Test download with token in query param (frontend pattern)"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_download_with_query_token(self, admin_token):
        """Test download using token in query param (as frontend does)"""
        # Get existing backup
        hist_response = requests.get(
            f"{BASE_URL}/api/admin/backup/historico",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        backups = hist_response.json()
        
        available = [b for b in backups if b.get("arquivo_disponivel")]
        if not available:
            pytest.skip("No available backups")
        
        backup_id = available[0]["id"]
        
        # Download with token in query param
        response = requests.get(
            f"{BASE_URL}/api/admin/backup/download/{backup_id}?token={admin_token}",
            stream=True
        )
        assert response.status_code == 200, f"Download with query token failed: {response.status_code}"
        print(f"✓ Download with query param token works for backup {backup_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
