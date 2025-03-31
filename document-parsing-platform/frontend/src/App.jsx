import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import ConfigPage from './pages/ConfigPage'
import OutputPage from './pages/OutputPage'
import Navbar from './components/Navbar'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/configure" element={<ConfigPage />} />
            <Route path="/output" element={<OutputPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}