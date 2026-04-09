"""
Script v4: Enriquecer Regulamento - Adicionar blindagem jurídica dos 3 pilares restantes:
  1. RANKING PROFISSIONAL/AMADOR
  2. RANKING DA GALERA – PACE LIVRE
  3. RANKING DAS ASSESSORIAS/EQUIPES (ROE-RR)
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

BLOCO_RANKING_PROFISSIONAL = """
________________________________________

## REGULAMENTO – RANKING PROFISSIONAL/AMADOR

### 1. Disposições Gerais

O Ranking Profissional/Amador da Ranking Run tem como objetivo reconhecer e classificar atletas de corrida de rua com base em suas colocações oficiais em provas e competições, atribuindo pontuação proporcional ao desempenho alcançado.

Este ranking possui caráter **exclusivamente informativo e de entretenimento**, não constituindo certificação, homologação ou credenciamento oficial de atletas por parte de federações, confederações, associações ou quaisquer entidades reguladoras do esporte, em conformidade com o disposto na **Cláusula 1-A** e **Cláusula 1-B** do Regulamento Geral da plataforma e nos termos da **Lei n. 9.615/1998 (Lei Pelé)**.

________________________________________

### 2. Elegibilidade e Cadastro

a) **Cadastro obrigatório** — Para participar do Ranking Profissional/Amador, o atleta deve possuir cadastro ativo na plataforma Ranking Run, com dados pessoais válidos e verificáveis, em conformidade com a **LGPD** (Lei n. 13.709/2018);

b) **Modalidade de inscrição** — No ato do cadastro ou a qualquer momento posterior, o atleta deve optar pela modalidade **"Profissional/Amador"**, declarando que participará de provas oficiais com colocação registrada;

c) **Categorias disponíveis** — O sistema reconhece as seguintes categorias de atletas:
- **Normal** (Masculino/Feminino) — colocações de 1º a 10º lugar;
- **PCD** (Pessoa com Deficiência) — colocações de 1º a 3º lugar;
- **Cadeirante** — colocações de 1º a 3º lugar.

d) **Separação por gênero** — Os rankings são separados por gênero (Masculino e Feminino), garantindo equidade competitiva;

e) **Período de teste** — Novos cadastros dispõem de um período de teste de 30 (trinta) dias corridos para submissão de resultados, contados a partir da data de criação da conta. Após esse período, o acesso continuado está condicionado à autorização administrativa.

________________________________________

### 3. Submissão de Resultados

a) **Dados obrigatórios** — Para submeter um resultado, o atleta deve informar:
- Nome da competição;
- Colocação obtida (dentro dos limites da sua categoria);
- Cidade e estado da competição;
- Data da competição (formato AAAA-MM-DD);
- Link para o resultado oficial da prova;
- Tempo oficial no formato HH:MM:SS;
- Distância da prova (em quilômetros);
- Foto do pódio (opcional).

b) **Prazo para submissão** — O resultado deve ser submetido em até **30 (trinta) dias corridos** após a data da competição. Resultados fora deste prazo serão automaticamente rejeitados pelo sistema;

c) **Validação de colocação** — O sistema valida automaticamente a colocação informada com base na categoria do atleta:
- **Normal**: apenas colocações de 1º a 10º lugar são aceitas;
- **PCD/Cadeirante**: apenas colocações de 1º a 3º lugar são aceitas;

d) **Aprovação administrativa** — Todo resultado submetido permanece em status "pendente" até que a administração da plataforma o aprove ou reprove, mediante análise do link de resultado oficial e das informações declaradas;

e) **Veracidade das informações** — O atleta é integralmente responsável pela veracidade dos dados informados na submissão, nos termos do **Art. 186 do Código Civil** (Lei n. 10.406/2002) e do **Art. 299 do Código Penal** (falsidade ideológica). A plataforma reserva-se o direito de verificar qualquer informação junto às fontes oficiais.

________________________________________

### 4. Sistema de Pontuação

O Ranking Profissional/Amador utiliza a seguinte tabela de pontuação por colocação:

**Categoria Normal (Masculino/Feminino):**

