import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Shield, CheckCircle, Lock, CreditCard, Star, BarChart3, Users, Activity, Clock, Zap, Timer, Copy, QrCode, RefreshCw, Trophy, PartyPopper, ArrowRight, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import confetti from 'canvas-confetti';
import EfiPay from 'payment-token-efi';

const API = process.env.REACT_APP_BACKEND_URL;

function fireConfetti() {
  const duration = 4000;
  const end = Date.now() + duration;
  const colors = ['#10b981', '#14b8a6', '#fbbf24', '#f59e0b', '#ffffff'];

  // Burst inicial
  confetti({ particleCount: 100, spread: 80, origin: { y: 0.6 }, colors });

  // Chuva continua
  const frame = () => {
    confetti({
      particleCount: 3,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
      colors,
    });
    confetti({
      particleCount: 3,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
      colors,
    });
    if (Date.now() < end) requestAnimationFrame(frame);
  };
  frame();

  // Burst final
  setTimeout(() => {
    confetti({ particleCount: 80, spread: 100, origin: { y: 0.4 }, colors });
  }, 1500);
}


function ConfirmacaoPagamento({ navigate }) {
  useEffect(() => {
    fireConfetti();
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center px-4" data-testid="confirmacao-pagamento">
      <div className="max-w-md w-full text-center">
        {/* Icone animado */}
        <div className="relative mx-auto mb-8 w-28 h-28">
          <div className="absolute inset-0 bg-emerald-500/20 rounded-full animate-ping" />
          <div className="relative w-28 h-28 bg-gradient-to-br from-emerald-500 to-teal-400 rounded-full flex items-center justify-center shadow-lg shadow-emerald-500/30">
            <CheckCircle className="w-14 h-14 text-white" strokeWidth={2.5} />
          </div>
        </div>

        {/* Texto principal */}
        <h1 className="text-3xl sm:text-4xl font-bold mb-3 bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent" data-testid="confirmacao-titulo">
          Pagamento Confirmado!
        </h1>
        <p className="text-gray-400 text-base mb-8">
          Seu acesso <span className="text-emerald-400 font-semibold">Atleta Premium</span> foi ativado com sucesso.
        </p>

        {/* Card de resumo */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-8 text-left" data-testid="confirmacao-resumo">
          <div className="flex items-center gap-3 mb-4 pb-4 border-b border-gray-800">
            <div className="w-10 h-10 bg-emerald-500/10 rounded-xl flex items-center justify-center">
              <Trophy className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="font-semibold text-white text-sm">Plano Atleta Premium</p>
              <p className="text-xs text-gray-500">Acesso completo ate 31/12/2026</p>
            </div>
          </div>
          <ul className="space-y-2.5">
            {[
              'Raio-X completo do atleta',
              'Integracao Strava',
              'Feed social: curtir, comentar e postar',
              'Stories e compartilhamento',
              'Edicao completa do perfil',
            ].map((item, i) => (
              <li key={i} className="flex items-center gap-2.5 text-sm text-gray-300">
                <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Botoes */}
        <div className="space-y-3">
          <Button
            onClick={() => navigate('/raio-x')}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white h-12 text-base font-medium"
            data-testid="btn-ir-raio-x"
          >
            Ver meu Raio-X <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
          <Button
            onClick={() => navigate('/')}
            variant="outline"
            className="w-full border-gray-700 text-gray-300 hover:bg-gray-800 h-11"
            data-testid="btn-ir-ranking"
          >
            Voltar ao Ranking
          </Button>
        </div>

        <p className="text-xs text-gray-600 mt-6">
          Pagamento processado com sucesso via Efi Bank
        </p>
      </div>
    </div>
  );
}


function PixCheckout({ token, planoInfo, onPaid }) {
  const [gerando, setGerando] = useState(false);
  const [pixData, setPixData] = useState(null);
  const [polling, setPolling] = useState(false);
  const pollingRef = useRef(null);

  const gerarPix = async () => {
    setGerando(true);
    try {
      const res = await fetch(`${API}/api/efi/pix/criar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({}),
      });
      if (!res.ok) {
        const err = await res.json();
        toast.error(err.detail || 'Erro ao gerar PIX');
        return;
      }
      const data = await res.json();
      setPixData(data);
      toast.success('QR Code PIX gerado!');
      startPolling(data.txid);
    } catch (err) {
      toast.error('Erro de conexao. Tente novamente.');
      console.error(err);
    } finally {
      setGerando(false);
    }
  };

  const startPolling = (txid) => {
    setPolling(true);
    if (pollingRef.current) clearInterval(pollingRef.current);
    pollingRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API}/api/efi/pix/status/${txid}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          if (data.payment_status === 'paid') {
            clearInterval(pollingRef.current);
            setPolling(false);
            onPaid();
          }
        }
      } catch {}
    }, 5000);
  };

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const copiarCodigoPix = () => {
    if (pixData?.qrcode?.qrcode) {
      navigator.clipboard.writeText(pixData.qrcode.qrcode);
      toast.success('Codigo PIX copiado!');
    }
  };

  if (pixData) {
    return (
      <div className="space-y-5" data-testid="pix-resultado">
        <div className="text-center">
          <p className="text-sm text-gray-400 mb-4">Escaneie o QR Code ou copie o codigo PIX</p>
          {pixData.qrcode?.imagemQrcode && (
            <div className="flex justify-center mb-4">
              <div className="bg-white rounded-xl p-3 inline-block">
                <img
                  src={pixData.qrcode.imagemQrcode}
                  alt="QR Code PIX"
                  className="w-52 h-52"
                  data-testid="pix-qrcode-img"
                />
              </div>
            </div>
          )}
          <div className="bg-gray-800/60 rounded-lg p-3 mb-4">
            <p className="text-xs text-gray-500 mb-1.5">PIX Copia e Cola</p>
            <p className="text-xs text-gray-300 font-mono break-all leading-relaxed select-all" data-testid="pix-copia-cola">
              {pixData.qrcode?.qrcode?.substring(0, 80)}...
            </p>
          </div>
          <Button
            onClick={copiarCodigoPix}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white h-11"
            data-testid="btn-copiar-pix"
          >
            <Copy className="w-4 h-4 mr-2" /> Copiar Codigo PIX
          </Button>
          {polling && (
            <div className="mt-4 flex items-center justify-center gap-2 text-amber-400" data-testid="pix-aguardando">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span className="text-sm">Aguardando confirmacao do pagamento...</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="text-center" data-testid="pix-gerar">
      <div className="mb-5">
        <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
          <QrCode className="w-8 h-8 text-emerald-400" />
        </div>
        <p className="text-gray-400 text-sm">Pague com PIX e tenha acesso imediato</p>
      </div>
      <Button
        onClick={gerarPix}
        disabled={gerando}
        className="w-full bg-emerald-600 hover:bg-emerald-500 text-white h-12 text-base font-medium"
        data-testid="btn-gerar-pix"
      >
        {gerando ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            Gerando PIX...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <QrCode className="w-4 h-4" /> Gerar QR Code PIX - R$ 97,00
          </span>
        )}
      </Button>
    </div>
  );
}

function CartaoCheckout({ token, onPaid }) {
  const [efiConfig, setEfiConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [detectingBrand, setDetectingBrand] = useState(false);
  const [cardBrand, setCardBrand] = useState('');
  const [parcelas, setParcelas] = useState(1);
  const [form, setForm] = useState({
    numero: '',
    cvv: '',
    mes: '',
    ano: '',
    titular: '',
    cpf: '',
    email: '',
    telefone: '',
  });
  const [erro, setErro] = useState('');

  const VALOR_TOTAL = 9700; // centavos

  const opcoesParcelamento = Array.from({ length: 12 }, (_, i) => {
    const n = i + 1;
    const valorParcela = Math.ceil(VALOR_TOTAL / n);
    return {
      parcelas: n,
      valorParcela,
      label: n === 1
        ? `1x de R$ ${(valorParcela / 100).toFixed(2).replace('.', ',')} (a vista)`
        : `${n}x de R$ ${(valorParcela / 100).toFixed(2).replace('.', ',')}`,
    };
  });

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await fetch(`${API}/api/efi/config`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setEfiConfig(data);
      }
    } catch (err) {
      console.error('Erro ao buscar config Efi:', err);
    }
  };

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
    setErro('');

    if (field === 'numero') {
      const limpo = value.replace(/\D/g, '');
      if (limpo.length >= 6 && !detectingBrand) {
        detectBrand(limpo);
      } else if (limpo.length < 6) {
        setCardBrand('');
      }
    }
  };

  const detectBrand = async (numero) => {
    setDetectingBrand(true);
    try {
      const brand = await EfiPay.CreditCard
        .setCardNumber(numero)
        .verifyCardBrand();
      if (brand && brand !== 'undefined' && brand !== 'unsupported') {
        setCardBrand(brand);
      } else {
        setCardBrand('');
      }
    } catch {
      setCardBrand('');
    } finally {
      setDetectingBrand(false);
    }
  };

  const formatCardNumber = (value) => {
    const limpo = value.replace(/\D/g, '');
    const groups = limpo.match(/.{1,4}/g);
    return groups ? groups.join(' ') : limpo;
  };

  const formatPhone = (value) => {
    const limpo = value.replace(/\D/g, '');
    if (limpo.length <= 2) return limpo;
    if (limpo.length <= 7) return `(${limpo.slice(0, 2)}) ${limpo.slice(2)}`;
    return `(${limpo.slice(0, 2)}) ${limpo.slice(2, 7)}-${limpo.slice(7, 11)}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');

    if (!efiConfig?.payee_code) {
      setErro('Configuracao do gateway indisponivel. Recarregue a pagina.');
      return;
    }

    const numero = form.numero.replace(/\D/g, '');
    if (numero.length < 13) { setErro('Numero do cartao invalido'); return; }
    if (form.cvv.length < 3) { setErro('CVV invalido'); return; }
    if (!form.mes || !form.ano) { setErro('Data de validade obrigatoria'); return; }
    if (!form.titular.trim()) { setErro('Nome do titular obrigatorio'); return; }
    const cpfLimpo = form.cpf.replace(/\D/g, '');
    if (cpfLimpo.length !== 11) { setErro('CPF invalido (11 digitos)'); return; }
    if (!form.email.includes('@')) { setErro('Email invalido'); return; }
    const telLimpo = form.telefone.replace(/\D/g, '');
    if (telLimpo.length < 10) { setErro('Telefone invalido (DDD + numero)'); return; }
    if (!cardBrand) { setErro('Bandeira do cartao nao identificada. Verifique o numero.'); return; }

    setLoading(true);

    try {
      // Step 1: Generate payment_token
      const tokenResult = await EfiPay.CreditCard
        .setAccount(efiConfig.payee_code)
        .setEnvironment(efiConfig.environment)
        .setCreditCardData({
          brand: cardBrand,
          number: numero,
          cvv: form.cvv,
          expirationMonth: form.mes,
          expirationYear: form.ano,
          holderName: form.titular,
          holderDocument: cpfLimpo,
          reuse: false,
        })
        .getPaymentToken();

      const paymentToken = tokenResult.payment_token;
      if (!paymentToken) {
        setErro('Falha ao gerar token de pagamento. Verifique os dados do cartao.');
        setLoading(false);
        return;
      }

      // Step 2: Send to backend
      const res = await fetch(`${API}/api/efi/cartao/criar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          payment_token: paymentToken,
          nome: form.titular,
          cpf: cpfLimpo,
          email: form.email,
          telefone: telLimpo,
          parcelas,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErro(data.detail || 'Erro ao processar pagamento');
        setLoading(false);
        return;
      }

      if (data.payment_status === 'paid' || data.status === 'approved') {
        toast.success('Pagamento aprovado!');
        onPaid();
      } else {
        setErro('Pagamento aguardando confirmacao. Tente novamente em instantes.');
      }
    } catch (err) {
      console.error('Erro no pagamento:', err);
      const msg = err?.error_description || err?.message || 'Erro ao processar pagamento. Verifique os dados.';
      setErro(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  const brandLabel = { visa: 'Visa', mastercard: 'Mastercard', amex: 'Amex', elo: 'Elo' };
  const selectedParcela = opcoesParcelamento.find(p => p.parcelas === parcelas);

  return (
    <form onSubmit={handleSubmit} className="space-y-4" data-testid="cartao-form-efi">
      {/* Card Number */}
      <div>
        <label className="text-xs text-gray-400 mb-1 block">Numero do Cartao</label>
        <div className="relative">
          <input
            type="text"
            maxLength={19}
            value={formatCardNumber(form.numero)}
            onChange={e => handleChange('numero', e.target.value)}
            placeholder="0000 0000 0000 0000"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none"
            data-testid="input-card-number"
          />
          {cardBrand && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded" data-testid="card-brand-badge">
              {brandLabel[cardBrand] || cardBrand}
            </span>
          )}
        </div>
      </div>

      {/* CVV + Expiry */}
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="text-xs text-gray-400 mb-1 block">Mes</label>
          <select
            value={form.mes}
            onChange={e => handleChange('mes', e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
            data-testid="select-card-month"
          >
            <option value="">MM</option>
            {Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, '0')).map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-400 mb-1 block">Ano</label>
          <select
            value={form.ano}
            onChange={e => handleChange('ano', e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
            data-testid="select-card-year"
          >
            <option value="">AAAA</option>
            {Array.from({ length: 10 }, (_, i) => String(2025 + i)).map(y => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-400 mb-1 block">CVV</label>
          <input
            type="text"
            maxLength={4}
            value={form.cvv}
            onChange={e => handleChange('cvv', e.target.value.replace(/\D/g, ''))}
            placeholder="123"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:ring-2 focus:ring-emerald-500 outline-none"
            data-testid="input-card-cvv"
          />
        </div>
      </div>

      {/* Holder Name */}
      <div>
        <label className="text-xs text-gray-400 mb-1 block">Nome do Titular</label>
        <input
          type="text"
          value={form.titular}
          onChange={e => handleChange('titular', e.target.value)}
          placeholder="Como esta no cartao"
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:ring-2 focus:ring-emerald-500 outline-none"
          data-testid="input-card-holder"
        />
      </div>

      {/* CPF + Telefone */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-400 mb-1 block">CPF</label>
          <input
            type="text"
            maxLength={14}
            value={form.cpf}
            onChange={e => handleChange('cpf', e.target.value)}
            placeholder="000.000.000-00"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:ring-2 focus:ring-emerald-500 outline-none"
            data-testid="input-card-cpf"
          />
        </div>
        <div>
          <label className="text-xs text-gray-400 mb-1 block">Telefone</label>
          <input
            type="text"
            maxLength={15}
            value={formatPhone(form.telefone)}
            onChange={e => handleChange('telefone', e.target.value)}
            placeholder="(11) 99999-9999"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:ring-2 focus:ring-emerald-500 outline-none"
            data-testid="input-card-telefone"
          />
        </div>
      </div>

      {/* Email */}
      <div>
        <label className="text-xs text-gray-400 mb-1 block">Email</label>
        <input
          type="email"
          value={form.email}
          onChange={e => handleChange('email', e.target.value)}
          placeholder="seu@email.com"
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm placeholder-gray-500 focus:ring-2 focus:ring-emerald-500 outline-none"
          data-testid="input-card-email"
        />
      </div>

      {/* Parcelas Selector */}
      <div>
        <label className="text-xs text-gray-400 mb-1 block">Parcelas</label>
        <select
          value={parcelas}
          onChange={e => setParcelas(Number(e.target.value))}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 text-white text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
          data-testid="select-parcelas"
        >
          {opcoesParcelamento.map(op => (
            <option key={op.parcelas} value={op.parcelas}>{op.label}</option>
          ))}
        </select>
      </div>

      {/* Error */}
      {erro && (
        <div className="flex items-start gap-2 bg-red-500/10 border border-red-500/20 rounded-lg p-3" data-testid="cartao-erro">
          <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-400">{erro}</p>
        </div>
      )}

      {/* Submit */}
      <Button
        type="submit"
        disabled={loading}
        className="w-full bg-emerald-600 hover:bg-emerald-500 text-white h-12 text-base font-medium"
        data-testid="btn-pagar-cartao"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            Processando pagamento...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <CreditCard className="w-4 h-4" /> Pagar com Cartao - {selectedParcela?.label || `R$ 97,00`}
          </span>
        )}
      </Button>

      <p className="text-xs text-gray-500 text-center">
        Pagamento seguro via Efi Bank. Bandeiras: Visa, Mastercard, Elo, Amex
      </p>
      {efiConfig?.is_sandbox && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-2.5 mt-2" data-testid="sandbox-warning">
          <p className="text-xs text-amber-400 text-center">
            Ambiente de homologacao: cartoes NAO serao debitados. Em producao, a operadora validara saldo e bloqueio do cartao.
          </p>
        </div>
      )}
    </form>
  );
}
export default function PagamentoPage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [planoInfo, setPlanoInfo] = useState(null);
  const [loadingPlano, setLoadingPlano] = useState(true);
  const [metodo, setMetodo] = useState('pix');
  const [pagamentoConfirmado, setPagamentoConfirmado] = useState(false);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchPlano();
  }, [token]);

  const fetchPlano = async () => {
    try {
      const res = await fetch(`${API}/api/pagamentos/meu-plano`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setPlanoInfo(data);
      if (data.tem_acesso_premium && data.status === 'autorizado') {
        toast.success('Voce ja possui acesso Premium!');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingPlano(false);
    }
  };

  const handlePaid = useCallback(() => {
    setPagamentoConfirmado(true);
  }, []);

  const recursos = [
    { icon: BarChart3, label: 'Raio-X completo do atleta' },
    { icon: Activity, label: 'Integracao Strava' },
    { icon: Users, label: 'Feed social: curtir, comentar e postar' },
    { icon: Star, label: 'Stories e compartilhamento' },
    { icon: Shield, label: 'Edicao completa do perfil' },
  ];

  if (loadingPlano) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Carregando...</div>
      </div>
    );
  }

  // Tela de confirmacao com confetti
  if (pagamentoConfirmado) {
    return <ConfirmacaoPagamento navigate={navigate} />;
  }

  const dataLimite = new Date('2026-12-14T23:59:59Z');
  const agora = new Date();
  const diffMs = dataLimite - agora;
  const diasRestantesOferta = Math.max(0, Math.ceil(diffMs / (1000 * 60 * 60 * 24)));
  const mostrarContagem = diasRestantesOferta <= 30 && diasRestantesOferta > 0;

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="pagamento-page">
      <div className="max-w-2xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-4 py-1.5 mb-6">
            <Star className="w-4 h-4 text-emerald-400" />
            <span className="text-sm text-emerald-400 font-medium">Atleta Premium</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold mb-3">
            Desbloqueie todo o potencial
          </h1>
          <p className="text-gray-400 text-base">
            Acesso completo a todas as funcionalidades do Ranking Run Pro
          </p>
        </div>

        {/* Banner contagem regressiva */}
        {mostrarContagem && (
          <div className="mb-8 rounded-xl overflow-hidden" data-testid="banner-contagem">
            <div className="bg-gradient-to-r from-red-600 to-orange-500 p-4 flex items-center justify-center gap-3">
              <Timer className="w-5 h-5 text-white animate-pulse" />
              <p className="text-white font-bold text-sm sm:text-base">
                {diasRestantesOferta === 1
                  ? 'Ultimo dia! A oferta encerra amanha!'
                  : `Faltam ${diasRestantesOferta} dias para o fim da oferta!`}
              </p>
            </div>
            <div className="bg-gray-900 border border-t-0 border-orange-500/30 px-4 py-2.5 text-center">
              <p className="text-xs text-gray-400">
                Apos 14/12/2026, o valor sera de <span className="text-white font-semibold">12x R$ 119,00</span>
              </p>
            </div>
          </div>
        )}

        {/* Status atual */}
        {planoInfo && (
          <div className={`rounded-xl p-4 mb-8 border ${
            planoInfo.status === 'autorizado' ? 'bg-emerald-500/10 border-emerald-500/30' :
            planoInfo.status === 'em_teste' ? 'bg-amber-500/10 border-amber-500/30' :
            'bg-red-500/10 border-red-500/30'
          }`} data-testid="status-plano">
            <div className="flex items-center gap-3">
              {planoInfo.status === 'autorizado' ? (
                <CheckCircle className="w-5 h-5 text-emerald-400" />
              ) : planoInfo.status === 'em_teste' ? (
                <Shield className="w-5 h-5 text-amber-400" />
              ) : (
                <Lock className="w-5 h-5 text-red-400" />
              )}
              <div>
                <p className="font-medium text-sm">
                  {planoInfo.status === 'autorizado' ? 'Plano Premium Ativo' :
                   planoInfo.status === 'em_teste' ? `Periodo de Teste - ${planoInfo.dias_restantes} dias restantes` :
                   'Acesso Expirado'}
                </p>
                {planoInfo.expira_em && (
                  <p className="text-xs text-gray-400 mt-0.5">
                    Valido ate {new Date(planoInfo.expira_em).toLocaleDateString('pt-BR')}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Card de preco */}
        <div className="bg-gray-900 rounded-2xl border border-gray-800 overflow-hidden mb-8 relative" data-testid="plano-card">
          <div className="absolute top-0 right-0 bg-red-500 text-white text-xs font-bold px-3 py-1.5 rounded-bl-xl" data-testid="badge-oferta">
            OFERTA
          </div>

          <div className="p-8 text-center border-b border-gray-800">
            <p className="text-gray-500 line-through text-lg mb-1" data-testid="preco-original">
              De R$ 197,00
            </p>
            <div className="flex items-baseline justify-center gap-1" data-testid="preco-atual">
              <span className="text-lg text-gray-400">5x de</span>
              <span className="text-5xl font-bold">R$ 19</span>
              <span className="text-lg text-gray-400 font-normal">,40</span>
            </div>
            <p className="text-gray-400 text-sm mt-2">ou R$ 97,00 a vista - Valido ate 31/12/2026</p>
            <div className="inline-flex items-center gap-1.5 mt-3 bg-amber-500/10 border border-amber-500/20 rounded-full px-3 py-1">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-xs text-amber-400 font-medium">Oferta valida ate 14/12/2026</span>
            </div>
          </div>

          <div className="p-6">
            <p className="text-sm text-gray-400 mb-4 font-medium uppercase tracking-wider">O que esta incluso</p>
            <ul className="space-y-3">
              {recursos.map((r, i) => (
                <li key={i} className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                    <r.icon className="w-4 h-4 text-emerald-400" />
                  </div>
                  <span className="text-sm text-gray-200">{r.label}</span>
                </li>
              ))}
              <li className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                  <CreditCard className="w-4 h-4 text-emerald-400" />
                </div>
                <span className="text-sm text-gray-200">Acesso ate 31/12/2026</span>
              </li>
            </ul>
          </div>

          {/* Metodos de pagamento */}
          <div className="p-6 pt-0">
            {planoInfo?.status === 'autorizado' ? (
              <Button
                className="w-full bg-gray-700 text-gray-300 cursor-not-allowed"
                disabled
                data-testid="btn-ja-premium"
              >
                <CheckCircle className="w-4 h-4 mr-2" /> Voce ja e Premium
              </Button>
            ) : (
              <div className="space-y-4">
                {/* Tabs de metodo */}
                <div className="flex rounded-lg overflow-hidden border border-gray-700" data-testid="metodo-tabs">
                  <button
                    onClick={() => setMetodo('pix')}
                    className={`flex-1 py-2.5 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
                      metodo === 'pix'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:text-gray-200'
                    }`}
                    data-testid="tab-pix"
                  >
                    <QrCode className="w-4 h-4" /> PIX
                  </button>
                  <button
                    onClick={() => setMetodo('cartao')}
                    className={`flex-1 py-2.5 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
                      metodo === 'cartao'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:text-gray-200'
                    }`}
                    data-testid="tab-cartao"
                  >
                    <CreditCard className="w-4 h-4" /> Cartao
                  </button>
                </div>

                {/* Conteudo do metodo selecionado */}
                {metodo === 'pix' ? (
                  <PixCheckout token={token} planoInfo={planoInfo} onPaid={handlePaid} />
                ) : (
                  <CartaoCheckout token={token} onPaid={handlePaid} />
                )}
              </div>
            )}
          </div>
        </div>

        {/* Voltar */}
        <div className="text-center">
          <button
            onClick={() => navigate('/')}
            className="text-sm text-gray-500 hover:text-gray-300 transition"
            data-testid="btn-voltar-ranking"
          >
            Voltar ao Ranking
          </button>
        </div>
      </div>
    </div>
  );
}
