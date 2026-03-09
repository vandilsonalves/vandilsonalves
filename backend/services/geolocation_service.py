# /app/backend/services/geolocation_service.py
# Serviço de Geolocalização baseada em IP

import aiohttp
import asyncio
import logging
from typing import Optional
from functools import lru_cache
import time

logger = logging.getLogger(__name__)

# Cache simples em memória (IP -> localização)
_geo_cache = {}
_cache_ttl = 3600  # 1 hora


async def get_geolocation(ip: str) -> dict:
    """
    Obtém informações de geolocalização baseadas no IP.
    Usa a API gratuita ip-api.com (limite: 45 requests/minuto)
    
    Args:
        ip: Endereço IP para localizar
    
    Returns:
        dict com informações de localização
    """
    # IPs locais/privados não têm geolocalização
    if is_private_ip(ip):
        return {
            "status": "local",
            "country": "Local",
            "countryCode": "LO",
            "region": "",
            "regionName": "Rede Local",
            "city": "Localhost",
            "zip": "",
            "lat": 0,
            "lon": 0,
            "timezone": "",
            "isp": "Local Network",
            "org": "",
            "as": "",
            "query": ip,
            "formatted": "Rede Local"
        }
    
    # Verificar cache
    cache_key = ip
    if cache_key in _geo_cache:
        cached_data, cached_time = _geo_cache[cache_key]
        if time.time() - cached_time < _cache_ttl:
            logger.debug(f"Geolocalização do cache para {ip}")
            return cached_data
    
    # Buscar da API
    try:
        async with aiohttp.ClientSession() as session:
            # Campos que queremos da API
            fields = "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
            url = f"http://ip-api.com/json/{ip}?fields={fields}&lang=pt-BR"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        # Formatar localização legível
                        city = data.get("city", "")
                        region = data.get("regionName", "")
                        country = data.get("country", "")
                        
                        parts = [p for p in [city, region, country] if p]
                        data["formatted"] = ", ".join(parts) if parts else "Desconhecido"
                        
                        # Salvar no cache
                        _geo_cache[cache_key] = (data, time.time())
                        
                        logger.info(f"Geolocalização obtida para {ip}: {data['formatted']}")
                        return data
                    else:
                        logger.warning(f"Geolocalização falhou para {ip}: {data.get('message', 'Unknown error')}")
                        return get_fallback_response(ip, data.get("message", "API error"))
                else:
                    logger.warning(f"Geolocalização HTTP error {response.status} para {ip}")
                    return get_fallback_response(ip, f"HTTP {response.status}")
                    
    except asyncio.TimeoutError:
        logger.warning(f"Geolocalização timeout para {ip}")
        return get_fallback_response(ip, "Timeout")
    except Exception as e:
        logger.error(f"Geolocalização erro para {ip}: {str(e)}")
        return get_fallback_response(ip, str(e))


def is_private_ip(ip: str) -> bool:
    """Verifica se é um IP privado/local"""
    if not ip or ip == "unknown":
        return True
    
    private_prefixes = [
        "127.",      # Localhost
        "10.",       # Classe A privado
        "172.16.",   # Classe B privado
        "172.17.",
        "172.18.",
        "172.19.",
        "172.20.",
        "172.21.",
        "172.22.",
        "172.23.",
        "172.24.",
        "172.25.",
        "172.26.",
        "172.27.",
        "172.28.",
        "172.29.",
        "172.30.",
        "172.31.",
        "192.168.",  # Classe C privado
        "169.254.",  # Link-local
        "::1",       # IPv6 localhost
        "fe80:",     # IPv6 link-local
        "fc00:",     # IPv6 unique local
        "fd00:",     # IPv6 unique local
    ]
    
    return any(ip.startswith(prefix) for prefix in private_prefixes) or ip == "localhost"


def get_fallback_response(ip: str, error: str = "") -> dict:
    """Retorna resposta padrão quando a API falha"""
    return {
        "status": "fail",
        "message": error,
        "country": "Desconhecido",
        "countryCode": "??",
        "region": "",
        "regionName": "",
        "city": "",
        "zip": "",
        "lat": 0,
        "lon": 0,
        "timezone": "",
        "isp": "",
        "org": "",
        "as": "",
        "query": ip,
        "formatted": "Localização indisponível"
    }


async def get_location_string(ip: str) -> str:
    """
    Retorna apenas a string de localização formatada.
    Útil para logs e exibição simples.
    """
    geo = await get_geolocation(ip)
    return geo.get("formatted", "Desconhecido")


async def get_location_details(ip: str) -> dict:
    """
    Retorna detalhes completos de localização para exibição no frontend.
    """
    geo = await get_geolocation(ip)
    
    return {
        "ip": ip,
        "cidade": geo.get("city", ""),
        "regiao": geo.get("regionName", ""),
        "pais": geo.get("country", ""),
        "codigo_pais": geo.get("countryCode", ""),
        "latitude": geo.get("lat", 0),
        "longitude": geo.get("lon", 0),
        "timezone": geo.get("timezone", ""),
        "isp": geo.get("isp", ""),
        "organizacao": geo.get("org", ""),
        "formatado": geo.get("formatted", "Desconhecido"),
        "is_local": is_private_ip(ip)
    }


# Limpar cache antigo periodicamente
def clear_old_cache():
    """Remove entradas antigas do cache"""
    current_time = time.time()
    keys_to_remove = []
    
    for key, (data, cached_time) in _geo_cache.items():
        if current_time - cached_time > _cache_ttl:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del _geo_cache[key]
    
    if keys_to_remove:
        logger.info(f"Cache de geolocalização limpo: {len(keys_to_remove)} entradas removidas")
