import { useState, useEffect, useContext } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { AuthContext } from '../context/AuthContext'
import { toast } from 'react-toastify'
import AnimatedPage from '../components/AnimatedPage'

const StatusBadge = ({ published }) =>
  published ? (
    <span className="badge badge-success">✓ Published</span>
  ) : (
    <span className="badge badge-gray">Draft</span>
  )

const Dashboard = () => {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)
  const { user } = useContext(AuthContext)

  useEffect(() => { fetchProjects() }, [])

  const fetchProjects = async () => {
    try {
      const { data } = await axios.get('/api/projects/')
      setProjects(data.filter(p => p.owner_username === user.username))
    } catch {
      toast.error('Failed to fetch projects')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (slug) => {
    if (!window.confirm('Are you sure you want to delete this project?')) return
    setDeleting(slug)
    try {
      await axios.delete(`/api/projects/${slug}/delete/`)
      toast.success('Project deleted')
      setProjects(prev => prev.filter(p => p.slug !== slug))
    } catch {
      toast.error('Failed to delete project')
    } finally {
      setDeleting(null)
    }
  }

  const published = projects.filter(p => p.is_published).length
  const drafts = projects.length - published

  return (
    <AnimatedPage>
      <div className="container" style={{ paddingTop: '3rem', paddingBottom: '4rem' }}>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{ marginBottom: '2.5rem' }}
        >
          {/* Welcome banner */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(234,88,12,0.12), rgba(219,39,119,0.08))',
            border: '1px solid rgba(234,88,12,0.2)',
            borderRadius: 'var(--radius-xl)',
            padding: '2rem 2.5rem',
            marginBottom: '2.5rem',
            position: 'relative',
            overflow: 'hidden',
          }}>
            {/* Glow orb */}
            <div style={{
              position: 'absolute',
              top: '-40px', right: '-40px',
              width: '200px', height: '200px',
              borderRadius: '50%',
              background: 'rgba(234,88,12,0.15)',
              filter: 'blur(40px)',
              pointerEvents: 'none',
            }} />
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1.5rem' }}>
              <div>
                <p style={{ color: 'var(--accent-primary)', fontWeight: 700, fontSize: '0.8rem', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                  WELCOME BACK
                </p>
                <h1 style={{ fontSize: '2.25rem', fontWeight: '900', marginBottom: '0.4rem', letterSpacing: '-0.02em' }}>
                  {user?.username}'s Studio
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
                  Manage and showcase your developer projects
                </p>
              </div>
              <Link to="/project/new">
                <motion.button
                  whileHover={{ scale: 1.05, boxShadow: 'var(--shadow-glow)' }}
                  whileTap={{ scale: 0.96 }}
                  className="btn btn-primary"
                  style={{ padding: '0.875rem 1.75rem', fontSize: '0.95rem' }}
                >
                  + New Project
                </motion.button>
              </Link>
            </div>
          </div>

          {/* Stats row */}
          {!loading && (
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
              {[
                { label: 'Total Projects', value: projects.length, color: '#fb923c' },
                { label: 'Published', value: published, color: '#34d399' },
                { label: 'Drafts', value: drafts, color: '#fbbf24' },
              ].map(({ label, value, color }) => (
                <motion.div
                  key={label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ type: 'spring', stiffness: 260, damping: 20 }}
                  style={{
                    flex: '1 1 140px',
                    background: 'var(--bg-glass)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '1.25rem 1.5rem',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '2rem', fontWeight: '900', color }}>{value}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: '0.25rem' }}>
                    {label}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Project list */}
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
                <div className="skeleton" style={{ height: '20px', width: '60%', marginBottom: '0.75rem' }} />
                <div className="skeleton" style={{ height: '60px', marginBottom: '1rem' }} />
                <div className="skeleton" style={{ height: '36px', width: '45%' }} />
              </div>
            ))}
          </div>
        ) : (
          <AnimatePresence>
            <div className="card-grid">
              {projects.map((project, i) => (
                <motion.div
                  key={project.id}
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.35, delay: i * 0.06 }}
                  whileHover={{ y: -4, boxShadow: 'var(--shadow-glow-sm), var(--shadow-md)' }}
                  style={{
                    background: 'var(--bg-glass)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: 'var(--radius-lg)',
                    overflow: 'hidden',
                    transition: 'box-shadow 0.3s ease, transform 0.3s ease',
                    position: 'relative',
                  }}
                >
                  {/* Status accent top border */}
                  <div style={{
                    position: 'absolute', top: 0, left: 0, right: 0, height: '2px',
                    background: project.is_published
                      ? 'linear-gradient(90deg, #34d399, transparent)'
                      : 'linear-gradient(90deg, #fbbf24, transparent)',
                  }} />

                  <div style={{ padding: '1.5rem' }}>
                    <Link to={`/project/${project.slug}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                      <h3 style={{
                        fontSize: '1.1rem',
                        fontWeight: '700',
                        marginBottom: '0.5rem',
                        letterSpacing: '-0.01em',
                        color: 'var(--text-primary)',
                      }}>
                        {project.title}
                      </h3>
                      <p style={{
                        color: 'var(--text-secondary)',
                        fontSize: '0.875rem',
                        lineHeight: 1.6,
                        marginBottom: '1.25rem',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}>
                        {project.short_description}
                      </p>
                    </Link>

                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      paddingTop: '1rem',
                      borderTop: '1px solid var(--border-primary)',
                    }}>
                      <StatusBadge published={project.is_published} />
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <Link to={`/project/edit/${project.slug}`}>
                          <motion.button
                            whileHover={{ scale: 1.06 }}
                            whileTap={{ scale: 0.95 }}
                            className="btn btn-ghost"
                            style={{ padding: '0.45rem 1rem', fontSize: '0.8rem' }}
                          >
                            ✏ Edit
                          </motion.button>
                        </Link>
                        <motion.button
                          whileHover={{ scale: 1.06 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => handleDelete(project.slug)}
                          disabled={deleting === project.slug}
                          className="btn btn-danger"
                          style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem' }}
                        >
                          {deleting === project.slug ? '…' : '✕'}
                        </motion.button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </AnimatePresence>
        )}

        {/* Empty state */}
        {!loading && projects.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
            style={{
              background: 'var(--bg-glass)',
              backdropFilter: 'blur(16px)',
              border: '1px solid var(--border-glass)',
              borderRadius: 'var(--radius-xl)',
              textAlign: 'center',
              padding: '5rem 2rem',
            }}
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
              style={{ fontSize: '4rem', marginBottom: '1.25rem' }}
            >
              🚀
            </motion.div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.75rem' }}>No projects yet</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
              Create your first project to get started
            </p>
            <Link to="/project/new">
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: 'var(--shadow-glow)' }}
                whileTap={{ scale: 0.96 }}
                className="btn btn-primary"
                style={{ padding: '0.875rem 2rem' }}
              >
                Create Your First Project
              </motion.button>
            </Link>
          </motion.div>
        )}
      </div>
    </AnimatedPage>
  )
}

export default Dashboard
