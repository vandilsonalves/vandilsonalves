import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import RankingPage from "@/pages/RankingPage";
import AtletaDetalhes from "@/pages/AtletaDetalhes";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RankingPage />} />
          <Route path="/atleta/:id" element={<AtletaDetalhes />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
