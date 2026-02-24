import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import RankingPage from "@/pages/RankingPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RankingPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
