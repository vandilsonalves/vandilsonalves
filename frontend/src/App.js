import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { Toaster } from "@/components/ui/sonner";
import RankingPage from "@/pages/RankingPage";
import AtletaDetalhes from "@/pages/AtletaDetalhes";
import LoginPage from "@/pages/LoginPage";
import CadastroPage from "@/pages/CadastroPage";
import SubmeterResultadoPage from "@/pages/SubmeterResultadoPage";
import AdminDashboard from "@/pages/AdminDashboard.jsx";
import PerfilAtletaPage from "@/pages/PerfilAtletaPage.jsx";
import AssessoriaPage from "@/pages/AssessoriaPage.jsx";
import DonoAssessoriaDashboard from "@/pages/DonoAssessoriaDashboard.jsx";
import RankingCorridasPage from "@/pages/RankingCorridasPage.jsx";
import ComoSerVerificadoPage from "@/pages/ComoSerVerificadoPage.jsx";
import DashboardEstrategico from "@/pages/admin/DashboardEstrategico";
import FeedPage from "@/pages/FeedPage";
import RegrasPage from "@/pages/RegrasPage";
import HistoricoSubmissoesPage from "@/pages/HistoricoSubmissoesPage";
import RankingCidadePage from "@/pages/RankingCidadePage";
import StravaAtividadesPage from "@/pages/StravaAtividadesPage";
import RaioXPage from "@/pages/RaioXPage";
import PagamentoPage from "@/pages/PagamentoPage";
import PagamentoSucessoPage from "@/pages/PagamentoSucessoPage";
import PagamentoCanceladoPage from "@/pages/PagamentoCanceladoPage";
import BirthdayPopup from "@/components/BirthdayPopup";
import SplashScreen from "@/components/SplashScreen";
import AccessGate from "@/components/AccessGate";
import { useAuth } from "@/context/AuthContext";
import PWAInstallPrompt from "@/components/PWAInstallPrompt";
import PrintProtection from "@/components/PrintProtection";

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
          </PrintProtectionWrapper>
        </BrowserRouter>
        <PWAInstallPrompt />
        <Toaster position="top-right" />
      </div>
    </AuthProvider>
  );
}

export default App;
