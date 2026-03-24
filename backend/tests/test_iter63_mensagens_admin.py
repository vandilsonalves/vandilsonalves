"""
Test Iteration 63: Mensagens Admin Feature
Tests for the new admin messaging system that allows sending messages to athletes
with various filters (todos, modalidade, genero, especial)
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"


class TestMensagensAdmin:
    """Tests for Admin Messaging System"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_admin_token(self):
        """Login as admin and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    
    def get_atleta_token(self):
        """Login as atleta and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ATLETA_EMAIL,
            "password": ATLETA_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Atleta login failed: {response.status_code} - {response.text}")
    
    # ============ CONTAGEM DESTINATARIOS TESTS ============
    
    def test_contagem_todos(self):
        """Test recipient count with filter 'todos'"""
        token = self.get_admin_token()
        
        params = {
            "filtro_tipo": "todos",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": "[]"
        }
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios",
            params=params,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total" in data, "Response should contain 'total' field"
        assert isinstance(data["total"], int), "Total should be an integer"
        assert data["total"] > 0, "Total should be greater than 0 for 'todos' filter"
        print(f"Contagem 'todos': {data['total']} atletas")
    
    def test_contagem_modalidade_profissional(self):
        """Test recipient count with modalidade profissional_amador filter"""
        token = self.get_admin_token()
        
        params = {
            "filtro_tipo": "modalidade",
            "filtro_modalidades": json.dumps(["profissional_amador"]),
            "filtro_generos": "[]",
            "filtro_especial": "[]"
        }
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios",
            params=params,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total" in data
        print(f"Contagem 'profissional_amador': {data['total']} atletas")
    
    def test_contagem_modalidade_galera(self):
        """Test recipient count with modalidade povao_pace_livre (Galera) filter"""
        token = self.get_admin_token()
        
        params = {
            "filtro_tipo": "modalidade",
            "filtro_modalidades": json.dumps(["povao_pace_livre"]),
            "filtro_generos": "[]",
            "filtro_especial": "[]"
        }
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios",
            params=params,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total" in data
        print(f"Contagem 'galera': {data['total']} atletas")
    
    def test_contagem_especial_donos_assessoria(self):
        """Test recipient count with especial donos_assessoria filter"""
        token = self.get_admin_token()
        
        params = {
            "filtro_tipo": "especial",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": json.dumps(["donos_assessoria"])
        }
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios",
            params=params,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total" in data
        print(f"Contagem 'donos_assessoria': {data['total']} atletas")
    
    def test_contagem_especial_individual(self):
        """Test recipient count with especial individual_sem_assessoria filter"""
        token = self.get_admin_token()
        
        params = {
            "filtro_tipo": "especial",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": json.dumps(["individual_sem_assessoria"])
        }
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios",
            params=params,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total" in data
        print(f"Contagem 'individual_sem_assessoria': {data['total']} atletas")
    
    def test_contagem_genero_masculino(self):
        """Test recipient count with genero M filter"""
        token = self.get_admin_token()
        
        params = {
            "filtro_tipo": "genero",
            "filtro_modalidades": "[]",
            "filtro_generos": json.dumps(["M"]),
            "filtro_especial": "[]"
        }
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios",
            params=params,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total" in data
        print(f"Contagem 'genero M': {data['total']} atletas")
    
    # ============ ENVIAR MENSAGEM TESTS ============
    
    def test_enviar_mensagem_todos(self):
        """Test sending message to all athletes"""
        token = self.get_admin_token()
        
        # Use multipart/form-data format (remove Content-Type header for requests to auto-set)
        headers = {"Authorization": f"Bearer {token}"}
        
        form_data = {
            "titulo": "TEST_Mensagem de Teste",
            "mensagem": "Esta é uma mensagem de teste do sistema de mensagens admin.",
            "link": "https://example.com/test",
            "anexos": "[]",
            "filtro_tipo": "todos",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": "[]"
        }
        
        # Create a new session without Content-Type header for form data
        response = requests.post(
            f"{BASE_URL}/api/admin/mensagens/enviar",
            data=form_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data, "Response should contain 'message' field"
        assert "total_enviados" in data, "Response should contain 'total_enviados' field"
        assert "mensagem_id" in data, "Response should contain 'mensagem_id' field"
        assert data["total_enviados"] > 0, "Should have sent to at least 1 athlete"
        print(f"Mensagem enviada para {data['total_enviados']} atletas. ID: {data['mensagem_id']}")
    
    def test_enviar_mensagem_sem_conteudo_falha(self):
        """Test that sending message without content fails"""
        token = self.get_admin_token()
        
        form_data = {
            "titulo": "TEST_Titulo sem mensagem",
            "mensagem": "",
            "link": "",
            "anexos": "[]",
            "filtro_tipo": "todos",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": "[]"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/admin/mensagens/enviar",
            data=form_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400, f"Expected 400 for empty message, got {response.status_code}"
        print("Correctly rejected empty message")
    
    def test_enviar_mensagem_apenas_link(self):
        """Test sending message with only link (no text)"""
        token = self.get_admin_token()
        
        headers = {"Authorization": f"Bearer {token}"}
        
        form_data = {
            "titulo": "TEST_Apenas Link",
            "mensagem": "",
            "link": "https://example.com/important-link",
            "anexos": "[]",
            "filtro_tipo": "especial",
            "filtro_modalidades": "[]",
            "filtro_generos": "[]",
            "filtro_especial": json.dumps(["donos_assessoria"])
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/mensagens/enviar",
            data=form_data,
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["total_enviados"] > 0
        print(f"Mensagem com apenas link enviada para {data['total_enviados']} donos de assessoria")
    
    # ============ HISTORICO TESTS ============
    
    def test_historico_mensagens(self):
        """Test getting message history"""
        token = self.get_admin_token()
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/mensagens/historico",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "mensagens" in data, "Response should contain 'mensagens' field"
        assert isinstance(data["mensagens"], list), "mensagens should be a list"
        
        if len(data["mensagens"]) > 0:
            msg = data["mensagens"][0]
            assert "id" in msg, "Message should have 'id'"
            assert "titulo" in msg, "Message should have 'titulo'"
            assert "mensagem" in msg, "Message should have 'mensagem'"
            assert "total_enviados" in msg, "Message should have 'total_enviados'"
            assert "data_envio" in msg, "Message should have 'data_envio'"
            print(f"Historico contém {len(data['mensagens'])} mensagens")
        else:
            print("Historico vazio (nenhuma mensagem enviada ainda)")
    
    # ============ NOTIFICACAO ATLETA TESTS ============
    
    def test_notificacao_atleta_recebe_mensagem_admin(self):
        """Test that athlete receives admin message as notification"""
        atleta_token = self.get_atleta_token()
        
        response = self.session.get(
            f"{BASE_URL}/api/notificacoes",
            headers={"Authorization": f"Bearer {atleta_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Response is an object with 'notificacoes' key
        notificacoes = data.get("notificacoes", [])
        
        # Check if there are any mensagem_admin notifications
        mensagens_admin = [n for n in notificacoes if n.get("tipo") == "mensagem_admin"]
        print(f"Atleta tem {len(mensagens_admin)} notificações do tipo 'mensagem_admin'")
        
        if len(mensagens_admin) > 0:
            notif = mensagens_admin[0]
            assert "titulo" in notif, "Notification should have 'titulo'"
            assert "mensagem" in notif, "Notification should have 'mensagem'"
            print(f"Última notificação admin: {notif.get('titulo')}")
    
    # ============ UPLOAD TESTS ============
    
    def test_upload_arquivo_sem_autenticacao_falha(self):
        """Test that upload without auth fails"""
        response = self.session.post(
            f"{BASE_URL}/api/admin/mensagens/upload",
            files={"arquivo": ("test.txt", b"test content", "text/plain")}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Upload sem autenticação corretamente rejeitado")
    
    # ============ PERMISSION TESTS ============
    
    def test_contagem_sem_autenticacao_falha(self):
        """Test that contagem without auth fails"""
        response = self.session.get(
            f"{BASE_URL}/api/admin/mensagens/contagem-destinatarios",
            params={"filtro_tipo": "todos"}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Contagem sem autenticação corretamente rejeitada")
    
    def test_enviar_sem_autenticacao_falha(self):
        """Test that sending without auth fails"""
        response = self.session.post(
            f"{BASE_URL}/api/admin/mensagens/enviar",
            data={"mensagem": "test", "filtro_tipo": "todos"}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Envio sem autenticação corretamente rejeitado")
    
    def test_historico_sem_autenticacao_falha(self):
        """Test that historico without auth fails"""
        response = self.session.get(
            f"{BASE_URL}/api/admin/mensagens/historico"
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("Historico sem autenticação corretamente rejeitado")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
