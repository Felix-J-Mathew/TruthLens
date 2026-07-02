import { Routes, Route } from "react-router-dom"
import Navbar from "./components/layout/Navbar.jsx"
import Footer from "./components/layout/Footer.jsx"
import HomePage from "./pages/HomePage.jsx"
import ImageAnalysisPage from "./pages/ImageAnalysisPage.jsx"
import TextAnalysisPage from "./pages/TextAnalysisPage.jsx"
import ReportPage from "./pages/ReportPage.jsx"

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/"        element={<HomePage />} />
          <Route path="/image"   element={<ImageAnalysisPage />} />
          <Route path="/text"    element={<TextAnalysisPage />} />
          <Route path="/report"  element={<ReportPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default App
