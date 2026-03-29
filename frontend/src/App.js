import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { Toaster } from "@/components/ui/sonner";
import { lazy, Suspense } from "react";
import BirthdayPopup from "@/components/BirthdayPopup";
import SplashScreen from "@/components/SplashScreen";
import AccessGate from "@/components/AccessGate";
import { useAuth } from "@/context/AuthContext";
import PWAInstallPrompt from "@/components/PWAInstallPrompt";
import PrintProtection from "@/components/PrintProtection";

// Lazy-loaded pages (carregam sob demanda)
const RankingPage = lazy(() => import("@/pages/RankingPage"));
const AtletaDetalhes = lazy(() => import("@/pages/AtletaDetalhes"));
const LoginPage = lazy(() => import("@/pages/LoginPage"));
const CadastroPage = lazy(() => import("@/pages/CadastroPage"));
const SubmeterResultadoPage = lazy(() => import("@/pages/SubmeterResultadoPage"));
const AdminDashboard = lazy(() => import("@/pages/AdminDashboard.jsx"));
const PerfilAtletaPage = lazy(() => import("@/pages/PerfilAtletaPage.jsx"));
const AssessoriaPage = lazy(() => import("@/pages/AssessoriaPage.jsx"));
const DonoAssessoriaDashboard = lazy(() => import("@/pages/DonoAssessoriaDashboard.jsx"));
const RankingCorridasPage = lazy(() => import("@/pages/RankingCorridasPage.jsx"));
const ComoSerVerificadoPage = lazy(() => import("@/pages/ComoSerVerificadoPage.jsx"));
const DashboardEstrategico = lazy(() => import("@/pages/admin/DashboardEstrategico"));
const FeedPage = lazy(() => import("@/pages/FeedPage"));
const RegrasPage = lazy(() => import("@/pages/RegrasPage"));
const HistoricoSubmissoesPage = lazy(() => import("@/pages/HistoricoSubmissoesPage"));
const RankingCidadePage = lazy(() => import("@/pages/RankingCidadePage"));
const StravaAtividadesPage = lazy(() => import("@/pages/StravaAtividadesPage"));
const RaioXPage = lazy(() => import("@/pages/RaioXPage"));
const PagamentoPage = lazy(() => import("@/pages/PagamentoPage"));
const PagamentoSucessoPage = lazy(() => import("@/pages/PagamentoSucessoPage"));
const PagamentoCanceladoPage = lazy(() => import("@/pages/PagamentoCanceladoPage"));

// Loading fallback minimalista
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-slate-50">
    <div className="w-8 h-8 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin" />
  </div>
);

function SplashScreenWrapper() {
  const { token, user } = useAuth();
  if (!token || !user || user.role === 'admin') return null;
  return <SplashScreen token={token} />;
}

function PrintProtectionWrapper({ children }) {
  const { token, user } = useAuth();
  if (!token || !user) return children;
  return <PrintProtection>{children}</PrintProtection>;
}

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <BirthdayPopup />
          <SplashScreenWrapper />
          <PrintProtectionWrapper>
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/" element={<RankingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/cadastro" element={<CadastroPage />} />
                <Route path="/atleta/:id" element={<AtletaDetalhes />} />
                <Route path="/assessoria/:nome" element={<AssessoriaPage />} />
                <Route path="/minha-assessoria" element={<DonoAssessoriaDashboard />} />
                <Route path="/ranking-corridas" element={<RankingCorridasPage />} />
                <Route path="/submeter-resultado" element={<SubmeterResultadoPage />} />
                <Route path="/como-ser-verificado" element={<ComoSerVerificadoPage />} />
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/admin/estrategico" element={<DashboardEstrategico />} />
                <Route path="/perfil" element={<AccessGate recurso="Edicao de Perfil"><PerfilAtletaPage /></AccessGate>} />
                <Route path="/feed" element={<AccessGate recurso="Feed Social"><FeedPage /></AccessGate>} />
                <Route path="/regras" element={<RegrasPage />} />
                <Route path="/historico" element={<HistoricoSubmissoesPage />} />
                <Route path="/ranking-cidade" element={<RankingCidadePage />} />
                <Route path="/strava-clube" element={<AccessGate recurso="Integracao Strava"><StravaAtividadesPage /></AccessGate>} />
                <Route path="/raio-x" element={<AccessGate recurso="Raio-X do Atleta"><RaioXPage /></AccessGate>} />
                <Route path="/pagamento" element={<PagamentoPage />} />
                <Route path="/pagamento/sucesso" element={<PagamentoSucessoPage />} />
                <Route path="/pagamento/cancelado" element={<PagamentoCanceladoPage />} />
              </Routes>
            </Suspense>
          </PrintProtectionWrapper>
        </BrowserRouter>
        <PWAInstallPrompt />
        <Toaster position="top-right" />
      </div>
    </AuthProvider>
  );
}

export default App;