| Colocação | Pontos |
|-----------|--------|
| 1º lugar  | 10     |
| 2º lugar  | 9      |
| 3º lugar  | 8      |
| 4º lugar  | 7      |
| 5º lugar  | 6      |
| 6º lugar  | 5      |
| 7º lugar  | 4      |
| 8º lugar  | 3      |
| 9º lugar  | 2      |
| 10º lugar | 1      |

**Categorias PCD e Cadeirante:**

| Colocação | Pontos |
|-----------|--------|
| 1º lugar  | 10     |
| 2º lugar  | 9      |
| 3º lugar  | 8      |

a) Colocações fora da tabela acima **não pontuam** e serão rejeitadas pelo sistema;

b) A pontuação é cumulativa ao longo do ano-calendário vigente;

c) O tempo registrado pelo atleta é armazenado para fins estatísticos e de composição do Raio-X do atleta, porém **não influencia diretamente a pontuação** do ranking.

________________________________________

### 5. Critérios de Classificação e Desempate

A classificação dos atletas no Ranking Profissional/Amador obedece aos seguintes critérios, em ordem de prioridade:

a) **Maior pontuação total acumulada** no ano-calendário vigente;

b) **Maior número de corridas registradas** (em caso de empate na pontuação);

c) Em caso de persistência de empate, prevalece o atleta com cadastro mais antigo na plataforma.

________________________________________

### 6. Periodicidade dos Rankings

O sistema disponibiliza os seguintes recortes temporais:

a) **Ranking Semanal** — Recalculado com base nas corridas registradas na semana corrente (segunda a domingo);

b) **Ranking Mensal** — Recalculado com base nas corridas registradas no mês-calendário corrente;

c) **Ranking Anual** — Acumulado de todas as corridas registradas no ano-calendário vigente (janeiro a dezembro).

Os rankings são atualizados automaticamente pelo sistema após cada aprovação de resultado.

________________________________________

### 7. Isenção de Responsabilidade

a) A Ranking Run **não certifica, homologa, credencia ou valida** a capacidade atlética, aptidão física ou nível competitivo de qualquer atleta listado no ranking;

b) O ranking reflete exclusivamente os dados autodeclarados pelos atletas e aprovados pela administração, podendo conter imprecisões inerentes ao modelo participativo da plataforma;

c) A plataforma **não se responsabiliza** por decisões tomadas por terceiros (organizadores de eventos, patrocinadores, treinadores, assessorias esportivas ou quaisquer outras entidades) com base nas classificações ou dados exibidos no ranking;

d) As classificações apresentadas **não substituem** os resultados oficiais das federações, confederações ou organizadores de eventos esportivos, conforme previsto na **Cláusula 33** do Regulamento Geral;

e) Nos termos do **Art. 19 do Marco Civil da Internet** (Lei n. 12.965/2014), a plataforma não poderá ser responsabilizada por dados informados pelos próprios atletas.

________________________________________

### 8. Proteção de Dados

Em conformidade com a **LGPD** (Lei n. 13.709/2018), ao submeter resultados, o atleta consente com o tratamento dos seguintes dados:

- Nome completo, gênero e categoria;
- Colocação, tempo, distância e local da competição;
- Link do resultado oficial;
- Dados de auditoria (IP, data/hora, sessão).

Esses dados são tratados com base no legítimo interesse do controlador (Art. 7°, IX, LGPD) e na execução do contrato de uso da plataforma (Art. 7°, V, LGPD). O atleta mantém todos os direitos previstos nos Arts. 17 a 22 da LGPD.

________________________________________

### 9. Disposições Finais do Ranking Profissional/Amador

a) A plataforma reserva-se o direito de alterar a tabela de pontuação, as categorias ou os critérios de classificação a qualquer tempo, mediante comunicação prévia aos usuários;

b) Resultados fraudulentos ou obtidos por meios ilícitos acarretarão a exclusão imediata do ranking e poderão resultar em banimento permanente da plataforma, conforme a **Cláusula 38** do Regulamento Geral;

