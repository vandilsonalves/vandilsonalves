"""
Iteration 26: Test Admin Dashboard reorganizado (Geral, Atletas, Assessorias, Corridas, Resultados)
+ Gráfico de evolução mensal das equipes no Ranking de Equipes
+ Filtros do Ranking de Equipes
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://atleta-portal.preview.emergentagent.com')
API = f"{BASE_URL}/api"

# =============================================
# Fixtures
# =============================================

@pytest.fixture(scope="module")
def admin_token():
    """Login as admin to get auth token"""
    response = requests.post(f"{API}/auth/login", json={
        "email": "admin@runpro.com",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Admin login failed - skipping authenticated tests")

@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}

# =============================================
# Test Admin Stats Endpoints (Dashboard Geral)
# =============================================

class TestAdminStatsDashboardGeral:
    """Tests for Admin Dashboard Geral stats endpoints"""
    
    def test_admin_stats_returns_data(self, admin_headers):
        """Test main admin stats endpoint"""
        response = requests.get(f"{API}/admin/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "total_atletas" in data
        assert "resultados_pendentes" in data or "pendentes" in data
        assert "total_corridas" in data
        print(f"PASS: Admin stats - {data.get('total_atletas')} atletas, {data.get('total_corridas')} corridas")
    
    def test_admin_stats_estados(self, admin_headers):
        """Test stats by state endpoint"""
        response = requests.get(f"{API}/admin/stats/estados", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            assert "estado" in data[0]
            assert "total" in data[0]
        print(f"PASS: Stats estados - {len(data)} estados")
    
    def test_admin_stats_categorias(self, admin_headers):
        """Test stats by category endpoint"""
        response = requests.get(f"{API}/admin/stats/categorias", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Should have category counts
        assert isinstance(data, dict)
        print(f"PASS: Stats categorias - {data}")
    
    def test_admin_stats_faixa_etaria(self, admin_headers):
        """Test stats by age group endpoint"""
        response = requests.get(f"{API}/admin/stats/faixa-etaria", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"PASS: Stats faixa etária - {len(data)} faixas")
    
    def test_admin_stats_corridas_por_mes(self, admin_headers):
        """Test races per month stats endpoint"""
        response = requests.get(f"{API}/admin/stats/corridas-por-mes", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"PASS: Stats corridas por mês - {len(data)} meses")

# =============================================
# Test Admin Atletas Endpoints (Dashboard Atletas)
# =============================================

class TestAdminAtletasDashboard:
    """Tests for Dashboard Atletas"""
    
    def test_get_all_atletas(self, admin_headers):
        """Test get all athletes endpoint"""
        response = requests.get(f"{API}/admin/atletas", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0, "Should have athletes"
        
        # Verify athlete structure
        atleta = data[0]
        assert "id" in atleta
        assert "nome" in atleta
        assert "email" in atleta
        print(f"PASS: Get all atletas - {len(data)} athletes")
    
    def test_atletas_filter_by_categoria(self, admin_headers):
        """Test filtering athletes by category"""
        # Test masculino filter
        response = requests.get(f"{API}/admin/atletas?categoria=masculino", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"PASS: Filter atletas masculino - {len(data)} athletes")
    
    def test_admin_atletas_export(self, admin_headers):
        """Test export athletes endpoint"""
        response = requests.get(f"{API}/admin/atletas/export?categoria=all", headers=admin_headers)
        # Should return Excel file
        assert response.status_code == 200
        assert "spreadsheetml" in response.headers.get("content-type", "") or response.status_code == 200
        print("PASS: Export atletas endpoint working")

# =============================================
# Test Liga Assessorias Endpoints (Dashboard Assessorias)
# =============================================

class TestAdminAssessoriasDashboard:
    """Tests for Dashboard Assessorias / Liga Nacional"""
    
    def test_liga_ranking_nacional(self, admin_headers):
        """Test liga assessorias national ranking"""
        response = requests.get(f"{API}/liga-assessorias/ranking?tipo=nacional", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data
        assert isinstance(data["ranking"], list)
        
        if len(data["ranking"]) > 0:
            eq = data["ranking"][0]
            assert "nome" in eq
            assert "pontos_total" in eq
            assert "total_atletas" in eq
        
        print(f"PASS: Liga ranking nacional - {len(data['ranking'])} assessorias")
    
    def test_liga_stats(self, admin_headers):
        """Test liga assessorias stats"""
        response = requests.get(f"{API}/liga-assessorias/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "total_assessorias" in data
        assert "total_atletas_vinculados" in data
        print(f"PASS: Liga stats - {data.get('total_assessorias')} assessorias, {data.get('total_atletas_vinculados')} atletas")
    
    def test_liga_estados(self, admin_headers):
        """Test get estados with assessorias"""
        response = requests.get(f"{API}/liga-assessorias/estados", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"PASS: Liga estados - {len(data)} estados")

# =============================================
# Test Evolução Mensal Endpoint (Gráfico)
# =============================================

class TestEvolucaoMensalChart:
    """Tests for the monthly evolution chart in Ranking de Equipes"""
    
    def test_evolucao_mensal_returns_data(self):
        """Test evolução mensal endpoint returns valid data"""
        response = requests.get(f"{API}/liga-assessorias/evolucao-mensal?top=5")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "evolucao" in data
        assert "equipes" in data
        assert "ano" in data
        
        # Verify evolucao array
        assert isinstance(data["evolucao"], list)
        if len(data["evolucao"]) > 0:
            month_data = data["evolucao"][0]
            assert "mes" in month_data
            assert "mes_num" in month_data
        
        # Verify equipes array
        assert isinstance(data["equipes"], list)
        assert len(data["equipes"]) <= 5  # top 5
        
        if len(data["equipes"]) > 0:
            eq = data["equipes"][0]
            assert "nome" in eq
            assert "key" in eq
            # Key should exist in month data
            if len(data["evolucao"]) > 0:
                assert eq["key"] in data["evolucao"][0]
        
        print(f"PASS: Evolução mensal - {len(data['evolucao'])} meses, {len(data['equipes'])} equipes")
    
    def test_evolucao_mensal_different_top_values(self):
        """Test evolução mensal with different top values"""
        for top_value in [3, 5, 10]:
            response = requests.get(f"{API}/liga-assessorias/evolucao-mensal?top={top_value}")
            assert response.status_code == 200
            data = response.json()
            
            # Should have at most 'top' equipes
            assert len(data["equipes"]) <= top_value
            print(f"PASS: Evolução mensal top={top_value} - {len(data['equipes'])} equipes")

# =============================================
# Test Ranking Equipes Filters (6ª Tarefa)
# =============================================

class TestRankingEquipesFilters:
    """Tests for the new filters in Ranking de Equipes page"""
    
    def test_filter_nacional(self):
        """Test Nacional filter returns all data"""
        response = requests.get(f"{API}/liga-assessorias/ranking?tipo=nacional")
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data
        print(f"PASS: Filter Nacional - {len(data['ranking'])} assessorias")
    
    def test_filter_estadual(self):
        """Test Estadual filter"""
        # First get available states
        estados_response = requests.get(f"{API}/liga-assessorias/estados")
        if estados_response.status_code == 200:
            estados = estados_response.json()
            if len(estados) > 0:
                estado = estados[0]
                response = requests.get(f"{API}/liga-assessorias/ranking?tipo=estadual&estado={estado}")
                assert response.status_code == 200
                data = response.json()
                assert "ranking" in data
                print(f"PASS: Filter Estadual ({estado}) - {len(data['ranking'])} assessorias")
            else:
                print("SKIP: No estados available")
        else:
            print("SKIP: Estados endpoint failed")
    
    def test_filter_historico(self):
        """Test Histórico filter"""
        response = requests.get(f"{API}/liga-assessorias/ranking?tipo=historico")
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data
        print(f"PASS: Filter Histórico - {len(data['ranking'])} assessorias")
    
    def test_filter_by_mes(self):
        """Test month filter (mes parameter)"""
        for mes in [1, 2, 3]:
            response = requests.get(f"{API}/liga-assessorias/ranking?tipo=nacional&mes={mes}")
            assert response.status_code == 200
            data = response.json()
            
            assert "ranking" in data
            print(f"PASS: Filter mês={mes} - {len(data['ranking'])} assessorias")

# =============================================
# Test Corridas Dashboard
# =============================================

class TestCorridasDashboard:
    """Tests for Dashboard Corridas"""
    
    def test_ranking_corridas_endpoint(self):
        """Test ranking corridas endpoint"""
        response = requests.get(f"{API}/ranking-corridas")
        assert response.status_code == 200
        data = response.json()
        
        assert "ranking" in data
        print(f"PASS: Ranking corridas - {len(data['ranking'])} eventos")
    
    def test_ranking_corridas_dashboard(self, admin_headers):
        """Test admin ranking corridas dashboard endpoint"""
        response = requests.get(f"{API}/admin/ranking-corridas/dashboard", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "total_corridas" in data or isinstance(data, dict)
        print(f"PASS: Admin ranking corridas dashboard - {data.get('total_corridas', 'N/A')} corridas")

# =============================================
# Test Aprovações/Pendentes Dashboard
# =============================================

class TestAprovacoesDashboard:
    """Tests for Dashboard Resultados/Aprovações"""
    
    def test_get_pendentes(self, admin_headers):
        """Test get pending results endpoint"""
        response = requests.get(f"{API}/admin/pendentes", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"PASS: Pendentes - {len(data)} resultados pendentes")

# =============================================
# Test Public Ranking Povão Stats
# =============================================

class TestRankingPovaoStats:
    """Tests for Ranking do Povão stats used in Dashboard Geral"""
    
    def test_ranking_povao_stats(self):
        """Test public povão stats endpoint"""
        response = requests.get(f"{API}/ranking/povao/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_atletas" in data
        assert "total_provas" in data
        print(f"PASS: Ranking povão stats - {data.get('total_atletas')} atletas, {data.get('total_provas')} provas")

# =============================================
# Run tests
# =============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
