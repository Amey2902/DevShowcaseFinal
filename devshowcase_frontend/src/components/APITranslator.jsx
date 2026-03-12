import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const APITranslator = ({ projectId, endpoints }) => {
  const [selectedFramework, setSelectedFramework] = useState('')
  const [translating, setTranslating] = useState(false)
  const [translatedCode, setTranslatedCode] = useState(null)
  const [error, setError] = useState('')

  const frameworks = [
    { id: 'express', name: 'Express.js', icon: '🟢', description: 'Node.js web framework' },
    { id: 'fastapi', name: 'FastAPI', icon: '🐍', description: 'Modern Python API framework' },
    { id: 'flask', name: 'Flask', icon: '🌶️', description: 'Lightweight Python framework' },
    { id: 'django', name: 'Django REST', icon: '🎸', description: 'Python web framework' },
    { id: 'spring', name: 'Spring Boot', icon: '☕', description: 'Java enterprise framework' }
  ]

  const handleTranslate = async () => {
    if (!selectedFramework) {
      setError('Please select a target framework')
      return
    }

    setTranslating(true)
    setError('')

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/projects/${projectId}/translate/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          target_framework: selectedFramework
        })
      })

      const data = await response.json()

      if (response.ok) {
        setTranslatedCode(data)
      } else {
        setError(data.error || 'Translation failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setTranslating(false)
    }
  }

  const downloadCode = (filename, content) => {
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getFileExtension = (framework) => {
    const extensions = {
      'express': 'js',
      'fastapi': 'py',
      'flask': 'py',
      'django': 'py',
      'spring': 'java'
    }
    return extensions[framework] || 'txt'
  }

  return (
    <div style={{ 
      background: 'rgba(17,24,39,0.4)', 
      borderRadius: 'var(--radius-lg)', 
      padding: '2rem',
      border: '1px solid var(--border-secondary)'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <motion.div
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          style={{ fontSize: '2rem' }}
        >
          🔄
        </motion.div>
        <div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            API Framework Translator
          </h3>
          <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.875rem' }}>
            Convert your {endpoints?.length || 0} detected endpoints to any framework
          </p>
        </div>
      </div>

      {/* Framework Selection */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ 
          display: 'block', 
          fontSize: '0.875rem', 
          fontWeight: 600, 
          color: 'var(--text-primary)', 
          marginBottom: '0.75rem' 
        }}>
          Select Target Framework
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
          {frameworks.map(framework => (
            <motion.div
              key={framework.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSelectedFramework(framework.id)}
              style={{
                padding: '1rem',
                borderRadius: 'var(--radius-md)',
                border: selectedFramework === framework.id 
                  ? '2px solid var(--accent-primary)' 
                  : '1px solid var(--border-primary)',
                background: selectedFramework === framework.id 
                  ? 'rgba(234,88,12,0.1)' 
                  : 'rgba(17,24,39,0.6)',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '1.25rem' }}>{framework.icon}</span>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{framework.name}</span>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0 }}>
                {framework.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Translate Button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleTranslate}
        disabled={translating || !selectedFramework}
        style={{
          width: '100%',
          padding: '1rem',
          background: 'var(--accent-gradient)',
          color: 'white',
          border: 'none',
          borderRadius: 'var(--radius-md)',
          fontSize: '1rem',
          fontWeight: 600,
          cursor: translating || !selectedFramework ? 'not-allowed' : 'pointer',
          opacity: translating || !selectedFramework ? 0.6 : 1,
          marginBottom: '1.5rem'
        }}
      >
        {translating ? (
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              style={{ 
                width: 16, 
                height: 16, 
                border: '2px solid white', 
                borderTopColor: 'transparent', 
                borderRadius: '50%' 
              }}
            />
            Translating API...
          </span>
        ) : (
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
            🚀 Translate to {frameworks.find(f => f.id === selectedFramework)?.name || 'Framework'}
          </span>
        )}
      </motion.button>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            style={{
              padding: '1rem',
              background: 'var(--error-bg)',
              border: '1px solid var(--error)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--error)',
              fontSize: '0.875rem',
              marginBottom: '1.5rem'
            }}
          >
            ❌ {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Translated Code Display */}
      <AnimatePresence>
        {translatedCode && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            style={{
              border: '1px solid var(--border-secondary)',
              borderRadius: 'var(--radius-lg)',
              overflow: 'hidden'
            }}
          >
            {/* Success Header */}
            <div style={{
              padding: '1rem',
              background: 'var(--success-bg)',
              borderBottom: '1px solid var(--border-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '1.25rem' }}>✅</span>
                <span style={{ fontWeight: 600, color: 'var(--success)' }}>
                  Translation Complete!
                </span>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  ({translatedCode.endpoints_count} endpoints → {translatedCode.target_framework})
                </span>
              </div>
            </div>

            {/* Generated Files */}
            <div style={{ padding: '1.5rem' }}>
              {Object.entries(translatedCode.generated_files).map(([filename, content]) => (
                <div key={filename} style={{ marginBottom: '1.5rem' }}>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between',
                    marginBottom: '0.75rem'
                  }}>
                    <h4 style={{ 
                      fontSize: '1rem', 
                      fontWeight: 600, 
                      color: 'var(--text-primary)', 
                      margin: 0,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      📄 {filename}.{getFileExtension(translatedCode.target_framework)}
                    </h4>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => downloadCode(
                        `${filename}.${getFileExtension(translatedCode.target_framework)}`, 
                        content
                      )}
                      style={{
                        padding: '0.5rem 1rem',
                        background: 'var(--accent-primary)',
                        color: 'white',
                        border: 'none',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        cursor: 'pointer'
                      }}
                    >
                      📥 Download
                    </motion.button>
                  </div>
                  
                  <pre style={{
                    background: 'rgba(0,0,0,0.3)',
                    padding: '1rem',
                    borderRadius: 'var(--radius-md)',
                    overflow: 'auto',
                    fontSize: '0.75rem',
                    lineHeight: 1.5,
                    color: 'var(--text-primary)',
                    maxHeight: '400px'
                  }}>
                    <code>{content}</code>
                  </pre>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default APITranslator