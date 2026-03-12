import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const getStatusIcon = (s) => ({ uploading: '📤', extracting: '📦', scanning: '🔍', analyzing: '🤖', extracting_endpoints: '🎯', completed: '✅', failed: '❌' }[s] || '⏳')
const getStatusLabel = (s) => ({ uploading: 'Uploading', extracting: 'Extracting Files', scanning: 'Security Scanning', analyzing: 'AI Analysis', extracting_endpoints: 'Extracting Endpoints', completed: 'Completed!', failed: 'Failed' }[s] || 'Processing…')

const AnalysisProgress = ({ uploadId, onComplete }) => {
  const [status, setStatus] = useState(null)
  const [polling, setPolling] = useState(true)

  useEffect(() => {
    if (!uploadId || !polling) return
    const pollStatus = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/uploads/${uploadId}/status/`, {
          headers: { 'Authorization': `Token ${localStorage.getItem('token')}` },
        })
        if (res.ok) {
          const data = await res.json()
          setStatus(data)
          if (data.status === 'completed' || data.status === 'failed') {
            setPolling(false)
            if (data.status === 'completed' && onComplete) onComplete(data)
          }
        }
      } catch (err) { console.error('Error polling status:', err) }
    }
    pollStatus()
    const interval = setInterval(pollStatus, 2000)
    return () => clearInterval(interval)
  }, [uploadId, polling, onComplete])

  if (!status) return (
    <div style={{
      background: 'var(--bg-glass)',
      backdropFilter: 'blur(16px)',
      border: '1px solid var(--border-glass)',
      borderRadius: 'var(--radius-lg)',
      padding: '2rem',
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
    }}>
      <div className="loading-spinner" />
      <span style={{ color: 'var(--text-secondary)' }}>Connecting to AI…</span>
    </div>
  )

  const isCompleted = status.status === 'completed'
  const isFailed = status.status === 'failed'
  const barColor = isFailed ? '#f87171' : isCompleted ? '#34d399' : 'var(--accent-gradient)'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        background: isCompleted
          ? 'linear-gradient(135deg, rgba(52,211,153,0.08), rgba(124,58,237,0.06))'
          : isFailed
            ? 'rgba(248,113,113,0.06)'
            : 'var(--bg-glass)',
        backdropFilter: 'blur(16px)',
        border: `1px solid ${isCompleted ? 'rgba(52,211,153,0.25)' : isFailed ? 'rgba(248,113,113,0.25)' : 'var(--border-glass)'}`,
        borderRadius: 'var(--radius-lg)',
        padding: '2rem',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <motion.span
            animate={!isCompleted && !isFailed ? { rotate: 360 } : {}}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            style={{ fontSize: '1.75rem' }}
          >
            {getStatusIcon(status.status)}
          </motion.span>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
            {getStatusLabel(status.status)}
          </h3>
        </div>
        {isCompleted && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200 }}
          >
            <span className="badge badge-success" style={{ fontSize: '0.85rem', padding: '0.4rem 1rem' }}>
              {status.endpoints_found} endpoints found
            </span>
          </motion.div>
        )}
      </div>

      {/* Progress bar */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{status.current_message}</span>
          <span style={{ fontSize: '0.875rem', fontWeight: 700, color: isCompleted ? 'var(--success)' : isFailed ? 'var(--error)' : 'var(--accent-primary)' }}>
            {status.progress_percentage}%
          </span>
        </div>
        <div style={{
          width: '100%',
          height: '8px',
          background: 'rgba(17,24,39,0.8)',
          borderRadius: '4px',
          overflow: 'hidden',
          border: '1px solid var(--border-primary)',
        }}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${status.progress_percentage}%` }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            style={{
              height: '100%',
              borderRadius: '4px',
              background: isFailed ? '#f87171' : isCompleted ? '#34d399' : 'linear-gradient(90deg, #ea580c, #db2777, #7c3aed)',
              backgroundSize: '200% 100%',
              animation: !isCompleted && !isFailed ? 'gradient-shift 2s linear infinite' : 'none',
            }}
          />
        </div>
      </div>

      {/* Metadata */}
      {(status.detected_language || status.detected_framework) && (
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          {status.detected_language && (
            <div style={{ display: 'flex', align: 'center', gap: '0.4rem' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Language:</span>
              <span className="badge badge-primary">{status.detected_language}</span>
            </div>
          )}
          {status.detected_framework && (
            <div style={{ display: 'flex', align: 'center', gap: '0.4rem' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Framework:</span>
              <span className="badge badge-primary">{status.detected_framework}</span>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      <AnimatePresence>
        {isFailed && status.error_message && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            style={{
              padding: '1rem 1.25rem',
              background: 'var(--error-bg)',
              border: '1px solid rgba(248,113,113,0.3)',
              borderLeft: '4px solid var(--error)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--error)',
            }}
          >
            <p style={{ fontWeight: 700, marginBottom: '0.25rem' }}>Error:</p>
            <p style={{ fontSize: '0.875rem' }}>{status.error_message}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Success */}
      <AnimatePresence>
        {isCompleted && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              padding: '1rem 1.25rem',
              background: 'var(--success-bg)',
              border: '1px solid rgba(52,211,153,0.3)',
              borderLeft: '4px solid var(--success)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--success)',
              fontWeight: 600,
            }}
          >
            ✨ Analysis complete! Found <strong>{status.endpoints_found}</strong> API endpoints. Refreshing your project...
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default AnalysisProgress
