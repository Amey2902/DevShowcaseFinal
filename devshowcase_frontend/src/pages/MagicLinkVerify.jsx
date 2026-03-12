import { useEffect, useState, useContext } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import { AuthContext } from '../context/AuthContext'
import AnimatedPage from '../components/AnimatedPage'

const MagicLinkVerify = () => {
  const { token } = useParams()
  const navigate = useNavigate()
  const { login } = useContext(AuthContext)
  const [status, setStatus] = useState('verifying') // verifying, success, error

  useEffect(() => {
    verifyToken()
  }, [token])

  const verifyToken = async () => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
      const response = await axios.post(`${API_URL}/api/auth/magic-link/verify/`, { token })
      
      // Log user in
      login(response.data.user, response.data.token)
      
      setStatus('success')
      toast.success('Successfully logged in!')
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate('/dashboard')
      }, 2000)
    } catch (error) {
      console.error('Verify error:', error)
      setStatus('error')
      toast.error(error.response?.data?.error || 'Invalid or expired link')
    }
  }

  return (
    <AnimatedPage>
      <div style={{ 
        minHeight: 'calc(100vh - 64px)', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '2rem'
      }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          style={{ width: '100%', maxWidth: '440px' }}
        >
          <div className="card card-elevated" style={{ padding: '3rem', textAlign: 'center' }}>
            {status === 'verifying' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  style={{ fontSize: '4rem', marginBottom: '1.5rem' }}
                >
                  ⚡
                </motion.div>
                <h3 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                  Verifying Magic Link...
                </h3>
                <p style={{ color: 'var(--text-secondary)' }}>
                  Please wait while we log you in
                </p>
              </motion.div>
            )}

            {status === 'success' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <motion.div
                  animate={{ 
                    scale: [1, 1.2, 1],
                  }}
                  transition={{ duration: 0.6 }}
                  style={{ fontSize: '4rem', marginBottom: '1.5rem' }}
                >
                  ✅
                </motion.div>
                <h3 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--success)' }}>
                  Success!
                </h3>
                <p style={{ color: 'var(--text-secondary)' }}>
                  You're logged in. Redirecting to dashboard...
                </p>
                <motion.div
                  style={{
                    width: '100%',
                    height: '4px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: '2px',
                    marginTop: '1.5rem',
                    overflow: 'hidden'
                  }}
                >
                  <motion.div
                    initial={{ width: '0%' }}
                    animate={{ width: '100%' }}
                    transition={{ duration: 2 }}
                    style={{
                      height: '100%',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    }}
                  />
                </motion.div>
              </motion.div>
            )}

            {status === 'error' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <motion.div
                  animate={{ 
                    rotate: [0, -10, 10, -10, 0],
                  }}
                  transition={{ duration: 0.5 }}
                  style={{ fontSize: '4rem', marginBottom: '1.5rem' }}
                >
                  ❌
                </motion.div>
                <h3 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--error)' }}>
                  Link Invalid or Expired
                </h3>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
                  This magic link has expired or has already been used.
                </p>
                <button
                  onClick={() => navigate('/magic-link')}
                  className="btn"
                  style={{ 
                    width: '100%',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: 'none'
                  }}
                >
                  Request New Magic Link
                </button>
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatedPage>
  )
}

export default MagicLinkVerify
