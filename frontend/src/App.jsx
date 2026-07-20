import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Intake from './pages/Intake'
import Dashboard from './pages/Dashboard'
import Review from './pages/Review'
import Cases from './pages/Cases'

function NotFound() {
  return (
    <div style={{ minHeight: '80vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 16 }}>
      <div style={{ fontSize: '4rem' }}>🕊️</div>
      <h1 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '2rem', margin: 0 }}>Page Not Found</h1>
      <p style={{ color: 'var(--text-muted)', margin: '8px 0 24px' }}>The page you're looking for doesn't exist.</p>
      <a href="/" className="btn-primary">Go Home</a>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/intake" element={<Intake />} />
        <Route path="/cases" element={<Cases />} />
        <Route path="/cases/:caseId" element={<Dashboard />} />
        <Route path="/cases/:caseId/tasks/:taskId" element={<Review />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
