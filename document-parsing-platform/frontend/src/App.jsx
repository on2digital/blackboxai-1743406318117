import { BrowserRouter, Routes, Route } from 'react-router-dom'
import UploadAndOutputPage from './pages/UploadAndOutputPage'
import ConfigPage from './pages/ConfigPage'
import Navbar from './components/Navbar'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<UploadAndOutputPage />} />
            <Route path="/configure" element={<ConfigPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
