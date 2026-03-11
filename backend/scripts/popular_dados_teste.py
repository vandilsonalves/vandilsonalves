#!/usr/bin/env python3
"""
Script para popular dados de teste - 220 atletas + 40 corridas
"""

import asyncio
import random
import uuid
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv('/app/backend/.env')

# Conexão com MongoDB
client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
db = client[os.environ.get('DB_NAME', 'ranking_run')]

# Dados para geração
ESTADOS = ['SP', 'RJ', 'MG', 'BA', 'PR', 'RS', 'SC', 'PE', 'CE', 'GO', 'DF', 'ES', 'MA', 'PA', 'PB']

CIDADES = {
    'SP': ['São Paulo', 'Campinas', 'Santos', 'Ribeirão Preto', 'Sorocaba'],
    'RJ': ['Rio de Janeiro', 'Niterói', 'Petrópolis', 'Nova Iguaçu'],
    'MG': ['Belo Horizonte', 'Uberlândia', 'Juiz de Fora', 'Contagem'],
    'BA': ['Salvador', 'Feira de Santana', 'Vitória da Conquista'],
    'PR': ['Curitiba', 'Londrina', 'Maringá', 'Foz do Iguaçu'],
    'RS': ['Porto Alegre', 'Caxias do Sul', 'Pelotas', 'Canoas'],
    'SC': ['Florianópolis', 'Joinville', 'Blumenau', 'Itajaí'],
    'PE': ['Recife', 'Olinda', 'Jaboatão', 'Caruaru'],
    'CE': ['Fortaleza', 'Juazeiro do Norte', 'Sobral'],
    'GO': ['Goiânia', 'Aparecida de Goiânia', 'Anápolis'],
    'DF': ['Brasília', 'Taguatinga', 'Ceilândia'],
    'ES': ['Vitória', 'Vila Velha', 'Serra', 'Cariacica'],
    'MA': ['São Luís', 'Imperatriz', 'Caxias'],
    'PA': ['Belém', 'Ananindeua', 'Santarém'],
    'PB': ['João Pessoa', 'Campina Grande', 'Santa Rita']
}

NOMES_MASCULINOS = [
    'João', 'Pedro', 'Lucas', 'Gabriel', 'Rafael', 'Matheus', 'Bruno', 'Felipe',
    'Gustavo', 'Leonardo', 'Ricardo', 'André', 'Carlos', 'Fernando', 'Eduardo',
    'Thiago', 'Daniel', 'Marcelo', 'Rodrigo', 'Alexandre', 'Paulo', 'Roberto',
    'Diego', 'Vinicius', 'Henrique', 'Caio', 'Victor', 'Arthur', 'Miguel', 'Enzo'
]

NOMES_FEMININOS = [
    'Maria', 'Ana', 'Julia', 'Mariana', 'Beatriz', 'Larissa', 'Amanda', 'Camila',
    'Fernanda', 'Patricia', 'Carolina', 'Leticia', 'Gabriela', 'Isabela', 'Rafaela',
    'Bruna', 'Juliana', 'Natalia', 'Vanessa', 'Priscila', 'Aline', 'Renata',
    'Daniela', 'Adriana', 'Monica', 'Paula', 'Tatiana', 'Carla', 'Sandra', 'Helena'
]

SOBRENOMES = [
    'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Almeida',
    'Pereira', 'Lima', 'Gomes', 'Costa', 'Ribeiro', 'Martins', 'Carvalho',
    'Araújo', 'Melo', 'Barbosa', 'Rocha', 'Cardoso', 'Correia', 'Nascimento',
    'Dias', 'Moreira', 'Monteiro', 'Mendes', 'Teixeira', 'Vieira', 'Nunes'
]

ASSESSORIAS = [
    'Runners Elite SP', 'Maratona Club RJ', 'Corredores do Sul PR', 'Nordeste Running PE',
    'Centro-Oeste Runners GO', 'Atletas MG', 'Bahia Runners BA', 'Catarinense Running SC',
    'Gaúchos Running RS', 'Capixaba Runners ES', 'Ceará Athletics CE', 'Maranhão Running MA',
    'Pará Running PA', 'Paraíba Runners PB', 'Brasília Running DF'
]

FAIXAS_ETARIAS = ['18-29', '30-39', '40-49', '50-59', '60+']
ETNIAS = ['Branca', 'Negra', 'Parda', 'Indígena', 'Amarela']

