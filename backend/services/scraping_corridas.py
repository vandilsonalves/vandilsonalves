"""
Serviço de Scraping de Corridas
Extrai dados de corridas de sites específicos como Ticket Sports, Minhas Inscrições, etc.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Optional
import json

# Headers para simular navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

# Mapeamento de estados por cidade conhecida
CIDADES_ESTADOS = {
    'são paulo': 'SP', 'rio de janeiro': 'RJ', 'belo horizonte': 'MG',
    'salvador': 'BA', 'fortaleza': 'CE', 'brasília': 'DF', 'curitiba': 'PR',
    'manaus': 'AM', 'recife': 'PE', 'porto alegre': 'RS', 'goiânia': 'GO',
    'belém': 'PA', 'guarulhos': 'SP', 'campinas': 'SP', 'são luís': 'MA',
    'maceió': 'AL', 'natal': 'RN', 'campo grande': 'MS', 'teresina': 'PI',
    'joão pessoa': 'PB', 'aracaju': 'SE', 'cuiabá': 'MT', 'florianópolis': 'SC',
    'vitória': 'ES', 'porto velho': 'RO', 'macapá': 'AP', 'boa vista': 'RR',
    'rio branco': 'AC', 'palmas': 'TO'
}


def extrair_estado_da_cidade(cidade: str) -> str:
    """Tenta extrair o estado a partir do nome da cidade"""
    cidade_lower = cidade.lower().strip()
    
    # Verificar se já tem UF no nome (ex: "São Paulo - SP" ou "São Paulo/SP")
    match = re.search(r'[-/]\s*([A-Z]{2})\s*$', cidade)
    if match:
        return match.group(1)
    
    # Procurar na lista de cidades conhecidas
    for cidade_conhecida, uf in CIDADES_ESTADOS.items():
        if cidade_conhecida in cidade_lower:
            return uf
    
    return ''


def limpar_texto(texto: str) -> str:
    """Remove espaços extras e caracteres especiais"""
    if not texto:
        return ''
    return ' '.join(texto.split()).strip()


def extrair_data(texto: str) -> str:
    """Tenta extrair data de um texto no formato YYYY-MM-DD"""
    if not texto:
        return ''
    
    # Padrões de data comuns
    padroes = [
        r'(\d{2})/(\d{2})/(\d{4})',  # DD/MM/YYYY
        r'(\d{2})-(\d{2})-(\d{4})',  # DD-MM-YYYY
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',  # D de Mês de YYYY
    ]
    
    meses = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }
    
    for padrao in padroes[:3]:
        match = re.search(padrao, texto)
        if match:
            grupos = match.groups()
            if len(grupos[0]) == 4:  # YYYY-MM-DD
                return f"{grupos[0]}-{grupos[1]}-{grupos[2]}"
            else:  # DD/MM/YYYY ou DD-MM-YYYY
                return f"{grupos[2]}-{grupos[1]}-{grupos[0]}"
    
    # Padrão com mês por extenso
    match = re.search(padroes[3], texto.lower())
    if match:
        dia, mes_nome, ano = match.groups()
        mes = meses.get(mes_nome, '01')
        return f"{ano}-{mes}-{dia.zfill(2)}"
    
    return ''


class ScraperCorridas:
    """Classe base para scraping de corridas"""
    
    def __init__(self, url: str):
        self.url = url
        self.soup = None
        self.corridas = []
        
    def fetch_page(self) -> bool:
        """Busca a página e cria o objeto BeautifulSoup"""
        try:
            response = requests.get(self.url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'lxml')
            return True
        except Exception as e:
            print(f"Erro ao buscar página: {e}")
            return False
    
    def extrair_corridas(self) -> List[Dict]:
        """Método a ser implementado pelas subclasses"""
        raise NotImplementedError


class ScraperTicketSports(ScraperCorridas):
    """Scraper para Ticket Sports"""
    
    def extrair_corridas(self) -> List[Dict]:
        if not self.fetch_page():
            return []
        
        corridas = []
        
        # Ticket Sports usa cards de eventos
        cards = self.soup.find_all(['div', 'article'], class_=re.compile(r'event|card|item', re.I))
        
        for card in cards:
            try:
                # Tentar extrair dados
                nome = ''
                link = ''
                cidade = ''
                data = ''
                organizador = 'Ticket Sports'
                
                # Nome do evento
                titulo = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name|heading', re.I))
                if titulo:
                    nome = limpar_texto(titulo.get_text())
                    if titulo.name == 'a' and titulo.get('href'):
                        link = titulo.get('href')
                
                # Link alternativo
                if not link:
                    link_elem = card.find('a', href=True)
                    if link_elem:
                        link = link_elem.get('href')
                
                # Cidade/Local
                local = card.find(['span', 'p', 'div'], class_=re.compile(r'location|city|local|place', re.I))
                if local:
                    cidade = limpar_texto(local.get_text())
                
                # Data
                data_elem = card.find(['span', 'p', 'div', 'time'], class_=re.compile(r'date|data|when', re.I))
                if data_elem:
                    data = extrair_data(data_elem.get_text())
                
                if nome and len(nome) > 3:
                    # Completar URL se necessário
                    if link and not link.startswith('http'):
                        base_url = '/'.join(self.url.split('/')[:3])
                        link = base_url + link if link.startswith('/') else base_url + '/' + link
                    
                    uf = extrair_estado_da_cidade(cidade)
                    
                    corridas.append({
                        'nome_corrida': nome,
                        'organizador': organizador,
                        'cidade': cidade.split('-')[0].split('/')[0].strip() if cidade else '',
                        'estado': uf,
                        'pagina_link': link or self.url,
                        'data_corrida': data,
                        'status': 'ativa'
                    })
            except Exception:
                continue
        
        return corridas


class ScraperMinhasInscricoes(ScraperCorridas):
    """Scraper para Minhas Inscrições"""
    
    def extrair_corridas(self) -> List[Dict]:
        if not self.fetch_page():
            return []
        
        corridas = []
        
        # Minhas Inscrições usa estrutura específica
        cards = self.soup.find_all(['div', 'li'], class_=re.compile(r'evento|event|card', re.I))
        
        for card in cards:
            try:
                nome = ''
                link = ''
                cidade = ''
                data = ''
                organizador = 'Minhas Inscrições'
                
                # Buscar título
                titulo = card.find(['h1', 'h2', 'h3', 'h4', 'a'])
                if titulo:
                    nome = limpar_texto(titulo.get_text())
                    if titulo.get('href'):
                        link = titulo.get('href')
                
                # Buscar informações adicionais
                info = card.find_all(['span', 'p', 'div'])
                for elem in info:
                    texto = limpar_texto(elem.get_text())
                    if any(uf in texto for uf in ['SP', 'RJ', 'MG', 'BA', 'CE', 'PR', 'RS', 'SC']):
                        cidade = texto
                    elif re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', texto):
                        data = extrair_data(texto)
                
                if nome and len(nome) > 3:
                    if link and not link.startswith('http'):
                        link = 'https://www.minhasinscricoes.com.br' + link
                    
                    uf = extrair_estado_da_cidade(cidade)
                    
                    corridas.append({
                        'nome_corrida': nome,
                        'organizador': organizador,
                        'cidade': cidade.split('-')[0].split('/')[0].strip() if cidade else '',
                        'estado': uf,
                        'pagina_link': link or self.url,
                        'data_corrida': data,
                        'status': 'ativa'
                    })
            except Exception:
                continue
        
        return corridas


class ScraperGenerico(ScraperCorridas):
    """Scraper genérico para qualquer site"""
    
    def extrair_corridas(self) -> List[Dict]:
        if not self.fetch_page():
            return []
        
        corridas = []
        
        # Tentar encontrar padrões comuns de listagem de eventos
        # Buscar por cards, lista de eventos, tabelas, etc.
        containers = self.soup.find_all(['div', 'article', 'li', 'tr'], 
            class_=re.compile(r'event|corrida|prova|card|item|row', re.I))
        
        if not containers:
            # Tentar buscar por links que parecem ser eventos
            containers = self.soup.find_all('a', href=re.compile(r'event|corrida|prova|inscri', re.I))
        
        for container in containers[:50]:  # Limitar a 50 para evitar muito processamento
            try:
                nome = ''
                link = ''
                cidade = ''
                data = ''
                organizador = ''
                
                # Extrair nome
                titulo = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b'])
                if titulo:
                    nome = limpar_texto(titulo.get_text())
                elif container.name == 'a':
                    nome = limpar_texto(container.get_text())
                
                # Extrair link
                if container.name == 'a':
                    link = container.get('href', '')
                else:
                    link_elem = container.find('a', href=True)
                    if link_elem:
                        link = link_elem.get('href', '')
                
                # Extrair texto completo para buscar cidade e data
                texto_completo = limpar_texto(container.get_text())
                
                # Tentar extrair data
                data = extrair_data(texto_completo)
                
                # Tentar extrair cidade/estado
                match_uf = re.search(r'([A-Za-zÀ-ú\s]+)\s*[-/]\s*([A-Z]{2})', texto_completo)
                if match_uf:
                    cidade = match_uf.group(1).strip()
                    estado = match_uf.group(2)
                else:
                    estado = ''
                    # Procurar menção de cidade conhecida
                    for cidade_conhecida, uf in CIDADES_ESTADOS.items():
                        if cidade_conhecida in texto_completo.lower():
                            cidade = cidade_conhecida.title()
                            estado = uf
                            break
                
                # Filtrar resultados válidos (nome deve ter mais de 5 caracteres e parecer um evento)
                palavras_chave = ['corrida', 'maratona', 'meia', 'km', '5k', '10k', '21k', '42k', 'run', 'marathon']
                if nome and len(nome) > 5 and any(kw in nome.lower() for kw in palavras_chave):
                    if link and not link.startswith('http'):
                        base_url = '/'.join(self.url.split('/')[:3])
                        link = base_url + link if link.startswith('/') else base_url + '/' + link
                    
                    corridas.append({
                        'nome_corrida': nome[:200],  # Limitar tamanho
                        'organizador': organizador or 'A definir',
                        'cidade': cidade[:100] if cidade else '',
                        'estado': estado if estado else extrair_estado_da_cidade(cidade),
                        'pagina_link': link or self.url,
                        'data_corrida': data,
                        'status': 'ativa'
                    })
            except Exception:
                continue
        
        # Remover duplicatas por nome
        corridas_unicas = []
        nomes_vistos = set()
        for corrida in corridas:
            if corrida['nome_corrida'].lower() not in nomes_vistos:
                nomes_vistos.add(corrida['nome_corrida'].lower())
                corridas_unicas.append(corrida)
        
        return corridas_unicas


def fazer_scraping(url: str) -> Dict:
    """
    Função principal que detecta o site e faz o scraping apropriado.
    Retorna um dicionário com status e lista de corridas.
    """
    url_lower = url.lower()
    
    try:
        # Detectar qual scraper usar
        if 'ticketsports' in url_lower:
            scraper = ScraperTicketSports(url)
            fonte = 'Ticket Sports'
        elif 'minhasinscricoes' in url_lower:
            scraper = ScraperMinhasInscricoes(url)
            fonte = 'Minhas Inscrições'
        else:
            scraper = ScraperGenerico(url)
            fonte = 'Genérico'
        
        corridas = scraper.extrair_corridas()
        
        return {
            'success': True,
            'fonte': fonte,
            'url': url,
            'total_encontradas': len(corridas),
            'corridas': corridas,
            'mensagem': f'{len(corridas)} corridas encontradas de {fonte}'
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
