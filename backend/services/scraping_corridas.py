"""
Serviço de Scraping Avançado de Corridas v2
- Scrapers específicos por API (Ticket Sports, etc.)
- Fallback inteligente: requests → Playwright
- Auto-detecção de sites que precisam de JavaScript
- Anti-duplicidade contra o banco de dados
- Cálculo automático de status (ativa/encerrada) pela data
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

ESTADOS_BR = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}

CIDADES_ESTADOS = {
    'rio branco': 'AC', 'maceió': 'AL', 'macapá': 'AP', 'manaus': 'AM',
    'salvador': 'BA', 'fortaleza': 'CE', 'brasília': 'DF', 'vitória': 'ES',
    'goiânia': 'GO', 'são luís': 'MA', 'cuiabá': 'MT', 'campo grande': 'MS',
    'belo horizonte': 'MG', 'belém': 'PA', 'joão pessoa': 'PB', 'curitiba': 'PR',
    'recife': 'PE', 'teresina': 'PI', 'rio de janeiro': 'RJ', 'natal': 'RN',
    'porto alegre': 'RS', 'porto velho': 'RO', 'boa vista': 'RR', 'florianópolis': 'SC',
    'são paulo': 'SP', 'aracaju': 'SE', 'palmas': 'TO',
    'guarulhos': 'SP', 'campinas': 'SP', 'santos': 'SP', 'sorocaba': 'SP',
    'ribeirão preto': 'SP', 'niterói': 'RJ', 'petrópolis': 'RJ',
    'contagem': 'MG', 'uberlândia': 'MG', 'juiz de fora': 'MG',
    'feira de santana': 'BA', 'porto seguro': 'BA', 'ilhéus': 'BA', 'caetité': 'BA',
    'joinville': 'SC', 'blumenau': 'SC', 'balneário camboriú': 'SC',
    'londrina': 'PR', 'maringá': 'PR', 'foz do iguaçu': 'PR',
    'caxias do sul': 'RS', 'pelotas': 'RS', 'gramado': 'RS',
    'olinda': 'PE', 'caruaru': 'PE', 'petrolina': 'PE',
    'aparecida de goiânia': 'GO', 'anápolis': 'GO',
    'vila velha': 'ES', 'serra': 'ES', 'cariacica': 'ES',
}

MESES_PT = {
    'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
    'abril': '04', 'maio': '05', 'junho': '06', 'julho': '07',
    'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11',
    'dezembro': '12',
    'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
    'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
    'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
}

# Sites que SEMPRE precisam de Playwright (SPA/JS-heavy)
SITES_PLAYWRIGHT = [
    'sympla.com.br', 'minhasinscricoes.com.br', 'races.com.br',
    'incentivoesporte.com.br', 'pscronos.com.br', 'assessocor.online',
    'corre10.com.br', 'vidasport.com.br', 'corre77.com.br',
    'esportecorrida.com.br', 'blackrun.com.br', 'riorunningtour.com.br',
    'corridaderuasuperacao.com.br', 'mssport.com.br', 'oestechip.com.br',
    'youmovin.com.br', 'runnerbrasil.com.br',
]

# Sites com API JSON direta
SITES_API = {
    'ticketsports.com.br/api': 'ticket_sports_api',
    'brasilcorrida.com.br/api': 'brasil_corrida_api',
    'centraldacorrida.com.br/api': 'central_corrida_api',
}


def calcular_status(data_str: str) -> str:
    """Calcula se a corrida está ativa ou encerrada baseado na data"""
    if not data_str:
        return 'ativa'
    try:
        data_evento = datetime.strptime(data_str[:10], "%Y-%m-%d")
        hoje = datetime.now()
        return 'encerrada' if data_evento.date() < hoje.date() else 'ativa'
    except Exception:
        return 'ativa'


def extrair_data(texto: str) -> str:
    """Extrai data e retorna no formato YYYY-MM-DD"""
    if not texto:
        return ''
    texto = texto.strip()

    # ISO format
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', texto)
    if m:
        return m.group(0)

    # DD/MM/YYYY
    m = re.search(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', texto)
    if m:
        d, mo, y = m.groups()
        return f"{y}-{mo.zfill(2)}-{d.zfill(2)}"

    # DD de MES de YYYY
    m = re.search(r'(\d{1,2})\s*(?:de\s+)?(\w+)\s*(?:de\s+)?(\d{4})', texto.lower())
    if m:
        d, mes_nome, y = m.groups()
        mo = MESES_PT.get(mes_nome[:3], '')
        if mo:
            return f"{y}-{mo}-{d.zfill(2)}"

    return ''


def extrair_estado(texto: str) -> str:
    """Extrai UF de um texto"""
    if not texto:
        return ''
    # Pattern: "Cidade - UF" or "Cidade, UF" or "Cidade/UF"
    m = re.search(r'[-/,]\s*([A-Z]{2})\s*$', texto.strip())
    if m and m.group(1) in ESTADOS_BR:
        return m.group(1)
    m = re.search(r'\(([A-Z]{2})\)', texto)
    if m and m.group(1) in ESTADOS_BR:
        return m.group(1)
    # Buscar cidade conhecida
    for cidade, uf in CIDADES_ESTADOS.items():
        if cidade in texto.lower():
            return uf
    for uf, nome in ESTADOS_BR.items():
        if nome.lower() in texto.lower():
            return uf
    return ''


def extrair_cidade(texto: str) -> str:
    """Extrai nome da cidade removendo UF"""
    if not texto:
        return ''
    c = re.sub(r'\s*[-/,]\s*[A-Z]{2}\s*$', '', texto.strip())
    c = re.sub(r'\s*\([A-Z]{2}\)\s*$', '', c)
    c = re.sub(r'\s*-\s*Brasil\s*$', '', c, flags=re.IGNORECASE)
    return c.strip()[:100]


def limpar_texto(t: str) -> str:
    if not t:
        return ''
    return re.sub(r'\s+', ' ', t).strip()


def eh_corrida_valida(nome: str) -> bool:
    if not nome or len(nome) < 5:
        return False
    nl = nome.lower().strip()
    bloqueadas = [
        'minha conta', 'login', 'cadastro', 'senha', 'contato', 'sobre',
        'política', 'termos', 'carrinho', 'checkout', 'menu', 'home',
        'facebook', 'instagram', 'twitter', 'youtube', 'whatsapp',
        'copyright', 'desenvolvido por', 'ver mais', 'saiba mais',
        'fale conosco', 'quem somos'
    ]
    for p in bloqueadas:
        if p in nl:
            return False
    positivas = [
        'corrida', 'maratona', 'meia maratona', 'meia-maratona',
        'run', 'running', 'marathon', '5k', '10k', '21k', '42k',
        '5km', '10km', '21km', '42km', 'trail', 'trilha', 'circuito',
        'night run', 'color run', 'race', 'prova', 'desafio',
        'rústica', 'rustica', 'cross', 'ultra', 'revezamento',
        'etapa', 'volta', 'travessia', 'km'
    ]
    negativas = [
        'ciclismo', 'bike', 'bicicleta', 'mtb', 'pedal',
        'natação', 'swim', 'triathlon', 'futebol', 'vôlei',
        'workshop', 'curso', 'palestra', 'show', 'festa',
        'yoga', 'pilates', 'crossfit'
    ]
    for p in negativas:
        if p in nl:
            return False
    for p in positivas:
        if p in nl:
            return True
    if re.search(r'\d+\s*k(?:m)?', nl):
        return True
    return False


def criar_corrida(nome, organizador, cidade, estado, link, data_str, fonte=""):
    """Cria corrida padronizada com status automático"""
    nome = limpar_texto(nome)[:200]
    organizador = limpar_texto(organizador)[:100] or fonte
    cidade = extrair_cidade(cidade)
    if not estado:
        estado = extrair_estado(cidade or "")
    data = extrair_data(data_str) if data_str else ''
    status = calcular_status(data)
    return {
        'nome_corrida': nome,
        'organizador': organizador,
        'cidade': cidade,
        'estado': estado.upper()[:2] if estado else '',
        'pagina_link': link or '',
        'data_corrida': data,
        'status': status
    }


# ============== SCRAPERS ESPECÍFICOS POR API ==============

def scrape_ticket_sports_api(url: str) -> List[Dict]:
    """Scraper para API JSON do Ticket Sports"""
    try:
        # Se a URL não é a API, converter
        if '/api/events/list' not in url:
            url = 'https://www.ticketsports.com.br/api/events/list?quantity=720&atlheteId=0&quickFilter=corrida-de-rua'

        api_headers = {
            **HEADERS,
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.ticketsports.com.br/',
            'Origin': 'https://www.ticketsports.com.br',
        }
        resp = requests.get(url, headers=api_headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if not isinstance(data, list):
            return []

        corridas = []
        for ev in data:
            nome = ev.get('title', '')
            if not nome:
                continue
            endereco = ev.get('address', '')
            cidade = extrair_cidade(endereco)
            estado = extrair_estado(endereco)
            data_str = ev.get('date', '')
            org = ev.get('organizer', 'Ticket Sports')
            link = ev.get('uri', '')
            corridas.append(criar_corrida(nome, org, cidade, estado, link, data_str, 'Ticket Sports'))

        return corridas
    except Exception as e:
        logger.error(f"Ticket Sports API error: {e}")
        return []


def scrape_central_inscricoes_html(url: str) -> List[Dict]:
    """Scraper HTML para Central das Inscrições"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'lxml')
        corridas = []
        cards = soup.find_all(['div', 'article', 'a'], class_=re.compile(r'event|card|item|evento', re.I))
        for card in cards:
            nome_el = card.find(['h2', 'h3', 'h4', 'a', 'strong'])
            if not nome_el:
                continue
            nome = limpar_texto(nome_el.get_text())
            if not eh_corrida_valida(nome):
                continue
            link = ''
            a_el = card.find('a', href=True) if card.name != 'a' else card
            if a_el and a_el.get('href'):
                link = urljoin(url, a_el['href'])
            texto = limpar_texto(card.get_text())
            data = extrair_data(texto)
            cidade, estado = '', ''
            m = re.search(r'([A-Za-zÀ-ú\s]+)\s*[-/,]\s*([A-Z]{2})', texto)
            if m:
                cidade = m.group(1).strip()
                estado = m.group(2)
            corridas.append(criar_corrida(nome, 'Central das Inscrições', cidade, estado, link, data, 'Central das Inscrições'))
        return corridas
    except Exception as e:
        logger.error(f"Central Inscrições error: {e}")
        return []