EVENTOS_CORRIDA = [
    'Maratona de São Paulo 2025', 'Meia Maratona do Rio 2025', 'Corrida de Reis 2025',
    '10K Night Run', '5K Sunset Run', 'Trail Run Serra da Mantiqueira',
    'Maratona de Curitiba', 'Corrida Noturna Porto Alegre', 'Meia de Brasília',
    '10K Beira Mar', 'Maratona do Nordeste', 'Corrida do Pantanal',
    '21K Floripa', 'Meia de BH', 'Corrida da Independência'
]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def gerar_tempo(distancia: str) -> str:
    """Gera tempo de corrida baseado na distância"""
    tempos = {
        '5KM': (18, 35),    # 18-35 min
        '10KM': (38, 70),   # 38-70 min
        '21KM': (85, 150),  # 1h25 - 2h30
        '42KM': (180, 330)  # 3h - 5h30
    }
    min_t, max_t = tempos.get(distancia, (30, 60))
    minutos = random.randint(min_t, max_t)
    horas = minutos // 60
    mins = minutos % 60
    segundos = random.randint(0, 59)
    if horas > 0:
        return f"{horas}:{mins:02d}:{segundos:02d}"
    return f"{mins}:{segundos:02d}"

def gerar_pace() -> str:
    """Gera pace para Povão (min/km)"""
    minutos = random.randint(5, 9)
    segundos = random.randint(0, 59)
    return f"{minutos}:{segundos:02d}"

async def criar_atleta(nome: str, genero: str, categoria: str, modalidade: str, 
                       assessoria: str, estado: str, is_dono: bool = False):
    """Cria um atleta no banco"""
    cidade = random.choice(CIDADES.get(estado, ['Capital']))
    email = f"{nome.lower().replace(' ', '_')}_{random.randint(100,999)}@email.com"
    
    atleta = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "email": email,
        "password_hash": hash_password("senha123"),
        "role": "dono_assessoria" if is_dono else "atleta",
        "genero": genero,
        "categoria": categoria,  # normal, pcd, cadeirante
        "modalidade_usuario": modalidade,  # profissional_amador ou povao_pace_livre
        "equipe": assessoria,
        "estado": estado,
        "cidade": cidade,
        "faixa_etaria": random.choice(FAIXAS_ETARIAS),
        "etnia": random.choice(ETNIAS),
        "data_nascimento": f"{random.randint(1965, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "telefone": f"({random.randint(11,99)}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
        "foto_url": f"https://ui-avatars.com/api/?name={nome.replace(' ', '+')}&size=128&background=random&bold=true",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "aprovado": True,
        "ativo": True
    }
    
    await db.usuarios.insert_one(atleta)
    return atleta