c) Este regulamento complementar deve ser interpretado em conjunto com o Regulamento Geral da Ranking Run, a Carta de Princípios, a Política de Integridade e o Estatuto Institucional.

"""

BLOCO_RANKING_GALERA = """
________________________________________

## REGULAMENTO – RANKING DA GALERA (PACE LIVRE)

### 1. Disposições Gerais

O Ranking da Galera – Pace Livre da Ranking Run tem como objetivo promover a participação democrática de corredores de todos os níveis, valorizando a **distância percorrida** como critério principal de pontuação, independentemente de colocação ou tempo oficial.

Este ranking foi concebido para celebrar a prática esportiva em si, incentivando atletas amadores e recreativos a registrarem suas corridas e acumularem pontos com base no esforço individual.

O Ranking da Galera possui caráter **exclusivamente informativo, recreativo e de entretenimento**, não constituindo certificação, homologação ou reconhecimento oficial de desempenho atlético por parte de federações, confederações ou entidades reguladoras do esporte, conforme disposto na **Cláusula 1-A** e **Cláusula 1-B** do Regulamento Geral e nos termos da **Lei n. 9.615/1998 (Lei Pelé)**.

________________________________________

### 2. Elegibilidade e Cadastro

a) **Cadastro obrigatório** — O atleta deve possuir cadastro ativo na plataforma, em conformidade com a **LGPD** (Lei n. 13.709/2018);

b) **Modalidade de inscrição** — O atleta deve optar pela modalidade **"Pace Livre"** (Ranking da Galera) no ato do cadastro ou em alteração posterior no perfil;

c) **Abertura universal** — Não há restrição de categoria, idade, gênero ou nível competitivo para participação no Ranking da Galera;

d) **Separação por gênero** — Os rankings são separados por gênero (Masculino e Feminino), garantindo equidade na classificação;

e) **Período de teste** — Aplicam-se as mesmas regras do período de teste de 30 (trinta) dias previstas no Ranking Profissional/Amador.

________________________________________

### 3. Submissão de Resultados

a) **Dados obrigatórios** — Para submeter um resultado no Ranking da Galera, o atleta deve informar:
- Nome da competição ou treino oficial;
- Cidade e estado do evento;
- Data do evento (formato AAAA-MM-DD);
- Link para resultado ou evidência de participação;
- Tempo no formato HH:MM:SS (obrigatório, porém **não pontua**);
- Distância percorrida (em quilômetros).

b) **Colocação não aplicável** — No Ranking da Galera, a colocação é **irrelevante** para fins de pontuação. Qualquer valor de colocação informado será automaticamente desconsiderado pelo sistema (forçado a zero);

c) **Prazo para submissão** — Aplica-se o mesmo prazo de **30 (trinta) dias corridos** após a data do evento;

d) **Aprovação administrativa** — Todos os resultados estão sujeitos à aprovação da administração antes de integrarem o ranking.

________________________________________

### 4. Sistema de Pontuação

O Ranking da Galera utiliza a seguinte tabela de pontuação baseada exclusivamente na **distância percorrida**:

| Faixa de Distância       | Pontos |
|--------------------------|--------|
| Abaixo de 5 km           | 0      |
| 5 km a 9 km              | 5      |
| 10 km a 20 km            | 7      |
| 21 km ou mais (meia+)    | 9      |

a) A pontuação é atribuída por evento/corrida submetida e aprovada;

b) A pontuação é **cumulativa** ao longo do ano-calendário vigente;

c) Corridas com distância inferior a 5 km **não pontuam** no Ranking da Galera;

d) O tempo registrado é armazenado para fins estatísticos e composição do Raio-X do atleta, mas **não influencia a pontuação**;

e) A distância informada é de responsabilidade exclusiva do atleta, sendo passível de verificação pela administração.

________________________________________

### 5. Critérios de Classificação e Desempate

A classificação dos atletas obedece aos seguintes critérios, em ordem de prioridade:

a) **Maior pontuação total acumulada** no ano-calendário vigente;

b) **Maior número de corridas registradas** (em caso de empate na pontuação);

c) **Maior distância acumulada** (em caso de persistência de empate);

