# /app/backend/services/cache_service.py
"""
Sistema de Cache Inteligente com Redis
- TTL configurável por endpoint
- Invalidação automática quando dados são alterados
- Fallback para execução direta se Redis não estiver disponível
"""

import redis
import json
import hashlib
import logging
from functools import wraps
from typing import Any, Callable, Optional
from datetime import timedelta
import asyncio
import os

logger = logging.getLogger(__name__)

# Configuração do Redis
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# TTL padrão em segundos (5 minutos)
DEFAULT_TTL = 300

# TTL específicos por tipo de dado
CACHE_TTL = {
    'ranking': 300,           # 5 min - rankings mudam com menos frequência
    'ranking_povao': 300,     # 5 min
    'ranking_semanal': 300,   # 5 min
    'ranking_mensal': 600,    # 10 min - mensal muda menos
    'ranking_destaque': 600,  # 10 min
    'estados': 3600,          # 1 hora - raramente muda
    'faixas_etarias': 3600,   # 1 hora - raramente muda
    'equipes': 600,           # 10 min
    'liga_assessorias': 300,  # 5 min
    'corridas_eventos': 300,  # 5 min
    'stats': 60,              # 1 min - stats mais dinâmicas
}

# Prefixos de cache para invalidação em grupo
CACHE_PREFIXES = {
    'ranking': 'cache:ranking:',
    'liga': 'cache:liga:',
    'corridas': 'cache:corridas:',
    'stats': 'cache:stats:',
    'general': 'cache:general:',
}


class CacheService:
    """Serviço de cache com Redis"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._available = False
        self._stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }
    
    @property
    def client(self) -> Optional[redis.Redis]:
        """Conexão lazy com Redis"""
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Testar conexão
                self._client.ping()
                self._available = True
                logger.info(f"✅ Redis conectado em {REDIS_HOST}:{REDIS_PORT}")
            except Exception as e:
                logger.warning(f"⚠️ Redis não disponível: {e}. Cache desabilitado.")
                self._available = False
                self._client = None
        return self._client
    
    @property
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        if self._client is None:
            _ = self.client  # Tenta conectar
        return self._available
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Gera chave de cache única baseada nos argumentos"""
        # Criar hash dos argumentos
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{prefix}{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache"""
        if not self.is_available:
            return None
        
        try:
            value = await asyncio.to_thread(self.client.get, key)
            if value:
                self._stats['hits'] += 1
                return json.loads(value)
            self._stats['misses'] += 1
            return None
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Erro ao buscar cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        """Salva valor no cache"""
        if not self.is_available:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            await asyncio.to_thread(self.client.setex, key, ttl, serialized)
            return True
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Erro ao salvar cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        if not self.is_available:
            return False
        
        try:
            await asyncio.to_thread(self.client.delete, key)
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar cache: {e}")
            return False
    
    async def invalidate_prefix(self, prefix: str) -> int:
        """Invalida todas as chaves com determinado prefixo"""
        if not self.is_available:
            return 0
        
        try:
            # Buscar todas as chaves com o prefixo
            keys = await asyncio.to_thread(self.client.keys, f"{prefix}*")
            if keys:
                deleted = await asyncio.to_thread(self.client.delete, *keys)
                logger.info(f"🗑️ Cache invalidado: {deleted} chaves com prefixo '{prefix}'")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Erro ao invalidar cache: {e}")
            return 0
    
    async def invalidate_rankings(self):
        """Invalida todo cache de rankings"""
        await self.invalidate_prefix(CACHE_PREFIXES['ranking'])
    
    async def invalidate_liga(self):
        """Invalida todo cache da liga de assessorias"""
        await self.invalidate_prefix(CACHE_PREFIXES['liga'])
    
    async def invalidate_corridas(self):
        """Invalida todo cache de corridas/eventos"""
        await self.invalidate_prefix(CACHE_PREFIXES['corridas'])
    
    async def invalidate_all(self):
        """Invalida todo o cache"""
        if not self.is_available:
            return
        
        try:
            await asyncio.to_thread(self.client.flushdb)
            logger.info("🗑️ Todo o cache foi invalidado")
        except Exception as e:
            logger.error(f"Erro ao invalidar todo cache: {e}")
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do cache"""
        total = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
        
        info = {}
        if self.is_available:
            try:
                info = self.client.info('memory')
            except:
                pass
        
        return {
            'available': self._available,
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'errors': self._stats['errors'],
            'hit_rate_percent': round(hit_rate, 2),
            'memory_used': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 'N/A')
        }


# Instância global
cache_service = CacheService()


def cached(prefix: str = 'general', ttl_key: str = None, ttl: int = None):
    """
    Decorator para cache de funções async.
    
    Args:
        prefix: Prefixo para a chave de cache (ranking, liga, corridas, etc)
        ttl_key: Chave do dicionário CACHE_TTL para TTL específico
        ttl: TTL em segundos (sobrescreve ttl_key)
    
    Exemplo:
        @cached(prefix='ranking', ttl_key='ranking_povao')
        async def get_ranking_povao(genero: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Se cache não disponível, executar direto
            if not cache_service.is_available:
                return await func(*args, **kwargs)
            
            # Gerar chave de cache
            cache_prefix = CACHE_PREFIXES.get(prefix, CACHE_PREFIXES['general'])
            cache_key = cache_service._generate_key(
                f"{cache_prefix}{func.__name__}:",
                *args,
                **kwargs
            )
            
            # Tentar buscar do cache
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"🎯 Cache HIT: {cache_key}")
                return cached_value
            
            # Cache miss - executar função
            logger.debug(f"❌ Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Salvar no cache
            cache_ttl = ttl or CACHE_TTL.get(ttl_key, DEFAULT_TTL)
            await cache_service.set(cache_key, result, cache_ttl)
            
            return result
        
        return wrapper
    return decorator


# Funções auxiliares para invalidação de cache em operações CRUD
async def invalidate_on_ranking_change():
    """Chamar quando rankings forem alterados"""
    await cache_service.invalidate_rankings()
    await cache_service.invalidate_prefix(CACHE_PREFIXES['stats'])


async def invalidate_on_liga_change():
    """Chamar quando dados da liga forem alterados"""
    await cache_service.invalidate_liga()


async def invalidate_on_corrida_change():
    """Chamar quando corridas/eventos forem alterados"""
    await cache_service.invalidate_corridas()
