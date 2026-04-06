import { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { ScrollText, CheckCircle2 } from 'lucide-react';

const CadastroTermoModal = ({ open, onOpenChange, onAccept }) => {
  const termoRef = useRef(null);
  const [scrolledToBottom, setScrolledToBottom] = useState(false);

  const handleTermoScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    if (scrollHeight - scrollTop - clientHeight < 50) {
      setScrolledToBottom(true);
    }
  };

  const handleAceitarTermo = () => {
    setScrolledToBottom(false);
    onAccept();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ScrollText className="w-5 h-5 text-emerald-600" />
            Regulamento da Plataforma Ranking Run
          </DialogTitle>
          <DialogDescription>
            Leia atentamente o regulamento abaixo. Role até o final para habilitar o botão de aceite.
          </DialogDescription>
        </DialogHeader>
        
        <div 
          ref={termoRef}
          onScroll={handleTermoScroll}
          className="flex-1 overflow-y-auto border rounded-lg p-4 bg-slate-50 dark:bg-slate-900 text-xs leading-relaxed max-h-[50vh]"
        >
          <div className="space-y-4 text-slate-700 dark:text-slate-300">
            <h3 className="font-bold text-sm text-emerald-700">REGULAMENTO OFICIAL DA PLATAFORMA RANKING RUN</h3>
            
            <section>
              <h4 className="font-semibold text-emerald-600">1. DISPOSIÇÕES GERAIS</h4>
              <p>1.1. A Plataforma Ranking Run é um sistema de ranqueamento de atletas de corrida de rua, desenvolvido para promover a competição saudável e o reconhecimento dos participantes.</p>
              <p>1.2. Ao se cadastrar, o atleta declara ter lido, compreendido e aceito integralmente este regulamento.</p>
              <p>1.3. A Ranking Run reserva-se o direito de alterar este regulamento a qualquer momento, mediante comunicação prévia aos usuários.</p>
            </section>

            <section>
              <h4 className="font-semibold text-emerald-600">2. CADASTRO E PARTICIPAÇÃO</h4>
              <p>2.1. O cadastro é gratuito e destinado a atletas maiores de 18 anos ou menores com autorização dos responsáveis legais.</p>
              <p>2.2. Os dados fornecidos devem ser verdadeiros e atualizados. Informações falsas podem resultar em exclusão da plataforma.</p>
              <p>2.3. Cada pessoa física pode ter apenas um cadastro ativo na plataforma.</p>
              <p>2.4. O atleta é responsável pela segurança de suas credenciais de acesso (e-mail e senha).</p>
            </section>

            <section>
              <h4 className="font-semibold text-emerald-600">3. MODALIDADES DE PARTICIPAÇÃO</h4>
              <p>3.1. RANKING PROFISSIONAL/AMADOR: Pontuação baseada na colocação em provas oficiais (1º ao 10º lugar).</p>
              <p>3.2. RANKING DA GALERA: Pontuação baseada exclusivamente na distância percorrida, independente da colocação.</p>
              <p>3.3. RANKING DE EQUIPES/ASSESSORIAS: Pontuação coletiva baseada nos resultados dos atletas vinculados.</p>
            </section>

            <section>
              <h4 className="font-semibold text-emerald-600">4. SISTEMA DE PONTUAÇÃO</h4>
              <p>4.1. PROFISSIONAL/AMADOR: 1º lugar = 10pts, 2º = 9pts, 3º = 8pts, até 10º = 1pt.</p>
              <p>4.2. GALERA: 5km a 9km = 5 pts, 10km a 20km = 7 pts, 21km ou mais = 9 pts.</p>
              <p>4.3. EQUIPES: Atleta cadastrado = +0,5pt, Resultado lançado = +1,0pt, Pódio (2º-5º) = +0,5pt, 1º lugar = +1,0pt.</p>
              <p>4.4. Os pontos são acumulados por período (mensal, anual e histórico).</p>
            </section>

            <section>
              <h4 className="font-semibold text-emerald-600">5. SUBMISSÃO DE RESULTADOS</h4>
              <p>5.1. Os resultados devem ser submetidos com documentação comprobatória (foto do resultado oficial, print do chip time, etc.).</p>
              <p>5.2. Resultados fraudulentos ou adulterados resultarão em exclusão imediata e permanente da plataforma.</p>
              <p>5.3. A equipe de moderação da Ranking Run reserva-se o direito de solicitar documentação adicional.</p>
              <p>5.4. Resultados não aprovados não geram pontuação e não aparecem no ranking.</p>
            </section>

            <section>
              <h4 className="font-semibold text-emerald-600">6. EQUIPES E ASSESSORIAS</h4>
              <p>6.1. Cada atleta pode estar vinculado a apenas uma equipe/assessoria por vez.</p>
              <p>6.2. A transferência de equipe só pode ser realizada a cada 15 dias.</p>
              <p>6.3. O responsável/dono da assessoria não pode transferir-se para outra equipe enquanto for responsável legal.</p>
              <p>6.4. A exclusão de uma assessoria remove automaticamente todos os pontos vinculados.</p>
            </section>

            <section>
              <h4 className="font-semibold text-emerald-600">7. AVALIAÇÃO DE CORRIDAS</h4>
              <p>7.1. Apenas atletas que participaram efetivamente de uma corrida podem avaliá-la.</p>
              <p>7.2. Avaliações fraudulentas podem caracterizar falsidade ideológica e gerar responsabilização civil ou legal.</p>
              <p>7.3. Cada atleta pode avaliar cada corrida apenas uma vez.</p>
            </section>

            <section>
              <h4 className="font-semibold text-emerald-600">8. PRIVACIDADE E DADOS</h4>
              <p>8.1. Os dados pessoais são tratados conforme a Lei Geral de Proteção de Dados (LGPD).</p>
              <p>8.2. Informações de ranking e desempenho podem ser exibidas publicamente na plataforma.</p>
              <p>8.3. O atleta pode solicitar a exclusão de seus dados a qualquer momento.</p>
            </section>

            <section>
              <h4 className="font-semibold text-emerald-600">9. CONDUTAS PROIBIDAS</h4>
              <p>9.1. É proibido: fornecer informações falsas, utilizar múltiplas contas, manipular resultados, prejudicar outros atletas, utilizar linguagem ofensiva ou discriminatória.</p>
              <p>9.2. Violações podem resultar em suspensão temporária ou exclusão permanente da plataforma.</p>
            </section>

            <section>
              <h4 className="font-semibold text-emerald-600">10. DISPOSIÇÕES FINAIS</h4>
              <p>10.1. Casos omissos serão analisados pela administração da Ranking Run.</p>
              <p>10.2. Este regulamento entra em vigor na data de aceite pelo atleta.</p>
              <p>10.3. Dúvidas e sugestões podem ser enviadas através dos canais oficiais da plataforma.</p>
            </section>

            <div className="mt-6 p-3 bg-amber-100 dark:bg-amber-900/30 rounded-lg border border-amber-300">
              <p className="font-semibold text-amber-800 dark:text-amber-200 text-center">
                Ao clicar em "EU CONCORDO", você declara ter lido e aceito integralmente este regulamento.
              </p>
            </div>
          </div>
        </div>

        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button 
            onClick={handleAceitarTermo}
            disabled={!scrolledToBottom}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            <CheckCircle2 className="w-4 h-4 mr-2" />
            {scrolledToBottom ? 'EU CONCORDO' : 'Role até o final para aceitar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CadastroTermoModal;