d) Em último caso, prevalece o atleta com cadastro mais antigo.

________________________________________

### 6. Periodicidade dos Rankings

O sistema disponibiliza os seguintes recortes temporais:

a) **Ranking Semanal** — Corridas dos últimos 7 dias;

b) **Ranking Mensal** — Corridas do mês-calendário corrente;

c) **Ranking Anual** — Acumulado de janeiro a dezembro do ano vigente.

d) **Destaques do Mês** — O sistema destaca automaticamente o atleta mais ativo (maior número de corridas) e o atleta com mais pontos do mês corrente.

________________________________________

### 7. Isenção de Responsabilidade

a) A Ranking Run **não certifica, homologa ou valida** a distância percorrida ou o tempo declarado pelos atletas;

b) O ranking reflete dados autodeclarados e aprovados pela administração, podendo conter imprecisões inerentes ao modelo participativo;

c) A plataforma **não se responsabiliza** por decisões de terceiros baseadas nos dados do Ranking da Galera;

d) A participação no Ranking da Galera **não implica** reconhecimento de aptidão física, capacidade atlética ou preparo para provas de qualquer distância;

e) A Ranking Run recomenda que todo atleta consulte um profissional de saúde antes de iniciar ou intensificar a prática esportiva, não podendo a plataforma ser responsabilizada por lesões, acidentes ou quaisquer danos à saúde decorrentes da prática esportiva.

________________________________________

### 8. Proteção de Dados

Aplicam-se integralmente as disposições de proteção de dados previstas no Ranking Profissional/Amador (Seção 8 do regulamento complementar correspondente), em conformidade com a **LGPD** (Lei n. 13.709/2018) e o **Marco Civil da Internet** (Lei n. 12.965/2014).

________________________________________

### 9. Disposições Finais do Ranking da Galera

a) A plataforma reserva-se o direito de alterar as faixas de distância, os valores de pontuação ou os critérios de classificação, mediante comunicação prévia;

b) Resultados fraudulentos acarretarão exclusão do ranking e possível banimento, conforme a **Cláusula 38** do Regulamento Geral;

c) Este regulamento complementar deve ser interpretado em conjunto com o Regulamento Geral da Ranking Run.

"""

BLOCO_RANKING_ASSESSORIAS = """
________________________________________

## REGULAMENTO – RANKING DAS ASSESSORIAS/EQUIPES (LIGA ROE-RR)

### 1. Disposições Gerais

O Ranking das Assessorias/Equipes da Ranking Run, denominado **Liga ROE-RR** (Ranking Oficial de Equipes – Ranking Run), tem como objetivo reconhecer e classificar assessorias esportivas e equipes de corrida de rua com base no desempenho coletivo de seus atletas vinculados.

A Liga ROE-RR possui caráter **exclusivamente informativo e de entretenimento**, não constituindo certificação, homologação, credenciamento ou regulação de assessorias esportivas ou equipes por parte de federações, confederações, conselhos profissionais (como o CREF/CONFEF) ou quaisquer entidades reguladoras do esporte ou da educação física, em conformidade com a **Cláusula 1-A** e **Cláusula 1-B** do Regulamento Geral e nos termos da **Lei n. 9.615/1998 (Lei Pelé)**.

A participação no ranking **não implica** reconhecimento da qualidade técnica dos serviços prestados pela assessoria, não substitui avaliações de órgãos competentes e não confere qualquer certificação profissional aos responsáveis pela equipe.

________________________________________

### 2. Elegibilidade e Cadastro

a) **Cadastro de assessoria** — A assessoria ou equipe deve estar cadastrada na plataforma Ranking Run com as seguintes informações: nome, cidade, estado e identificação do responsável (dono);

b) **Responsável (Dono)** — Cada assessoria deve possuir um responsável cadastrado com o perfil "Dono de Assessoria", que será o representante oficial perante a plataforma;

c) **Vínculo de atletas** — Os atletas são vinculados à assessoria através do campo "equipe" em seu perfil cadastral;

d) **Mínimo para participação** — Não há quantidade mínima de atletas para que a assessoria apareça no ranking, porém o selo de **verificação** requer condições específicas (vide Seção 7).

