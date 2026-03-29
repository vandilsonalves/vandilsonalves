# /app/backend/services/cache_service.py
"""
Sistema de Cache em Memória (sem Redis)
- TTL configurável por endpoint
- Invalidação automática quando dados são alterados
- 100% in-process, sem dependência externa
"""

import json
import hashlib
import logging
import threading
from functools import wraps
from typing import Any, Callable, Optional
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# TTL padrão em segundos (5 minutos)
DEFAULT_TTL = 300

# TTL específicos por tipo de dado
CACHE_TTL = {
    'ranking': 300,
    'ranking_povao': 300,
    'ranking_semanal': 600,
    'ranking_mensal': 900,
    'ranking_destaque': 900,
    'estados': 7200,
    'faixas_etarias': 7200,
    'equipes': 1200,
    'liga_assessorias': 600,
    'corridas_eventos': 600,
    'stats': 120,
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
    """Serviço de cache em memória usando cachetools"""

    def __init__(self, maxsize: int = 2048):
        self._cache = TTLCache(maxsize=maxsize, ttl=DEFAULT_TTL)
        self._lock = threading.Lock()
        self._available = True
        self._stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }

    @property
    def is_available(self) -> bool:
        return self._available

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{prefix}{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        try:
            with self._lock:
                value = self._cache.get(key)
            if value is not None:
                self._stats['hits'] += 1
                return value
            self._stats['misses'] += 1
            return None
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Erro ao buscar cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        try:
            with self._lock:
                self._cache[key] = value
            return True
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Erro ao salvar cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            with self._lock:
                self._cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar cache: {e}")
            return False

    async def invalidate_prefix(self, prefix: str) -> int:
        try:
            with self._lock:
                keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
                for k in keys_to_delete:
                    self._cache.pop(k, None)
            if keys_to_delete:
                logger.info(f"Cache invalidado: {len(keys_to_delete)} chaves com prefixo '{prefix}'")
            return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Erro ao invalidar cache: {e}")
            return 0

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalida chaves que contenham o pattern (compat com chamadas antigas)"""
        prefix = pattern.replace("*", "")
        return await self.invalidate_prefix(prefix)

    async def invalidate_rankings(self):
        await self.invalidate_prefix(CACHE_PREFIXES['ranking'])

    async def invalidate_liga(self):
        await self.invalidate_prefix(CACHE_PREFIXES['liga'])

    async def invalidate_corridas(self):
        await self.invalidate_prefix(CACHE_PREFIXES['corridas'])

    async def invalidate_all(self):
        with self._lock:
            self._cache.clear()
        logger.info("Todo o cache foi invalidado")

    async def invalidate_feed(self):
        """Invalida cache do feed (substitui redis_client.keys('feed:*'))"""
        await self.invalidate_prefix("feed:")

    def get_stats(self) -> dict:
        total = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
        with self._lock:
            cache_size = len(self._cache)
        return {
            'available': True,
            'type': 'in-memory (cachetools)',
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'errors': self._stats['errors'],
            'hit_rate_percent': round(hit_rate, 2),
            'cached_keys': cache_size,
            'memory_used': 'N/A (in-process)',
            'connected_clients': 'N/A'
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
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cache_service.is_available:
                return await func(*args, **kwargs)

            cache_prefix = CACHE_PREFIXES.get(prefix, CACHE_PREFIXES['general'])
            cache_key = cache_service._generate_key(
                f"{cache_prefix}{func.__name__}:",
                *args,
                **kwargs
            )

            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = await func(*args, **kwargs)

            cache_ttl = ttl or CACHE_TTL.get(ttl_key, DEFAULT_TTL)
            await cache_service.set(cache_key, result, cache_ttl)

            return result

        return wrapper
    return decorator


# Funções auxiliares para invalidação (API compatível)
async def invalidate_on_ranking_change():
    await cache_service.invalidate_rankings()
    await cache_service.invalidate_prefix(CACHE_PREFIXES['stats'])


async def invalidate_on_liga_change():
    await cache_service.invalidate_liga()


async def invalidate_on_corrida_change():
    await cache_service.invalidate_corridas()
