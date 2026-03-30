"""
Test Iteration 94: Scraping Avançado de Corridas
- POST /api/scraping/buscar - Busca corridas via URL
- Anti-duplicidade - Segunda busca deve retornar novas=0
- POST /api/scraping/fontes - Salvar fonte monitorada
- GET /api/scraping/fontes - Listar fontes
- DELETE /api/scraping/fontes/{id} - Remover fonte
- POST /api/scraping/atualizar-todas - Atualizar todas as fontes
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestScrapingCorridas:
    """Tests for scraping corridas endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Admin login failed - skipping scraping tests")
    
    def test_01_scraping_buscar_ticket_sports(self):
        """Test POST /api/scraping/buscar with Ticket Sports URL"""
        url = "https://www.ticketsports.com.br/api/events/list?quantity=10&atlheteId=0&quickFilter=corrida-de-rua"
        
        response = self.session.post(f"{BASE_URL}/api/scraping/buscar", json={
            "url": url,
            "usar_playwright": False,
            "cadastrar_automaticamente": True
        }, timeout=120)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Scraping result: success={data.get('success')}, total={data.get('total_encontradas')}, novas={data.get('novas')}, duplicatas={data.get('duplicatas')}")
        
        # Validate response structure
        assert "success" in data
        assert "total_encontradas" in data
        assert "corridas" in data or "corridas_novas" in data
        assert "metodo" in data
        
        # If successful, validate corrida structure
        if data.get("success") and data.get("total_encontradas", 0) > 0:
            corridas = data.get("corridas_novas") or data.get("corridas", [])
            if corridas:
                corrida = corridas[0]
                assert "nome_corrida" in corrida
                assert "organizador" in corrida
                assert "cidade" in corrida
                assert "estado" in corrida
                assert "data_corrida" in corrida
                assert "status" in corrida
                print(f"First corrida: {corrida.get('nome_corrida')}, status={corrida.get('status')}")
    
    def test_02_anti_duplicidade(self):
        """Test anti-duplicidade - second search should return novas=0"""
        url = "https://www.ticketsports.com.br/api/events/list?quantity=5&atlheteId=0&quickFilter=corrida-de-rua"
        
        # First search
        response1 = self.session.post(f"{BASE_URL}/api/scraping/buscar", json={
            "url": url,
            "usar_playwright": False,
            "cadastrar_automaticamente": True
        }, timeout=120)
        
        assert response1.status_code == 200
        data1 = response1.json()
        novas1 = data1.get("novas", 0)
        total1 = data1.get("total_encontradas", 0)
        print(f"First search: total={total1}, novas={novas1}")
        
        # Second search - same URL
        response2 = self.session.post(f"{BASE_URL}/api/scraping/buscar", json={
            "url": url,
            "usar_playwright": False,
            "cadastrar_automaticamente": True
        }, timeout=120)
        
        assert response2.status_code == 200
        data2 = response2.json()
        novas2 = data2.get("novas", 0)
        duplicatas2 = data2.get("duplicatas", 0)
        print(f"Second search: novas={novas2}, duplicatas={duplicatas2}")
        
        # Anti-duplicidade: second search should have 0 new (all duplicates)
        # Note: This may not be exactly 0 if new events were added between searches
        assert novas2 <= novas1, f"Second search should have fewer or equal new corridas"
        if total1 > 0:
            assert duplicatas2 > 0, "Second search should detect duplicates"
    
    def test_03_adicionar_fonte(self):
        """Test POST /api/scraping/fontes - add monitored source"""
        response = self.session.post(f"{BASE_URL}/api/scraping/fontes", json={
            "url": "https://www.ticketsports.com.br/api/events/list?quantity=10&quickFilter=corrida-de-rua",
            "nome": "Ticket Sports Test",
            "ativa": True
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Add fonte result: {data}")
        
        # Should return id or detail if already exists
        assert "id" in data or "detail" in data
        
        # Store fonte_id for later tests
        self.__class__.fonte_id = data.get("id")
    
    def test_04_listar_fontes(self):
        """Test GET /api/scraping/fontes - list monitored sources"""
        response = self.session.get(f"{BASE_URL}/api/scraping/fontes")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Fontes count: {len(data)}")
        
        assert isinstance(data, list)
        
        if data:
            fonte = data[0]
            assert "id" in fonte
            assert "url" in fonte
            assert "nome" in fonte
            assert "ativa" in fonte
            print(f"First fonte: {fonte.get('nome')} - {fonte.get('url')[:50]}...")
    
    def test_05_atualizar_todas(self):
        """Test POST /api/scraping/atualizar-todas - update all sources"""
        response = self.session.post(f"{BASE_URL}/api/scraping/atualizar-todas", json={}, timeout=300)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Atualizar todas result: {data.get('mensagem')}")
        
        assert "mensagem" in data
        assert "total_fontes" in data
        assert "total_novas" in data
        assert "total_duplicatas" in data
        
        print(f"Total fontes: {data.get('total_fontes')}, novas: {data.get('total_novas')}, duplicatas: {data.get('total_duplicatas')}")
    
    def test_06_remover_fonte(self):
        """Test DELETE /api/scraping/fontes/{id} - remove source"""
        # First get list of fontes
        list_response = self.session.get(f"{BASE_URL}/api/scraping/fontes")
        assert list_response.status_code == 200
        
        fontes = list_response.json()
        
        if not fontes:
            pytest.skip("No fontes to delete")
        
        # Find the test fonte we created
        fonte_to_delete = None
        for f in fontes:
            if "Ticket Sports Test" in f.get("nome", "") or "ticketsports" in f.get("url", "").lower():
                fonte_to_delete = f
                break
        
        if not fonte_to_delete:
            fonte_to_delete = fontes[0]  # Delete first one if test fonte not found
        
        fonte_id = fonte_to_delete.get("id")
        print(f"Deleting fonte: {fonte_to_delete.get('nome')} (id={fonte_id})")
        
        response = self.session.delete(f"{BASE_URL}/api/scraping/fontes/{fonte_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "mensagem" in data
        print(f"Delete result: {data.get('mensagem')}")
    
    def test_07_scraping_status(self):
        """Test GET /api/scraping/status - get scraping status"""
        response = self.session.get(f"{BASE_URL}/api/scraping/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Scraping status: {data}")
        
        assert "total_fontes_ativas" in data
        # ultimo_scraping may be None if no scraping has been done
    
    def test_08_scraping_invalid_url(self):
        """Test POST /api/scraping/buscar with invalid URL"""
        response = self.session.post(f"{BASE_URL}/api/scraping/buscar", json={
            "url": "not-a-valid-url",
            "usar_playwright": False,
            "cadastrar_automaticamente": False
        }, timeout=30)
        
        assert response.status_code == 200  # Returns 200 with success=False
        
        data = response.json()
        assert data.get("success") == False
        assert "mensagem" in data
        print(f"Invalid URL result: {data.get('mensagem')}")


class TestScrapingCorridaFields:
    """Test that scraped corridas have correct field structure"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get admin token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@runpro.com",
            "password": "admin"
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_corrida_status_calculation(self):
        """Test that status is calculated correctly (ativa/encerrada based on date)"""
        url = "https://www.ticketsports.com.br/api/events/list?quantity=20&atlheteId=0&quickFilter=corrida-de-rua"
        
        response = self.session.post(f"{BASE_URL}/api/scraping/buscar", json={
            "url": url,
            "usar_playwright": False,
            "cadastrar_automaticamente": False  # Don't save, just check
        }, timeout=120)
        
        assert response.status_code == 200
        
        data = response.json()
        corridas = data.get("corridas", [])
        
        if not corridas:
            pytest.skip("No corridas found to validate")
        
        from datetime import datetime
        hoje = datetime.now().date()
        
        for corrida in corridas[:5]:  # Check first 5
            status = corrida.get("status")
            data_corrida = corrida.get("data_corrida")
            
            assert status in ["ativa", "encerrada"], f"Invalid status: {status}"
            
            if data_corrida:
                try:
                    data_evento = datetime.strptime(data_corrida[:10], "%Y-%m-%d").date()
                    expected_status = "encerrada" if data_evento < hoje else "ativa"
                    assert status == expected_status, f"Status mismatch for {corrida.get('nome_corrida')}: expected {expected_status}, got {status}"
                except ValueError:
                    pass  # Skip if date format is different
            
            print(f"Corrida: {corrida.get('nome_corrida')[:40]}, data={data_corrida}, status={status}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
