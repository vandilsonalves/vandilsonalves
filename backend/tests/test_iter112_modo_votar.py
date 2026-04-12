"""
Iteration 112: Modo 'Votar' Feature Tests
Tests for the new voting mode where admin creates categories with options (A, B, C...)
and athletes see clickable buttons instead of text fields.

Features tested:
1. Backend: POST /api/premiacao/admin/premiacoes/{id}/categorias accepts 'opcoes' array
2. Backend: GET /api/premiacao/p/{id}/categorias returns opcoes array for each category
3. Backend: POST /api/premiacao/p/{id}/votar accepts a vote where nome_indicado is one of the opcoes
4. Backend: Modo 'indicar' still requires link_indicado
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"

# Known premiacao IDs from context
PREMIACAO_VOTAR_ID = "38191d93"  # Votação Cor da Camisa 2026, modo=votar, OPEN
PREMIACAO_INDICAR_ID = "310d78e2"  # PRÊMIO NACIONAL, modo=indicar, OPEN
CATEGORIA_COM_OPCOES_ID = "59c06999"  # Cor da Camisa with opcoes


class TestModoVotarBackend:
    """Backend tests for Modo Votar feature"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def atleta_token(self):
        """Get atleta authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Atleta login failed: {response.status_code} - {response.text}")
    
    # ==================== Test 1: Verify premiacao modo=votar exists ====================
    def test_01_premiacao_votar_exists(self):
        """Verify the premiacao with modo=votar exists and is open"""
        response = requests.get(f"{BASE_URL}/api/premiacao/p/{PREMIACAO_VOTAR_ID}")
        assert response.status_code == 200, f"Failed to get premiacao: {response.text}"
        
        data = response.json()
        assert data.get("id") == PREMIACAO_VOTAR_ID
        assert data.get("modo_votacao") == "votar", f"Expected modo_votacao='votar', got '{data.get('modo_votacao')}'"
        assert data.get("votacao_aberta") == True, "Premiacao should be open"
        print(f"✓ Premiacao '{data.get('titulo')}' exists with modo_votacao='votar' and is open")
    
    # ==================== Test 2: GET categorias returns opcoes array ====================
    def test_02_get_categorias_returns_opcoes(self):
        """GET /api/premiacao/p/{id}/categorias returns opcoes array for each category"""
        response = requests.get(f"{BASE_URL}/api/premiacao/p/{PREMIACAO_VOTAR_ID}/categorias")
        assert response.status_code == 200, f"Failed to get categorias: {response.text}"
        
        categorias = response.json()
        assert isinstance(categorias, list), "Response should be a list"
        assert len(categorias) > 0, "Should have at least one category"
        
        # Find category with opcoes
        cat_with_opcoes = None
        for cat in categorias:
            if cat.get("opcoes") and len(cat.get("opcoes", [])) > 0:
                cat_with_opcoes = cat
                break
        
        assert cat_with_opcoes is not None, "Should have at least one category with opcoes"
        assert "opcoes" in cat_with_opcoes, "Category should have 'opcoes' field"
        assert isinstance(cat_with_opcoes["opcoes"], list), "opcoes should be a list"
        assert len(cat_with_opcoes["opcoes"]) >= 2, "Should have at least 2 options"
        
        print(f"✓ Found category '{cat_with_opcoes.get('nome')}' with opcoes: {cat_with_opcoes['opcoes']}")
    
    # ==================== Test 3: Admin can create category with opcoes ====================
    def test_03_admin_create_category_with_opcoes(self, admin_token):
        """POST /api/premiacao/admin/premiacoes/{id}/categorias accepts 'opcoes' array"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        payload = {
            "nome": "TEST_Categoria_Opcoes",
            "descricao": "Test category with voting options",
            "opcoes": ["Opção A", "Opção B", "Opção C", "Opção D"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{PREMIACAO_VOTAR_ID}/categorias",
            json=payload,
            headers=headers
        )
        assert response.status_code == 200, f"Failed to create category: {response.text}"
        
        data = response.json()
        assert data.get("nome") == "TEST_Categoria_Opcoes"
        assert "opcoes" in data, "Response should include opcoes"
        assert data["opcoes"] == ["Opção A", "Opção B", "Opção C", "Opção D"], f"opcoes mismatch: {data['opcoes']}"
        assert "id" in data, "Response should include category id"
        
        # Store for cleanup
        self.__class__.test_category_id = data["id"]
        print(f"✓ Created category with opcoes, id: {data['id']}")
    
    # ==================== Test 4: Verify created category has opcoes ====================
    def test_04_verify_created_category_opcoes(self):
        """Verify the created category appears in GET with opcoes"""
        response = requests.get(f"{BASE_URL}/api/premiacao/p/{PREMIACAO_VOTAR_ID}/categorias")
        assert response.status_code == 200
        
        categorias = response.json()
        test_cat = next((c for c in categorias if c.get("nome") == "TEST_Categoria_Opcoes"), None)
        
        assert test_cat is not None, "Test category should exist"
        assert test_cat.get("opcoes") == ["Opção A", "Opção B", "Opção C", "Opção D"]
        print(f"✓ Test category verified with opcoes: {test_cat['opcoes']}")
    
    # ==================== Test 5: Atleta can vote with one of the opcoes ====================
    def test_05_atleta_vote_with_opcao(self, atleta_token):
        """POST /api/premiacao/p/{id}/votar accepts vote where nome_indicado is one of opcoes"""
        headers = {"Authorization": f"Bearer {atleta_token}"}
        
        # Get the test category id
        cat_id = getattr(self.__class__, 'test_category_id', None)
        if not cat_id:
            pytest.skip("Test category not created")
        
        payload = {
            "premiacao_id": PREMIACAO_VOTAR_ID,
            "categoria_id": cat_id,
            "nome_indicado": "Opção B",  # One of the opcoes
            "link_indicado": ""  # Not required for modo votar
        }
        
        response = requests.post(
            f"{BASE_URL}/api/premiacao/p/{PREMIACAO_VOTAR_ID}/votar",
            json=payload,
            headers=headers
        )
        assert response.status_code == 200, f"Failed to vote: {response.text}"
        
        data = response.json()
        assert "message" in data
        print(f"✓ Atleta voted successfully: {data.get('message')}")
    
    # ==================== Test 6: Verify vote was recorded ====================
    def test_06_verify_vote_recorded(self, atleta_token):
        """Verify the vote was recorded correctly"""
        headers = {"Authorization": f"Bearer {atleta_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/premiacao/p/{PREMIACAO_VOTAR_ID}/meus-votos",
            headers=headers
        )
        assert response.status_code == 200, f"Failed to get votes: {response.text}"
        
        votos = response.json()
        cat_id = getattr(self.__class__, 'test_category_id', None)
        
        test_voto = next((v for v in votos if v.get("categoria_id") == cat_id), None)
        assert test_voto is not None, "Vote should be recorded"
        assert test_voto.get("nome_indicado") == "Opção B"
        print(f"✓ Vote verified: {test_voto.get('nome_indicado')}")
    
    # ==================== Test 7: Modo indicar still requires link ====================
    def test_07_modo_indicar_requires_link(self, atleta_token):
        """POST /api/premiacao/p/{id}/votar for modo=indicar requires link_indicado"""
        headers = {"Authorization": f"Bearer {atleta_token}"}
        
        # First get categories for indicar premiacao
        cats_response = requests.get(f"{BASE_URL}/api/premiacao/p/{PREMIACAO_INDICAR_ID}/categorias")
        if cats_response.status_code != 200 or len(cats_response.json()) == 0:
            pytest.skip("No categories in indicar premiacao")
        
        cat_id = cats_response.json()[0]["id"]
        
        # Try to vote without link
        payload = {
            "premiacao_id": PREMIACAO_INDICAR_ID,
            "categoria_id": cat_id,
            "nome_indicado": "Test Indicado",
            "link_indicado": ""  # Empty link
        }
        
        response = requests.post(
            f"{BASE_URL}/api/premiacao/p/{PREMIACAO_INDICAR_ID}/votar",
            json=payload,
            headers=headers
        )
        
        # Should fail because link is required for modo indicar
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        assert "link" in response.text.lower() or "obrigatório" in response.text.lower(), \
            f"Error should mention link requirement: {response.text}"
        print(f"✓ Modo indicar correctly requires link: {response.json().get('detail')}")
    
    # ==================== Test 8: Admin GET categorias includes opcoes ====================
    def test_08_admin_get_categorias_includes_opcoes(self, admin_token):
        """GET /api/premiacao/admin/premiacoes/{id}/categorias includes opcoes"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{PREMIACAO_VOTAR_ID}/categorias",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        categorias = response.json()
        cat_with_opcoes = next((c for c in categorias if c.get("opcoes") and len(c["opcoes"]) > 0), None)
        
        assert cat_with_opcoes is not None, "Should have category with opcoes"
        assert "total_votos" in cat_with_opcoes, "Admin view should include total_votos"
        print(f"✓ Admin categorias includes opcoes and total_votos")
    
    # ==================== Test 9: Atleta can change vote ====================
    def test_09_atleta_can_change_vote(self, atleta_token):
        """Atleta can change vote to different option"""
        headers = {"Authorization": f"Bearer {atleta_token}"}
        
        cat_id = getattr(self.__class__, 'test_category_id', None)
        if not cat_id:
            pytest.skip("Test category not created")
        
        payload = {
            "premiacao_id": PREMIACAO_VOTAR_ID,
            "categoria_id": cat_id,
            "nome_indicado": "Opção C",  # Different option
            "link_indicado": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/premiacao/p/{PREMIACAO_VOTAR_ID}/votar",
            json=payload,
            headers=headers
        )
        assert response.status_code == 200, f"Failed to change vote: {response.text}"
        
        data = response.json()
        assert data.get("atualizado") == True, "Should indicate vote was updated"
        print(f"✓ Vote changed successfully: {data.get('message')}")
    
    # ==================== Test 10: Cleanup - Delete test category ====================
    def test_10_cleanup_delete_test_category(self, admin_token):
        """Cleanup: Delete the test category"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        cat_id = getattr(self.__class__, 'test_category_id', None)
        if not cat_id:
            pytest.skip("No test category to delete")
        
        response = requests.delete(
            f"{BASE_URL}/api/premiacao/admin/premiacoes/{PREMIACAO_VOTAR_ID}/categorias/{cat_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Failed to delete: {response.text}"
        print(f"✓ Test category deleted")
    
    # ==================== Test 11: Verify existing category with opcoes ====================
    def test_11_verify_existing_categoria_cor_camisa(self):
        """Verify the existing 'Cor da Camisa' category has opcoes"""
        response = requests.get(f"{BASE_URL}/api/premiacao/p/{PREMIACAO_VOTAR_ID}/categorias")
        assert response.status_code == 200
        
        categorias = response.json()
        # Look for category with id 59c06999 or exact name "Cor da Camisa"
        cor_camisa = next((c for c in categorias if c.get("id") == CATEGORIA_COM_OPCOES_ID or c.get("nome") == "Cor da Camisa"), None)
        
        if cor_camisa:
            assert "opcoes" in cor_camisa, f"Cor da Camisa should have opcoes, got: {cor_camisa}"
            expected_opcoes = ['Vermelho', 'Azul', 'Branco', 'Preto', 'Verde']
            assert cor_camisa["opcoes"] == expected_opcoes, f"Expected {expected_opcoes}, got {cor_camisa['opcoes']}"
            print(f"✓ Cor da Camisa category has correct opcoes: {cor_camisa['opcoes']}")
        else:
            # Check if any category has opcoes
            cat_with_opcoes = next((c for c in categorias if c.get("opcoes") and len(c["opcoes"]) > 0), None)
            if cat_with_opcoes:
                print(f"✓ Found category with opcoes: {cat_with_opcoes['nome']} - {cat_with_opcoes['opcoes']}")
            else:
                pytest.fail("No category with opcoes found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
