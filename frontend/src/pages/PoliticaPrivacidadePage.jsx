import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Shield, ArrowLeft, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

const sections = [
  {
    id: 'sobre',
    title: '1. Sobre o Ranking Run',
    content: `O Ranking Run é uma plataforma digital voltada para atletas de corrida de rua, com o objetivo de centralizar informações, promover engajamento e facilitar a visualização de dados esportivos provenientes de integrações autorizadas pelo usuário.

A plataforma nasceu com o propósito de fortalecer a corrida de rua, conectando atletas e facilitando o acesso às informações. Nosso objetivo nunca foi, e nunca será, substituir, replicar, interferir ou competir com federações, confederações, associações, entidades oficiais, organizações esportivas oficiais, ou órgãos dirigentes ou reguladores. Pelo contrário, buscamos atuar como uma plataforma complementar, agregando valor ao ecossistema e incentivando ainda mais a prática esportiva.

Respeitamos e reconhecemos a autoridade dessas organizações e nosso objetivo é apenas fornecer ferramentas adicionais que melhorem a acessibilidade aos dados, o envolvimento dos atletas e a visibilidade dentro da comunidade.`
  },
  {
    id: 'dados',
    title: '2. Dados Coletados',
    content: `O Ranking Run coleta e trata os seguintes dados pessoais, sempre mediante consentimento do titular:

a) Dados de Cadastro: nome completo, e-mail, cidade, estado, data de nascimento, sexo/gênero, equipe/assessoria esportiva.

b) Dados de Atividade Esportiva: resultados de corridas (tempo, posição, categoria), distâncias percorridas, histórico de participações em eventos, dados de desempenho e estatísticas.

c) Dados de Integração com Terceiros: atividades provenientes do Strava (mediante autorização OAuth), incluindo distância percorrida, tempo de atividade, tipo de atividade, data e informações públicas do perfil.

d) Dados de Navegação: informações de acesso, logs de utilização, endereço IP, tipo de dispositivo e navegador, exclusivamente para fins de segurança e melhoria da plataforma.

e) Dados de Pagamento: processados exclusivamente por intermediadores de pagamento autorizados (Stripe e similares). O Ranking Run NÃO armazena dados de cartão de crédito, débito ou informações financeiras sensíveis em seus servidores.`
  },
  {
    id: 'finalidade',
    title: '3. Finalidade do Tratamento de Dados',
    content: `Os dados pessoais são tratados para as seguintes finalidades específicas, nos termos do artigo 7 da LGPD:

a) Execução do Serviço (Art. 7, V, LGPD): viabilizar o funcionamento da plataforma, incluindo ranking, raio-x do atleta, feed social e painéis administrativos.

b) Consentimento do Titular (Art. 7, I, LGPD): integração com serviços de terceiros (Strava), envio de comunicações e notificações.

c) Legítimo Interesse (Art. 7, IX, LGPD): melhoria contínua da plataforma, análises estatísticas agregadas e geração de relatórios de desempenho.

d) Cumprimento de Obrigação Legal (Art. 7, II, LGPD): manutenção de registros conforme exigências do Marco Civil da Internet (Lei n. 12.965/2014) e regulamentações aplicáveis.

O Ranking Run NÃO utiliza os dados para:
- Venda ou comercialização a terceiros;
- Publicidade direcionada baseada em dados de terceiros;
- Perfilamento discriminatório;
- Qualquer finalidade não expressamente prevista nesta Política.`
  },
  {
    id: 'strava',
    title: '4. Integração com o Strava',
    content: `O Ranking Run utiliza a API oficial do Strava para permitir que os usuários conectem suas contas e visualizem suas próprias atividades dentro da plataforma. Ao conectar sua conta Strava, o usuário autoriza o Ranking Run a acessar dados básicos de atividades, incluindo:

- Distância percorrida
- Tempo de atividade
- Tipo de atividade
- Data da atividade
- Informações públicas associadas ao perfil

Esses dados são acessados exclusivamente mediante autorização do usuário, através do fluxo oficial de autenticação do Strava (OAuth 2.0).

O Ranking Run pode exibir informações provenientes de clubes do Strava dos quais o usuário já faz parte, como o clube oficial: https://www.strava.com/clubs/rankingrun. Essas informações são exibidas dentro da plataforma apenas para facilitar o acesso e visualização, sem alteração ou redistribuição indevida.

O Ranking Run utiliza a API do Strava de acordo com os termos estabelecidos pelo próprio Strava, disponíveis em: https://www.strava.com/legal/api. O Ranking Run não é afiliado oficialmente ao Strava, mas utiliza seus serviços de forma autorizada via API.

O usuário pode a qualquer momento desconectar sua conta Strava ou revogar permissões diretamente no Strava. Após a desconexão, o Ranking Run interrompe imediatamente a sincronização de dados.`
  },
  {
    id: 'direitos',
    title: '5. Direitos do Titular dos Dados',
    content: `Em conformidade com os artigos 17 a 22 da LGPD, o titular dos dados possui os seguintes direitos, que podem ser exercidos a qualquer momento:

a) Confirmação da existência de tratamento (Art. 18, I);
b) Acesso aos dados (Art. 18, II);
c) Correção de dados incompletos, inexatos ou desatualizados (Art. 18, III);
d) Anonimização, bloqueio ou eliminação de dados desnecessários, excessivos ou tratados em desconformidade (Art. 18, IV);
e) Portabilidade dos dados a outro fornecedor de serviço (Art. 18, V);
f) Eliminação dos dados pessoais tratados com base no consentimento (Art. 18, VI);
g) Informação das entidades públicas e privadas com as quais o controlador realizou uso compartilhado de dados (Art. 18, VII);
h) Informação sobre a possibilidade de não fornecer consentimento e sobre as consequências da negativa (Art. 18, VIII);
i) Revogação do consentimento a qualquer momento (Art. 18, IX).

Para exercer qualquer desses direitos, o titular pode entrar em contato através do e-mail: suporte@rankingrun.com.br. O prazo para atendimento é de até 15 (quinze) dias úteis, conforme previsto na legislação.`
  },
  {
    id: 'seguranca',
    title: '6. Segurança e Armazenamento',
    content: `O Ranking Run adota medidas técnicas e administrativas aptas a proteger os dados pessoais de acessos não autorizados e de situações acidentais ou ilícitas de destruição, perda, alteração, comunicação ou qualquer forma de tratamento inadequado ou ilícito (Art. 46, LGPD), incluindo:

a) Criptografia de dados sensíveis em trânsito (HTTPS/TLS) e em repouso;
b) Controle de acesso restrito baseado em funções (RBAC) com autenticação JWT;
c) Monitoramento contínuo de segurança e detecção de atividades suspeitas;
d) Backups regulares com redundância geográfica;
e) Separação de ambientes de desenvolvimento, teste e produção;
f) Política de senha forte e autenticação multifator para administradores;
g) Revisão periódica de vulnerabilidades e atualizações de segurança.

Os dados são armazenados em servidores seguros com infraestrutura em nuvem certificada, em conformidade com padrões internacionais de segurança da informação.`
  },
  {
    id: 'compartilhamento',
    title: '7. Compartilhamento de Dados',
    content: `O Ranking Run NÃO comercializa, aluga ou compartilha dados pessoais com terceiros para fins comerciais.

O compartilhamento de dados ocorre exclusivamente nas seguintes hipóteses:

a) Processamento de pagamentos: dados transacionais são compartilhados com processadores de pagamento (Stripe) exclusivamente para a efetivação de transações financeiras, sujeitos às políticas de privacidade e segurança desses processadores;

b) Integração Strava: dados são trocados com a API do Strava conforme autorização específica do usuário;

c) Cumprimento legal: quando exigido por autoridade competente, ordem judicial ou obrigação legal expressa (Art. 7, II, LGPD);

d) Proteção de direitos: quando necessário para proteger os direitos, a propriedade ou a segurança do Ranking Run, de seus usuários ou do público.`
  },
  {
    id: 'lgpd',
    title: '8. Conformidade Legal',
    content: `O Ranking Run opera em total conformidade com o ordenamento jurídico brasileiro, especialmente:

a) Lei Geral de Proteção de Dados Pessoais (Lei n. 13.709/2018 — LGPD): garante transparência, consentimento, finalidade, adequação, necessidade, livre acesso, qualidade dos dados, segurança, prevenção e não discriminação no tratamento de dados pessoais.

b) Marco Civil da Internet (Lei n. 12.965/2014): respeita a inviolabilidade da intimidade e da vida privada, a proteção dos dados pessoais e a preservação da estabilidade, segurança e funcionalidade da rede.

c) Código de Defesa do Consumidor (Lei n. 8.078/1990): assegura ao consumidor a proteção contra práticas abusivas, o direito à informação adequada e clara e a proteção contra publicidade enganosa.

d) Constituição da República Federativa do Brasil (Art. 5, X, XII e LXXIX): assegura a inviolabilidade da intimidade, da vida privada, da honra e da imagem das pessoas, o sigilo das comunicações e a proteção dos dados pessoais como direito fundamental.

e) Regulamento Geral sobre a Proteção de Dados da União Europeia (GDPR, Regulamento UE 2016/679): embora a plataforma opere primariamente no Brasil, adota as melhores práticas internacionais de proteção de dados como referência complementar.

f) Decreto n. 8.771/2016: regulamenta o Marco Civil da Internet e estabelece diretrizes sobre guarda de dados pessoais, padrões de segurança e procedimentos para apuração de infrações.`
  },
  {
    id: 'cookies',
    title: '9. Cookies e Tecnologias de Rastreamento',
    content: `O Ranking Run utiliza cookies e tecnologias similares exclusivamente para:

a) Manutenção da sessão do usuário (cookies de autenticação);
b) Preferências de interface (modo escuro/claro);
c) Análise de uso agregado para melhoria da experiência.

Não utilizamos cookies de rastreamento publicitário de terceiros. O usuário pode configurar seu navegador para recusar cookies, embora isso possa afetar a funcionalidade da plataforma.`
  },
  {
    id: 'menores',
    title: '10. Proteção de Menores',
    content: `O Ranking Run não se destina a menores de 14 anos. O tratamento de dados pessoais de crianças e adolescentes, quando aplicável, será realizado em conformidade com o artigo 14 da LGPD, sempre com o consentimento específico e em destaque dado por pelo menos um dos pais ou pelo responsável legal.`
  },
  {
    id: 'retencao',
    title: '11. Retenção e Eliminação de Dados',
    content: `Os dados pessoais são armazenados pelo tempo necessário ao cumprimento das finalidades descritas nesta Política, observando os seguintes critérios:

a) Dados de conta ativa: mantidos enquanto a conta estiver ativa;
b) Dados de conta inativa: eliminados após 24 meses de inatividade, salvo obrigação legal de retenção;
c) Registros de acesso: mantidos por 6 meses conforme o Marco Civil da Internet;
d) Dados financeiros: mantidos pelo prazo legal exigido pela legislação tributária.

O titular pode solicitar a eliminação de seus dados a qualquer momento, sendo a solicitação atendida no prazo de 15 dias úteis, exceto quando a retenção for exigida por lei.`
  },
  {
    id: 'incidentes',
    title: '12. Incidentes de Segurança',
    content: `Em caso de incidente de segurança que possa acarretar risco ou dano relevante aos titulares, o Ranking Run compromete-se a:

a) Comunicar a Autoridade Nacional de Proteção de Dados (ANPD) em prazo razoável (Art. 48, LGPD);
b) Comunicar ao titular dos dados afetados;
c) Descrever a natureza dos dados pessoais afetados;
d) Indicar as medidas técnicas e de segurança utilizadas e as medidas para reverter ou mitigar os efeitos do incidente.`
  },
  {
    id: 'transferencia',
    title: '13. Transferência Internacional de Dados',
    content: `Eventualmente, dados pessoais podem ser processados em servidores localizados fora do Brasil, exclusivamente para fins de armazenamento em nuvem e processamento técnico. Nesses casos, asseguramos que:

a) O país de destino proporciona grau de proteção de dados pessoais adequado ao previsto na LGPD (Art. 33, I);
b) São utilizadas cláusulas contratuais padrão que garantam o cumprimento dos princípios e direitos do titular (Art. 33, II, b);
c) O controlador oferece garantias de observância dos princípios e direitos do titular através de verificação e monitoramento constantes.`
  },
  {
    id: 'complementar',
    title: '14. Natureza Complementar da Plataforma',
    content: `O Ranking Run reafirma seu compromisso como plataforma complementar ao ecossistema esportivo. Declaramos expressamente que:

a) Não somos, não pretendemos ser e não nos apresentamos como federação, confederação, associação, liga ou qualquer tipo de entidade reguladora do esporte;

b) Não interferimos, substituímos, replicamos ou competimos com as atividades, competências ou atribuições de organizações esportivas oficiais, órgãos dirigentes ou entidades reguladoras do esporte em qualquer nível (municipal, estadual, nacional ou internacional);

c) Os rankings, classificações e análises gerados pela plataforma têm caráter exclusivamente informativo e de entretenimento, não possuindo qualquer valor oficial, homologatório ou regulatório;

d) Atuamos como ferramenta de apoio à comunidade de corrida de rua, promovendo engajamento, visibilidade e acesso facilitado a informações já disponíveis publicamente;

e) Respeitamos integralmente a autonomia e a autoridade das entidades esportivas competentes, e nos colocamos à disposição para colaboração dentro dos limites legais.`
  },
  {
    id: 'responsabilidade',
    title: '15. Limitação de Responsabilidade',
    content: `O Ranking Run emprega todos os esforços para manter a precisão e atualidade das informações disponibilizadas na plataforma. Contudo:

a) Os dados esportivos são inseridos por usuários ou obtidos de fontes terceiras (Strava, organizadores de eventos), podendo conter imprecisões. O Ranking Run não garante a exatidão absoluta dessas informações;

b) A plataforma não se responsabiliza por decisões tomadas com base exclusivamente nos dados aqui apresentados;

c) Rankings e classificações são gerados por algoritmos proprietários e não possuem valor oficial;

d) O Ranking Run reserva-se o direito de suspender, modificar ou encerrar funcionalidades a qualquer momento, mediante aviso prévio razoável aos usuários.`
  },
  {
    id: 'propriedade',
    title: '16. Propriedade Intelectual',
    content: `Todo o conteúdo da plataforma — incluindo, mas não se limitando a, textos, gráficos, logotipos, ícones, imagens, compilações de dados, software e algoritmos — é de propriedade exclusiva do Ranking Run ou de seus licenciadores, protegido pela Lei de Direitos Autorais (Lei n. 9.610/1998) e pela Lei de Propriedade Industrial (Lei n. 9.279/1996).

É expressamente proibida a reprodução, distribuição, modificação, engenharia reversa ou utilização não autorizada de qualquer conteúdo da plataforma sem prévia autorização por escrito.`
  },
  {
    id: 'alteracoes',
    title: '17. Alterações na Política',
    content: `Esta Política pode ser atualizada a qualquer momento para refletir alterações legislativas, decisões judiciais, orientações da ANPD ou melhorias nos serviços. As alterações entram em vigor imediatamente após a publicação na plataforma.

Recomendamos a revisão periódica desta Política. A continuidade do uso da plataforma após alterações constitui aceitação dos novos termos.`
  },
  {
    id: 'contato',
    title: '18. Contato e Encarregado de Dados (DPO)',
    content: `Para exercer seus direitos, esclarecer dúvidas ou realizar solicitações relacionadas ao tratamento de dados pessoais, entre em contato:

E-mail: suporte@rankingrun.com.br

O Ranking Run designa um Encarregado de Proteção de Dados (DPO), conforme artigo 41 da LGPD, responsável por aceitar reclamações e comunicações dos titulares, prestar esclarecimentos e adotar providências. O contato do DPO é realizado através do mesmo canal de e-mail indicado acima.`
  },
  {
    id: 'foro',
    title: '19. Foro e Legislação Aplicável',
    content: `Esta Política de Privacidade é regida pela legislação da República Federativa do Brasil. Fica eleito o foro da Comarca da sede do Ranking Run para dirimir quaisquer controvérsias oriundas deste documento, com exclusão de qualquer outro, por mais privilegiado que seja.`
  },
];

