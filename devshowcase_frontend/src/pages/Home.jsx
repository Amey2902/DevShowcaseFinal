import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import AnimatedPage from '../components/AnimatedPage'

/* ─── Floating Blob ─── */
const Blob = ({ style }) => (
  <div
    style={{
      position: 'absolute',
      borderRadius: '50%',
      filter: 'blur(80px)',
      opacity: 0.18,
      animation: 'blob-move 12s ease-in-out infinite',
      ...style,
    }}
  />
)

/* ─── Project Card ─── */
const techColors = ['#ea580c', '#db2777', '#7c3aed', '#f59e0b', '#ec4899', '#10b981']
const ProjectCard = ({ project, match_percentage, reason, index }) => {
  const accentColor = techColors[index % techColors.length]
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -6, boxShadow: `0 20px 60px rgba(0,0,0,0.5), 0 0 30px ${accentColor}28` }}
      style={{
        background: 'var(--bg-glass)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        border: '1px solid var(--border-glass)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
        cursor: 'pointer',
        position: 'relative',
        transition: 'box-shadow 0.3s ease, transform 0.3s ease',
      }}
    >
      {/* Coloured top accent border */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0,
        height: '3px',
        background: `linear-gradient(90deg, ${accentColor}, transparent)`,
      }} />

      <Link to={`/project/${project.slug}`} style={{ textDecoration: 'none', color: 'inherit' }}>
        <div style={{ padding: '1.5rem' }}>
          {/* Header row */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.875rem', marginBottom: '1rem' }}>
            <motion.div
              whileHover={{ rotate: 20 }}
              transition={{ type: 'spring', stiffness: 300 }}
              style={{
                width: 46,
                height: 46,
                borderRadius: 'var(--radius-md)',
                background: `linear-gradient(135deg, ${accentColor}33, ${accentColor}11)`,
                border: `1px solid ${accentColor}44`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.4rem',
                flexShrink: 0,
              }}
            >
              🚀
            </motion.div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <h3 style={{
                fontSize: '1.1rem',
                fontWeight: '700',
                marginBottom: '0.4rem',
                color: 'var(--text-primary)',
                letterSpacing: '-0.01em',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {project.title}
              </h3>
              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                <span className="badge badge-success">Published</span>
                {match_percentage !== null && (
                  <span className="badge" style={{
                    background: `${accentColor}20`,
                    color: accentColor,
                    border: `1px solid ${accentColor}40`,
                  }}>
                    {match_percentage}% Match
                  </span>
                )}
                {project.sandbox_available && (
                  <span className="badge badge-primary">🧪 Sandbox</span>
                )}
              </div>
            </div>
          </div>

          {/* Description */}
          <p style={{
            color: 'var(--text-secondary)',
            fontSize: '0.875rem',
            lineHeight: 1.65,
            marginBottom: '1rem',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}>
            {project.short_description}
          </p>

          {reason && (
            <p style={{
              fontSize: '0.8rem',
              color: 'var(--accent-primary)',
              fontStyle: 'italic',
              marginBottom: '1rem',
            }}>
              💡 {reason}
            </p>
          )}

          {/* Footer */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingTop: '1rem',
            borderTop: '1px solid var(--border-primary)',
          }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              by <span style={{ color: 'var(--text-tertiary)', fontWeight: 600 }}>{project.owner_username}</span>
            </span>
            <span style={{
              fontSize: '0.8rem',
              color: accentColor,
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}>
              Explore →
            </span>
          </div>
        </div>
      </Link>
    </motion.div>
  )
}

/* ─── Main Home Component ─── */
const Home = () => {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [searchResults, setSearchResults] = useState(null)

  useEffect(() => { fetchProjects() }, [])

  const fetchProjects = async () => {
    try {
      const { data } = await axios.get('/api/projects/')
      setProjects(data.filter(p => p.is_published))
    } catch {
      toast.error('Failed to fetch projects')
    } finally {
      setLoading(false)
    }
  }

  const handleAISearch = async () => {
    if (!searchQuery.trim()) { setSearchResults(null); return }
    setSearching(true)
    try {
      const { data } = await axios.post('/api/projects/search/ai/', { query: searchQuery })
      setSearchResults(data.results)
    } catch {
      toast.error('AI search failed')
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }

  const displayProjects = searchResults !== null
    ? searchResults
    : projects.map(p => ({ project: p, match_percentage: null }))

  return (
    <AnimatedPage>
      <div style={{ minHeight: 'calc(100vh - 66px)' }}>

        {/* ─── Hero Section ─── */}
        <section style={{ position: 'relative', padding: '7rem 0 5rem', textAlign: 'center', overflow: 'hidden' }}>
          {/* Background blobs */}
          <Blob style={{ width: 600, height: 600, background: '#ea580c', top: '-200px', left: '-100px', animationDelay: '0s' }} />
          <Blob style={{ width: 500, height: 500, background: '#db2777', top: '-100px', right: '-150px', animationDelay: '-4s' }} />
          <Blob style={{ width: 400, height: 400, background: '#7c3aed', bottom: '-150px', left: '30%', animationDelay: '-8s' }} />

          <div className="container" style={{ position: 'relative', zIndex: 1 }}>
            {/* Eyebrow badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.05 }}
              style={{ marginBottom: '1.5rem' }}
            >
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '0.4rem 1rem',
                background: 'rgba(234,88,12,0.12)',
                border: '1px solid rgba(234,88,12,0.3)',
                borderRadius: '9999px',
                fontSize: '0.8rem',
                fontWeight: 700,
                color: 'var(--accent-primary)',
                letterSpacing: '0.04em',
              }}>
                ✦ DEVELOPER PORTFOLIO PLATFORM
              </span>
            </motion.div>

            {/* Main headline */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
              style={{
                fontSize: 'clamp(2.5rem, 6vw, 5rem)',
                fontWeight: '900',
                marginBottom: '1.5rem',
                letterSpacing: '-0.04em',
                lineHeight: 1.05,
              }}
            >
              Explore Developer
              <br />
              <span className="text-gradient">Projects Interactively</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              style={{
                fontSize: '1.2rem',
                color: 'var(--text-secondary)',
                maxWidth: '560px',
                margin: '0 auto 2.5rem',
                lineHeight: 1.7,
              }}
            >
              Discover, test, and understand APIs through live sandboxes. No setup required.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.42 }}
              style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}
            >
              <Link to="/login">
                <motion.button
                  whileHover={{ scale: 1.06, boxShadow: 'var(--shadow-glow)' }}
                  whileTap={{ scale: 0.96 }}
                  className="btn btn-primary"
                  style={{ padding: '0.9rem 2.25rem', fontSize: '1rem' }}
                >
                  ✦ Get Started Free
                </motion.button>
              </Link>
              <motion.button
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                onClick={() => document.getElementById('projects-section')?.scrollIntoView({ behavior: 'smooth' })}
                className="btn btn-secondary"
                style={{ padding: '0.9rem 2.25rem', fontSize: '1rem' }}
              >
                Browse Projects ↓
              </motion.button>
            </motion.div>

            {/* Stats row */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.65 }}
              style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '3rem',
                marginTop: '4rem',
                flexWrap: 'wrap',
              }}
            >
              {[
                { value: projects.length || '—', label: 'Live Projects' },
                { value: '∞', label: 'API Endpoints' },
                { value: 'AI', label: 'Powered Search' },
              ].map(({ value, label }) => (
                <div key={label} style={{ textAlign: 'center' }}>
                  <div style={{
                    fontSize: '2rem',
                    fontWeight: '900',
                    background: 'var(--accent-gradient)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}>
                    {value}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', letterSpacing: '0.06em', textTransform: 'uppercase', marginTop: '0.25rem' }}>
                    {label}
                  </div>
                </div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* ─── Projects Section ─── */}
        <section id="projects-section" style={{ padding: '5rem 0 6rem' }}>
          <div className="container">

            {/* Section header */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              style={{ marginBottom: '2.5rem' }}
            >
              <h2 style={{ fontSize: '2.25rem', fontWeight: '800', marginBottom: '0.5rem', letterSpacing: '-0.02em' }}>
                {searchResults !== null ? '🔍 Search Results' : '✦ Featured Projects'}
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
                {searchResults !== null
                  ? `${displayProjects.length} project${displayProjects.length !== 1 ? 's' : ''} found`
                  : 'Live sandboxes you can explore right now'}
              </p>
            </motion.div>

            {/* AI Search Bar */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4 }}
              style={{
                marginBottom: '3rem',
                display: 'flex',
                gap: '0.75rem',
                maxWidth: '720px',
                alignItems: 'center',
              }}
            >
              <div style={{ flex: 1, position: 'relative' }}>
                <span style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  fontSize: '1rem',
                  pointerEvents: 'none',
                }}>🔍</span>
                <input
                  type="text"
                  placeholder="Search with AI: 'e-commerce React', 'auth API'..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && handleAISearch()}
                  className="form-input"
                  style={{ paddingLeft: '2.75rem' }}
                />
              </div>
              <motion.button
                whileHover={{ scale: 1.04, boxShadow: 'var(--shadow-glow-sm)' }}
                whileTap={{ scale: 0.96 }}
                onClick={handleAISearch}
                disabled={searching || !searchQuery.trim()}
                className="btn btn-primary"
                style={{ minWidth: '130px', flexShrink: 0 }}
              >
                {searching ? (
                  <motion.span
                    animate={{ opacity: [1, 0.4, 1] }}
                    transition={{ duration: 1.2, repeat: Infinity }}
                  >
                    Thinking…
                  </motion.span>
                ) : '✦ AI Search'}
              </motion.button>
              <AnimatePresence>
                {searchResults !== null && (
                  <motion.button
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    whileHover={{ scale: 1.04 }}
                    whileTap={{ scale: 0.96 }}
                    onClick={() => { setSearchQuery(''); setSearchResults(null) }}
                    className="btn btn-ghost"
                  >
                    ✕ Clear
                  </motion.button>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Cards */}
            {loading ? (
              <div className="card-grid">
                {[1, 2, 3].map(i => (
                  <div key={i} style={{
                    background: 'var(--bg-glass)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '1.5rem',
                  }}>
                    <div className="skeleton" style={{ height: '20px', width: '65%', marginBottom: '0.75rem' }} />
                    <div className="skeleton" style={{ height: '14px', width: '30%', marginBottom: '1.25rem' }} />
                    <div className="skeleton" style={{ height: '60px', marginBottom: '1rem' }} />
                    <div className="skeleton" style={{ height: '1px', marginBottom: '1rem' }} />
                    <div className="skeleton" style={{ height: '14px', width: '40%' }} />
                  </div>
                ))}
              </div>
            ) : (
              <div className="card-grid">
                {displayProjects.map(({ project, match_percentage, reason }, index) => (
                  <ProjectCard
                    key={project.id}
                    project={project}
                    match_percentage={match_percentage}
                    reason={reason}
                    index={index}
                  />
                ))}
              </div>
            )}

            {/* Empty state */}
            {!loading && displayProjects.length === 0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="empty-state"
                style={{
                  background: 'var(--bg-glass)',
                  border: '1px solid var(--border-glass)',
                  borderRadius: 'var(--radius-xl)',
                  padding: '4rem 2rem',
                }}
              >
                <div style={{ fontSize: '3.5rem', marginBottom: '0.5rem' }}>
                  {searchResults !== null ? '🔍' : '🚀'}
                </div>
                <div style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
                  {searchResults !== null
                    ? 'No projects match your search. Try different keywords!'
                    : 'No published projects yet. Be the first to create one!'}
                </div>
              </motion.div>
            )}
          </div>
        </section>
      </div>
    </AnimatedPage>
  )
}

export default Home
