"""
Serviço de Scraping de Corridas - Versão Melhorada
Extrai dados de corridas de sites específicos como Ticket Sports, Minhas Inscrições, Webrun, etc.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict
import json

# Headers para simular navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Mapeamento completo de estados brasileiros
ESTADOS_BR = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}

# Mapeamento de capitais e cidades importantes para UF
CIDADES_ESTADOS = {
    # Capitais
    'rio branco': 'AC', 'maceió': 'AL', 'macapá': 'AP', 'manaus': 'AM',
    'salvador': 'BA', 'fortaleza': 'CE', 'brasília': 'DF', 'vitória': 'ES',
    'goiânia': 'GO', 'são luís': 'MA', 'cuiabá': 'MT', 'campo grande': 'MS',
    'belo horizonte': 'MG', 'belém': 'PA', 'joão pessoa': 'PB', 'curitiba': 'PR',
    'recife': 'PE', 'teresina': 'PI', 'rio de janeiro': 'RJ', 'natal': 'RN',
    'porto alegre': 'RS', 'porto velho': 'RO', 'boa vista': 'RR', 'florianópolis': 'SC',
    'são paulo': 'SP', 'aracaju': 'SE', 'palmas': 'TO',
    # Outras cidades importantes
    'guarulhos': 'SP', 'campinas': 'SP', 'santos': 'SP', 'sorocaba': 'SP',
    'ribeirão preto': 'SP', 'são bernardo': 'SP', 'santo andré': 'SP',
    'niterói': 'RJ', 'petrópolis': 'RJ', 'búzios': 'RJ', 'angra dos reis': 'RJ',
    'contagem': 'MG', 'uberlândia': 'MG', 'juiz de fora': 'MG', 'ouro preto': 'MG',
    'feira de santana': 'BA', 'porto seguro': 'BA', 'ilhéus': 'BA', 'caetité': 'BA',
    'joinville': 'SC', 'blumenau': 'SC', 'balneário camboriú': 'SC',
    'londrina': 'PR', 'maringá': 'PR', 'foz do iguaçu': 'PR',
    'caxias do sul': 'RS', 'pelotas': 'RS', 'gramado': 'RS',
    'olinda': 'PE', 'caruaru': 'PE', 'petrolina': 'PE',
    'caucaia': 'CE', 'juazeiro do norte': 'CE',
    'aparecida de goiânia': 'GO', 'anápolis': 'GO',
    'vila velha': 'ES', 'serra': 'ES', 'cariacica': 'ES',
}

# Meses em português
MESES_PT = {
    'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
    'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
    'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12',
    'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
    'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
    'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
}


def extrair_estado_da_cidade(texto: str) -> str:
    """Tenta extrair o estado (UF) a partir do texto"""
    if not texto:
        return ''
    
    texto_clean = texto.strip()
    
    # Padrão 1: "Cidade - UF" ou "Cidade/UF" ou "Cidade, UF"
    match = re.search(r'[-/,]\s*([A-Z]{2})\s*$', texto_clean)
    if match:
        uf = match.group(1)
        if uf in ESTADOS_BR:
            return uf
    
    # Padrão 2: UF entre parênteses "(UF)"
    match = re.search(r'\(([A-Z]{2})\)', texto_clean)
    if match:
        uf = match.group(1)
        if uf in ESTADOS_BR:
            return uf
    
    # Padrão 3: Buscar cidade conhecida
    texto_lower = texto_clean.lower()
    for cidade, uf in CIDADES_ESTADOS.items():
        if cidade in texto_lower:
            return uf
    
    # Padrão 4: Buscar nome do estado por extenso
    for uf, nome in ESTADOS_BR.items():
        if nome.lower() in texto_lower:
            return uf
    
    return ''


def extrair_cidade(texto: str) -> str:
    """Extrai apenas o nome da cidade, removendo UF e outros sufixos"""
    if not texto:
        return ''
    
    # Remover UF e separadores
    cidade = re.sub(r'\s*[-/,]\s*[A-Z]{2}\s*$', '', texto.strip())
    cidade = re.sub(r'\s*\([A-Z]{2}\)\s*$', '', cidade)
    cidade = re.sub(r'\s*-\s*Brasil\s*$', '', cidade, flags=re.IGNORECASE)
    
    return cidade.strip()


def limpar_texto(texto: str) -> str:
    """Remove espaços extras, quebras de linha e caracteres especiais"""
    if not texto:
        return ''
    # Normalizar espaços e quebras de linha
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def extrair_data(texto: str) -> str:
    """Tenta extrair data de um texto e retorna no formato YYYY-MM-DD"""
    if not texto:
        return ''
    
    texto_lower = texto.lower().strip()
    
    # Padrão 1: DD/MM/YYYY ou DD-MM-YYYY
    match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', texto)
    if match:
        dia, mes, ano = match.groups()
        return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
    
    # Padrão 2: YYYY-MM-DD (ISO)
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', texto)
    if match:
        return match.group(0)
    
    # Padrão 3: "DD de Mês de YYYY" ou "DD Mês YYYY"
    match = re.search(r'(\d{1,2})\s*(?:de\s+)?(\w+)\s*(?:de\s+)?(\d{4})', texto_lower)
    if match:
        dia, mes_nome, ano = match.groups()
        mes = MESES_PT.get(mes_nome[:3], '')
        if mes:
            return f"{ano}-{mes}-{dia.zfill(2)}"
    
    # Padrão 4: "Mês DD, YYYY" (formato americano)
    match = re.search(r'(\w+)\s+(\d{1,2}),?\s*(\d{4})', texto_lower)
    if match:
        mes_nome, dia, ano = match.groups()
        mes = MESES_PT.get(mes_nome[:3], '')
        if mes:
            return f"{ano}-{mes}-{dia.zfill(2)}"
    
    return ''


def eh_corrida_valida(nome: str) -> bool:
    """Verifica se o nome parece ser de uma corrida de rua"""
    if not nome or len(nome) < 3:
        return False
    
    nome_lower = nome.lower().strip()
    
    # Palavras que DEFINITIVAMENTE não são corridas (navegação, login, etc)
    palavras_bloqueadas = [
        'minha conta', 'meu perfil', 'login', 'cadastro', 'cadastre',
        'senha', 'contato', 'sobre', 'política', 'privacidade', 'termos',
        'fale conosco', 'quem somos', 'nossa história', 'empresa especializada',
        'carrinho', 'sacola', 'checkout', 'comprar', 'adicionar',
        'menu', 'home', 'início', 'voltar', 'ver mais', 'saiba mais',
        'leia mais', 'clique aqui', 'acesse', 'entre', 'sair',
        'facebook', 'instagram', 'twitter', 'youtube', 'whatsapp',
        'todos os direitos', 'copyright', 'desenvolvido por'
    ]
    
    for palavra in palavras_bloqueadas:
        if palavra in nome_lower:
            return False
    
    # Se for muito curto, provavelmente não é nome de corrida
    if len(nome_lower) < 8:
        return False
    
    # Palavras-chave que indicam corrida (mais abrangente)
    palavras_positivas = [
        'corrida', 'maratona', 'meia maratona', 'meia-maratona',
        'run', 'running', 'marathon', 'half marathon',
        '5k', '10k', '21k', '42k', '5km', '10km', '21km', '42km',
        'trail', 'trilha', 'circuito', 'volta', 'travessia',
        'night run', 'color run', 'track', 'race', 'prova',
        'desafio', 'challenge', 'km', 'quilômetros', 'quilometros',
        'rústica', 'rustica', 'cross', 'ultra', 'revezamento',
        'etapa', 'xcm'
    ]
    
    # Palavras que indicam que NÃO é corrida
    palavras_negativas = [
        'ciclismo', 'bike', 'bicicleta', 'mtb', 'pedal', 'cycling',
        'natação', 'natacao', 'swim', 'aquathlon', 'triathlon',
        'futebol', 'vôlei', 'volei', 'basquete', 'tênis', 'tenis',
        'workshop', 'curso', 'palestra', 'congresso', 'seminário',
        'show', 'festa', 'balada', 'carnaval', 'réveillon',
        'yoga', 'pilates', 'crossfit', 'musculação'
    ]
    
    # Verificar palavras negativas primeiro
    for palavra in palavras_negativas:
        if palavra in nome_lower:
            return False
    
    # Verificar palavras positivas
    for palavra in palavras_positivas:
        if palavra in nome_lower:
            return True
    
    # Se tiver números seguidos de 'k' ou 'km', provavelmente é corrida
    if re.search(r'\d+\s*k(?:m)?', nome_lower):
        return True
    
    return False


class ScraperBase:
    """Classe base para scrapers"""
    
    def __init__(self, url: str):
        self.url = url
        self.soup = None
        self.fonte = "Genérico"
        
    def fetch_page(self) -> bool:
        """Busca a página e cria o objeto BeautifulSoup"""
        try:
            response = requests.get(self.url, headers=HEADERS, timeout=30, verify=True)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'lxml')
            return True
        except requests.exceptions.SSLError:
            # Tentar sem verificação SSL
            try:
                response = requests.get(self.url, headers=HEADERS, timeout=30, verify=False)
                response.raise_for_status()
                self.soup = BeautifulSoup(response.content, 'lxml')
                return True
            except Exception:
                return False
        except Exception:
            return False
    
    def extrair_corridas(self) -> List[Dict]:
        """Método a ser implementado pelas subclasses"""
        raise NotImplementedError
    
    def criar_corrida(self, nome: str, organizador: str, cidade: str, estado: str, 
                      link: str, data: str) -> Dict:
        """Cria um dicionário de corrida padronizado"""
        
        # Limpar e validar dados
        nome = limpar_texto(nome)[:200]
        organizador = limpar_texto(organizador)[:100] or self.fonte
        cidade = extrair_cidade(cidade)[:100]
        estado = estado or extrair_estado_da_cidade(cidade)
        
        # Garantir que link é absoluto
        if link and not link.startswith('http'):
            base_url = '/'.join(self.url.split('/')[:3])
            link = base_url + (link if link.startswith('/') else '/' + link)
        
        return {
            'nome_corrida': nome,
            'organizador': organizador,
            'cidade': cidade,
            'estado': estado.upper()[:2] if estado else '',
            'pagina_link': link or self.url,
            'data_corrida': data,
            'status': 'ativa'
        }


class ScraperTicketSports(ScraperBase):
    """Scraper otimizado para Ticket Sports"""
    
    def __init__(self, url: str):
        super().__init__(url)
        self.fonte = "Ticket Sports"
    
    def extrair_corridas(self) -> List[Dict]:
        if not self.fetch_page():
            return []
        
        corridas = []
        
        # Ticket Sports usa cards com classe específica
        cards = self.soup.find_all('div', class_=re.compile(r'event|card|item|produto', re.I))
        
        for card in cards:
            try:
                nome = ''
                link = ''
                cidade = ''
                data = ''
                organizador = self.fonte
                
                # Buscar título/nome
                for tag in ['h2', 'h3', 'h4', 'a']:
                    titulo = card.find(tag, class_=re.compile(r'title|name|nome', re.I))
                    if titulo:
                        nome = limpar_texto(titulo.get_text())
                        if titulo.name == 'a' and titulo.get('href'):
                            link = titulo.get('href')
                        break
                
                if not nome:
                    link_elem = card.find('a', href=True)
                    if link_elem:
                        nome = limpar_texto(link_elem.get_text())
                        link = link_elem.get('href')
                
                # Buscar local/cidade
                local = card.find(['span', 'p', 'div'], class_=re.compile(r'local|city|cidade|location', re.I))
                if local:
                    cidade = limpar_texto(local.get_text())
                
                # Buscar data
                data_elem = card.find(['span', 'time', 'p'], class_=re.compile(r'date|data|when', re.I))
                if data_elem:
                    data = extrair_data(data_elem.get_text())
                
                # Validar e adicionar
                if nome and eh_corrida_valida(nome):
                    corridas.append(self.criar_corrida(nome, organizador, cidade, '', link, data))
                    
            except Exception:
                continue
        
        return corridas


class ScraperMinhasInscricoes(ScraperBase):
    """Scraper otimizado para Minhas Inscrições"""
    
    def __init__(self, url: str):
        super().__init__(url)
        self.fonte = "Minhas Inscrições"
    
    def extrair_corridas(self) -> List[Dict]:
        if not self.fetch_page():
            return []
        
        corridas = []
        
        # Buscar cards de eventos
        cards = self.soup.find_all(['div', 'article', 'li'], class_=re.compile(r'evento|event|card|item', re.I))
        
        for card in cards:
            try:
                nome = ''
                link = ''
                cidade = ''
                data = ''
                estado = ''
                
                # Título
                titulo = card.find(['h1', 'h2', 'h3', 'h4', 'a'])
                if titulo:
                    nome = limpar_texto(titulo.get_text())
                    if titulo.get('href'):
                        link = titulo.get('href')
                
                # Extrair informações do texto completo
                texto = limpar_texto(card.get_text())
                
                # Buscar UF no texto
                match_uf = re.search(r'([A-Za-zÀ-ú\s]+)\s*[-/]\s*([A-Z]{2})', texto)
                if match_uf:
                    cidade = match_uf.group(1).strip()
                    estado = match_uf.group(2)
                
                # Buscar data
                data = extrair_data(texto)
                
                if nome and eh_corrida_valida(nome):
                    if link and not link.startswith('http'):
                        link = 'https://www.minhasinscricoes.com.br' + link
                    
                    corridas.append(self.criar_corrida(nome, self.fonte, cidade, estado, link, data))
                    
            except Exception:
                continue
        
        return corridas


class ScraperWebrun(ScraperBase):
    """Scraper otimizado para Webrun"""
    
    def __init__(self, url: str):
        super().__init__(url)
        self.fonte = "Webrun"
    
    def extrair_corridas(self) -> List[Dict]:
        if not self.fetch_page():
            return []
        
        corridas = []
        
        # Webrun lista eventos em tabelas ou divs
        eventos = self.soup.find_all(['tr', 'div', 'article'], class_=re.compile(r'event|corrida|prova|calendario', re.I))
        
        if not eventos:
            # Tentar buscar links de eventos
            eventos = self.soup.find_all('a', href=re.compile(r'evento|corrida|prova', re.I))
        
        for evento in eventos:
            try:
                nome = ''
                link = ''
                cidade = ''
                data = ''
                
                if evento.name == 'a':
                    nome = limpar_texto(evento.get_text())
                    link = evento.get('href', '')
                else:
                    titulo = evento.find(['a', 'h2', 'h3', 'td'])
                    if titulo:
                        nome = limpar_texto(titulo.get_text())
                        if titulo.name == 'a':
                            link = titulo.get('href', '')
                
                # Extrair cidade e data do texto
                texto = limpar_texto(evento.get_text())
                data = extrair_data(texto)
                
                # Buscar cidade
                for cidade_conhecida, uf in CIDADES_ESTADOS.items():
                    if cidade_conhecida in texto.lower():
                        cidade = cidade_conhecida.title()
                        break
                
                if nome and eh_corrida_valida(nome):
                    if link and not link.startswith('http'):
                        link = 'https://www.webrun.com.br' + link
                    
                    corridas.append(self.criar_corrida(nome, self.fonte, cidade, '', link, data))
                    
            except Exception:
                continue
        
        return corridas


class ScraperSympla(ScraperBase):
    """Scraper para Sympla"""
    
    def __init__(self, url: str):
        super().__init__(url)
        self.fonte = "Sympla"
    
    def extrair_corridas(self) -> List[Dict]:
        if not self.fetch_page():
            return []
        
        corridas = []
        
        # Sympla usa cards com estrutura específica
        cards = self.soup.find_all(['div', 'article'], class_=re.compile(r'event|card|EventCard', re.I))
        
        for card in cards:
            try:
                nome = ''
                link = ''
                cidade = ''
                data = ''
                
                # Título
                titulo = card.find(['h2', 'h3', 'a'], class_=re.compile(r'title|name', re.I))
                if titulo:
                    nome = limpar_texto(titulo.get_text())
                    if titulo.get('href'):
                        link = titulo.get('href')
                
                # Local
                local = card.find(class_=re.compile(r'location|local|venue', re.I))
                if local:
                    cidade = limpar_texto(local.get_text())
                
                # Data
                data_elem = card.find(class_=re.compile(r'date|data', re.I))
                if data_elem:
                    data = extrair_data(data_elem.get_text())
                
                if nome and eh_corrida_valida(nome):
                    if link and not link.startswith('http'):
                        link = 'https://www.sympla.com.br' + link
                    
                    corridas.append(self.criar_corrida(nome, self.fonte, cidade, '', link, data))
                    
            except Exception:
                continue
        
        return corridas


class ScraperGenerico(ScraperBase):
    """Scraper genérico melhorado para qualquer site"""
    
    def __init__(self, url: str):
        super().__init__(url)
        self.fonte = "Site Genérico"
    
    def extrair_corridas(self) -> List[Dict]:
        if not self.fetch_page():
            return []
        
        corridas = []
        nomes_vistos = set()
        
        # Estratégia 1: Buscar todos os links da página
        todos_links = self.soup.find_all('a', href=True)
        
        for link in todos_links:
            try:
                texto = limpar_texto(link.get_text())
                href = link.get('href', '')
                
                # Pular links muito curtos ou de navegação
                if len(texto) < 5 or texto.lower() in ['home', 'início', 'voltar', 'ver mais', 'saiba mais']:
                    continue
                
                # Verificar se parece ser uma corrida
                if eh_corrida_valida(texto):
                    nome_lower = texto.lower()
                    if nome_lower not in nomes_vistos:
                        nomes_vistos.add(nome_lower)
                        
                        # Tentar extrair cidade do texto do link ou elementos próximos
                        cidade = ''
                        estado = ''
                        data = ''
                        
                        # Buscar elementos irmãos ou pais para informações adicionais
                        parent = link.parent
                        if parent:
                            texto_contexto = limpar_texto(parent.get_text())
                            data = extrair_data(texto_contexto)
                            
                            # Buscar cidade/estado
                            match_local = re.search(r'([A-Za-zÀ-ú\s]+)\s*[-/,]\s*([A-Z]{2})', texto_contexto)
                            if match_local:
                                cidade = match_local.group(1).strip()[:30]
                                estado = match_local.group(2)
                            else:
                                for cidade_conhecida, uf in CIDADES_ESTADOS.items():
                                    if cidade_conhecida in texto_contexto.lower():
                                        cidade = cidade_conhecida.title()
                                        estado = uf
                                        break
                        
                        corridas.append(self.criar_corrida(texto, '', cidade, estado, href, data))
            except Exception:
                continue
        
        # Estratégia 2: Buscar containers de eventos
        containers = self.soup.find_all(['div', 'article', 'li', 'tr', 'section'], 
            class_=re.compile(r'event|corrida|prova|card|item|row|entry|post|produto|calendario', re.I))
        
        for container in containers[:100]:
            try:
                # Buscar título em tags de heading ou links
                nome = ''
                link = ''
                
                for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'a', 'strong', 'b', 'span']:
                    titulo = container.find(tag)
                    if titulo:
                        texto_titulo = limpar_texto(titulo.get_text())
                        if len(texto_titulo) > 3 and texto_titulo.lower() not in nomes_vistos:
                            if eh_corrida_valida(texto_titulo):
                                nome = texto_titulo
                                if titulo.name == 'a':
                                    link = titulo.get('href', '')
                                break
                
                if not nome:
                    continue
                
                nome_lower = nome.lower()
                if nome_lower in nomes_vistos:
                    continue
                
                nomes_vistos.add(nome_lower)
                
                # Extrair texto completo para buscar cidade e data
                texto = limpar_texto(container.get_text())
                data = extrair_data(texto)
                
                # Buscar cidade/estado
                estado = ''
                cidade = ''
                match_local = re.search(r'([A-Za-zÀ-ú\s]+)\s*[-/,]\s*([A-Z]{2})', texto)
                if match_local:
                    cidade = match_local.group(1).strip()
                    estado = match_local.group(2)
                else:
                    for cidade_conhecida, uf in CIDADES_ESTADOS.items():
                        if cidade_conhecida in texto.lower():
                            cidade = cidade_conhecida.title()
                            estado = uf
                            break
                
                # Verificar novamente se é corrida válida antes de adicionar
                if eh_corrida_valida(nome):
                    corridas.append(self.criar_corrida(nome, '', cidade, estado, link, data))
                    
            except Exception:
                continue
        
        # Estratégia 3: Buscar texto que parece ser nome de corrida em qualquer lugar
        texto_completo = self.soup.get_text()
        
        # Padrões comuns de nomes de corridas
        padroes_corrida = [
            r'(\d+[ªºa]?\s*(?:corrida|maratona|meia|etapa)[^,\n]{5,50})',
            r'((?:corrida|maratona|meia|circuito|desafio)\s+[^,\n]{5,50})',
            r'(\w+\s+(?:run|running|race)\s*\d*k?m?)',
        ]
        
        for padrao in padroes_corrida:
            matches = re.findall(padrao, texto_completo, re.IGNORECASE)
            for match in matches[:20]:
                nome = limpar_texto(match)
                nome_lower = nome.lower()
                if nome_lower not in nomes_vistos and eh_corrida_valida(nome):
                    nomes_vistos.add(nome_lower)
                    corridas.append(self.criar_corrida(nome, '', '', '', '', ''))
        
        return corridas


def detectar_scraper(url: str) -> ScraperBase:
    """Detecta o scraper apropriado baseado na URL"""
    url_lower = url.lower()
    
    if 'ticketsports' in url_lower:
        return ScraperTicketSports(url)
    elif 'minhasinscricoes' in url_lower:
        return ScraperMinhasInscricoes(url)
    elif 'webrun' in url_lower:
        return ScraperWebrun(url)
    elif 'sympla' in url_lower:
        return ScraperSympla(url)
    else:
        return ScraperGenerico(url)


def fazer_scraping(url: str, usar_playwright: bool = False) -> Dict:
    """
    Função principal que detecta o site e faz o scraping apropriado.
    Retorna um dicionário com status e lista de corridas.
    
    Args:
        url: URL do site de corridas
        usar_playwright: Se True, usa Playwright para sites com JavaScript pesado
    """
    
    # Validar URL
    if not url or not url.startswith(('http://', 'https://')):
        return {
            'success': False,
            'fonte': 'Erro',
            'url': url,
            'total_encontradas': 0,
            'corridas': [],
            'mensagem': 'URL inválida. Use uma URL completa (http:// ou https://)'
        }
    
    try:
        # Se usar_playwright=True, tenta primeiro com Playwright
        if usar_playwright:
            resultado = fazer_scraping_playwright(url)
            if resultado['success'] and resultado['total_encontradas'] > 0:
                return resultado
        
        # Scraping normal com requests/BeautifulSoup
        scraper = detectar_scraper(url)
        corridas = scraper.extrair_corridas()
        
        # Remover duplicatas finais
        corridas_unicas = []
        nomes_vistos = set()
        for corrida in corridas:
            chave = (corrida['nome_corrida'].lower(), corrida['data_corrida'])
            if chave not in nomes_vistos:
                nomes_vistos.add(chave)
                corridas_unicas.append(corrida)
        
        # Se não encontrou nada e não tentou Playwright ainda, tenta com Playwright
        if len(corridas_unicas) == 0 and not usar_playwright:
            resultado_pw = fazer_scraping_playwright(url)
            if resultado_pw['success'] and resultado_pw['total_encontradas'] > 0:
                return resultado_pw
        
        return {
            'success': True,
            'fonte': scraper.fonte,
            'url': url,
            'total_encontradas': len(corridas_unicas),
            'corridas': corridas_unicas,
            'mensagem': f'{len(corridas_unicas)} corridas encontradas de {scraper.fonte}'
        }
    
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'fonte': 'Erro',
            'url': url,
            'total_encontradas': 0,
            'corridas': [],
            'mensagem': 'Timeout: O site demorou muito para responder'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'fonte': 'Erro',
            'url': url,
            'total_encontradas': 0,
            'corridas': [],
            'mensagem': 'Erro de conexão: Não foi possível acessar o site'
        }
    except Exception as e:
        return {
            'success': False,
            'fonte': 'Erro',
            'url': url,
            'total_encontradas': 0,
            'corridas': [],
            'mensagem': f'Erro ao fazer scraping: {str(e)}'
        }


def fazer_scraping_playwright(url: str) -> Dict:
    """
    Faz scraping usando Playwright para sites que dependem de JavaScript.
    Útil para sites modernos com SPAs ou renderização dinâmica.
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Configurar timeouts
            page.set_default_timeout(30000)
            
            # Navegar e aguardar carregamento
            page.goto(url, wait_until='networkidle')
            
            # Aguardar um pouco mais para JavaScript carregar
            page.wait_for_timeout(2000)
            
            # Obter HTML renderizado
            html_content = page.content()
            browser.close()
            
            # Processar com BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Tentar extrair corridas do HTML renderizado
            corridas = extrair_corridas_html_generico(soup, url)
            
            return {
                'success': True,
                'fonte': 'Playwright (JavaScript)',
                'url': url,
                'total_encontradas': len(corridas),
                'corridas': corridas,
                'mensagem': f'{len(corridas)} corridas encontradas via Playwright'
            }
            
    except ImportError:
        return {
            'success': False,
            'fonte': 'Erro',
            'url': url,
            'total_encontradas': 0,
            'corridas': [],
            'mensagem': 'Playwright não está instalado. Use: pip install playwright && playwright install chromium'
        }
    except Exception as e:
        return {
            'success': False,
            'fonte': 'Erro',
            'url': url,
            'total_encontradas': 0,
            'corridas': [],
            'mensagem': f'Erro no scraping com Playwright: {str(e)}'
        }