________________________________________

### 3. Sistema de Pontuação (ROE-RR)

A pontuação da Liga ROE-RR é composta por dois eixos:

**Eixo 1 – Cadastro de Atletas:**
- **+0,5 ponto** por cada atleta cadastrado e vinculado à assessoria na plataforma.

**Eixo 2 – Resultados Aprovados dos Atletas:**
- **+1,0 ponto** por cada resultado de corrida aprovado de um atleta da assessoria;
- **+1,0 ponto adicional** se o atleta obteve **1º lugar** na corrida;
- **+0,5 ponto adicional** se o atleta obteve do **2º ao 5º lugar** na corrida.

**Exemplo de cálculo:**
- Assessoria com 20 atletas vinculados: 20 x 0,5 = **10,0 pontos de cadastro**;
- 15 resultados aprovados: 15 x 1,0 = **15,0 pontos**;
- 3 vitórias (1º lugar): 3 x 1,0 = **3,0 pontos adicionais**;
- 5 pódios (2º a 5º): 5 x 0,5 = **2,5 pontos adicionais**;
- **Total: 30,5 pontos**.

________________________________________

### 4. Regra de Transferência de Atletas

A Ranking Run adota a regra de **vinculação temporal dos resultados**, que funciona da seguinte forma:

a) **Os pontos ficam na assessoria onde foram conquistados** — Se um atleta registra resultados enquanto vinculado à Assessoria A e posteriormente transfere-se para a Assessoria B, os pontos dos resultados obtidos durante o período na Assessoria A **permanecem contabilizados para a Assessoria A**;

b) **Resultados futuros na nova assessoria** — Após a transferência, apenas os resultados obtidos a partir da data de entrada na nova assessoria serão contabilizados para a Assessoria B;

c) **Histórico de equipes** — O sistema mantém um histórico de todas as movimentações de equipe do atleta, incluindo datas de entrada e saída, para garantir a correta atribuição dos pontos;

d) **Transparência** — O número de atletas que realizaram transferências é exibido como indicador de transparência no perfil da assessoria.

Esta regra visa garantir a **integridade competitiva** do ranking, impedindo que assessorias se beneficiem de resultados obtidos por atletas que não estavam vinculados à equipe no momento da conquista.

________________________________________

### 5. Critérios de Classificação e Desempate

A classificação das assessorias obedece aos seguintes critérios, em ordem de prioridade:

a) **Maior pontuação total** (soma de pontos de cadastro + pontos de resultados);

b) **Maior número de primeiros lugares** obtidos pelos atletas;

c) **Maior número de atletas vinculados**;

d) **Maior número de resultados válidos**;

e) Em caso de persistência de empate, prevalece a assessoria com cadastro mais antigo.

________________________________________

### 6. Filtros e Recortes

O ranking pode ser visualizado nos seguintes recortes:

a) **Nacional** — Classificação geral de todas as assessorias do Brasil;

b) **Estadual** — Classificação filtrada por Unidade Federativa;

c) **Por Cidade** — Classificação filtrada por município;

d) **Mensal** — Classificação baseada nos resultados de um mês específico do ano vigente.

________________________________________

### 7. Selos e Verificação

**Sistema de Selos (Nacional):**

| Posição          | Selo    |
|------------------|---------|
| 1ª a 20ª         | Ouro    |
| 21ª a 50ª        | Prata   |
| 51ª em diante    | Bronze  |

**Sistema de Selos (Estadual):**

| Posição          | Selo    |
|------------------|---------|
| 1ª a 10ª         | Prata   |
| 11ª em diante    | Bronze  |

**Selo de Verificação** — Uma assessoria recebe o selo "Verificada" quando cumpre simultaneamente os seguintes requisitos:
- Possuir um responsável (dono) identificado;
- Ter pelo menos **10 (dez) atletas** vinculados;
- Ter pelo menos **5 (cinco) resultados aprovados** válidos.

Os selos possuem caráter meramente indicativo de posição no ranking e **não constituem** certificação de qualidade, habilitação profissional ou qualquer forma de credenciamento da assessoria.

