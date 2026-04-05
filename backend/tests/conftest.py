"""
Configuração centralizada para testes.
Credenciais e URLs devem ser definidas via variáveis de ambiente.
"""
import os

API_URL = os.environ.get("TEST_API_URL", "http://localhost:8001/api")
ADMIN_EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "admin@runpro.com")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "admin")
ATLETA_EMAIL = os.environ.get("TEST_ATLETA_EMAIL", "teste.dono@teste.com")
ATLETA_PASSWORD = os.environ.get("TEST_ATLETA_PASSWORD", "123456")