def extrair_corridas_html_generico(soup: BeautifulSoup, url: str) -> List[Dict]:
    """
    Extrator genérico de corridas para HTML renderizado por JavaScript.
    Tenta encontrar padrões comuns de eventos/corridas.
    """
    corridas = []
    
    # Padrões comuns de containers de eventos
    event_selectors = [
        'div[class*="event"]',
        'div[class*="corrida"]',
        'div[class*="race"]',
        'article',
        'div[class*="card"]',
        'li[class*="event"]',
        'div[class*="item"]',
    ]
    
    for selector in event_selectors:
        elementos = soup.select(selector)
        for elem in elementos:
            corrida = extrair_info_evento_generico(elem, url)
            if corrida and corrida.get('nome_corrida'):
                corridas.append(corrida)
    
    # Remover duplicatas
    corridas_unicas = []
    nomes_vistos = set()
    for corrida in corridas:
        chave = corrida['nome_corrida'].lower()
        if chave not in nomes_vistos and len(corrida['nome_corrida']) > 5:
            nomes_vistos.add(chave)
            corridas_unicas.append(corrida)
    
    return corridas_unicas[:50]  # Limitar a 50 resultados


def extrair_info_evento_generico(elem, url: str) -> Dict:
    """Tenta extrair informações de um elemento HTML genérico"""
    
    # Buscar nome do evento
    nome = ''
    for tag in ['h1', 'h2', 'h3', 'h4', 'a', 'span[class*="title"]', 'div[class*="title"]']:
        nome_elem = elem.select_one(tag)
        if nome_elem and nome_elem.get_text(strip=True):
            nome = nome_elem.get_text(strip=True)
            if len(nome) > 5:
                break
    
    if not nome or len(nome) < 5:
        return None
    
    # Buscar data
    data = ''
    texto_completo = elem.get_text()
    
    # Padrões de data comuns
    data_patterns = [
        r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})',  # DD/MM/YYYY
        r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',   # DD de MES de YYYY
        r'(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})',   # YYYY-MM-DD
    ]
    
    for pattern in data_patterns:
        match = re.search(pattern, texto_completo, re.IGNORECASE)
        if match:
            groups = match.groups()
            try:
                if len(groups[0]) == 4:  # YYYY-MM-DD
                    data = f"{groups[2]}/{groups[1]}/{groups[0]}"
                elif groups[1].isalpha():  # DD de MES de YYYY
                    mes = MESES_PT.get(groups[1].lower(), '01')
                    data = f"{groups[0].zfill(2)}/{mes}/{groups[2]}"
                else:  # DD/MM/YYYY
                    data = f"{groups[0].zfill(2)}/{groups[1].zfill(2)}/{groups[2]}"
                break
            except:
                pass
    
    # Buscar cidade/estado
    cidade = ''
    estado = ''
    local_elem = elem.select_one('[class*="local"], [class*="location"], [class*="cidade"]')
    if local_elem:
        local_texto = local_elem.get_text(strip=True)
        estado = extrair_estado_da_cidade(local_texto)
        cidade = local_texto.split('-')[0].strip() if '-' in local_texto else local_texto
    
    # Buscar link
    link = ''
    link_elem = elem.select_one('a[href]')
    if link_elem:
        href = link_elem.get('href', '')
        if href.startswith('/'):
            from urllib.parse import urljoin
            link = urljoin(url, href)
        elif href.startswith('http'):
            link = href
    
    return {
        'nome_corrida': nome[:200],
        'data_corrida': data,
        'cidade': cidade[:100] if cidade else '',
        'estado': estado,
        'distancias': [],
        'link_inscricao': link,
        'fonte': 'Playwright'
    }
