# /app/backend/models/rbac.py
# Modelos para o Sistema RBAC (Role Based Access Control)

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid


# ==================== ROLES E PERMISSÕES ====================

class Role(BaseModel):
    """Papel/Função de administrador"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str  # super_admin, colaborador, admin_emergencia
    descricao: str
    nivel: int  # 1 = super_admin, 2 = colaborador, 3 = emergencia
    permissoes: List[str] = []  # Lista de códigos de permissão
    ativo: bool = True
    criado_em: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Permissao(BaseModel):
    """Permissão individual do sistema"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    codigo: str  # Ex: "aprovar_corridas", "gerenciar_admins"
    nome: str
    descricao: str
    categoria: str  # Ex: "corridas", "atletas", "sistema"


# ==================== ADMINISTRADORES ====================

class Administrador(BaseModel):
    """Administrador do sistema"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    email: str
    password_hash: str = ""
    role_id: str  # ID do Role
    role_nome: str  # Cache do nome do role para exibição
    status: str = "ativo"  # ativo, inativo, bloqueado
    foto_url: str = ""
    
    # Segurança
    dois_fatores_ativo: bool = False
    dois_fatores_secret: str = ""  # Para TOTP se implementado
    
    # Metadados
    criado_em: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    criado_por: str = ""  # ID do admin que criou
    ultimo_login: Optional[str] = None
    ultimo_ip: Optional[str] = None
    ultimo_dispositivo: Optional[str] = None
    
    # Flags especiais
    is_super_admin: bool = False
    is_emergencia: bool = False
    invisivel: bool = False  # Para admin de emergência


class AdminCreate(BaseModel):
    """Dados para criar novo administrador"""
    nome: str
    email: str
    password: str
    role_id: str


class AdminUpdate(BaseModel):
    """Dados para atualizar administrador"""
    nome: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    role_id: Optional[str] = None


# ==================== LOGS DE AUDITORIA ====================

class AdminLog(BaseModel):
    """Log de ação administrativa"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identificação do admin
    admin_id: str
    admin_nome: str
    admin_role: str
    
    # Ação realizada
    tipo_acao: str  # Ex: "aprovar_corrida", "criar_admin", "login"
    descricao: str
    
    # Registro afetado
    entidade_tipo: Optional[str] = None  # Ex: "corrida", "atleta", "admin"
    entidade_id: Optional[str] = None
    entidade_nome: Optional[str] = None
    
    # Dados técnicos
    ip_address: str
    user_agent: str = ""
    dispositivo: str = ""  # Extraído do user_agent
    localizacao_aproximada: str = ""  # Baseado no IP
    
    # Metadados
    data_hora: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Dados adicionais (JSON)
    dados_extras: dict = {}


class LoginHistory(BaseModel):
    """Histórico de login de administradores"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    admin_nome: str
    
    # Dados do login
    sucesso: bool
    ip_address: str
    user_agent: str = ""
    dispositivo: str = ""
    navegador: str = ""
    cidade_aproximada: str = ""
    
    # Timestamp
    data_hora: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Motivo de falha (se aplicável)
    motivo_falha: Optional[str] = None


# ==================== 2FA ====================

class CodigoVerificacao(BaseModel):
    """Código de verificação 2FA por email"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    email: str
    codigo: str  # 6 dígitos
    tipo: str = "login"  # login, acao_critica
    
    criado_em: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expira_em: str  # 10 minutos após criação
    usado: bool = False
    usado_em: Optional[str] = None


# ==================== ALERTAS DE SEGURANÇA ====================