________________________________________

### 8. Responsabilidade e Isenção

a) A Ranking Run **não certifica, credencia, habilita ou avalia** a qualidade dos serviços prestados por assessorias esportivas ou equipes listadas no ranking;

b) A classificação no ranking **não implica** recomendação, endosso ou validação da competência técnica de treinadores, preparadores físicos ou responsáveis pela assessoria;

c) O ranking reflete exclusivamente os dados de resultados esportivos dos atletas vinculados, não guardando qualquer relação com a qualidade do serviço, metodologia de treino, capacitação profissional ou conformidade regulatória da assessoria;

d) A plataforma **não se responsabiliza** por relações contratuais entre assessorias e seus atletas, ficando estas subordinadas exclusivamente ao contrato privado entre as partes;

e) A Ranking Run **não verifica** o registro profissional dos responsáveis pela assessoria junto ao CREF/CONFEF ou outros órgãos reguladores, cabendo ao consumidor esta verificação nos termos do **Código de Defesa do Consumidor** (Lei n. 8.078/1990);

f) A participação no ranking **não exime** a assessoria de cumprir todas as obrigações legais aplicáveis à sua atividade, incluindo registro junto ao CREF (Conselho Regional de Educação Física), cumprimento de normas trabalhistas e tributárias, e observância das normas de segurança e saúde aplicáveis;

g) Nos termos do **Art. 14, §3° do CDC** (Lei n. 8.078/1990), a plataforma não responde por danos causados a terceiros quando a culpa é exclusiva do prestador de serviço (assessoria) ou de terceiros.

________________________________________

### 9. Uso de Marca e Licenciamento

a) A utilização do nome, selos, logotipos ou classificações da Liga ROE-RR por assessorias para fins de divulgação está sujeita às regras de licenciamento de marca previstas no **Contrato de Licenciamento de Uso de Marca** da Ranking Run;

b) O uso indevido da marca, selos ou classificações da Liga ROE-RR está sujeito às sanções previstas na **Lei de Propriedade Industrial** (Lei n. 9.279/1996) e no contrato de licenciamento;

c) A exibição do selo e da classificação obtida está condicionada à manutenção do vínculo ativo com a plataforma e à regularidade das obrigações contratuais.

________________________________________

### 10. Proteção de Dados

a) Os dados das assessorias e de seus responsáveis são tratados em conformidade com a **LGPD** (Lei n. 13.709/2018);

b) O responsável pela assessoria consente com a exibição pública do nome da assessoria, cidade, estado, posição no ranking, selo obtido e estatísticas agregadas de desempenho;

c) Dados individuais de atletas vinculados são tratados conforme as disposições de proteção de dados previstas nos regulamentos complementares do Ranking Profissional/Amador e do Ranking da Galera;

d) O responsável mantém todos os direitos previstos nos Arts. 17 a 22 da LGPD.

________________________________________

### 11. Disposições Finais do Ranking de Assessorias

a) A plataforma reserva-se o direito de alterar o sistema de pontuação, os critérios de selos ou os requisitos de verificação, mediante comunicação prévia;

b) Assessorias que praticarem fraude, manipulação de resultados ou qualquer conduta em desacordo com este regulamento estarão sujeitas a exclusão do ranking e banimento da plataforma;

c) A regra de transferência de atletas (Seção 4) é de aplicação imediata e retroativa para fins de integridade do ranking;

d) Este regulamento complementar deve ser interpretado em conjunto com o Regulamento Geral da Ranking Run, a Carta de Princípios, a Política de Integridade, o Estatuto Institucional e o Contrato de Licenciamento de Uso de Marca.

