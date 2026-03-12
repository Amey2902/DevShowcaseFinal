import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import AnimatedPage from '../components/AnimatedPage'

const MagicLinkLogin = () => {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [emailSent, setEmailSent] = useState(false)
  const [error, setError] = useState(null)

  // Add error boundary effect
  useEffect(() => {
    const handleError = (event) => {
      console.error('JavaScript error caught:', event.error)
      setError(event.error?.message || 'An unexpected error occurred')
    }

    window.addEventListener('error', handleError)
    return () => window.removeEventListener('error', handleError)
  }, [])

  // Add debugging for component state
  useEffect(() => {
    console.log('MagicLinkLogin state:', { email, loading, emailSent, error })
  }, [email, loading, emailSent, error])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email) { toast.error('Please enter your email'); return }
    setLoading(true)
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
      console.log('Sending magic link request to:', `${API_URL}/api/auth/magic-link/request/`)
      console.log('Email:', email)
      
      const response = await axios.post(`${API_URL}/api/auth/magic-link/request/`, { email })
      console.log('Magic link response:', response.data)
      
      setEmailSent(true)
      toast.success('Magic link sent! Check your email.')
    } catch (error) {
      console.error('Magic link error:', error)
      toast.error(error.response?.data?.error || 'Failed to send magic link')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatedPage>
      {/* Error Display */}
      {error && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          background: 'red',
          color: 'white',
          padding: '1rem',
          borderRadius: '8px',
          zIndex: 9999
        }}>
          Error: {error}
        </div>
      )}
      
      {/* Full-page gradient bg */}
      <div style={{
        minHeight: 'calc(100vh - 66px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background orbs */}
        <div style={{
          position: 'absolute', top: '-100px', left: '-100px',
          width: '500px', height: '500px', borderRadius: '50%',
          background: 'rgba(234,88,12,0.12)', filter: 'blur(80px)',
          animation: 'blob-move 14s ease-in-out infinite', pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', bottom: '-80px', right: '-80px',
          width: '400px', height: '400px', borderRadius: '50%',
          background: 'rgba(219,39,119,0.1)', filter: 'blur(80px)',
          animation: 'blob-move 18s ease-in-out infinite reverse', pointerEvents: 'none',
        }} />

        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          style={{ width: '100%', maxWidth: '440px', position: 'relative', zIndex: 1 }}
        >
          <div style={{
            background: 'rgba(17,24,39,0.75)',
            backdropFilter: 'blur(24px) saturate(200%)',
            WebkitBackdropFilter: 'blur(24px) saturate(200%)',
            border: '1px solid var(--border-glass)',
            borderRadius: 'var(--radius-xl)',
            padding: '2.75rem',
            boxShadow: 'var(--shadow-xl)',
          }}>
            <AnimatePresence mode="wait">
              {!emailSent ? (
                <motion.div
                  key="form"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                >
                  {/* Icon */}
                  <motion.div
                    initial={{ scale: 0, rotate: -20 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                    style={{ textAlign: 'center', marginBottom: '2rem' }}
                  >
                    <motion.div
                      animate={{ boxShadow: ['0 0 20px rgba(234,88,12,0.3)', '0 0 40px rgba(219,39,119,0.55)', '0 0 20px rgba(234,88,12,0.3)'] }}
                      transition={{ duration: 3, repeat: Infinity }}
                      style={{
                        width: 72, height: 72,
                        margin: '0 auto 1.5rem',
                        borderRadius: 'var(--radius-lg)',
                        background: 'var(--accent-gradient)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '2rem',
                      }}
                    >
                      ✦
                    </motion.div>
                    <h2 style={{
                      fontSize: '1.875rem',
                      fontWeight: '800',
                      marginBottom: '0.5rem',
                      letterSpacing: '-0.025em',
                    }}>
                      Welcome to DevShowcase
                    </h2>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.65 }}>
                      Enter your email to get started — no password needed!
                    </p>
                  </motion.div>

                  <form onSubmit={handleSubmit}>
                    <div className="form-group">
                      <label className="form-label">Email Address</label>
                      <input
                        type="email"
                        className="form-input"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="you@example.com"
                        autoComplete="email"
                        autoFocus
                        required
                      />
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.03, boxShadow: 'var(--shadow-glow)' }}
                      whileTap={{ scale: 0.97 }}
                      type="submit"
                      disabled={loading}
                      className="btn btn-primary"
                      style={{
                        width: '100%',
                        padding: '0.9rem',
                        fontSize: '1rem',
                        marginTop: '0.25rem',
                      }}
                    >
                      {loading ? (
                        <motion.span
                          animate={{ opacity: [1, 0.4, 1] }}
                          transition={{ duration: 1.3, repeat: Infinity }}
                        >
                          Sending magic link…
                        </motion.span>
                      ) : '✦ Send Magic Link'}
                    </motion.button>
                  </form>

                  <div style={{
                    marginTop: '1.75rem',
                    padding: '1rem 1.25rem',
                    background: 'rgba(234,88,12,0.06)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid rgba(234,88,12,0.14)',
                  }}>
                    <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.6 }}>
                      💡 <strong style={{ color: 'var(--text-primary)' }}>New here?</strong> We'll create your account automatically when you click the magic link.
                    </p>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="success"
                  initial={{ opacity: 0, scale: 0.92 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.92 }}
                  transition={{ duration: 0.35 }}
                  style={{ textAlign: 'center' }}
                >
                  <motion.div
                    animate={{ scale: [1, 1.15, 1], rotate: [0, 8, -8, 0] }}
                    transition={{ duration: 0.7 }}
                    style={{ fontSize: '4rem', marginBottom: '1.5rem' }}
                  >
                    📧
                  </motion.div>
                  <h3 style={{ fontSize: '1.5rem', fontWeight: '800', marginBottom: '0.875rem' }}>
                    Check Your Inbox!
                  </h3>
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '1.25rem', lineHeight: 1.65 }}>
                    Magic link sent to <strong style={{ color: 'var(--text-primary)' }}>{email}</strong>
                    <br />
                    Click the link in the email to log in.
                  </p>
                  <div style={{
                    padding: '0.875rem 1.25rem',
                    background: 'rgba(234,88,12,0.08)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid rgba(234,88,12,0.15)',
                    marginBottom: '1.75rem',
                  }}>
                    <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', margin: 0 }}>
                      ⏳ Link expires in 15 minutes
                    </p>
                  </div>
                  <button
                    onClick={() => { 
                      console.log('Resend button clicked - resetting form')
                      setEmailSent(false); 
                      setEmail('');
                      setError(null);
                      // Focus the email input after state update
                      setTimeout(() => {
                        const emailInput = document.querySelector('input[type="email"]');
                        if (emailInput) emailInput.focus();
                      }, 100);
                    }}
                    className="btn btn-secondary"
                    style={{ width: '100%' }}
                  >
                    ← Send Another Link
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </AnimatedPage>
  )
}

export default MagicLinkLogin
