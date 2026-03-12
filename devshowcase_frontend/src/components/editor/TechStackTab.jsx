import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import './EditorTabs.css'

const TechStackTab = ({ project, onUpdate }) => {
  const [formData, setFormData] = useState({ name: '', purpose: '', reason: '', alternative: '' })

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/techstack/', { ...formData, project: project.id })
      toast.success('Tech stack item added')
      setFormData({ name: '', purpose: '', reason: '', alternative: '' })
      onUpdate()
    } catch {
      toast.error('Failed to add tech stack item')
    }
  }

  const techColors = ['#ea580c', '#db2777', '#7c3aed', '#f59e0b', '#ec4899', '#10b981']

  return (
    <div>
      <h3 className="editor-section-title">🛠 Tech Stack</h3>

      {/* Existing tech stack */}
      <div style={{ marginBottom: '2rem' }}>
        {project.tech_stack.length === 0 ? (
          <div style={{
            padding: '2.5rem',
            textAlign: 'center',
            background: 'rgba(17,24,39,0.4)',
            border: '2px dashed var(--border-secondary)',
            borderRadius: 'var(--radius-lg)',
            color: 'var(--text-muted)',
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🔧</div>
            <p style={{ fontWeight: 600 }}>No technologies added yet</p>
            <p style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>Use the form below to add your stack</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
            {project.tech_stack.map((item, i) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                style={{
                  background: 'rgba(17,24,39,0.6)',
                  border: '1px solid var(--border-primary)',
                  borderLeft: `3px solid ${techColors[i % techColors.length]}`,
                  borderRadius: 'var(--radius-lg)',
                  padding: '1.25rem',
                  transition: 'border-color 0.2s ease',
                }}
              >
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
                  {item.name}
                </h4>
                <p style={{ fontSize: '0.8rem', color: techColors[i % techColors.length], fontWeight: 600, marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  {item.purpose}
                </p>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{item.reason}</p>
                {item.alternative && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>Alt: {item.alternative}</p>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Add form */}
      <div className="editor-form">
        <h4 className="editor-form-title">+ Add New Technology</h4>
        <form onSubmit={handleSubmit}>
          {[
            { key: 'name', label: 'Technology Name', type: 'input', required: true },
            { key: 'purpose', label: 'Purpose', type: 'input', required: true },
            { key: 'reason', label: 'Why this tech?', type: 'textarea', required: true },
            { key: 'alternative', label: 'Alternative (Optional)', type: 'input', required: false },
          ].map(({ key, label, type, required }) => (
            <div key={key} className="form-group">
              <label className="form-label">{label}</label>
              {type === 'textarea' ? (
                <textarea className="form-textarea" rows={3} value={formData[key]} onChange={e => setFormData({ ...formData, [key]: e.target.value })} required={required} />
              ) : (
                <input type="text" className="form-input" value={formData[key]} onChange={e => setFormData({ ...formData, [key]: e.target.value })} required={required} />
              )}
            </div>
          ))}
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} type="submit" className="btn btn-primary">
            + Add Tech Stack Item
          </motion.button>
        </form>
      </div>
    </div>
  )
}

export default TechStackTab