async def criar_corrida(atleta_id: str, atleta_nome: str, distancia: str, 
                        evento: str, estado: str, aprovada: bool = True):
    """Cria uma corrida para o atleta"""
    data = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
    
    corrida = {
        "id": str(uuid.uuid4()),
        "usuario_id": atleta_id,
        "nome_atleta": atleta_nome,
        "nome_evento": evento,
        "data": data,
        "distancia": distancia,
        "tempo": gerar_tempo(distancia),
        "colocacao_geral": random.randint(1, 500),
        "colocacao_faixa": random.randint(1, 50),
        "colocacao_sexo": random.randint(1, 200),
        "pontos": random.randint(10, 100),
        "cidade": random.choice(CIDADES.get(estado, ['Capital'])),
        "estado": estado,
        "modalidade": "profissional_amador",
        "ano": 2025,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    if aprovada:
        await db.corridas.insert_one(corrida)
    else:
        corrida["status"] = "pendente"
        corrida["foto_podio_url"] = ""
        await db.resultados_pendentes.insert_one(corrida)
    
    return corrida

async def criar_corrida_povao(atleta_id: str, atleta_nome: str, estado: str):
    """Cria uma corrida para atleta Povão"""
    data = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
    distancia = random.choice([5, 10, 15, 20, 25])  # km
    
    corrida = {
        "id": str(uuid.uuid4()),
        "usuario_id": atleta_id,
        "nome_atleta": atleta_nome,
        "nome_evento": f"Treino Livre - {random.choice(['Parque', 'Orla', 'Pista', 'Rua'])}",
        "data": data,
        "distancia": f"{distancia}KM",
        "pace": gerar_pace(),
        "pontos_povao": distancia,  # 1 ponto por km
        "cidade": random.choice(CIDADES.get(estado, ['Capital'])),
        "estado": estado,
        "modalidade": "povao_pace_livre",
        "ano": 2025,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.corridas.insert_one(corrida)
    return corrida

async def main():
    print("=" * 60)
    print("POPULANDO DADOS DE TESTE")
    print("=" * 60)
    
    # Limpar dados de teste anteriores (opcional)
    # await db.usuarios.delete_many({"email": {"$regex": "@email.com$"}})
    
    atletas_criados = []
    contador = {"total": 0}
    
    # Distribuir assessorias por estado
    assessorias_por_estado = {ass: ESTADOS[i % len(ESTADOS)] for i, ass in enumerate(ASSESSORIAS)}
    
    # 15 Donos de Assessoria (um para cada assessoria)
    print("\n📋 Criando 15 Donos de Assessoria...")
    donos = []
    for i, assessoria in enumerate(ASSESSORIAS):
        estado = assessorias_por_estado[assessoria]
        genero = 'M' if i % 2 == 0 else 'F'
        nome = random.choice(NOMES_MASCULINOS if genero == 'M' else NOMES_FEMININOS) + ' ' + random.choice(SOBRENOMES)
        atleta = await criar_atleta(nome, genero, 'normal', 'profissional_amador', assessoria, estado, is_dono=True)
        donos.append(atleta)
        atletas_criados.append(atleta)
        contador["total"] += 1
    print(f"   ✓ {len(donos)} donos de assessoria criados")
    
    # 30 Atletas Masculino Profissional/Amador
    print("\n👨 Criando 30 Atletas Masculino Profissional/Amador...")
    for i in range(30):
        nome = random.choice(NOMES_MASCULINOS) + ' ' + random.choice(SOBRENOMES)
        assessoria = random.choice(ASSESSORIAS)
        estado = assessorias_por_estado[assessoria]
        atleta = await criar_atleta(nome, 'M', 'normal', 'profissional_amador', assessoria, estado)
        atletas_criados.append(atleta)
        contador["total"] += 1
    print(f"   ✓ 30 atletas masculinos criados")
    
    # 30 Atletas Feminino Profissional/Amador
    print("\n👩 Criando 30 Atletas Feminino Profissional/Amador...")
    for i in range(30):
        nome = random.choice(NOMES_FEMININOS) + ' ' + random.choice(SOBRENOMES)
        assessoria = random.choice(ASSESSORIAS)
        estado = assessorias_por_estado[assessoria]
        atleta = await criar_atleta(nome, 'F', 'normal', 'profissional_amador', assessoria, estado)
        atletas_criados.append(atleta)
        contador["total"] += 1
    print(f"   ✓ 30 atletas femininas criadas")
    
    # 30 Atletas PCD Masculino
    print("\n♿👨 Criando 30 Atletas PCD Masculino...")
    for i in range(30):
        nome = random.choice(NOMES_MASCULINOS) + ' ' + random.choice(SOBRENOMES)
        assessoria = random.choice(ASSESSORIAS)
        estado = assessorias_por_estado[assessoria]
        atleta = await criar_atleta(nome, 'M', 'pcd', 'profissional_amador', assessoria, estado)
        atletas_criados.append(atleta)
        contador["total"] += 1
    print(f"   ✓ 30 atletas PCD masculinos criados")
    
    # 30 Atletas PCD Feminino
    print("\n♿👩 Criando 30 Atletas PCD Feminino...")
    for i in range(30):
        nome = random.choice(NOMES_FEMININOS) + ' ' + random.choice(SOBRENOMES)
        assessoria = random.choice(ASSESSORIAS)
        estado = assessorias_por_estado[assessoria]
        atleta = await criar_atleta(nome, 'F', 'pcd', 'profissional_amador', assessoria, estado)
        atletas_criados.append(atleta)
        contador["total"] += 1
    print(f"   ✓ 30 atletas PCD femininas criadas")
    
    # 10 Atletas Cadeirante Masculino
    print("\n🦽👨 Criando 10 Atletas Cadeirante Masculino...")
    for i in range(10):
        nome = random.choice(NOMES_MASCULINOS) + ' ' + random.choice(SOBRENOMES)
        assessoria = random.choice(ASSESSORIAS)
        estado = assessorias_por_estado[assessoria]
        atleta = await criar_atleta(nome, 'M', 'cadeirante', 'profissional_amador', assessoria, estado)
        atletas_criados.append(atleta)
        contador["total"] += 1
    print(f"   ✓ 10 atletas cadeirantes masculinos criados")
    
    # 10 Atletas Cadeirante Feminino
    print("\n🦽👩 Criando 10 Atletas Cadeirante Feminino...")
    for i in range(10):
        nome = random.choice(NOMES_FEMININOS) + ' ' + random.choice(SOBRENOMES)
        assessoria = random.choice(ASSESSORIAS)
        estado = assessorias_por_estado[assessoria]
        atleta = await criar_atleta(nome, 'F', 'cadeirante', 'profissional_amador', assessoria, estado)
        atletas_criados.append(atleta)
        contador["total"] += 1
    print(f"   ✓ 10 atletas cadeirantes femininas criadas")
    
    # 40 Atletas Masculino Povão
    print("\n🏃👨 Criando 40 Atletas Masculino Povão...")
    for i in range(40):
        nome = random.choice(NOMES_MASCULINOS) + ' ' + random.choice(SOBRENOMES)
        assessoria = random.choice(ASSESSORIAS) if i < 35 else "INDIVIDUAL"
        estado = assessorias_por_estado.get(assessoria, random.choice(ESTADOS))
        atleta = await criar_atleta(nome, 'M', 'normal', 'povao_pace_livre', assessoria, estado)
        atletas_criados.append(atleta)
        contador["total"] += 1
    print(f"   ✓ 40 atletas povão masculinos criados")
    
    # 40 Atletas Feminino Povão
    print("\n🏃👩 Criando 40 Atletas Feminino Povão...")
    for i in range(40):
        nome = random.choice(NOMES_FEMININOS) + ' ' + random.choice(SOBRENOMES)
        assessoria = random.choice(ASSESSORIAS) if i < 35 else "INDIVIDUAL"
        estado = assessorias_por_estado.get(assessoria, random.choice(ESTADOS))
        atleta = await criar_atleta(nome, 'F', 'normal', 'povao_pace_livre', assessoria, estado)
        atletas_criados.append(atleta)
        contador["total"] += 1
    print(f"   ✓ 40 atletas povão femininas criadas")
    
    print(f"\n✅ Total de atletas criados: {contador['total']}")
    
    # Criar 40 corridas
    print("\n🏁 Criando 40 corridas...")
    corridas_criadas = 0
    
    # Selecionar atletas para corridas (apenas profissional_amador)
    atletas_prof = [a for a in atletas_criados if a['modalidade_usuario'] == 'profissional_amador']
    
    for i in range(40):
        atleta = random.choice(atletas_prof)
        evento = random.choice(EVENTOS_CORRIDA)
        distancia = random.choice(['5KM', '10KM', '21KM', '42KM'])
        aprovada = i < 30  # 30 aprovadas, 10 pendentes
        
        await criar_corrida(
            atleta['id'], 
            atleta['nome'], 
            distancia, 
            evento, 
            atleta['estado'],
            aprovada
        )
        corridas_criadas += 1
    
    print(f"   ✓ 30 corridas aprovadas criadas")
    print(f"   ✓ 10 corridas pendentes criadas")
    
    # Criar corridas para atletas Povão
    print("\n🏃 Criando corridas para atletas Povão...")
    atletas_povao = [a for a in atletas_criados if a['modalidade_usuario'] == 'povao_pace_livre']
    corridas_povao = 0
    
    for atleta in atletas_povao[:50]:  # 50 atletas povão com corridas
        for _ in range(random.randint(1, 3)):
            await criar_corrida_povao(atleta['id'], atleta['nome'], atleta['estado'])
            corridas_povao += 1
    
    print(f"   ✓ {corridas_povao} corridas Povão criadas")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    print(f"✅ Total de atletas: {contador['total']}")
    print(f"   - Profissional/Amador Masculino: 30")
    print(f"   - Profissional/Amador Feminino: 30")
    print(f"   - PCD Masculino: 30")
    print(f"   - PCD Feminino: 30")
    print(f"   - Cadeirante Masculino: 10")
    print(f"   - Cadeirante Feminino: 10")
    print(f"   - Povão Masculino: 40")
    print(f"   - Povão Feminino: 40")
    print(f"   - Donos de Assessoria: 15")
    print(f"\n✅ Total de corridas: {corridas_criadas + corridas_povao}")
    print(f"   - Aprovadas: 30")
    print(f"   - Pendentes: 10")
    print(f"   - Povão: {corridas_povao}")
    print(f"\n✅ Assessorias: {len(ASSESSORIAS)}")
    print(f"✅ Atletas INDIVIDUAL: 10")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
