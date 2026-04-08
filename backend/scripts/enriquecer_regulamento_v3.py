"""
Script v3: Enriquecer Regulamento - usa inserção por linha para evitar problemas de \r
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def enriquecer():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    reg = await db.configuracoes.find_one({"tipo": "regulamento"})
    if not reg:
        return

    conteudo = reg.get("conteudo", "")
    lines = conteudo.split("\n")
    
    # Helper: find line index containing text
    def find_line(text, start=0):
        for i in range(start, len(lines)):
            if text in lines[i]:
                return i
        return -1
    
    insertions = []  # (after_line_idx, text_to_insert)
    
    # ===================================================================
    # 1. APÓS "### 2. Definições" → inserir "1-A. Objetivo" e "1-B. Natureza"
    #    ANTES da linha "### 2. Definições" (na linha do separador)
    # ===================================================================
    idx_s2 = find_line("### 2. Defini")
    if idx_s2 > 0:
        # Insert BEFORE the separator line (idx_s2 - 1 is the ________ line)
        # We insert new sections between the LGPD paragraph and the separator
        bloco_objetivo_natureza = """\r
### 1-A. Objetivo Central da Plataforma\r
\r
A plataforma Ranking Run foi concebida com o propósito de fortalecer a corrida de rua no Brasil, conectando atletas e facilitando o acesso a informações esportivas. Seu objetivo central é centralizar informações, promover engajamento e facilitar a visualização de dados esportivos provenientes de avaliações dos próprios atletas e integrações autorizadas.\r
\r
A Ranking Run declara expressamente que seu objetivo **nunca foi, e nunca será**, substituir, replicar, interferir ou competir com federações, confederações, associações, entidades oficiais, organizações esportivas oficiais, ou quaisquer órgãos dirigentes ou reguladores do esporte, em qualquer nível — municipal, estadual, nacional ou internacional.\r
\r
A plataforma atua exclusivamente como **ferramenta complementar** ao ecossistema esportivo, agregando valor à comunidade e incentivando a prática esportiva por meio de:\r
- transparência nas avaliações de eventos;\r
- compartilhamento de experiências entre atletas;\r
- geração de indicadores estatísticos sobre a percepção da comunidade de corredores;\r
- promoção de visibilidade e engajamento dentro da comunidade de corrida de rua.\r
\r
Todas as funcionalidades oferecidas pela plataforma — incluindo rankings, classificações, análises e estatísticas — possuem caráter **exclusivamente informativo e de entretenimento**, sem qualquer valor oficial, homologatório ou regulatório.\r
________________________________________\r
\r
### 1-B. Natureza Complementar da Plataforma\r
\r
A Ranking Run reafirma seu compromisso como plataforma complementar ao ecossistema esportivo brasileiro e internacional, declarando expressamente que:\r
\r
a) **Não é entidade esportiva** — Não somos, não pretendemos ser e não nos apresentamos como federação, confederação, associação, liga ou qualquer tipo de entidade reguladora do esporte;\r
\r
b) **Não interfere em competências oficiais** — Não interferimos, substituímos, replicamos ou competimos com as atividades, competências ou atribuições de organizações esportivas oficiais, órgãos dirigentes ou entidades reguladoras do esporte em qualquer nível (municipal, estadual, nacional ou internacional);\r
\r
c) **Rankings informativos** — Os rankings, classificações e análises gerados pela plataforma têm caráter exclusivamente informativo e de entretenimento, não possuindo qualquer valor oficial, homologatório ou regulatório, conforme reforçado pela Cláusula 33 deste Regulamento;\r
\r
d) **Ferramenta de apoio** — Atuamos como ferramenta de apoio à comunidade de corrida de rua, promovendo engajamento, visibilidade e acesso facilitado a informações já disponíveis publicamente ou compartilhadas voluntariamente pelos usuários;\r
\r
e) **Respeito à autoridade esportiva** — Respeitamos integralmente a autonomia e a autoridade das entidades esportivas competentes, reconhecidas pelo ordenamento jurídico brasileiro, e nos colocamos à disposição para colaboração dentro dos limites legais;\r
\r
f) **Conformidade constitucional** — A atuação da plataforma encontra amparo nos princípios constitucionais de livre iniciativa (Art. 170, caput e parágrafo único, CF/88), liberdade de expressão (Art. 5°, IV e IX, CF/88) e direito de acesso à informação (Art. 5°, XIV, CF/88), não se confundindo com a atividade regulatória das entidades esportivas oficiais previstas na Lei n. 9.615/1998 (Lei Pelé).\r"""
        insertions.append((idx_s2 - 1, bloco_objetivo_natureza))

    # ===================================================================
    # 2. APÓS Section 1 "não sendo responsável..." → inserir fundamentação legal
    # ===================================================================
    idx_resp = find_line("não sendo responsável pela organização, execução ou qualidade")
    if idx_resp > 0:
        bloco_legal = """\r
