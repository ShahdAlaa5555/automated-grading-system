import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import UploadPage from "./pages/UploadPage";
// import LoginPage from "./pages/LoginPage";
// import ProcessingPage from "./pages/ProcessingPage";
// import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/upload" element={<UploadPage />} />
        {/* Add these later */}
        {/* <Route path="/login" element={<LoginPage />} /> */}
        {/* <Route path="/processing" element={<ProcessingPage />} /> */}
        {/* <Route path="/results" element={<ResultsPage />} /> */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;