class AlertaSeguranca(BaseModel):
    """Alerta de segurança do sistema"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    tipo: str  # "admin_emergencia_usado", "tentativa_invasao", "acao_suspeita"
    titulo: str
    descricao: str
    
    admin_id: Optional[str] = None
    admin_nome: Optional[str] = None
    
    ip_address: str
    dispositivo: str = ""
    
    data_hora: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Notificação
    email_enviado: bool = False
    email_enviado_para: str = ""
    email_enviado_em: Optional[str] = None
    
    # Resolução
    resolvido: bool = False
    resolvido_por: Optional[str] = None
    resolvido_em: Optional[str] = None


# ==================== PERMISSÕES DO SISTEMA ====================

# Lista de todas as permissões disponíveis
PERMISSOES_SISTEMA = {
    # Corridas
    "aprovar_corridas": {"nome": "Aprovar Corridas", "descricao": "Aprovar corridas cadastradas", "categoria": "corridas"},
    "reprovar_corridas": {"nome": "Reprovar Corridas", "descricao": "Reprovar corridas cadastradas", "categoria": "corridas"},
    "aprovar_resultados": {"nome": "Aprovar Resultados", "descricao": "Aprovar resultados de provas", "categoria": "resultados"},
    "moderar_avaliacoes": {"nome": "Moderar Avaliações", "descricao": "Moderar avaliações de corridas", "categoria": "corridas"},
    
    # Atletas
    "visualizar_atletas": {"nome": "Visualizar Atletas", "descricao": "Visualizar cadastros de atletas", "categoria": "atletas"},
    "editar_atletas": {"nome": "Editar Atletas", "descricao": "Editar dados de atletas", "categoria": "atletas"},
    "excluir_atletas": {"nome": "Excluir Atletas", "descricao": "Excluir atletas do sistema", "categoria": "atletas"},
    
    # Assessorias
    "visualizar_assessorias": {"nome": "Visualizar Assessorias", "descricao": "Visualizar assessorias", "categoria": "assessorias"},
    "gerenciar_assessorias": {"nome": "Gerenciar Assessorias", "descricao": "Gerenciar assessorias", "categoria": "assessorias"},
    
    # Comunicação
    "enviar_mensagens": {"nome": "Enviar Mensagens", "descricao": "Enviar mensagens limitadas", "categoria": "comunicacao"},
    
    # Administração (Super Admin apenas)
    "criar_admins": {"nome": "Criar Admins", "descricao": "Criar novos administradores", "categoria": "sistema"},
    "editar_admins": {"nome": "Editar Admins", "descricao": "Editar administradores", "categoria": "sistema"},
    "excluir_admins": {"nome": "Excluir Admins", "descricao": "Excluir administradores", "categoria": "sistema"},
    "visualizar_logs": {"nome": "Visualizar Logs", "descricao": "Visualizar logs de auditoria", "categoria": "sistema"},
    "configuracoes_sistema": {"nome": "Configurações", "descricao": "Alterar configurações do sistema", "categoria": "sistema"},
    "exportar_dados": {"nome": "Exportar Dados", "descricao": "Exportar banco de dados completo", "categoria": "sistema"},
    "dados_financeiros": {"nome": "Dados Financeiros", "descricao": "Acessar dados financeiros", "categoria": "sistema"},
    "alterar_pontuacao": {"nome": "Alterar Pontuação", "descricao": "Alterar regras de pontuação", "categoria": "sistema"},
    "restaurar_dados": {"nome": "Restaurar Dados", "descricao": "Restaurar dados ou backups", "categoria": "sistema"},
    
    # Admin de Emergência (Exclusivas)
    "bloquear_admins": {"nome": "Bloquear Admins", "descricao": "Bloquear administradores", "categoria": "emergencia"},
    "revogar_permissoes": {"nome": "Revogar Permissões", "descricao": "Revogar permissões administrativas", "categoria": "emergencia"},
    "modo_manutencao": {"nome": "Modo Manutenção", "descricao": "Ativar modo de manutenção", "categoria": "emergencia"},
    "encerrar_sessoes": {"nome": "Encerrar Sessões", "descricao": "Encerrar sessões ativas", "categoria": "emergencia"},
    "exportar_logs_seguranca": {"nome": "Exportar Logs Segurança", "descricao": "Exportar logs de segurança", "categoria": "emergencia"},
}

# Roles pré-definidos
ROLES_PREDEFINIDOS = {
    "super_admin": {
        "nome": "Super Admin",
        "descricao": "Administrador Principal com acesso total ao sistema",
        "nivel": 1,
        "permissoes": list(PERMISSOES_SISTEMA.keys())  # Todas as permissões
    },
    "colaborador": {
        "nome": "Colaborador",
        "descricao": "Administrador Operacional com permissões limitadas",
        "nivel": 2,
        "permissoes": [
            "aprovar_corridas", "reprovar_corridas", "aprovar_resultados",
            "moderar_avaliacoes", "visualizar_atletas", "visualizar_assessorias",
            "enviar_mensagens"
        ]
    },
    "admin_emergencia": {
        "nome": "Admin de Emergência",
        "descricao": "Conta especial para situações críticas",
        "nivel": 3,
        "permissoes": list(PERMISSOES_SISTEMA.keys())  # Todas as permissões
    }
}