O presente regulamento encontra-se em conformidade com o ordenamento jurídico brasileiro, sendo regido especialmente pelas seguintes normas:\r
\r
a) **Lei Geral de Proteção de Dados Pessoais** (Lei n. 13.709/2018 — LGPD) — assegurando transparência, consentimento, finalidade, adequação, necessidade, livre acesso, qualidade dos dados, segurança, prevenção e não discriminação no tratamento de dados pessoais coletados pela plataforma;\r
\r
b) **Marco Civil da Internet** (Lei n. 12.965/2014) — respeitando a inviolabilidade da intimidade e da vida privada, a proteção dos dados pessoais, a preservação da estabilidade, segurança e funcionalidade da rede, e a liberdade de expressão prevista no Art. 19;\r
\r
c) **Código de Defesa do Consumidor** (Lei n. 8.078/1990) — assegurando ao consumidor a proteção contra práticas abusivas, o direito à informação adequada e clara sobre os serviços prestados e a proteção contra publicidade enganosa;\r
\r
d) **Constituição da República Federativa do Brasil de 1988** — Art. 5°, incisos IV (liberdade de manifestação do pensamento), IX (liberdade de expressão da atividade intelectual), X (inviolabilidade da intimidade, vida privada, honra e imagem), XII (inviolabilidade das comunicações de dados), XIV (direito de acesso à informação) e LXXIX (proteção dos dados pessoais como direito fundamental);\r
\r
e) **Regulamento Geral sobre a Proteção de Dados da União Europeia** (GDPR, Regulamento UE 2016/679) — a plataforma adota as melhores práticas internacionais de proteção de dados como referência complementar;\r
\r
f) **Decreto n. 8.771/2016** — que regulamenta o Marco Civil da Internet e estabelece diretrizes sobre guarda de dados pessoais, padrões de segurança e procedimentos para apuração de infrações;\r
\r
g) **Lei de Direitos Autorais** (Lei n. 9.610/1998) — aplicável à proteção da propriedade intelectual do conteúdo, algoritmos e compilações de dados gerados pela plataforma;\r
\r
h) **Lei de Propriedade Industrial** (Lei n. 9.279/1996) — aplicável à proteção de marcas, logotipos e elementos visuais da plataforma Ranking Run.\r"""
        insertions.append((idx_resp, bloco_legal))

    # ===================================================================
    # 3. APÓS "Caso o atleta tente registrar nova avaliação" → proteção de dados
    # ===================================================================
    idx_s5 = find_line("Caso o atleta tente registrar nova avaliação")
    if idx_s5 > 0:
        bloco_dados_aval = """\r
**Proteção de dados na avaliação**: Em conformidade com o Art. 7°, incisos I e V, da LGPD, ao registrar uma avaliação, o atleta consente com a coleta e o tratamento dos seguintes dados para fins de auditoria, segurança e prevenção de fraudes:\r
- endereço IP do dispositivo utilizado;\r
- data e hora do registro;\r
- identificador da sessão de autenticação;\r
- informações do navegador (user-agent).\r
\r
Esses dados são tratados com base no legítimo interesse do controlador (Art. 7°, IX, LGPD) para garantir a integridade estatística do ranking e são armazenados em conformidade com as normas de segurança previstas no Art. 46 da LGPD e no Decreto n. 8.771/2016.\r
\r
O atleta mantém todos os direitos previstos nos Arts. 17 a 22 da LGPD sobre seus dados pessoais, incluindo o direito de acesso, correção, eliminação e portabilidade, podendo exercê-los nos termos da Política de Privacidade da plataforma.\r"""
        insertions.append((idx_s5, bloco_dados_aval))

    # ===================================================================
    # 4. APÓS "exclusão de cadastro" (Seção 12) → referências legais conduta
    # ===================================================================
    idx_excl = find_line("exclusão de cadastro")
    if idx_excl > 0:
        bloco_conduta = """\r
