"""
Script para enriquecer o Regulamento com referências legais da Política de Privacidade.
NÃO REMOVE nada existente — apenas insere/ajusta para blindagem jurídica.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def enriquecer_regulamento():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]

    reg = await db.configuracoes.find_one({"tipo": "regulamento"})
    if not reg:
        print("Regulamento não encontrado!")
        return

    conteudo = reg.get("conteudo", "")

    # ===================================================================
    # 1. ENRIQUECER SEÇÃO 1 — Disposições Gerais
    #    Adicionar parágrafo com fundamentação legal completa
    # ===================================================================
    old_s1 = """A plataforma Ranking Run atua exclusivamente como meio tecnológico de coleta, organização e exibição de avaliações realizadas pelos próprios usuários, não sendo responsável pela organização, execução ou qualidade das corridas avaliadas.
________________________________________
### 2. Definições"""

    new_s1 = """A plataforma Ranking Run atua exclusivamente como meio tecnológico de coleta, organização e exibição de avaliações realizadas pelos próprios usuários, não sendo responsável pela organização, execução ou qualidade das corridas avaliadas.

O presente regulamento encontra-se em conformidade com o ordenamento jurídico brasileiro, sendo regido especialmente pelas seguintes normas:

a) **Lei Geral de Proteção de Dados Pessoais** (Lei n. 13.709/2018 — LGPD) — assegurando transparência, consentimento, finalidade, adequação, necessidade, livre acesso, qualidade dos dados, segurança, prevenção e não discriminação no tratamento de dados pessoais coletados pela plataforma;

b) **Marco Civil da Internet** (Lei n. 12.965/2014) — respeitando a inviolabilidade da intimidade e da vida privada, a proteção dos dados pessoais, a preservação da estabilidade, segurança e funcionalidade da rede, e a liberdade de expressão prevista no Art. 19;

c) **Código de Defesa do Consumidor** (Lei n. 8.078/1990) — assegurando ao consumidor a proteção contra práticas abusivas, o direito à informação adequada e clara sobre os serviços prestados e a proteção contra publicidade enganosa;

d) **Constituição da República Federativa do Brasil de 1988** — Art. 5°, incisos IV (liberdade de manifestação do pensamento), IX (liberdade de expressão da atividade intelectual), X (inviolabilidade da intimidade, vida privada, honra e imagem), XII (inviolabilidade das comunicações de dados), XIV (direito de acesso à informação) e LXXIX (proteção dos dados pessoais como direito fundamental);

e) **Regulamento Geral sobre a Proteção de Dados da União Europeia** (GDPR, Regulamento UE 2016/679) — a plataforma adota as melhores práticas internacionais de proteção de dados como referência complementar;

f) **Decreto n. 8.771/2016** — que regulamenta o Marco Civil da Internet e estabelece diretrizes sobre guarda de dados pessoais, padrões de segurança e procedimentos para apuração de infrações;

g) **Lei de Direitos Autorais** (Lei n. 9.610/1998) — aplicável à proteção da propriedade intelectual do conteúdo, algoritmos e compilações de dados gerados pela plataforma;

h) **Lei de Propriedade Industrial** (Lei n. 9.279/1996) — aplicável à proteção de marcas, logotipos e elementos visuais da plataforma Ranking Run.
________________________________________

### 1-A. Objetivo Central da Plataforma

A plataforma Ranking Run foi concebida com o propósito de fortalecer a corrida de rua no Brasil, conectando atletas e facilitando o acesso a informações esportivas. Seu objetivo central é centralizar informações, promover engajamento e facilitar a visualização de dados esportivos provenientes de avaliações dos próprios atletas e integrações autorizadas.

A Ranking Run declara expressamente que seu objetivo **nunca foi, e nunca será**, substituir, replicar, interferir ou competir com federações, confederações, associações, entidades oficiais, organizações esportivas oficiais, ou quaisquer órgãos dirigentes ou reguladores do esporte, em qualquer nível — municipal, estadual, nacional ou internacional.

A plataforma atua exclusivamente como **ferramenta complementar** ao ecossistema esportivo, agregando valor à comunidade e incentivando a prática esportiva por meio de:
- transparência nas avaliações de eventos;
- compartilhamento de experiências entre atletas;
- geração de indicadores estatísticos sobre a percepção da comunidade de corredores;
- promoção de visibilidade e engajamento dentro da comunidade de corrida de rua.

Todas as funcionalidades oferecidas pela plataforma — incluindo rankings, classificações, análises e estatísticas — possuem caráter **exclusivamente informativo e de entretenimento**, sem qualquer valor oficial, homologatório ou regulatório.
________________________________________

### 1-B. Natureza Complementar da Plataforma

A Ranking Run reafirma seu compromisso como plataforma complementar ao ecossistema esportivo brasileiro e internacional, declarando expressamente que:

a) **Não é entidade esportiva** — Não somos, não pretendemos ser e não nos apresentamos como federação, confederação, associação, liga ou qualquer tipo de entidade reguladora do esporte;

b) **Não interfere em competências oficiais** — Não interferimos, substituímos, replicamos ou competimos com as atividades, competências ou atribuições de organizações esportivas oficiais, órgãos dirigentes ou entidades reguladoras do esporte em qualquer nível (municipal, estadual, nacional ou internacional);

c) **Rankings informativos** — Os rankings, classificações e análises gerados pela plataforma têm caráter exclusivamente informativo e de entretenimento, não possuindo qualquer valor oficial, homologatório ou regulatório, conforme reforçado pela Cláusula 33 deste Regulamento;

d) **Ferramenta de apoio** — Atuamos como ferramenta de apoio à comunidade de corrida de rua, promovendo engajamento, visibilidade e acesso facilitado a informações já disponíveis publicamente ou compartilhadas voluntariamente pelos usuários;

e) **Respeito à autoridade esportiva** — Respeitamos integralmente a autonomia e a autoridade das entidades esportivas competentes, reconhecidas pelo ordenamento jurídico brasileiro, e nos colocamos à disposição para colaboração dentro dos limites legais;

f) **Conformidade constitucional** — A atuação da plataforma encontra amparo nos princípios constitucionais de livre iniciativa (Art. 170, caput e parágrafo único, CF/88), liberdade de expressão (Art. 5°, IV e IX, CF/88) e direito de acesso à informação (Art. 5°, XIV, CF/88), não se confundindo com a atividade regulatória das entidades esportivas oficiais previstas na Lei n. 9.615/1998 (Lei Pelé).
________________________________________
### 2. Definições"""

    conteudo = conteudo.replace(old_s1, new_s1)

    # ===================================================================
    # 2. ENRIQUECER SEÇÃO 5 — Direito de Avaliação
    #    Adicionar referência à LGPD e coleta de dados durante avaliação
    # ===================================================================
    old_s5 = """Caso o atleta tente registrar nova avaliação, o sistema informará que a avaliação já foi realizada.
________________________________________
### 6. Momento da Avaliação"""

    new_s5 = """Caso o atleta tente registrar nova avaliação, o sistema informará que a avaliação já foi realizada.

**Proteção de dados na avaliação**: Em conformidade com o Art. 7°, incisos I e V, da LGPD, ao registrar uma avaliação, o atleta consente com a coleta e o tratamento dos seguintes dados para fins de auditoria, segurança e prevenção de fraudes:
- endereço IP do dispositivo utilizado;
- data e hora do registro;
- identificador da sessão de autenticação;
- informações do navegador (user-agent).

Esses dados são tratados com base no legítimo interesse do controlador (Art. 7°, IX, LGPD) para garantir a integridade estatística do ranking e são armazenados em conformidade com as normas de segurança previstas no Art. 46 da LGPD e no Decreto n. 8.771/2016.

O atleta mantém todos os direitos previstos nos Arts. 17 a 22 da LGPD sobre seus dados pessoais, incluindo o direito de acesso, correção, eliminação e portabilidade, podendo exercê-los nos termos da Política de Privacidade da plataforma.
________________________________________
### 6. Momento da Avaliação"""

    conteudo = conteudo.replace(old_s5, new_s5)

    # ===================================================================
    # 3. ENRIQUECER SEÇÃO 12 — Conduta dos Usuários
    #    Adicionar referências ao Marco Civil e CDC
    # ===================================================================
    old_s12_end = """Caso sejam identificadas condutas abusivas, a plataforma poderá aplicar medidas como:
•	remoção de avaliações;
•	suspensão de conta;
•	exclusão de cadastro.
________________________________________
### 13. Responsabilidade da Plataforma"""

    new_s12_end = """Caso sejam identificadas condutas abusivas, a plataforma poderá aplicar medidas como:
•	remoção de avaliações;
•	suspensão de conta;
•	exclusão de cadastro.

As condutas abusivas praticadas por meio da plataforma sujeitam o infrator às responsabilidades previstas no ordenamento jurídico brasileiro, incluindo:
- **Marco Civil da Internet** (Art. 21 e 22 da Lei n. 12.965/2014) — que prevê a responsabilização civil por danos decorrentes de conteúdo gerado por terceiros;
- **Código de Defesa do Consumidor** (Art. 39 da Lei n. 8.078/1990) — que veda práticas abusivas nas relações de consumo;
- **Código Civil Brasileiro** (Arts. 186 e 927) — que estabelece o dever de reparação por atos ilícitos que causem dano a outrem;
- **Código Penal Brasileiro** (Arts. 138 a 140) — nos casos em que as avaliações configurem calúnia, difamação ou injúria.

A plataforma cooperará com autoridades competentes mediante requisição judicial ou administrativa fundamentada, em conformidade com o Art. 10 do Marco Civil da Internet e o Art. 22 da mesma lei.
________________________________________
### 13. Responsabilidade da Plataforma"""

    conteudo = conteudo.replace(old_s12_end, new_s12_end)

    # ===================================================================
    # 4. ENRIQUECER SEÇÃO 13 — Responsabilidade da Plataforma
    #    Adicionar referência ao Marco Civil Art. 18/19
    # ===================================================================
    old_s13 = """Eventuais conflitos entre atletas e organizadores devem ser resolvidos diretamente entre as partes envolvidas.
________________________________________
### 14. Isenção de Responsabilidade"""

    new_s13 = """Eventuais conflitos entre atletas e organizadores devem ser resolvidos diretamente entre as partes envolvidas.

Nos termos do **Art. 19 do Marco Civil da Internet** (Lei n. 12.965/2014), a plataforma somente poderá ser responsabilizada civilmente por danos decorrentes de conteúdo gerado por terceiros se, após ordem judicial específica, não tomar as providências para tornar indisponível o conteúdo apontado como infringente. A Ranking Run mantém canais de atendimento para recebimento de notificações e solicitações de correção (Cláusula 24 deste Regulamento).

A limitação de responsabilidade da plataforma encontra amparo também no **Art. 18 do Marco Civil da Internet**, que estabelece que o provedor de conexão à internet não será responsabilizado civilmente por danos decorrentes de conteúdo gerado por terceiros.
________________________________________
### 14. Isenção de Responsabilidade"""

    conteudo = conteudo.replace(old_s13, new_s13)

    # ===================================================================
    # 5. ENRIQUECER SEÇÃO 14 — Isenção de Responsabilidade
    #    Adicionar referências constitucionais
    # ===================================================================
    old_s14 = """Dessa forma, o ranking não deve ser interpretado como certificação técnica, recomendação oficial ou garantia de qualidade.
________________________________________
### 15. Direito de Moderação"""

    new_s14 = """Dessa forma, o ranking não deve ser interpretado como certificação técnica, recomendação oficial ou garantia de qualidade.

A isenção de responsabilidade aqui prevista encontra fundamento nos seguintes dispositivos legais:
- **Art. 5°, IV e IX da Constituição Federal** — que asseguram a liberdade de manifestação do pensamento e de expressão, desde que não anônima;
- **Art. 19 do Marco Civil da Internet** — que limita a responsabilidade do provedor de aplicações por conteúdo gerado por terceiros;
- **Art. 14, §3° do CDC** — que exclui a responsabilidade do fornecedor quando prova a culpa exclusiva do consumidor ou de terceiro.

As avaliações registradas na plataforma constituem manifestações protegidas pelo direito fundamental à liberdade de expressão (Art. 5°, IV, CF/88), ressalvados os casos de abuso tipificados na legislação penal e civil.
________________________________________
### 15. Direito de Moderação"""

    conteudo = conteudo.replace(old_s14, new_s14)

    # ===================================================================
    # 6. ENRIQUECER SEÇÃO 19 — Liberdade de Opinião
    #    Adicionar fundamentação constitucional e Marco Civil
    # ===================================================================
    old_s19 = """A Ranking Run não se responsabiliza pelo conteúdo opinativo das avaliações registradas pelos usuários, uma vez que tais manifestações são produzidas diretamente pelos próprios atletas cadastrados.
Caso algum conteúdo específico seja considerado ofensivo, ilegal ou em desacordo com este regulamento, poderá ser analisado pela equipe da plataforma mediante solicitação formal."""

    new_s19 = """A Ranking Run não se responsabiliza pelo conteúdo opinativo das avaliações registradas pelos usuários, uma vez que tais manifestações são produzidas diretamente pelos próprios atletas cadastrados, em exercício do direito fundamental à liberdade de expressão previsto no **Art. 5°, incisos IV e IX, da Constituição Federal de 1988**, e regulamentado pelo **Art. 19 do Marco Civil da Internet** (Lei n. 12.965/2014).

O exercício da liberdade de opinião encontra-se também protegido pelo **Art. 3° do Marco Civil da Internet**, que estabelece como princípio disciplinador do uso da internet no Brasil a garantia da liberdade de expressão, comunicação e manifestação de pensamento, nos termos da Constituição Federal.

Caso algum conteúdo específico seja considerado ofensivo, ilegal ou em desacordo com este regulamento, poderá ser analisado pela equipe da plataforma mediante solicitação formal, em observância ao procedimento previsto nos **Arts. 19 e 21 do Marco Civil da Internet** e respeitados os direitos constitucionais de ampla defesa e contraditório (Art. 5°, LV, CF/88)."""

    conteudo = conteudo.replace(old_s19, new_s19)

    # ===================================================================
    # 7. ENRIQUECER SEÇÃO 22 — Foro e Legislação Aplicável
    #    Adicionar referências legais explícitas
    # ===================================================================
    old_s22 = """### 22. Cláusula de Foro e Legislação Aplicável
Este regulamento é regido pelas leis da República Federativa do Brasil.
Eventuais controvérsias decorrentes da utilização da plataforma deverão ser resolvidas, preferencialmente, por meio de solução amigável entre as partes.
Na impossibilidade de acordo, fica eleito o foro da comarca da sede administrativa da plataforma Ranking Run para dirimir quaisquer questões relacionadas ao presente regulamento, com renúncia expressa de qualquer outro foro, por mais privilegiado que seja."""

    new_s22 = """### 22. Cláusula de Foro e Legislação Aplicável
Este regulamento é regido pelas leis da República Federativa do Brasil, com especial observância à:
- **Constituição da República Federativa do Brasil de 1988**;
- **Lei Geral de Proteção de Dados Pessoais** (Lei n. 13.709/2018 — LGPD);
- **Marco Civil da Internet** (Lei n. 12.965/2014);
- **Código de Defesa do Consumidor** (Lei n. 8.078/1990);
- **Decreto n. 8.771/2016** (regulamentação do Marco Civil);
- **Código Civil Brasileiro** (Lei n. 10.406/2002);
- **Lei de Direitos Autorais** (Lei n. 9.610/1998);
- **Lei de Propriedade Industrial** (Lei n. 9.279/1996).

Eventuais controvérsias decorrentes da utilização da plataforma deverão ser resolvidas, preferencialmente, por meio de solução amigável entre as partes, podendo as partes recorrer, se desejarem, a mecanismos alternativos de resolução de conflitos, como mediação ou arbitragem, nos termos da **Lei n. 13.140/2015** (Lei de Mediação) e da **Lei n. 9.307/1996** (Lei de Arbitragem).
Na impossibilidade de acordo, fica eleito o foro da comarca da sede administrativa da plataforma Ranking Run para dirimir quaisquer questões relacionadas ao presente regulamento, com renúncia expressa de qualquer outro foro, por mais privilegiado que seja."""

    conteudo = conteudo.replace(old_s22, new_s22)

    # ===================================================================
    # 8. ENRIQUECER SEÇÃO 23 — Participação Voluntária
    #    Adicionar referência à liberdade de informação (CF)
    # ===================================================================
    old_s23_end = """Dessa forma, a presença de uma corrida no Ranking das Corridas da plataforma Ranking Run não depende de autorização prévia do organizador, uma vez que se trata de informação de interesse público relacionada a eventos esportivos realizados em espaços públicos ou abertos à participação da comunidade esportiva."""

    new_s23_end = """Dessa forma, a presença de uma corrida no Ranking das Corridas da plataforma Ranking Run não depende de autorização prévia do organizador, uma vez que se trata de informação de interesse público relacionada a eventos esportivos realizados em espaços públicos ou abertos à participação da comunidade esportiva.

Este entendimento encontra fundamento no **direito constitucional de acesso à informação** (Art. 5°, XIV e XXXIII, CF/88) e no **princípio da publicidade** aplicável a eventos realizados em espaços públicos, sendo respeitado o direito de retificação previsto na Cláusula 24 deste Regulamento."""

    conteudo = conteudo.replace(old_s23_end, new_s23_end)

    # ===================================================================
    # 9. ENRIQUECER SEÇÃO 27 — Proibição de Uso Comercial Indevido
    #    Adicionar referência à propriedade intelectual
    # ===================================================================
    old_s27_end = """Caso uma corrida utilize sua posição no ranking para fins promocionais, deverá fazê-lo de forma transparente, mencionando que a classificação se refere exclusivamente às avaliações registradas pelos usuários da plataforma."""

    new_s27_end = """Caso uma corrida utilize sua posição no ranking para fins promocionais, deverá fazê-lo de forma transparente, mencionando que a classificação se refere exclusivamente às avaliações registradas pelos usuários da plataforma.

O uso indevido do nome, logotipo, marca ou qualquer elemento visual da Ranking Run está sujeito às sanções previstas na **Lei de Propriedade Industrial** (Lei n. 9.279/1996) e na **Lei de Direitos Autorais** (Lei n. 9.610/1998), podendo a plataforma adotar as medidas judiciais cabíveis para proteção de sua propriedade intelectual, incluindo a busca e apreensão de materiais e a indenização por danos materiais e morais."""

    conteudo = conteudo.replace(old_s27_end, new_s27_end)

    # ===================================================================
    # 10. ENRIQUECER CARTA DE PRINCÍPIOS — Propósito da Plataforma
    #     Adicionar fundamentação legal
    # ===================================================================
    old_carta = """## 1. Propósito da Plataforma
A plataforma Ranking Run nasce com o propósito de fortalecer a comunidade da corrida de rua por meio da transparência, do compartilhamento de experiências entre atletas e da valorização dos eventos esportivos.
O sistema de avaliações e rankings foi criado para oferecer aos corredores um espaço onde possam registrar suas percepções sobre as corridas que participam, contribuindo para a construção de um ambiente mais informativo e colaborativo."""

    new_carta = """## 1. Propósito da Plataforma
A plataforma Ranking Run nasce com o propósito de fortalecer a comunidade da corrida de rua por meio da transparência, do compartilhamento de experiências entre atletas e da valorização dos eventos esportivos.
O sistema de avaliações e rankings foi criado para oferecer aos corredores um espaço onde possam registrar suas percepções sobre as corridas que participam, contribuindo para a construção de um ambiente mais informativo e colaborativo.

O propósito da plataforma fundamenta-se nos princípios constitucionais de **livre iniciativa** (Art. 170, caput e parágrafo único, CF/88), **liberdade de expressão** (Art. 5°, IV e IX, CF/88), **direito de acesso à informação** (Art. 5°, XIV, CF/88) e **proteção dos dados pessoais como direito fundamental** (Art. 5°, LXXIX, CF/88).

A Ranking Run reconhece e respeita a autoridade das entidades esportivas oficiais previstas na **Lei n. 9.615/1998 (Lei Pelé)** e atua exclusivamente como plataforma complementar de caráter informativo, sem qualquer pretensão de exercer atividades regulatórias ou de governança esportiva."""

    conteudo = conteudo.replace(old_carta, new_carta)

    # ===================================================================
    # 11. ENRIQUECER POLÍTICA DE INTEGRIDADE — Introdução
    #     Adicionar referência à LGPD e Marco Civil
    # ===================================================================
    old_integ = """Esta política tem como objetivo:
•	assegurar que o ranking reflita de forma legítima a percepção da comunidade de corredores;
•	prevenir e combater tentativas de manipulação do sistema de avaliações;
•	garantir a consistência estatística das classificações apresentadas;
•	estabelecer diretrizes claras de governança da plataforma."""

    new_integ = """Esta política tem como objetivo:
•	assegurar que o ranking reflita de forma legítima a percepção da comunidade de corredores;
•	prevenir e combater tentativas de manipulação do sistema de avaliações;
•	garantir a consistência estatística das classificações apresentadas;
•	estabelecer diretrizes claras de governança da plataforma;
•	proteger os dados pessoais dos usuários em conformidade com a **LGPD** (Lei n. 13.709/2018) e o **Marco Civil da Internet** (Lei n. 12.965/2014);
•	assegurar a conformidade das operações da plataforma com o ordenamento jurídico brasileiro e as melhores práticas internacionais de proteção de dados (**GDPR**, Regulamento UE 2016/679)."""

    conteudo = conteudo.replace(old_integ, new_integ)

    # ===================================================================
    # SALVAR
    # ===================================================================
    versao_atual = reg.get("versao", "1.3")
    partes = versao_atual.split(".")
    partes[-1] = str(int(partes[-1]) + 1)
    nova_versao = ".".join(partes)

    await db.configuracoes.update_one(
        {"tipo": "regulamento"},
        {"$set": {
            "conteudo": conteudo,
            "versao": nova_versao,
            "data_atualizacao": datetime.now(timezone.utc).isoformat(),
            "atualizado_por": "sistema",
            "atualizado_por_nome": "Blindagem Jurídica Automatizada"
        }}
    )

    print(f"Regulamento atualizado com sucesso!")
    print(f"Versão: {versao_atual} -> {nova_versao}")
    print(f"Tamanho: {len(reg.get('conteudo',''))} -> {len(conteudo)} caracteres")

    # Verificação
    verificacao = await db.configuracoes.find_one({"tipo": "regulamento"}, {"_id": 0, "versao": 1})
    print(f"Verificação DB: versão = {verificacao.get('versao')}")

asyncio.run(enriquecer_regulamento())