export default function PoliticaPrivacidadePage() {
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState({});

  const toggle = (id) => setExpanded(p => ({ ...p, [id]: !p[id] }));

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
      {/* Header */}
      <div className="bg-slate-900 text-white">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <Button variant="ghost" onClick={() => navigate(-1)} className="text-slate-400 hover:text-white mb-4" data-testid="btn-voltar-politica">
            <ArrowLeft className="w-4 h-4 mr-2" />Voltar
          </Button>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-600 rounded-xl">
              <Shield className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold">Política de Privacidade</h1>
              <p className="text-slate-400 text-sm mt-1">Ranking Run — Última atualização: Abril 2026</p>
            </div>
          </div>
        </div>
      </div>

      {/* Conteúdo */}
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-3" data-testid="politica-privacidade-content">
        {/* Preâmbulo */}
        <Card className="border-emerald-200 dark:border-emerald-900 bg-emerald-50/50 dark:bg-emerald-950/20">
          <CardContent className="p-5">
            <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              A presente Política de Privacidade descreve como o <strong>Ranking Run</strong> coleta, utiliza, armazena e protege os dados dos usuários, em conformidade com a Lei Geral de Proteção de Dados Pessoais (Lei n. 13.709/2018 — LGPD), o Marco Civil da Internet (Lei n. 12.965/2014), o Código de Defesa do Consumidor (Lei n. 8.078/1990) e demais normas aplicáveis.
            </p>
            <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed mt-3">
              Prezamos pela <strong>transparência</strong> e pela <strong>proteção de todos os dados</strong> confiados à nossa plataforma. Ao utilizar nossos serviços, você concorda com os termos aqui descritos.
            </p>
          </CardContent>
        </Card>

        {/* Seções */}
        {sections.map(s => (
          <Card key={s.id} className="overflow-hidden transition-shadow hover:shadow-md" data-testid={`section-${s.id}`}>
            <button
              className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
              onClick={() => toggle(s.id)}
            >
              <h2 className="text-base font-bold text-slate-800 dark:text-white">{s.title}</h2>
              {expanded[s.id] ? <ChevronUp className="w-5 h-5 text-slate-400 shrink-0" /> : <ChevronDown className="w-5 h-5 text-slate-400 shrink-0" />}
            </button>
            {expanded[s.id] && (
              <CardContent className="pt-0 pb-5 px-5 border-t border-slate-100 dark:border-slate-800">
                <div className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed whitespace-pre-line mt-3">
                  {s.content}
                </div>
              </CardContent>
            )}
          </Card>
        ))}

        {/* Links Externos */}
        <Card className="bg-slate-900 text-white border-0">
          <CardContent className="p-5 space-y-3">
            <h3 className="font-bold text-lg">Links de Referência</h3>
            <div className="flex flex-col gap-2">
              <a href="https://www.strava.com/legal/api" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-sm inline-flex items-center gap-1">
                <ExternalLink className="w-3 h-3" />Termos de Uso da API do Strava
              </a>
              <a href="https://www.strava.com/legal/privacy" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-sm inline-flex items-center gap-1">
                <ExternalLink className="w-3 h-3" />Política de Privacidade do Strava
              </a>
              <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-sm inline-flex items-center gap-1">
                <ExternalLink className="w-3 h-3" />Lei Geral de Proteção de Dados (LGPD)
              </a>
              <a href="https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l12965.htm" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-sm inline-flex items-center gap-1">
                <ExternalLink className="w-3 h-3" />Marco Civil da Internet
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center text-xs text-slate-400 py-4">
          Ranking Run — Todos os direitos reservados — 2026
        </p>
      </div>
    </div>
  );
}