As condutas abusivas praticadas por meio da plataforma sujeitam o infrator às responsabilidades previstas no ordenamento jurídico brasileiro, incluindo:\r
- **Marco Civil da Internet** (Arts. 21 e 22 da Lei n. 12.965/2014) — que prevê a responsabilização civil por danos decorrentes de conteúdo gerado por terceiros;\r
- **Código de Defesa do Consumidor** (Art. 39 da Lei n. 8.078/1990) — que veda práticas abusivas nas relações de consumo;\r
- **Código Civil Brasileiro** (Arts. 186 e 927 da Lei n. 10.406/2002) — que estabelece o dever de reparação por atos ilícitos que causem dano a outrem;\r
- **Código Penal Brasileiro** (Arts. 138 a 140) — nos casos em que as avaliações configurem calúnia, difamação ou injúria.\r
\r
A plataforma cooperará com autoridades competentes mediante requisição judicial ou administrativa fundamentada, em conformidade com o Art. 10 do Marco Civil da Internet.\r"""
        insertions.append((idx_excl, bloco_conduta))

    # ===================================================================
    # 5. APÓS "Eventuais conflitos entre atletas e organizadores" (S13) → Marco Civil
    # ===================================================================
    idx_conf = find_line("Eventuais conflitos entre atletas e organizadores devem ser resolvidos")
    if idx_conf > 0:
        bloco_mc = """\r
Nos termos do **Art. 19 do Marco Civil da Internet** (Lei n. 12.965/2014), a plataforma somente poderá ser responsabilizada civilmente por danos decorrentes de conteúdo gerado por terceiros se, após ordem judicial específica, não tomar as providências para tornar indisponível o conteúdo apontado como infringente. A Ranking Run mantém canais de atendimento para recebimento de notificações e solicitações de correção (Cláusula 24 deste Regulamento).\r
\r
A limitação de responsabilidade da plataforma encontra amparo também no **Art. 18 do Marco Civil da Internet**, que estabelece que o provedor de conexão à internet não será responsabilizado civilmente por danos decorrentes de conteúdo gerado por terceiros.\r"""
        insertions.append((idx_conf, bloco_mc))

    # ===================================================================
    # 6. APÓS "ranking não deve ser interpretado como certificação" (S14) → CF
    # ===================================================================
    idx_cert = find_line("ranking não deve ser interpretado como certificação técnica")
    if idx_cert > 0:
        bloco_cf = """\r
A isenção de responsabilidade aqui prevista encontra fundamento nos seguintes dispositivos legais:\r
- **Art. 5°, IV e IX da Constituição Federal** — que asseguram a liberdade de manifestação do pensamento e de expressão, desde que não anônima;\r
- **Art. 19 do Marco Civil da Internet** (Lei n. 12.965/2014) — que limita a responsabilidade do provedor de aplicações por conteúdo gerado por terceiros;\r
- **Art. 14, §3° do Código de Defesa do Consumidor** (Lei n. 8.078/1990) — que exclui a responsabilidade do fornecedor quando prova a culpa exclusiva do consumidor ou de terceiro.\r
\r
As avaliações registradas na plataforma constituem manifestações protegidas pelo direito fundamental à liberdade de expressão (Art. 5°, IV, CF/88), ressalvados os casos de abuso tipificados na legislação penal e civil.\r"""
        insertions.append((idx_cert, bloco_cf))

    # ===================================================================
    # 7. ENRIQUECER Seção 19 - Liberdade de Opinião (replace line)
    # ===================================================================
    idx_s19_resp = find_line("A Ranking Run não se responsabiliza pelo conteúdo opinativo das avaliações")
    if idx_s19_resp > 0:
        lines[idx_s19_resp] = "A Ranking Run não se responsabiliza pelo conteúdo opinativo das avaliações registradas pelos usuários, uma vez que tais manifestações são produzidas diretamente pelos próprios atletas cadastrados, em exercício do direito fundamental à liberdade de expressão previsto no **Art. 5°, incisos IV e IX, da Constituição Federal de 1988**, e regulamentado pelo **Art. 19 do Marco Civil da Internet** (Lei n. 12.965/2014).\r"

    idx_s19_caso = find_line("Caso algum conteúdo específico seja considerado ofensivo")
    if idx_s19_caso > 0:
        lines[idx_s19_caso] = "Caso algum conteúdo específico seja considerado ofensivo, ilegal ou em desacordo com este regulamento, poderá ser analisado pela equipe da plataforma mediante solicitação formal, em observância ao procedimento previsto nos **Arts. 19 e 21 do Marco Civil da Internet** e respeitados os direitos constitucionais de ampla defesa e contraditório (Art. 5°, LV, CF/88).\r"

    # Add after line about "produzidas diretamente" a reference to Art. 3 Marco Civil
    if idx_s19_resp > 0:
        bloco_mc_s19 = """\r
