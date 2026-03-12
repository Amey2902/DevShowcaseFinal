import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import MagicLinkLogin from './pages/MagicLinkLogin'
import MagicLinkVerify from './pages/MagicLinkVerify'
import Dashboard from './pages/Dashboard'
import ProjectNew from './pages/ProjectNew'
import ProjectEdit from './pages/ProjectEdit'
import ProjectView from './pages/ProjectView'
import TestPage from './pages/TestPage'
import PrivateRoute from './components/PrivateRoute'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-container">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<MagicLinkLogin />} />
            <Route path="/test" element={<TestPage />} />
            <Route path="/auth/verify/:token" element={<MagicLinkVerify />} />
            <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/project/new" element={<PrivateRoute><ProjectNew /></PrivateRoute>} />
            <Route path="/project/edit/:slug" element={<PrivateRoute><ProjectEdit /></PrivateRoute>} />
            <Route path="/project/:slug" element={<ProjectView />} />
          </Routes>
          <ToastContainer position="top-right" autoClose={3000} />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
