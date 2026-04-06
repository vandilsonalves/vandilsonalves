"""
Testes unitários para funcionalidades críticas recentes:
1. Senha Mestra Super Admin (login universal + alteração de senha)
2. Submissão e Aprovação de Corridas (fluxo completo)
3. Anti-duplicidade de corridas (mesmo nome/cidade/estado)
4. Exportações Excel (14 endpoints)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://geo-filtered-admin.preview.emergentagent.com')
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@runpro.com"
ADMIN_PASSWORD = "admin"
ATLETA_EMAIL = "teste.dono@teste.com"
ATLETA_PASSWORD = "123456"
MASTER_PASSWORD = "d7ff103ad1250@#$"


def login(email, password):
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"Login falhou para {email}: {r.text}"
    return r.json()["token"]


# ==================== 1. SENHA MESTRA SUPER ADMIN ====================

class TestSenhaMestra:
    """Testa login universal e alteração de senha via senha mestra"""

    def test_login_com_senha_mestra_atleta(self):
        """Deve permitir login em conta de atleta usando senha mestra"""
        r = requests.post(f"{API}/auth/login", json={"email": ATLETA_EMAIL, "password": MASTER_PASSWORD})
        assert r.status_code == 200
        assert "token" in r.json()
        assert r.json()["user"]["email"] == ATLETA_EMAIL

    def test_login_com_senha_mestra_admin(self):
        """Deve permitir login em conta admin usando senha mestra"""
        r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": MASTER_PASSWORD})
        assert r.status_code == 200
        assert "token" in r.json()

    def test_login_com_senha_errada_deve_falhar(self):
        """Deve rejeitar senha incorreta (que não é mestra nem real)"""
        r = requests.post(f"{API}/auth/login", json={"email": ATLETA_EMAIL, "password": "senhaErrada999"})
        assert r.status_code == 401

    def test_alterar_senha_com_mestra_como_atual(self):
        """Deve aceitar senha mestra no campo 'senha_atual' para alterar senha"""
        token = login(ATLETA_EMAIL, ATLETA_PASSWORD)
        nova_senha = f"temp_{uuid.uuid4().hex[:8]}"
        
        # Alterar usando senha mestra
        r = requests.post(f"{API}/atletas/alterar-senha",
            headers={"Authorization": f"Bearer {token}"},
            json={"senha_atual": MASTER_PASSWORD, "nova_senha": nova_senha, "confirmar_senha": nova_senha}
        )
        assert r.status_code == 200
        
        # Verificar que nova senha funciona
        r2 = requests.post(f"{API}/auth/login", json={"email": ATLETA_EMAIL, "password": nova_senha})
        assert r2.status_code == 200
        
        # Restaurar senha original
        token2 = r2.json()["token"]
        requests.post(f"{API}/atletas/alterar-senha",
            headers={"Authorization": f"Bearer {token2}"},
            json={"senha_atual": MASTER_PASSWORD, "nova_senha": ATLETA_PASSWORD, "confirmar_senha": ATLETA_PASSWORD}
        )


# ==================== 2. SUBMISSÃO E APROVAÇÃO DE CORRIDAS ====================

class TestSubmissaoAprovacaoCorridas:
    """Testa o fluxo completo de submissão e aprovação de corridas"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.token_atleta = login(ATLETA_EMAIL, ATLETA_PASSWORD)
        self.token_admin = login(ADMIN_EMAIL, ADMIN_PASSWORD)
        self.headers_atleta = {"Authorization": f"Bearer {self.token_atleta}"}
        self.headers_admin = {"Authorization": f"Bearer {self.token_admin}"}
        self.unique = uuid.uuid4().hex[:6]

    def _criar_corrida(self, nome, cidade="TestCity", estado="SP", status="ativa", token=None):
        form = {
            "nome_corrida": nome,
            "organizador": "Org Teste",
            "cidade": cidade,
            "estado": estado,
            "data_corrida": "2026-08-15",
            "status": status
        }
        headers = {"Authorization": f"Bearer {token or self.token_atleta}"}
        return requests.post(f"{API}/corridas-eventos", data=form, headers=headers)

    def test_atleta_submete_corrida_pendente(self):
        """Corrida submetida por atleta deve ficar pendente"""
        r = self._criar_corrida(f"Corrida Pendente {self.unique}")
        assert r.status_code == 200
        data = r.json()
        assert "aprovação" in data["message"].lower() or "aprovada" in data["message"].lower()

    def test_admin_submete_corrida_aprovada_automaticamente(self):
        """Corrida submetida por admin deve ser aprovada automaticamente"""
        r = self._criar_corrida(f"Corrida Admin {self.unique}", token=self.token_admin)
        assert r.status_code == 200
        assert "sucesso" in r.json()["message"].lower()

    def test_listar_corridas_pendentes(self):
        """Admin deve ver corridas pendentes"""
        nome = f"Corrida ListPend {self.unique}"
        self._criar_corrida(nome, cidade=f"Cidade{self.unique}")
        
        r = requests.get(f"{API}/corridas-eventos/pendentes", headers=self.headers_admin)
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_aprovar_corrida(self):
        """Admin deve conseguir aprovar uma corrida pendente"""
        nome = f"Corrida Aprovar {self.unique}"
        create_r = self._criar_corrida(nome, cidade=f"AprovCidade{self.unique}")
        corrida_id = create_r.json()["id"]
        
        r = requests.post(f"{API}/corridas-eventos/{corrida_id}/aprovar", 
                         headers=self.headers_admin, json={})
        assert r.status_code == 200
        assert "aprovada" in r.json()["message"].lower()

    def test_rejeitar_corrida_com_motivo(self):
        """Admin deve conseguir rejeitar com motivo"""
        nome = f"Corrida Rejeitar {self.unique}"
        create_r = self._criar_corrida(nome, cidade=f"RejCidade{self.unique}")
        corrida_id = create_r.json()["id"]
        
        r = requests.post(f"{API}/corridas-eventos/{corrida_id}/rejeitar",
                         headers=self.headers_admin,
                         json={"motivo": "Corrida duplicada"})
        assert r.status_code == 200
        assert "rejeitada" in r.json()["message"].lower()

    def test_corrida_pendente_nao_aparece_listagem_publica(self):
        """Corridas pendentes NÃO devem aparecer na listagem pública"""
        nome = f"Corrida Invisivel {self.unique}"
        cidade_unica = f"InvisCid{self.unique}"
        self._criar_corrida(nome, cidade=cidade_unica)
        
        r = requests.get(f"{API}/corridas-eventos", params={"cidade": cidade_unica})
        assert r.status_code == 200
        nomes = [c["nome_corrida"] for c in r.json()]
        assert nome not in nomes

    def test_corrida_encerrada_ano_diferente_bloqueada(self):
        """Corrida encerrada de ano diferente do corrente deve ser bloqueada"""
        form = {
            "nome_corrida": f"Corrida 2025 {self.unique}",
            "organizador": "Org",
            "cidade": "Cidade",
            "estado": "SP",
            "data_corrida": "2025-06-01",
            "status": "encerrada"
        }
        r = requests.post(f"{API}/corridas-eventos", data=form, headers=self.headers_atleta)
        assert r.status_code == 400
        assert "ano corrente" in r.json()["detail"].lower()