O exercício da liberdade de opinião encontra-se também protegido pelo **Art. 3° do Marco Civil da Internet**, que estabelece como princípio disciplinador do uso da internet no Brasil a garantia da liberdade de expressão, comunicação e manifestação de pensamento, nos termos da Constituição Federal.\r"""
        insertions.append((idx_s19_resp, bloco_mc_s19))

    # ===================================================================
    # 8. ENRIQUECER Seção 22 - Foro (replace entire section content)
    # ===================================================================
    idx_foro = find_line("### 22. Cláusula de Foro")
    if idx_foro > 0:
        # Replace the "Este regulamento é regido" line
        idx_regido = find_line("Este regulamento é regido pelas leis da República", idx_foro)
        if idx_regido > 0:
            lines[idx_regido] = """Este regulamento é regido pelas leis da República Federativa do Brasil, com especial observância à:\r
- **Constituição da República Federativa do Brasil de 1988**;\r
- **Lei Geral de Proteção de Dados Pessoais** (Lei n. 13.709/2018 — LGPD);\r
- **Marco Civil da Internet** (Lei n. 12.965/2014);\r
- **Código de Defesa do Consumidor** (Lei n. 8.078/1990);\r
- **Decreto n. 8.771/2016** (regulamentação do Marco Civil);\r
- **Código Civil Brasileiro** (Lei n. 10.406/2002);\r
- **Lei de Direitos Autorais** (Lei n. 9.610/1998);\r
- **Lei de Propriedade Industrial** (Lei n. 9.279/1996).\r"""

        # Replace the "Eventuais controvérsias" line
        idx_controv = find_line("Eventuais controvérsias decorrentes da utilização", idx_foro)
        if idx_controv > 0:
            lines[idx_controv] = "Eventuais controvérsias decorrentes da utilização da plataforma deverão ser resolvidas, preferencialmente, por meio de solução amigável entre as partes, podendo as partes recorrer, se desejarem, a mecanismos alternativos de resolução de conflitos, como mediação ou arbitragem, nos termos da **Lei n. 13.140/2015** (Lei de Mediação) e da **Lei n. 9.307/1996** (Lei de Arbitragem).\r"

    # ===================================================================
    # 9. APÓS "espaços públicos ou abertos" (S23) → CF reference
    # ===================================================================
    idx_s23 = find_line("espaços públicos ou abertos à participação da comunidade esportiva")
    if idx_s23 > 0:
        bloco_s23 = """\r
Este entendimento encontra fundamento no **direito constitucional de acesso à informação** (Art. 5°, XIV e XXXIII, CF/88) e no **princípio da publicidade** aplicável a eventos realizados em espaços públicos, sendo respeitado o direito de retificação previsto na Cláusula 24 deste Regulamento.\r"""
        insertions.append((idx_s23, bloco_s23))

    # ===================================================================
    # 10. APÓS "avaliações registradas pelos usuários da plataforma" (S27) → PI
    # ===================================================================
    idx_s27 = find_line("mencionando que a classificação se refere exclusivamente às avaliações registradas")
    if idx_s27 > 0:
        bloco_s27 = """\r
O uso indevido do nome, logotipo, marca ou qualquer elemento visual da Ranking Run está sujeito às sanções previstas na **Lei de Propriedade Industrial** (Lei n. 9.279/1996) e na **Lei de Direitos Autorais** (Lei n. 9.610/1998), podendo a plataforma adotar as medidas judiciais cabíveis para proteção de sua propriedade intelectual, incluindo a busca e apreensão de materiais e a indenização por danos materiais e morais.\r"""
        insertions.append((idx_s27, bloco_s27))

    # ===================================================================
    # 11. APÓS "ambiente mais informativo e colaborativo" (Carta Princípios S1) → Legal foundation
    # ===================================================================
    idx_carta = find_line("contribuindo para a construção de um ambiente mais informativo e colaborativo", 280)
    if idx_carta > 0:
        bloco_carta = """\r
