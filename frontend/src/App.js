import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import RankingPage from "@/pages/RankingPage";
import AtletaDetalhes from "@/pages/AtletaDetalhes";
import LoginPage from "@/pages/LoginPage";
import CadastroPage from "@/pages/CadastroPage";
import SubmeterResultadoPage from "@/pages/SubmeterResultadoPage";
import AdminDashboard from "@/pages/AdminDashboard.jsx";
import PerfilAtletaPage from "@/pages/PerfilAtletaPage.jsx";

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<RankingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/cadastro" element={<CadastroPage />} />
            <Route path="/atleta/:id" element={<AtletaDetalhes />} />
            <Route path="/submeter-resultado" element={<SubmeterResultadoPage />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/perfil" element={<PerfilAtletaPage />} />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

export default App;
