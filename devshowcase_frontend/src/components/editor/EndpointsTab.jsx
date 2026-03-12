import { useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import './EditorTabs.css'

const methodColor = {
  GET: '#3b82f6',
  POST: '#10b981',
  PUT: '#f59e0b',
  PATCH: '#db2777',
  DELETE: '#ef4444',
}

const EndpointsTab = ({ project, onUpdate }) => {
  const [formData, setFormData] = useState({
    name: '', method: 'GET', url: '', headers: '{}', sample_body: '{}', description: '',
  })

  // Debug logging
  console.log('EndpointsTab - project:', project)
  console.log('EndpointsTab - project.endpoints:', project?.endpoints)

  // Safety check for endpoints
  const endpoints = project?.endpoints || []

  // If project is not loaded yet, show loading
  if (!project) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div className="loading-spinner" />
        <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>Loading endpoints...</p>
      </div>
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/endpoints/', {
        ...formData,
        project: project.id,
        headers: JSON.parse(formData.headers),
        sample_body: JSON.parse(formData.sample_body),
      })
      toast.success('Endpoint added')
      setFormData({ name: '', method: 'GET', url: '', headers: '{}', sample_body: '{}', description: '' })
      onUpdate()
    } catch (error) {
      toast.error(error.response?.data?.url?.[0] || 'Failed to add endpoint')
    }
  }

  const handleDelete = async (endpointId) => {
    if (!window.confirm('Delete this endpoint?')) return
    try {
      await axios.delete(`/api/endpoints/${endpointId}/delete/`)
      toast.success('Endpoint deleted')
      onUpdate()
    } catch {
      toast.error('Failed to delete endpoint')
    }
  }

  return (
    <div>
      <h3 className="editor-section-title">🔌 API Endpoints</h3>

      {/* Existing endpoints */}
      <div style={{ marginBottom: '2rem' }}>
        {endpoints.length === 0 ? (
          <div style={{
            padding: '3rem',
            textAlign: 'center',
            background: 'rgba(17,24,39,0.4)',
            border: '2px dashed var(--border-secondary)',
            borderRadius: 'var(--radius-lg)',
            color: 'var(--text-muted)',
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📭</div>
            <p style={{ fontWeight: 600, fontSize: '1rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>No endpoints yet</p>
            <p style={{ fontSize: '0.875rem' }}>Add one manually below or use the 🤖 Auto-Detect tab to scan your code.</p>
          </div>
        ) : (
          endpoints.map((endpoint, i) => (
            <motion.div
              key={endpoint.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              style={{
                background: 'rgba(17,24,39,0.6)',
                border: '1px solid var(--border-primary)',
                borderLeft: `3px solid ${methodColor[endpoint.method] || '#6b7280'}`,
                borderRadius: 'var(--radius-lg)',
                padding: '1.25rem 1.5rem',
                marginBottom: '1rem',
                position: 'relative',
                transition: 'border-color 0.2s, box-shadow 0.2s',
              }}
              whileHover={{ boxShadow: 'var(--shadow-glow-sm)' }}
            >
              {/* AI detected badge */}
              {endpoint.auto_detected && (
                <div style={{
                  position: 'absolute', top: '1rem', right: '1rem',
                  padding: '0.3rem 0.75rem',
                  background: 'linear-gradient(135deg, #059669, #34d399)',
                  color: 'white',
                  borderRadius: '6px',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  display: 'flex', alignItems: 'center', gap: '4px',
                  letterSpacing: '0.04em',
                }}>
                  ✨ AI Detected
                </div>
              )}

              {/* Method + name row */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                <span style={{
                  padding: '0.3rem 0.75rem',
                  background: methodColor[endpoint.method] || '#6b7280',
                  color: 'white',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  fontWeight: 800,
                  letterSpacing: '0.04em',
                  flexShrink: 0,
                }}>
                  {endpoint.method}
                </span>
                <span style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{endpoint.name}</span>
                {endpoint.auth_required && (
                  <span style={{
                    padding: '0.25rem 0.625rem',
                    background: 'rgba(251,191,36,0.15)',
                    color: 'var(--warning)',
                    border: '1px solid rgba(251,191,36,0.3)',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                  }}>🔒 Auth Required</span>
                )}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleDelete(endpoint.id)}
                  className="btn btn-danger"
                  style={{ marginLeft: 'auto', padding: '0.35rem 0.875rem', fontSize: '0.8rem' }}
                >
                  🗑 Delete
                </motion.button>
              </div>

              {/* URL */}
              <div style={{
                padding: '0.6rem 1rem',
                background: 'rgba(10,15,30,0.6)',
                borderRadius: '6px',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.875rem',
                color: 'var(--accent-cyan)',
                marginBottom: '0.75rem',
                border: '1px solid var(--border-primary)',
                wordBreak: 'break-all',
              }}>
                {endpoint.url}
              </div>

              {endpoint.description && (
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.65, marginBottom: '0.75rem' }}>
                  {endpoint.description}
                </p>
              )}

              {/* AI-detected metadata */}
              {endpoint.auto_detected && (
                <div style={{
                  padding: '1rem',
                  background: 'rgba(124,58,237,0.05)',
                  border: '1px solid rgba(124,58,237,0.15)',
                  borderRadius: '8px',
                  marginTop: '0.75rem',
                  fontSize: '0.85rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                }}>
                  {endpoint.detected_from_file && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <span>📁</span>
                      <strong style={{ color: 'var(--accent-cyan)' }}>Source:</strong>
                      <span style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>{endpoint.detected_from_file}</span>
                      {endpoint.detected_at_line && (
                        <span style={{ padding: '0.1rem 0.5rem', background: 'rgba(124,58,237,0.2)', color: 'var(--accent-cyan)', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                          Line {endpoint.detected_at_line}
                        </span>
                      )}
                    </div>
                  )}
                  {endpoint.path_parameters?.length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <span>🔗</span>
                      <strong style={{ color: 'var(--accent-cyan)' }}>Path Params:</strong>
                      {endpoint.path_parameters.map((p, i) => (
                        <span key={i} style={{ padding: '0.15rem 0.5rem', background: 'rgba(234,88,12,0.2)', color: 'var(--accent-primary)', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                          {typeof p === 'object' ? p.name || JSON.stringify(p) : p}
                        </span>
                      ))}
                    </div>
                  )}
                  {endpoint.query_parameters?.length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <span>❓</span>
                      <strong style={{ color: 'var(--accent-cyan)' }}>Query Params:</strong>
                      {endpoint.query_parameters.map((p, i) => (
                        <span key={i} style={{ padding: '0.15rem 0.5rem', background: 'rgba(124,58,237,0.2)', color: 'var(--accent-cyan)', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                          {typeof p === 'object' ? p.name || JSON.stringify(p) : p}
                        </span>
                      ))}
                    </div>
                  )}
                  {endpoint.auth_type && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span>🔐</span>
                      <strong style={{ color: 'var(--accent-cyan)' }}>Auth:</strong>
                      <span style={{ padding: '0.15rem 0.5rem', background: 'rgba(251,191,36,0.2)', color: 'var(--warning)', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>{endpoint.auth_type}</span>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          ))
        )}
      </div>

      {/* Add form */}
      <div className="editor-form">
        <h4 className="editor-form-title">+ Add New Endpoint</h4>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Endpoint Name</label>
            <input type="text" className="form-input" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required />
          </div>
          <div className="form-group">
            <label className="form-label">HTTP Method</label>
            <select className="form-select" value={formData.method} onChange={e => setFormData({ ...formData, method: e.target.value })}
              style={{ color: methodColor[formData.method] || 'var(--text-primary)', fontWeight: 700 }}>
              {['GET', 'POST', 'PUT', 'PATCH', 'DELETE'].map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">URL</label>
            <input type="url" className="form-input" value={formData.url} onChange={e => setFormData({ ...formData, url: e.target.value })} required />
          </div>
          <div className="form-group">
            <label className="form-label">Headers (JSON)</label>
            <textarea className="form-textarea code-textarea" rows={3} value={formData.headers} onChange={e => setFormData({ ...formData, headers: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Sample Body (JSON)</label>
            <textarea className="form-textarea code-textarea" rows={4} value={formData.sample_body} onChange={e => setFormData({ ...formData, sample_body: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-textarea" rows={3} value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} />
          </div>
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} type="submit" className="btn btn-primary">
            + Add Endpoint
          </motion.button>
        </form>
      </div>
    </div>
  )
}

export default EndpointsTab