O propósito da plataforma fundamenta-se nos princípios constitucionais de **livre iniciativa** (Art. 170, caput e parágrafo único, CF/88), **liberdade de expressão** (Art. 5°, IV e IX, CF/88), **direito de acesso à informação** (Art. 5°, XIV, CF/88) e **proteção dos dados pessoais como direito fundamental** (Art. 5°, LXXIX, CF/88).\r
\r
A Ranking Run reconhece e respeita a autoridade das entidades esportivas oficiais previstas na **Lei n. 9.615/1998 (Lei Pelé)** e atua exclusivamente como plataforma complementar de caráter informativo, sem qualquer pretensão de exercer atividades regulatórias ou de governança esportiva.\r"""
        insertions.append((idx_carta, bloco_carta))

    # ===================================================================
    # 12. APÓS "estabelecer diretrizes claras de governança" (Integridade) → LGPD/GDPR
    # ===================================================================
    idx_integ = find_line("estabelecer diretrizes claras de governança da plataforma")
    if idx_integ > 0:
        bloco_integ = "•\tproteger os dados pessoais dos usuários em conformidade com a **LGPD** (Lei n. 13.709/2018) e o **Marco Civil da Internet** (Lei n. 12.965/2014);\r\n•\tassegurar a conformidade das operações da plataforma com o ordenamento jurídico brasileiro e as melhores práticas internacionais de proteção de dados (**GDPR**, Regulamento UE 2016/679).\r"
        insertions.append((idx_integ, bloco_integ))

    # ===================================================================
    # APLICAR INSERÇÕES (de trás pra frente para não bagunçar índices)
    # ===================================================================
    insertions.sort(key=lambda x: x[0], reverse=True)
    for after_idx, text in insertions:
        new_lines = text.split("\n")
        for i, nl in enumerate(new_lines):
            lines.insert(after_idx + 1 + i, nl)

    novo_conteudo = "\n".join(lines)

    # ===================================================================
    # SALVAR
    # ===================================================================
    versao_atual = reg.get("versao", "1.4")
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
            "atualizado_por_nome": "Blindagem Jurídica v2"
        }}
    )

    print(f"Regulamento atualizado com sucesso!")
    print(f"Versão: {versao_atual} -> {nova_versao}")
    print(f"Tamanho: {len(reg.get('conteudo',''))} -> {len(novo_conteudo)} caracteres")
    print(f"Inserções aplicadas: {len(insertions)}")

    # Verificação final
    novo = await db.configuracoes.find_one({"tipo": "regulamento"}, {"_id": 0})
    c = novo.get("conteudo", "")
    checks = [
        ('1-A. Objetivo Central', '1-A. Objetivo Central' in c),
        ('1-B. Natureza Complementar', '1-B. Natureza Complementar' in c),
        ('Fundamentação Legal S1', 'Lei Geral de Proteção de Dados Pessoais' in c),
        ('Proteção dados avaliação', 'Proteção de dados na avaliação' in c),
        ('Marco Civil Conduta', 'Arts. 21 e 22 da Lei n. 12.965/2014' in c),
        ('Art. 19 Responsabilidade', 'Art. 19 do Marco Civil da Internet' in c),
        ('CF Isenção Resp', 'Art. 5°, IV e IX da Constituição Federal' in c),
        ('S19 CF liberdade', 'Art. 3° do Marco Civil da Internet' in c),
        ('Foro enriquecido', 'Lei n. 13.140/2015' in c),
        ('S23 acesso info', 'direito constitucional de acesso à informação' in c),
        ('S27 propriedade intelectual', 'busca e apreensão' in c),
        ('Carta Princípios Lei Pelé', 'Lei n. 9.615/1998 (Lei Pelé)' in c),
        ('Integridade LGPD', 'proteger os dados pessoais dos usuários' in c),
    ]
    all_ok = True
    for name, result in checks:
        status = 'OK' if result else 'FALHOU'
        if not result:
            all_ok = False
        print(f'  [{status}] {name}')
    
    if all_ok:
        print("\nTODAS as inserções foram aplicadas com sucesso!")
    else:
        print("\nALGUMAS inserções falharam - verificar manualmente.")

asyncio.run(enriquecer())
