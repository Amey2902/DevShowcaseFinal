import { useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import './EditorTabs.css'

const OverviewTab = ({ project, onUpdate }) => {
  const [formData, setFormData] = useState({
    title: project.title,
    short_description: project.short_description,
    problem_statement: project.problem_statement,
    category: project.category,
    github_url: project.github_url,
    demo_url: project.demo_url,
  })
  const [generatingSandbox, setGeneratingSandbox] = useState(false)
  const [sandboxActive, setSandboxActive] = useState(project.sandbox_available || false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.put(`/api/projects/${project.slug}/update/`, formData)
      toast.success('Overview updated')
      onUpdate()
    } catch {
      toast.error('Failed to update overview')
    }
  }

  const handleGenerateSandbox = async () => {
    setGeneratingSandbox(true)
    try {
      await axios.post(`/api/sandbox/generate/${project.id}/`)
      toast.success(sandboxActive ? 'Sandbox regenerated successfully' : 'Sandbox generated successfully')
      setSandboxActive(true)
      onUpdate()
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to generate sandbox')
    } finally {
      setGeneratingSandbox(false)
    }
  }

  return (
    <div>
      {/* Sandbox section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          marginBottom: '2rem',
          padding: '1.5rem',
          background: sandboxActive
            ? 'linear-gradient(135deg, rgba(52,211,153,0.12), rgba(124,58,237,0.08))'
            : 'linear-gradient(135deg, rgba(234,88,12,0.12), rgba(219,39,119,0.08))',
          border: `1px solid ${sandboxActive ? 'rgba(52,211,153,0.25)' : 'rgba(234,88,12,0.25)'}`,
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
            <span style={{ fontSize: '1.25rem' }}>{sandboxActive ? '🟢' : '⚪'}</span>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Sandbox Mode</h3>
          </div>
          <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            {sandboxActive
              ? '✓ Sandbox is active — API requests will execute in isolated mode'
              : 'Generate a sandbox to let visitors test your API endpoints live'}
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
          type="button"
          onClick={handleGenerateSandbox}
          disabled={generatingSandbox}
          className={`btn ${sandboxActive ? 'btn-success' : 'btn-primary'}`}
          style={{ padding: '0.65rem 1.25rem', fontSize: '0.875rem', flexShrink: 0 }}
        >
          {generatingSandbox ? '⏳ Generating…' : sandboxActive ? '🔄 Regenerate Sandbox' : '⚙️ Generate Sandbox'}
        </motion.button>
      </motion.div>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        {[
          { key: 'title', label: 'Title', type: 'input' },
          { key: 'short_description', label: 'Short Description', type: 'textarea', rows: 3 },
          { key: 'problem_statement', label: 'Problem Statement', type: 'textarea', rows: 5 },
          { key: 'category', label: 'Category', type: 'input' },
          { key: 'github_url', label: 'GitHub URL', type: 'url' },
          { key: 'demo_url', label: 'Demo URL', type: 'url' },
        ].map(({ key, label, type, rows }, i) => (
          <motion.div
            key={key}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="form-group"
          >
            <label className="form-label">{label}</label>
            {type === 'textarea' ? (
              <textarea
                className="form-textarea"
                rows={rows}
                value={formData[key] || ''}
                onChange={e => setFormData({ ...formData, [key]: e.target.value })}
              />
            ) : (
              <input
                type={type}
                className="form-input"
                value={formData[key] || ''}
                onChange={e => setFormData({ ...formData, [key]: e.target.value })}
              />
            )}
          </motion.div>
        ))}
        <motion.button
          whileHover={{ scale: 1.02, boxShadow: 'var(--shadow-glow-sm)' }}
          whileTap={{ scale: 0.98 }}
          type="submit"
          className="btn btn-primary"
          style={{ padding: '0.75rem 2rem' }}
        >
          💾 Save Overview
        </motion.button>
      </form>
    </div>
  )
}

export default OverviewTab
