import { useContext, useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { AuthContext } from '../context/AuthContext'
import axios from 'axios'
import { toast } from 'react-toastify'

const Navbar = () => {
  const { user, logout } = useContext(AuthContext)
  const navigate = useNavigate()
  const location = useLocation()
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => { setMenuOpen(false) }, [location.pathname])

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout/')
      logout()
      toast.success('Logged out successfully')
      navigate('/')
    } catch {
      toast.error('Logout failed')
    }
  }

  const avatarLetter = user?.username?.[0]?.toUpperCase() || '?'

  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{
        background: scrolled
          ? 'rgba(10, 15, 30, 0.92)'
          : 'rgba(10, 15, 30, 0.60)',
        borderBottom: '1px solid var(--border-glass)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        backdropFilter: 'blur(24px) saturate(180%)',
        WebkitBackdropFilter: 'blur(24px) saturate(180%)',
        boxShadow: scrolled ? '0 4px 32px rgba(0,0,0,0.5)' : 'none',
        transition: 'background 0.4s ease, box-shadow 0.4s ease',
      }}
    >
      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '66px',
        }}
      >
        {/* Logo */}
        <Link to="/" style={{ textDecoration: 'none' }}>
          <motion.div
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            {/* Icon mark */}
            <motion.div
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
              style={{
                width: 32,
                height: 32,
                borderRadius: '8px',
                background: 'var(--accent-gradient)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1rem',
                boxShadow: '0 0 16px rgba(234,88,12,0.4)',
              }}
            >
              ⬡
            </motion.div>
            <span
              style={{
                fontSize: '1.375rem',
                fontWeight: '800',
                background: 'var(--accent-gradient)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                letterSpacing: '-0.03em',
              }}
            >
              DevShowcase
            </span>
          </motion.div>
        </Link>

        {/* Desktop nav */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.75rem' }}>
          {user ? (
            <>
              <Link to="/dashboard" className="navbar-link">Dashboard</Link>
              <Link to="/project/new" className="navbar-link">New Project</Link>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {/* Avatar */}
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: '50%',
                    background: 'var(--accent-gradient)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.875rem',
                    fontWeight: '700',
                    color: 'white',
                    boxShadow: '0 0 12px rgba(234,88,12,0.4)',
                    cursor: 'default',
                  }}
                  title={user.username}
                >
                  {avatarLetter}
                </motion.div>
                <motion.button
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.96 }}
                  onClick={handleLogout}
                  className="btn btn-ghost"
                  style={{ padding: '0.45rem 1rem', fontSize: '0.875rem' }}
                >
                  Logout
                </motion.button>
              </div>
            </>
          ) : (
            <Link to="/login">
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: 'var(--shadow-glow)' }}
                whileTap={{ scale: 0.96 }}
                className="btn btn-primary"
                style={{ padding: '0.6rem 1.4rem' }}
              >
                ✦ Get Started
              </motion.button>
            </Link>
          )}
        </div>
      </div>
    </motion.nav>
  )
}

export default Navbar