"""


async def enriquecer():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    reg = await db.configuracoes.find_one({"tipo": "regulamento"})
    if not reg:
        print("ERRO: Regulamento não encontrado!")
        return

    conteudo = reg.get("conteudo", "")
    
    # Verificar se já foi aplicado
    if "RANKING PROFISSIONAL/AMADOR" in conteudo and "RANKING DA GALERA" in conteudo and "LIGA ROE-RR" in conteudo:
        print("Os 3 pilares JÁ estão presentes no regulamento. Nada a fazer.")
        return

    lines = conteudo.split("\n")
    
    # Encontrar a linha "CONSIDERAÇÃO FINAL" para inserir ANTES dela
    insert_idx = -1
    for i, line in enumerate(lines):
        if "CONSIDERAÇÃO FINAL" in line.upper():
            # Voltar para antes do separador ________
            idx = i - 1
            while idx > 0 and lines[idx].strip() in ("", "________________________________________"):
                idx -= 1
            insert_idx = idx + 1
            break
    
    if insert_idx == -1:
        # Fallback: inserir no final
        insert_idx = len(lines)
        print("AVISO: 'CONSIDERAÇÃO FINAL' não encontrada, inserindo no final.")

    # Construir o bloco completo
    bloco_completo = BLOCO_RANKING_PROFISSIONAL + BLOCO_RANKING_GALERA + BLOCO_RANKING_ASSESSORIAS
    
    # Inserir as novas linhas
    novas_linhas = bloco_completo.split("\n")
    for i, nl in enumerate(novas_linhas):
        lines.insert(insert_idx + i, nl)

    novo_conteudo = "\n".join(lines)

    # Atualizar versão
    versao_atual = reg.get("versao", "1.6")
    partes = versao_atual.split(".")
    partes[-1] = str(int(partes[-1]) + 1)
    nova_versao = ".".join(partes)

    await db.configuracoes.update_one(
        {"tipo": "regulamento"},
        {"$set": {
            "conteudo": novo_conteudo,
            "versao": nova_versao,
            "data_atualizacao": datetime.now(timezone.utc).isoformat(),
            "atualizado_por": "sistema",
            "atualizado_por_nome": "Blindagem Jurídica v4 - 3 Pilares"
        }}
    )

    print(f"Regulamento atualizado com sucesso!")
    print(f"Versão: {versao_atual} -> {nova_versao}")
    print(f"Tamanho: {len(reg.get('conteudo', ''))} -> {len(novo_conteudo)} caracteres")

    # Verificação
    novo = await db.configuracoes.find_one({"tipo": "regulamento"}, {"_id": 0})
    c = novo.get("conteudo", "")
    checks = [
        ("Pilar 1: Ranking Profissional", "REGULAMENTO – RANKING PROFISSIONAL/AMADOR" in c),
        ("  Tabela de pontos colocação", "1º lugar  | 10" in c),
        ("  Categorias PCD/Cadeirante", "Categorias PCD e Cadeirante" in c),
        ("  Prazo 30 dias", "30 (trinta) dias corridos" in c),
        ("  Art. 186 Código Civil", "Art. 186 do Código Civil" in c),
        ("Pilar 2: Ranking da Galera", "REGULAMENTO – RANKING DA GALERA" in c),
        ("  Tabela distância", "5 km a 9 km" in c),
        ("  Pace livre sem colocação", "colocação é irrelevante" in c),
        ("  Saúde disclaimer", "consulte um profissional de saúde" in c),
        ("Pilar 3: Assessorias ROE-RR", "LIGA ROE-RR" in c),
        ("  Pontuação +0,5 atleta", "+0,5 ponto" in c),
        ("  Regra transferência", "vinculação temporal dos resultados" in c),
        ("  Selos Ouro/Prata/Bronze", "Ouro" in c and "Prata" in c and "Bronze" in c),
        ("  CREF/CONFEF disclaimer", "CREF/CONFEF" in c),
        ("  Lei Pelé todas seções", c.count("Lei n. 9.615/1998") >= 4),
        ("  Contrato Licenciamento ref", "Contrato de Licenciamento" in c),
    ]

    all_ok = True
    for name, result in checks:
        status = "OK" if result else "FALHOU"
        if not result:
            all_ok = False
        print(f"  [{status}] {name}")

    if all_ok:
        print(f"\nTODAS as {len(checks)} verificações passaram!")
    else:
        print("\nALGUMAS verificações falharam - checar manualmente.")


asyncio.run(enriquecer())
