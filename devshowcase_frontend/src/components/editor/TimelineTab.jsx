import { useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import './EditorTabs.css'

const TimelineTab = ({ project, onUpdate }) => {
  const [formData, setFormData] = useState({ title: '', description: '', event_date: '' })

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/timeline/', { ...formData, project: project.id })
      toast.success('Timeline event added')
      setFormData({ title: '', description: '', event_date: '' })
      onUpdate()
    } catch {
      toast.error('Failed to add timeline event')
    }
  }

  return (
    <div>
      <h3 className="editor-section-title">📅 Project Timeline</h3>

      {/* Existing events */}
      <div style={{ marginBottom: '2rem', position: 'relative' }}>
        {project.timeline_events.length > 0 && (
          <div style={{
            position: 'absolute',
            left: '100px',
            top: 0, bottom: 0,
            width: '2px',
            background: 'linear-gradient(to bottom, var(--accent-primary), transparent)',
            opacity: 0.3,
          }} />
        )}
        {project.timeline_events.length === 0 ? (
          <div style={{
            padding: '2.5rem',
            textAlign: 'center',
            background: 'rgba(17,24,39,0.4)',
            border: '2px dashed var(--border-secondary)',
            borderRadius: 'var(--radius-lg)',
            color: 'var(--text-muted)',
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📅</div>
            <p style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>No timeline events yet</p>
            <p style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>Add milestones to show your project's journey</p>
          </div>
        ) : (
          project.timeline_events.map((event, i) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.07 }}
              style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start', marginBottom: '1.25rem' }}
            >
              <div style={{
                flexShrink: 0,
                width: '100px',
                textAlign: 'right',
                paddingTop: '0.9rem',
                fontSize: '0.78rem',
                fontWeight: 700,
                color: 'var(--accent-primary)',
                letterSpacing: '0.02em',
              }}>
                {event.event_date}
              </div>
              <div style={{
                flex: 1,
                background: 'rgba(17,24,39,0.6)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-lg)',
                padding: '1.125rem 1.375rem',
                position: 'relative',
                transition: 'border-color 0.2s',
              }}>
                {/* Glowing dot */}
                <div style={{
                  position: 'absolute',
                  left: '-8px', top: '1rem',
                  width: '14px', height: '14px',
                  borderRadius: '50%',
                  background: 'var(--accent-primary)',
                  border: '3px solid var(--bg-secondary)',
                  boxShadow: '0 0 10px rgba(234,88,12,0.5)',
                }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>{event.title}</h4>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.65 }}>{event.description}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Add form */}
      <div className="editor-form">
        <h4 className="editor-form-title">+ Add New Event</h4>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Event Title</label>
            <input type="text" className="form-input" value={formData.title} onChange={e => setFormData({ ...formData, title: e.target.value })} required />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-textarea" rows={3} value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} required />
          </div>
          <div className="form-group">
            <label className="form-label">Event Date</label>
            <input type="date" className="form-input" value={formData.event_date} onChange={e => setFormData({ ...formData, event_date: e.target.value })} required
              style={{ colorScheme: 'dark' }} />
          </div>
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} type="submit" className="btn btn-primary">
            + Add Timeline Event
          </motion.button>
        </form>
      </div>
    </div>
  )
}

export default TimelineTab