# ==================== 3. ANTI-DUPLICIDADE DE CORRIDAS ====================

class TestAntiDuplicidadeCorridas:
    """Testa que corridas duplicadas na mesma cidade/estado são bloqueadas"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.unique = uuid.uuid4().hex[:6]

    def test_duplicata_mesma_cidade_bloqueada(self):
        """Corrida com mesmo nome na mesma cidade/estado deve ser bloqueada"""
        nome = f"Corrida Dup {self.unique}"
        cidade = f"DupCity{self.unique}"
        
        form = {
            "nome_corrida": nome, "organizador": "Org", "cidade": cidade,
            "estado": "MG", "data_corrida": "2026-09-01", "status": "ativa"
        }
        r1 = requests.post(f"{API}/corridas-eventos", data=form, headers=self.headers)
        assert r1.status_code == 200
        
        r2 = requests.post(f"{API}/corridas-eventos", data=form, headers=self.headers)
        assert r2.status_code == 400
        assert "duplicada" in r2.json()["detail"].lower() or "já existe" in r2.json()["detail"].lower()

    def test_mesmo_nome_cidade_diferente_permitido(self):
        """Corrida com mesmo nome em cidades diferentes deve ser permitida"""
        nome = f"Corrida Universal {self.unique}"
        
        form1 = {
            "nome_corrida": nome, "organizador": "Org", "cidade": f"CidadeA{self.unique}",
            "estado": "SP", "data_corrida": "2026-09-01", "status": "ativa"
        }
        form2 = {
            "nome_corrida": nome, "organizador": "Org", "cidade": f"CidadeB{self.unique}",
            "estado": "RJ", "data_corrida": "2026-09-01", "status": "ativa"
        }
        
        r1 = requests.post(f"{API}/corridas-eventos", data=form1, headers=self.headers)
        assert r1.status_code == 200
        
        r2 = requests.post(f"{API}/corridas-eventos", data=form2, headers=self.headers)
        assert r2.status_code == 200


# ==================== 4. EXPORTAÇÕES EXCEL ====================

class TestExportacoesExcel:
    """Testa que todos os 15 endpoints de exportação retornam Excel válido"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.token = login(ADMIN_EMAIL, ADMIN_PASSWORD)

    ENDPOINTS = [
        "/admin/exportar/atletas-profissional",
        "/admin/exportar/atletas-galera",
        "/admin/exportar/donos-assessoria",
        "/admin/exportar/assessorias",
        "/admin/exportar/corridas-parceiras",
        "/admin/exportar/corridas-avaliadas",
        "/admin/exportar/media-avaliacoes",
        "/admin/exportar/engajamento",
        "/admin/exportar/retencao",
        "/admin/exportar/aprovacoes-logs",
        "/admin/exportar/autorizacoes",
        "/admin/exportar/financeiro",
        "/admin/exportar/mensagens",
        "/admin/exportar/logs-admin",
        "/admin/exportar/dados-submetidos",
    ]

    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_export_endpoint_returns_xlsx(self, endpoint):
        """Cada endpoint de exportação deve retornar HTTP 200 com content-type xlsx"""
        r = requests.get(f"{API}{endpoint}", params={"token": self.token})
        assert r.status_code == 200, f"Falhou {endpoint}: {r.status_code} {r.text[:200]}"
        ct = r.headers.get("content-type", "")
        assert "spreadsheetml" in ct or "octet-stream" in ct, f"Content-type inesperado para {endpoint}: {ct}"
        assert len(r.content) > 100, f"Arquivo muito pequeno para {endpoint}: {len(r.content)} bytes"

    def test_export_requer_autenticacao_admin(self):
        """Endpoints de exportação devem rejeitar usuários não-admin"""
        token_atleta = login(ATLETA_EMAIL, ATLETA_PASSWORD)
        r = requests.get(f"{API}/admin/exportar/atletas-profissional", params={"token": token_atleta})
        assert r.status_code in [401, 403]
