import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import AnimatedPage from '../components/AnimatedPage'

const ProjectNew = () => {
  const [formData, setFormData] = useState({ title: '', short_description: '', category: '' })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await axios.post('/api/projects/create/', formData)
      toast.success('Project created!')
      navigate(`/project/edit/${data.slug}`)
    } catch {
      toast.error('Failed to create project')
    } finally {
      setLoading(false)
    }
  }

  const fields = [
    { key: 'title', label: 'Project Title', type: 'input', placeholder: 'e.g. E-Commerce REST API' },
    { key: 'short_description', label: 'Short Description', type: 'textarea', placeholder: 'A brief description of what your project does…' },
    { key: 'category', label: 'Category', type: 'input', placeholder: 'e.g. Web API, Machine Learning, CLI Tool' },
  ]

  return (
    <AnimatedPage>
      <div style={{
        minHeight: 'calc(100vh - 66px)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        padding: '4rem 1.5rem',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background glow */}
        <div style={{
          position: 'absolute', top: '10%', right: '5%',
          width: '400px', height: '400px', borderRadius: '50%',
          background: 'rgba(234,88,12,0.08)', filter: 'blur(80px)',
          pointerEvents: 'none',
        }} />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{ width: '100%', maxWidth: '640px', position: 'relative', zIndex: 1 }}
        >
          {/* Page header */}
          <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
              style={{
                width: 56, height: 56,
                borderRadius: 'var(--radius-lg)',
                background: 'var(--accent-gradient)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.5rem',
                margin: '0 auto 1.25rem',
                boxShadow: 'var(--shadow-glow-sm)',
              }}
            >
              🚀
            </motion.div>
            <h1 style={{
              fontSize: '2rem',
              fontWeight: '900',
              letterSpacing: '-0.025em',
              marginBottom: '0.5rem',
            }}>
              Create New Project
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Start with the basics — you can add more details in the editor
            </p>
          </div>

          {/* Form card */}
          <div style={{
            background: 'var(--bg-glass)',
            backdropFilter: 'blur(20px) saturate(180%)',
            WebkitBackdropFilter: 'blur(20px) saturate(180%)',
            border: '1px solid var(--border-glass)',
            borderRadius: 'var(--radius-xl)',
            padding: '2.5rem',
            boxShadow: 'var(--shadow-lg)',
          }}>
            <form onSubmit={handleSubmit}>
              {fields.map(({ key, label, type, placeholder }, i) => (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15 + i * 0.08 }}
                  className="form-group"
                >
                  <label className="form-label">{label}</label>
                  {type === 'textarea' ? (
                    <textarea
                      className="form-textarea"
                      rows={3}
                      placeholder={placeholder}
                      value={formData[key]}
                      onChange={e => setFormData({ ...formData, [key]: e.target.value })}
                    />
                  ) : (
                    <input
                      type="text"
                      className="form-input"
                      placeholder={placeholder}
                      value={formData[key]}
                      onChange={e => setFormData({ ...formData, [key]: e.target.value })}
                      required={key === 'title'}
                    />
                  )}
                </motion.div>
              ))}

              <motion.button
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.45 }}
                whileHover={{ scale: 1.02, boxShadow: 'var(--shadow-glow)' }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={loading}
                className="btn btn-primary"
                style={{ width: '100%', padding: '0.9rem', fontSize: '1rem', marginTop: '0.5rem' }}
              >
                {loading ? (
                  <motion.span animate={{ opacity: [1, 0.4, 1] }} transition={{ duration: 1.2, repeat: Infinity }}>
                    Creating project…
                  </motion.span>
                ) : '🚀 Create Project'}
              </motion.button>
            </form>
          </div>
        </motion.div>
      </div>
    </AnimatedPage>
  )
}

export default ProjectNew
