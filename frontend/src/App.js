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
import BirthdayPopup from "@/components/BirthdayPopup";
import DashboardEstrategico from "@/pages/admin/DashboardEstrategico";
import FeedPage from "@/pages/FeedPage";
import RegrasPage from "@/pages/RegrasPage";
import HistoricoSubmissoesPage from "@/pages/HistoricoSubmissoesPage";

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <BirthdayPopup />
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
            <Route path="/perfil" element={<PerfilAtletaPage />} />
            <Route path="/feed" element={<FeedPage />} />
            <Route path="/regras" element={<RegrasPage />} />
            <Route path="/historico" element={<HistoricoSubmissoesPage />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" />
      </div>
    </AuthProvider>
  );
}

export default App;
