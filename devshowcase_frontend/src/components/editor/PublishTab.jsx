import { useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'
import './EditorTabs.css'

const PublishTab = ({ project, onUpdate }) => {
  const [isPublished, setIsPublished] = useState(project.is_published)
  const [loading, setLoading] = useState(false)

  const handleTogglePublish = async () => {
    setLoading(true)
    try {
      await axios.put(`/api/projects/${project.slug}/update/`, { is_published: !isPublished })
      setIsPublished(!isPublished)
      toast.success(isPublished ? 'Project unpublished' : '🎉 Project published!')
      onUpdate()
    } catch {
      toast.error('Failed to update publish status')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="editor-section-title">📢 Publish Project</h3>

      <div style={{
        background: isPublished
          ? 'linear-gradient(135deg, rgba(52,211,153,0.08), rgba(124,58,237,0.06))'
          : 'rgba(17,24,39,0.5)',
        border: `1px solid ${isPublished ? 'rgba(52,211,153,0.25)' : 'var(--border-glass)'}`,
        borderRadius: 'var(--radius-xl)',
        padding: '2.5rem',
      }}>
        {/* Status indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
          <motion.div
            animate={isPublished ? { scale: [1, 1.15, 1] } : {}}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            style={{
              width: 48, height: 48,
              borderRadius: '50%',
              background: isPublished ? 'rgba(52,211,153,0.15)' : 'rgba(100,116,139,0.15)',
              border: `2px solid ${isPublished ? 'var(--success)' : 'var(--border-secondary)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
            }}
          >
            {isPublished ? '✓' : '○'}
          </motion.div>
          <div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.25rem' }}>
              Current Status
            </p>
            <span className={isPublished ? 'badge badge-success' : 'badge badge-gray'} style={{ fontSize: '0.85rem' }}>
              {isPublished ? '✓ Published' : 'Draft'}
            </span>
          </div>
        </div>

        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', lineHeight: 1.65, marginBottom: '2rem' }}>
          {isPublished
            ? 'Your project is live and visible to the public. Visitors can explore your API endpoints and architecture.'
            : 'Your project is private — only you can see it. Publish when you\'re ready to share it with the world.'}
        </p>

        {/* Action buttons */}
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <motion.button
            whileHover={{ scale: 1.04, boxShadow: isPublished ? '0 0 20px rgba(248,113,113,0.3)' : 'var(--shadow-glow)' }}
            whileTap={{ scale: 0.96 }}
            onClick={handleTogglePublish}
            disabled={loading}
            className={`btn ${isPublished ? 'btn-danger' : 'btn-success'}`}
            style={{ padding: '0.75rem 2rem', fontSize: '0.95rem' }}
          >
            {loading ? '⏳ Updating…' : isPublished ? '⬇ Unpublish Project' : '🚀 Publish Project'}
          </motion.button>

          {isPublished && (
            <Link to={`/project/${project.slug}`} target="_blank" rel="noopener noreferrer">
              <motion.button
                whileHover={{ scale: 1.04 }}
                className="btn btn-secondary"
                style={{ padding: '0.75rem 1.5rem', fontSize: '0.95rem' }}
              >
                👁 View Public Page ↗
              </motion.button>
            </Link>
          )}
        </div>

        {/* Public URL */}
        {isPublished && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
            style={{ marginTop: '2rem' }}
          >
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
              Public URL
            </p>
            <div style={{
              padding: '0.75rem 1rem',
              background: 'rgba(10,15,30,0.6)',
              border: '1px solid var(--border-primary)',
              borderRadius: 'var(--radius-md)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.875rem',
              color: 'var(--accent-cyan)',
              wordBreak: 'break-all',
            }}>
              {window.location.origin}/project/{project.slug}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default PublishTab
