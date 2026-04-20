import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { Toaster } from "@/components/ui/sonner";
import axios from "axios";
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
import CorridasParceirasPage from "@/pages/CorridasParceirasPage";
import RaioXPage from "@/pages/RaioXPage";
import PagamentoPage from "@/pages/PagamentoPage";
import PagamentoSucessoPage from "@/pages/PagamentoSucessoPage";
import PagamentoCanceladoPage from "@/pages/PagamentoCanceladoPage";
import FeedEquipePage from "@/pages/FeedEquipePage";
import PoliticaPrivacidadePage from "@/pages/PoliticaPrivacidadePage";
import ParceirosPage from "@/pages/ParceirosPage";
import VotacaoPage from "@/pages/VotacaoPage";
import HistoricoTemporadasPage from "@/pages/HistoricoTemporadasPage";
import CookieConsent from "@/components/CookieConsent";
import BirthdayPopup from "@/components/BirthdayPopup";
import SplashScreen from "@/components/SplashScreen";
import AccessGate from "@/components/AccessGate";
import { useAuth } from "@/context/AuthContext";
import PWAInstallPrompt from "@/components/PWAInstallPrompt";
import PrintProtection from "@/components/PrintProtection";

const API = process.env.REACT_APP_BACKEND_URL;

// Axios interceptor global - envia token em TODAS as requisições
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Axios response interceptor - auto-refresh on 401
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Skip 429 - just let the component handle it
    if (error.response?.status === 429) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      // Skip refresh for auth endpoints
      if (originalRequest.url?.includes('/auth/login') || 
          originalRequest.url?.includes('/auth/refresh') ||
          originalRequest.url?.includes('/auth/register') ||
          originalRequest.url?.includes('/auth/cadastro')) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return axios(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        isRefreshing = false;
        // Sem refresh token - apenas rejeitar, não redirecionar
        return Promise.reject(error);
      }

      try {
        const res = await axios.post(`${API}/api/auth/refresh`, { refresh_token: refreshToken });
        const newToken = res.data.token;
        localStorage.setItem('token', newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        processQueue(null, newToken);
        return axios(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        // Não redirecionar - deixar o AuthContext lidar com sessão expirada
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    
    return Promise.reject(error);
  }
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
              <Route path="/corridas-parceiras" element={<CorridasParceirasPage />} />
              <Route path="/raio-x" element={<AccessGate recurso="Raio-X do Atleta"><RaioXPage /></AccessGate>} />
              <Route path="/pagamento" element={<PagamentoPage />} />
              <Route path="/pagamento/sucesso" element={<PagamentoSucessoPage />} />
              <Route path="/pagamento/cancelado" element={<PagamentoCanceladoPage />} />
              <Route path="/feed-equipe" element={<FeedEquipePage />} />
              <Route path="/politica-de-privacidade" element={<PoliticaPrivacidadePage />} />
              <Route path="/parceiros" element={<ParceirosPage />} />
              <Route path="/votacao" element={<VotacaoPage />} />
              <Route path="/historico-temporadas" element={<HistoricoTemporadasPage />} />
            </Routes>
            <CookieConsent />
          </PrintProtectionWrapper>
        </BrowserRouter>
        <PWAInstallPrompt />
        <Toaster position="top-right" />
      </div>
    </AuthProvider>
  );
}

export default App;
