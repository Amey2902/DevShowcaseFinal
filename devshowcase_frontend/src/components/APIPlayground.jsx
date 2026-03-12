import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import './APIPlayground.css'

const APIPlayground = ({ endpoints, isOwner = false, projectId }) => {
  const [selectedEndpoint, setSelectedEndpoint] = useState(null)
  const [requestBody, setRequestBody] = useState('{}')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [liveMode, setLiveMode] = useState(false)
  const [pathParamValues, setPathParamValues] = useState({})
  const [activeTab, setActiveTab] = useState('test')
  const [selectedFramework, setSelectedFramework] = useState('')
  const [translating, setTranslating] = useState(false)
  const [translatedCode, setTranslatedCode] = useState(null)
  const [translationError, setTranslationError] = useState('')
  const [translatedResponse, setTranslatedResponse] = useState(null)
  const [executingTranslated, setExecutingTranslated] = useState(false)

  const frameworks = [
    { id: 'express', name: 'Express.js', icon: '🟢', description: 'Node.js web framework' },
    { id: 'fastapi', name: 'FastAPI', icon: '🐍', description: 'Modern Python API framework' },
    { id: 'flask', name: 'Flask', icon: '🌶️', description: 'Lightweight Python framework' },
    { id: 'django', name: 'Django REST', icon: '🎸', description: 'Python web framework' },
    { id: 'spring', name: 'Spring Boot', icon: '☕', description: 'Java enterprise framework' }
  ]

  // Get default sample values for path parameters
  const getDefaultParamValue = (param) => {
    const sampleValues = {
      'id': '1',
      'user_id': 'user123',
      'userId': 'user123',
      'post_id': 'post456',
      'postId': 'post456',
      'comment_id': 'comment789',
      'commentId': 'comment789',
      'product_id': 'prod123',
      'productId': 'prod123',
      'order_id': 'order456',
      'orderId': 'order456',
      'category_id': 'cat123',
      'categoryId': 'cat123',
    }
    return sampleValues[param] || '123'
  }

  // Helper function to resolve path parameters in URL
  const resolvePathParameters = (url, pathParameters, customValues = {}) => {
    if (!pathParameters || pathParameters.length === 0) {
      return url
    }

    let resolvedUrl = url

    pathParameters.forEach(param => {
      const value = customValues[param] || getDefaultParamValue(param)
      // Replace both :param and {param} formats
      resolvedUrl = resolvedUrl.replace(new RegExp(`:${param}\\b`, 'g'), value)
      resolvedUrl = resolvedUrl.replace(new RegExp(`\\{${param}\\}`, 'g'), value)
    })

    return resolvedUrl
  }

  const handleEndpointSelect = (endpoint) => {
    setSelectedEndpoint(endpoint)
    setRequestBody(JSON.stringify(endpoint.sample_body, null, 2))
    setResponse(null)
    
    // Initialize path parameter values with defaults
    if (endpoint.path_parameters && endpoint.path_parameters.length > 0) {
      const initialValues = {}
      endpoint.path_parameters.forEach(param => {
        initialValues[param] = getDefaultParamValue(param)
      })
      setPathParamValues(initialValues)
    } else {
      setPathParamValues({})
    }
  }

  const handlePathParamChange = (param, value) => {
    setPathParamValues(prev => ({
      ...prev,
      [param]: value
    }))
  }

  const handleTranslate = async () => {
    if (!selectedFramework) {
      setTranslationError('Please select a target framework')
      return
    }

    if (!projectId) {
      setTranslationError('Project ID not available')
      return
    }

    setTranslating(true)
    setTranslationError('')

    try {
      const response = await axios.post(`http://127.0.0.1:8000/api/projects/${projectId}/translate/`, {
        target_framework: selectedFramework
      }, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      })

      setTranslatedCode(response.data)
      toast.success(`Successfully translated to ${frameworks.find(f => f.id === selectedFramework)?.name}`)
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Translation failed'
      setTranslationError(errorMsg)
      toast.error(errorMsg)
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

  const handleExecuteTranslated = async () => {
    if (!selectedEndpoint || !selectedFramework) return

    setExecutingTranslated(true)
    try {
      const customBody = JSON.parse(requestBody)
      
      const result = await axios.post('/api/execute/translated/', {
        endpoint_id: selectedEndpoint.id,
        target_framework: selectedFramework,
        custom_body: customBody,
        custom_path_params: pathParamValues,
      })
      
      setTranslatedResponse(result.data)
      toast.success(`Executed as ${frameworks.find(f => f.id === selectedFramework)?.name}`)
    } catch (error) {
      toast.error('Failed to execute translated endpoint')
      setTranslatedResponse({
        mode: 'error',
        status_code: 500,
        data: null,
        error: error.message,
        framework: selectedFramework
      })
    } finally {
      setExecutingTranslated(false)
    }
  }

  const handleExecute = async () => {
    if (!selectedEndpoint) return

    setLoading(true)
    try {
      const customBody = JSON.parse(requestBody)
      const url = liveMode ? '/api/execute/?mode=live' : '/api/execute/'
      
      const result = await axios.post(url, {
        endpoint_id: selectedEndpoint.id,
        custom_body: customBody,
        custom_path_params: pathParamValues,  // Send custom path parameter values
      })
      setResponse(result.data)
      
      if (liveMode) {
        toast.success('Live API test completed')
      }
    } catch (error) {
      toast.error('Failed to execute request')
      setResponse({
        mode: 'error',
        status_code: 500,
        data: null,
        error: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const getMethodColor = (method) => {
    const colors = {
      GET: '#10b981',
      POST: '#3b82f6',
      PUT: '#f59e0b',
      PATCH: '#db2777',
      DELETE: '#ef4444'
    }
    return colors[method] || '#ea580c'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h3 style={{ 
          fontSize: '1.875rem', 
          fontWeight: '800',
          letterSpacing: '-0.02em',
          margin: 0
        }}>
          API Playground
        </h3>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Tab Navigation */}
          <div style={{
            display: 'flex',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-primary)',
            borderRadius: 'var(--radius-lg)',
            padding: '0.25rem'
          }}>
            <button
              onClick={() => setActiveTab('test')}
              style={{
                padding: '0.5rem 1rem',
                background: activeTab === 'test' ? 'var(--accent-primary)' : 'transparent',
                color: activeTab === 'test' ? 'white' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              🧪 Test API
            </button>
            <button
              onClick={() => setActiveTab('translate')}
              style={{
                padding: '0.5rem 1rem',
                background: activeTab === 'translate' ? 'var(--accent-primary)' : 'transparent',
                color: activeTab === 'translate' ? 'white' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              🔄 Translate API
            </button>

          </div>

          {/* Live Mode Toggle (only show in test tab) */}
          {isOwner && activeTab === 'test' && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              padding: '0.75rem 1.25rem',
              background: 'var(--bg-tertiary)',
              border: `2px solid ${liveMode ? '#ef4444' : 'var(--border-primary)'}`,
              borderRadius: 'var(--radius-lg)'
            }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                  {liveMode ? '🔴 Live Mode' : '🧪 Sandbox Mode'}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                  {liveMode ? 'Testing real API' : 'Safe testing'}
                </span>
              </div>
              <button
                onClick={() => setLiveMode(!liveMode)}
                style={{
                  width: '52px',
                  height: '28px',
                  background: liveMode ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : '#d1d5db',
                  border: '2px solid var(--border-secondary)',
                  borderRadius: '14px',
                  cursor: 'pointer',
                  position: 'relative',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{
                  position: 'absolute',
                  top: '2px',
                  left: liveMode ? '24px' : '2px',
                  width: '20px',
                  height: '20px',
                  background: 'white',
                  borderRadius: '50%',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
                  transition: 'left 0.2s'
                }} />
              </button>
            </div>
          )}
        </div>
      </div>

      {liveMode && activeTab === 'test' && (
        <div style={{
          padding: '1rem 1.25rem',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 'var(--radius-md)',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <span style={{ fontSize: '1.5rem' }}>⚠️</span>
          <div>
            <p style={{ margin: 0, fontWeight: '600', color: '#ef4444', fontSize: '0.9375rem' }}>
              Live Mode Active
            </p>
            <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              Requests will call your real external API. Use with caution.
            </p>
          </div>
        </div>
      )}

      <div className="playground-grid">
        <div className="endpoints-sidebar">
          <h4 style={{ 
            fontSize: '0.875rem', 
            fontWeight: '700', 
            color: 'var(--text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '1rem'
          }}>
            Endpoints
          </h4>
          <div className="endpoints-list">
            {endpoints.map((endpoint) => (
              <button
                key={endpoint.id}
                onClick={() => handleEndpointSelect(endpoint)}
                className={`endpoint-item ${selectedEndpoint?.id === endpoint.id ? 'active' : ''}`}
              >
                <div className="endpoint-header">
                  <span
                    style={{ 
                      backgroundColor: getMethodColor(endpoint.method),
                      color: 'white',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '0.25rem',
                      fontSize: '0.75rem',
                      fontWeight: '700',
                      fontFamily: 'var(--font-mono)'
                    }}
                  >
                    {endpoint.method}
                  </span>
                  <span className="endpoint-name">{endpoint.name}</span>
                </div>
                <p className="endpoint-url" style={{ 
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.75rem',
                  color: 'var(--text-tertiary)',
                  marginTop: '0.5rem'
                }}>
                  {resolvePathParameters(endpoint.url, endpoint.path_parameters)}
                </p>
              </button>
            ))}
          </div>
        </div>

        <div className="playground-content">
          {activeTab === 'test' ? (
            // Test API Tab Content
            selectedEndpoint ? (
            <div>
              <div style={{
                padding: '1.5rem',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-lg)',
                marginBottom: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                  <span style={{
                    backgroundColor: getMethodColor(selectedEndpoint.method),
                    color: 'white',
                    padding: '0.375rem 0.75rem',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '0.875rem',
                    fontWeight: '700',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {selectedEndpoint.method}
                  </span>
                  <h4 style={{ fontSize: '1.25rem', fontWeight: '700', margin: 0 }}>
                    {selectedEndpoint.name}
                  </h4>
                </div>
                <p style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.875rem',
                  color: 'var(--text-secondary)',
                  marginBottom: '0.75rem',
                  padding: '0.75rem',
                  background: 'var(--bg-primary)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-primary)'
                }}>
                  {resolvePathParameters(selectedEndpoint.url, selectedEndpoint.path_parameters, pathParamValues)}
                </p>
                {selectedEndpoint.path_parameters && selectedEndpoint.path_parameters.length > 0 && (
                  <div style={{
                    padding: '1rem',
                    background: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    borderRadius: 'var(--radius-md)',
                    marginBottom: '0.75rem'
                  }}>
                    <div style={{ 
                      fontSize: '0.875rem', 
                      fontWeight: '700', 
                      color: 'var(--text-primary)',
                      marginBottom: '0.75rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      📌 Path Parameters
                    </div>
                    {selectedEndpoint.path_parameters.map(param => (
                      <div key={param} style={{ marginBottom: '0.75rem' }}>
                        <label style={{ 
                          display: 'block',
                          fontSize: '0.8125rem',
                          fontWeight: '600',
                          color: 'var(--text-secondary)',
                          marginBottom: '0.375rem',
                          fontFamily: 'var(--font-mono)'
                        }}>
                          {param}
                        </label>
                        <input
                          type="text"
                          value={pathParamValues[param] || ''}
                          onChange={(e) => handlePathParamChange(param, e.target.value)}
                          placeholder={`Enter ${param}`}
                          style={{
                            width: '100%',
                            padding: '0.5rem 0.75rem',
                            fontSize: '0.875rem',
                            fontFamily: 'var(--font-mono)',
                            background: 'var(--bg-primary)',
                            border: '1px solid var(--border-secondary)',
                            borderRadius: 'var(--radius-md)',
                            color: 'var(--text-primary)',
                            outline: 'none',
                            transition: 'border-color 0.2s'
                          }}
                          onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                          onBlur={(e) => e.target.style.borderColor = 'var(--border-secondary)'}
                        />
                      </div>
                    ))}
                  </div>
                )}
                {selectedEndpoint.description && (
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', margin: 0 }}>
                    {selectedEndpoint.description}
                  </p>
                )}
              </div>

              {selectedEndpoint.method !== 'GET' && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <label className="form-label" style={{ marginBottom: '0.75rem' }}>
                    Request Body (JSON)
                  </label>
                  <textarea
                    className="code-textarea"
                    rows="10"
                    value={requestBody}
                    onChange={(e) => setRequestBody(e.target.value)}
                    style={{
                      width: '100%',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.875rem',
                      lineHeight: '1.6',
                      background: 'var(--bg-primary)',
                      border: '1px solid var(--border-secondary)',
                      borderRadius: 'var(--radius-md)',
                      padding: '1rem',
                      color: 'var(--text-primary)',
                      resize: 'vertical'
                    }}
                  />
                </div>
              )}

              <button
                onClick={handleExecute}
                disabled={loading}
                className="btn btn-success"
                style={{ 
                  width: '100%', 
                  padding: '0.875rem', 
                  fontSize: '1rem', 
                  marginBottom: '1.5rem',
                  background: liveMode ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : undefined
                }}
              >
                {loading ? 'Executing...' : (liveMode ? '▶ Test Live API' : '▶ Run Request')}
              </button>

              {response && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h4 style={{ fontSize: '1.125rem', fontWeight: '700', margin: 0 }}>
                      Response
                    </h4>
                    {response.mode && (
                      <span style={{
                        padding: '0.375rem 0.875rem',
                        borderRadius: 'var(--radius-md)',
                        fontSize: '0.875rem',
                        fontWeight: '700',
                        background: response.mode === 'sandbox' 
                          ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                          : response.mode === 'live'
                          ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                          : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                        color: 'white'
                      }}>
                        {response.mode === 'sandbox' ? '🧪 Sandbox' : response.mode === 'live' ? '🔴 Live' : '⚠️ Error'}
                      </span>
                    )}
                  </div>
                  <div style={{
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-secondary)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '1.5rem'
                  }}>
                    <div style={{ marginBottom: '1rem' }}>
                      <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', fontWeight: '600' }}>
                        Status Code:{' '}
                      </span>
                      <span style={{
                        fontSize: '1.125rem',
                        fontWeight: '700',
                        fontFamily: 'var(--font-mono)',
                        color: response.status_code < 400 ? 'var(--success)' : 'var(--error)'
                      }}>
                        {response.status_code}
                      </span>
                    </div>
                    <pre style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.875rem',
                      lineHeight: '1.6',
                      color: 'var(--text-primary)',
                      margin: 0,
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      maxHeight: '400px',
                      overflowY: 'auto'
                    }}>
                      {JSON.stringify(response.data || response.error, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>🚀</div>
              <h4 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                Select an endpoint to test
              </h4>
              <p style={{ color: 'var(--text-secondary)' }}>
                Choose an endpoint from the sidebar to start testing
              </p>
            </div>
          )
          ) : activeTab === 'translate' ? (
            // Translate API Tab Content
            <div style={{ 
              background: 'rgba(17,24,39,0.4)', 
              borderRadius: 'var(--radius-lg)', 
              padding: '2rem',
              border: '1px solid var(--border-secondary)'
            }}>
              {/* Translation Header */}
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
                      onClick={() => {
                        setSelectedFramework(framework.id)
                        setTranslatedCode(null)
                        setTranslatedResponse(null)
                      }}
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

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                {/* Translate Button */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleTranslate}
                  disabled={translating || !selectedFramework}
                  style={{
                    flex: 1,
                    padding: '1rem',
                    background: 'var(--accent-gradient)',
                    color: 'white',
                    border: 'none',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '1rem',
                    fontWeight: 600,
                    cursor: translating || !selectedFramework ? 'not-allowed' : 'pointer',
                    opacity: translating || !selectedFramework ? 0.6 : 1
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
                      Translating...
                    </span>
                  ) : (
                    <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                      🔄 Generate Code
                    </span>
                  )}
                </motion.button>

                {/* Test Translated Button */}
                {selectedEndpoint && selectedFramework && (
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleExecuteTranslated}
                    disabled={executingTranslated || !selectedFramework}
                    style={{
                      flex: 1,
                      padding: '1rem',
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '1rem',
                      fontWeight: 600,
                      cursor: executingTranslated || !selectedFramework ? 'not-allowed' : 'pointer',
                      opacity: executingTranslated || !selectedFramework ? 0.6 : 1
                    }}
                  >
                    {executingTranslated ? (
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
                        Testing...
                      </span>
                    ) : (
                      <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                        🧪 Test as {frameworks.find(f => f.id === selectedFramework)?.name}
                      </span>
                    )}
                  </motion.button>
                )}
              </div>

              {/* Selected Endpoint Info */}
              {selectedEndpoint && selectedFramework && (
                <div style={{
                  padding: '1rem',
                  background: 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: '1.5rem'
                }}>
                  <div style={{ 
                    fontSize: '0.875rem', 
                    fontWeight: '700', 
                    color: 'var(--text-primary)',
                    marginBottom: '0.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    🎯 Testing: {selectedEndpoint.name} → {frameworks.find(f => f.id === selectedFramework)?.name}
                  </div>
                  <p style={{ 
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.75rem',
                    color: 'var(--text-secondary)',
                    margin: 0
                  }}>
                    {selectedEndpoint.method} {resolvePathParameters(selectedEndpoint.url, selectedEndpoint.path_parameters, pathParamValues)}
                  </p>
                </div>
              )}

              {/* Error Display */}
              <AnimatePresence>
                {translationError && (
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
                    ❌ {translationError}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Translated Response Display */}
              <AnimatePresence>
                {translatedResponse && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    style={{ marginBottom: '1.5rem' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                      <h4 style={{ fontSize: '1.125rem', fontWeight: '700', margin: 0 }}>
                        Translated Response
                      </h4>
                      <span style={{
                        padding: '0.375rem 0.875rem',
                        borderRadius: 'var(--radius-md)',
                        fontSize: '0.875rem',
                        fontWeight: '700',
                        background: translatedResponse.mode === 'translated_sandbox' 
                          ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' 
                          : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                        color: 'white'
                      }}>
                        {translatedResponse.mode === 'translated_sandbox' 
                          ? `🔄 ${frameworks.find(f => f.id === selectedFramework)?.name} Sandbox` 
                          : '⚠️ Error'}
                      </span>
                    </div>
                    <div style={{
                      background: 'var(--bg-primary)',
                      border: '1px solid var(--border-secondary)',
                      borderRadius: 'var(--radius-lg)',
                      padding: '1.5rem'
                    }}>
                      <div style={{ marginBottom: '1rem' }}>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', fontWeight: '600' }}>
                          Status Code:{' '}
                        </span>
                        <span style={{
                          fontSize: '1.125rem',
                          fontWeight: '700',
                          fontFamily: 'var(--font-mono)',
                          color: translatedResponse.status_code < 400 ? 'var(--success)' : 'var(--error)'
                        }}>
                          {translatedResponse.status_code}
                        </span>
                        {translatedResponse.framework && (
                          <>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', fontWeight: '600', marginLeft: '1rem' }}>
                              Framework:{' '}
                            </span>
                            <span style={{
                              fontSize: '0.875rem',
                              fontWeight: '600',
                              color: 'var(--accent-primary)'
                            }}>
                              {frameworks.find(f => f.id === translatedResponse.framework)?.name}
                            </span>
                          </>
                        )}
                      </div>
                      <pre style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.875rem',
                        lineHeight: '1.6',
                        color: 'var(--text-primary)',
                        margin: 0,
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        maxHeight: '400px',
                        overflowY: 'auto'
                      }}>
                        {JSON.stringify(translatedResponse.data || translatedResponse.error, null, 2)}
                      </pre>
                    </div>
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
          ) : null}
        </div>
      </div>
    </motion.div>
  )
}

export default APIPlayground
