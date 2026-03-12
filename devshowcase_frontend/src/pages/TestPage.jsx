import { useState, useEffect } from 'react'
import axios from 'axios'

const TestPage = () => {
  const [status, setStatus] = useState('Testing...')
  const [backendStatus, setBackendStatus] = useState('Checking...')
  const [magicLinkTest, setMagicLinkTest] = useState('Not tested')

  useEffect(() => {
    testConnection()
  }, [])

  const testConnection = async () => {
    try {
      // Test 1: Basic backend connection
      const response = await axios.get('http://127.0.0.1:8000/api/auth/me/')
      setBackendStatus('Backend reachable (401 expected)')
    } catch (error) {
      if (error.response?.status === 401) {
        setBackendStatus('✅ Backend connected (401 as expected)')
      } else {
        setBackendStatus(`❌ Backend error: ${error.message}`)
      }
    }

    // Test 2: Magic link endpoint
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/auth/magic-link/request/', {
        email: 'test@example.com'
      })
      setMagicLinkTest('✅ Magic link endpoint working')
    } catch (error) {
      setMagicLinkTest(`❌ Magic link error: ${error.message}`)
    }

    setStatus('Tests completed')
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'monospace' }}>
      <h1>DevShowcase Connection Test</h1>
      <div style={{ marginBottom: '1rem' }}>
        <strong>Overall Status:</strong> {status}
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <strong>Backend Connection:</strong> {backendStatus}
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <strong>Magic Link Endpoint:</strong> {magicLinkTest}
      </div>
      <div style={{ marginTop: '2rem' }}>
        <h3>Frontend Info:</h3>
        <p>Current URL: {window.location.href}</p>
        <p>User Agent: {navigator.userAgent}</p>
        <p>React Version: {React.version}</p>
      </div>
      <div style={{ marginTop: '2rem' }}>
        <button onClick={() => window.location.href = '/login'}>
          Go to Login Page
        </button>
      </div>
    </div>
  )
}

export default TestPage