def scrape_generico_html(url: str) -> List[Dict]:
    """Scraper genérico para qualquer site HTML"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'lxml')
        domain = urlparse(url).netloc.replace('www.', '')
        corridas = []
        nomes_vistos = set()

        # Strategy 1: event-like containers
        containers = soup.find_all(['div', 'article', 'li', 'section'],
            class_=re.compile(r'event|corrida|prova|card|item|produto|calendario', re.I))

        for c in containers[:200]:
            titulo_el = None
            for tag in ['h2', 'h3', 'h4', 'h5', 'a', 'strong']:
                titulo_el = c.find(tag)
                if titulo_el and len(titulo_el.get_text(strip=True)) > 5:
                    break
                titulo_el = None
            if not titulo_el:
                continue
            nome = limpar_texto(titulo_el.get_text())
            if nome.lower() in nomes_vistos or not eh_corrida_valida(nome):
                continue
            nomes_vistos.add(nome.lower())
            link = ''
            a_el = c.find('a', href=True)
            if a_el:
                link = urljoin(url, a_el['href'])
            texto = limpar_texto(c.get_text())
            data = extrair_data(texto)
            cidade, estado = '', ''
            m = re.search(r'([A-Za-zÀ-ú\s]+)\s*[-/,]\s*([A-Z]{2})', texto)
            if m:
                cidade = m.group(1).strip()
                estado = m.group(2)
            corridas.append(criar_corrida(nome, domain, cidade, estado, link, data, domain))

        # Strategy 2: all links
        for a in soup.find_all('a', href=True):
            nome = limpar_texto(a.get_text())
            if nome.lower() in nomes_vistos or not eh_corrida_valida(nome):
                continue
            nomes_vistos.add(nome.lower())
            link = urljoin(url, a['href'])
            parent = a.parent
            texto = limpar_texto(parent.get_text()) if parent else ''
            data = extrair_data(texto)
            cidade, estado = '', ''
            m = re.search(r'([A-Za-zÀ-ú\s]+)\s*[-/,]\s*([A-Z]{2})', texto)
            if m:
                cidade = m.group(1).strip()
                estado = m.group(2)
            corridas.append(criar_corrida(nome, domain, cidade, estado, link, data, domain))

        return corridas
    except Exception as e:
        logger.error(f"Generic HTML scraping error for {url}: {e}")
        return []


def scrape_com_playwright(url: str) -> List[Dict]:
    """Scraping com Playwright para sites JS-heavy"""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            context = browser.new_context(
                user_agent=HEADERS['User-Agent'],
                viewport={'width': 1920, 'height': 1080},
                locale='pt-BR'
            )
            page = context.new_page()
            page.set_default_timeout(45000)

            # Bloquear recursos pesados
            page.route("**/*.{png,jpg,jpeg,gif,svg,mp4,webm,woff2,woff,ttf}", lambda route: route.abort())

            page.goto(url, wait_until='domcontentloaded')
            page.wait_for_timeout(5000)

            # Scroll down para carregar mais
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, 'lxml')
        domain = urlparse(url).netloc.replace('www.', '')
        corridas = []
        nomes_vistos = set()

        # Parse the JS-rendered HTML
        containers = soup.find_all(['div', 'article', 'li', 'a', 'section'],
            class_=re.compile(r'event|corrida|prova|card|item|produto|calendario|race|sport', re.I))

        if not containers:
            containers = soup.find_all(['div', 'article', 'li'], attrs={'data-testid': True})

        if not containers:
            # Fallback: all divs with meaningful text
            containers = [el for el in soup.find_all(['div', 'article']) if el.find(['h2', 'h3', 'h4', 'h5'])]

        for c in containers[:300]:
            titulo_el = None
            for tag in ['h2', 'h3', 'h4', 'h5', 'a', 'strong', 'span']:
                titulo_el = c.find(tag)
                if titulo_el and len(titulo_el.get_text(strip=True)) > 5:
                    break
                titulo_el = None
            if not titulo_el:
                continue
            nome = limpar_texto(titulo_el.get_text())
            if nome.lower() in nomes_vistos or not eh_corrida_valida(nome):
                continue
            nomes_vistos.add(nome.lower())
            link = ''
            a_el = c.find('a', href=True) if c.name != 'a' else c
            if a_el and a_el.get('href'):
                link = urljoin(url, a_el['href'])
            texto = limpar_texto(c.get_text())
            data = extrair_data(texto)
            cidade, estado = '', ''
            m = re.search(r'([A-Za-zÀ-ú\s]+)\s*[-/,]\s*([A-Z]{2})', texto)
            if m:
                cidade = m.group(1).strip()
                estado = m.group(2)
            else:
                for cidade_conhecida, uf in CIDADES_ESTADOS.items():
                    if cidade_conhecida in texto.lower():
                        cidade = cidade_conhecida.title()
                        estado = uf
                        break
            corridas.append(criar_corrida(nome, domain, cidade, estado, link, data, f'Playwright ({domain})'))

        return corridas

    except Exception as e:
        logger.error(f"Playwright scraping error for {url}: {e}")
        return []


def precisa_playwright(url: str) -> bool:
    """Detecta se a URL precisa de Playwright"""
    domain = urlparse(url).netloc.lower().replace('www.', '')
    # Hash-based routing (SPA)
    if '#/' in url:
        return True
    for site in SITES_PLAYWRIGHT:
        if site in domain:
            return True
    return False


def detectar_api(url: str) -> Optional[str]:
    """Detecta se a URL é uma API conhecida"""
    for pattern, parser_name in SITES_API.items():
        if pattern in url:
            return parser_name
    return None


def fazer_scraping(url: str, usar_playwright: bool = False) -> Dict:
    """
    Função principal de scraping com fallback inteligente:
    1. Se é API conhecida → parser específico
    2. Se precisa Playwright → vai direto
    3. Tenta HTML simples
    4. Se não encontrar nada → tenta Playwright como fallback
    """
    if not url or not url.startswith(('http://', 'https://')):
        return {
            'success': False, 'fonte': 'Erro', 'url': url,
            'total_encontradas': 0, 'corridas': [],
            'mensagem': 'URL inválida. Use http:// ou https://',
            'metodo': 'none'
        }

    try:
        corridas = []
        metodo = 'html'

        # 1. API conhecida?
        api_type = detectar_api(url)
        if api_type == 'ticket_sports_api':
            corridas = scrape_ticket_sports_api(url)
            metodo = 'api'
        elif api_type == 'brasil_corrida_api':
            corridas = scrape_ticket_sports_api(url)  # Similar JSON
            metodo = 'api'
        elif api_type == 'central_corrida_api':
            corridas = scrape_generico_html(url)
            metodo = 'api'

        # 2. Força Playwright?
        elif usar_playwright or precisa_playwright(url):
            corridas = scrape_com_playwright(url)
            metodo = 'playwright'

        # 3. Tenta HTML simples
        else:
            domain = urlparse(url).netloc.lower()
            if 'centraldasinscricoes' in domain:
                corridas = scrape_central_inscricoes_html(url)
            else:
                corridas = scrape_generico_html(url)
            metodo = 'html'

            # 4. Fallback Playwright se nada encontrado
            if len(corridas) == 0:
                logger.info(f"HTML vazio, tentando Playwright para {url}")
                corridas = scrape_com_playwright(url)
                metodo = 'playwright_fallback'

        # Deduplicar
        unicas = []
        vistos = set()
        for c in corridas:
            chave = (c['nome_corrida'].lower().strip(), c['data_corrida'])
            if chave not in vistos:
                vistos.add(chave)
                unicas.append(c)

        domain = urlparse(url).netloc.replace('www.', '')
        return {
            'success': True,
            'fonte': domain,
            'url': url,
            'total_encontradas': len(unicas),
            'corridas': unicas,
            'mensagem': f'{len(unicas)} corridas encontradas via {metodo}',
            'metodo': metodo
        }

    except Exception as e:
        logger.error(f"Scraping error for {url}: {e}")
        return {
            'success': False, 'fonte': 'Erro', 'url': url,
            'total_encontradas': 0, 'corridas': [],
            'mensagem': f'Erro: {str(e)}',
            'metodo': 'error'
        }
