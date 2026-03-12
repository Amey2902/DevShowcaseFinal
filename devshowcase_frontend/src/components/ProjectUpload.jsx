import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const ProjectUpload = ({ projectId, onUploadStart }) => {
  const [uploadMethod, setUploadMethod] = useState('files')
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [githubUrl, setGithubUrl] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [generateArchitecture, setGenerateArchitecture] = useState(true) // New state for architecture generation

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (!file) return
    if (file.size > 100 * 1024 * 1024) { setError('File size exceeds 100MB limit'); return }
    if (!file.name.endsWith('.zip')) { setError('Only .zip files are allowed'); return }
    setSelectedFile(file)
    setError('')
  }

  const handleMultiFileSelect = (e) => {
    const files = Array.from(e.target.files)
    if (files.length === 0) return
    
    // Calculate total size
    const totalSize = files.reduce((sum, file) => sum + file.size, 0)
    if (totalSize > 50 * 1024 * 1024) {
      setError('Total file size exceeds 50MB limit')
      return
    }
    
    // Filter for code files only
    const codeFiles = files.filter(file => {
      const ext = file.name.split('.').pop().toLowerCase()
      return ['js', 'jsx', 'ts', 'tsx', 'py', 'java', 'cs', 'php', 'rb', 'go', 'cpp', 'c', 'h', 'hpp'].includes(ext)
    })
    
    if (codeFiles.length === 0) {
      setError('No valid code files found. Please select supported code files (.js, .ts, .py, .java, .cs, .php, .rb, .go, .cpp, etc.)')
      return
    }
    
    setSelectedFiles(codeFiles)
    setError('')
  }

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true) }
  const handleDragLeave = () => setIsDragging(false)
  
  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const items = Array.from(e.dataTransfer.items)
    const files = []
    
    // Handle folder drop
    if (items.length > 0 && items[0].webkitGetAsEntry) {
      const entries = items.map(item => item.webkitGetAsEntry())
      processEntries(entries, files)
    } else {
      // Handle file drop
      const droppedFiles = Array.from(e.dataTransfer.files)
      if (uploadMethod === 'zip') {
        handleFileSelect({ target: { files: droppedFiles } })
      } else {
        handleMultiFileSelect({ target: { files: droppedFiles } })
      }
    }
  }
  
  const processEntries = async (entries, files) => {
    for (const entry of entries) {
      if (entry.isFile) {
        const file = await getFileFromEntry(entry)
        const ext = file.name.split('.').pop().toLowerCase()
        if (['js', 'jsx', 'ts', 'tsx', 'py', 'java', 'cs', 'php', 'rb', 'go', 'cpp', 'c', 'h', 'hpp'].includes(ext)) {
          files.push(file)
        }
      } else if (entry.isDirectory) {
        const dirReader = entry.createReader()
        const dirEntries = await readAllDirectoryEntries(dirReader)
        await processEntries(dirEntries, files)
      }
    }
    
    if (files.length > 0) {
      const totalSize = files.reduce((sum, file) => sum + file.size, 0)
      if (totalSize > 50 * 1024 * 1024) {
        setError('Total file size exceeds 50MB limit')
        return
      }
      setSelectedFiles(files)
      setError('')
    }
  }
  
  const getFileFromEntry = (entry) => {
    return new Promise((resolve) => {
      entry.file(resolve)
    })
  }
  
  const readAllDirectoryEntries = (dirReader) => {
    return new Promise((resolve) => {
      const entries = []
      const readEntries = () => {
        dirReader.readEntries((results) => {
          if (results.length === 0) {
            resolve(entries)
          } else {
            entries.push(...results)
            readEntries()
          }
        })
      }
      readEntries()
    })
  }

  const handleFilesUpload = async () => {
    if (selectedFiles.length === 0) { setError('Please select files or a folder'); return }
    setUploading(true); setError('')
    const formData = new FormData()
    selectedFiles.forEach((file, index) => {
      formData.append('files', file)
      formData.append(`file_paths[${index}]`, file.webkitRelativePath || file.name)
    })
    formData.append('generate_architecture', generateArchitecture) // Add architecture generation flag
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/projects/${projectId}/upload/files/`, {
        method: 'POST',
        headers: { 'Authorization': `Token ${localStorage.getItem('token')}` },
        body: formData,
      })
      const data = await res.json()
      if (res.ok) onUploadStart(data.upload_id)
      else setError(data.error || 'Upload failed')
    } catch { setError('Network error. Please try again.') }
    finally { setUploading(false) }
  }

  const handleZipUpload = async () => {
    if (!selectedFile) { setError('Please select a file'); return }
    setUploading(true); setError('')
    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('generate_architecture', generateArchitecture) // Add architecture generation flag
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/projects/${projectId}/upload/zip/`, {
        method: 'POST',
        headers: { 'Authorization': `Token ${localStorage.getItem('token')}` },
        body: formData,
      })
      const data = await res.json()
      if (res.ok) onUploadStart(data.upload_id)
      else setError(data.error || 'Upload failed')
    } catch { setError('Network error. Please try again.') }
    finally { setUploading(false) }
  }

  const handleGithubUpload = async () => {
    if (!githubUrl) { setError('Please enter a GitHub URL'); return }
    setUploading(true); setError('')
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/projects/${projectId}/upload/github/`, {
        method: 'POST',
        headers: { 'Authorization': `Token ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          github_url: githubUrl,
          generate_architecture: generateArchitecture // Add architecture generation flag
        }),
      })
      const data = await res.json()
      if (res.ok) onUploadStart(data.upload_id)
      else setError(data.error || 'Upload failed')
    } catch { setError('Network error. Please try again.') }
    finally { setUploading(false) }
  }

  const handleUpload = () => {
    if (uploadMethod === 'files') return handleFilesUpload()
    if (uploadMethod === 'zip') return handleZipUpload()
    return handleGithubUpload()
  }

  const methodBtnStyle = (active) => ({
    flex: 1,
    padding: '0.875rem 1rem',
    borderRadius: 'var(--radius-md)',
    fontFamily: 'var(--font-sans)',
    fontWeight: 700,
    fontSize: '0.9rem',
    cursor: 'pointer',
    border: active ? 'none' : '1px solid var(--border-primary)',
    background: active ? 'var(--accent-gradient)' : 'rgba(17,24,39,0.6)',
    color: active ? 'white' : 'var(--text-secondary)',
    boxShadow: active ? 'var(--shadow-glow-sm)' : 'none',
    transition: 'all 0.25s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
  })

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
        <motion.div
          animate={{ rotate: [0, 15, -15, 0] }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          style={{ fontSize: '2rem' }}
        >
          🤖
        </motion.div>
        <h3 style={{ fontSize: '1.625rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em', margin: 0 }}>
          Auto-Detect API Endpoints
        </h3>
      </div>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', lineHeight: 1.65, fontSize: '0.9375rem' }}>
        Upload your project code and let AI automatically detect and document your API endpoints.
        Supports <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>Express.js, Flask, Django, FastAPI, NestJS, Spring Boot, and ASP.NET</span>.
      </p>

      {/* Method toggle */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '2rem' }}>
        <button onClick={() => setUploadMethod('files')} style={methodBtnStyle(uploadMethod === 'files')}>
          <span>�</span> Upload Files/Folder
        </button>
        <button onClick={() => setUploadMethod('github')} style={methodBtnStyle(uploadMethod === 'github')}>
          <span>🔗</span> GitHub URL
        </button>
      </div>

      {/* Files/Folder upload */}
      <AnimatePresence mode="wait">
        {uploadMethod === 'files' && (
          <motion.div
            key="files"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              style={{
                border: `2px dashed ${isDragging ? 'var(--accent-primary)' : 'var(--border-secondary)'}`,
                borderRadius: 'var(--radius-lg)',
                padding: '3rem 2rem',
                textAlign: 'center',
                background: isDragging ? 'rgba(234,88,12,0.06)' : 'rgba(17,24,39,0.4)',
                transition: 'all 0.25s ease',
                cursor: 'pointer',
              }}
            >
              <input 
                type="file" 
                multiple 
                webkitdirectory="" 
                directory="" 
                onChange={handleMultiFileSelect} 
                style={{ display: 'none' }} 
                id="folder-upload" 
              />
              <input 
                type="file" 
                multiple 
                accept=".js,.jsx,.ts,.tsx,.py,.java,.cs,.php,.rb,.go,.cpp,.c,.h,.hpp" 
                onChange={handleMultiFileSelect} 
                style={{ display: 'none' }} 
                id="files-upload" 
              />
              <label htmlFor="folder-upload" style={{ cursor: 'pointer', display: 'block' }}>
                <motion.div
                  animate={isDragging ? { scale: 1.1 } : { scale: 1 }}
                  style={{ fontSize: '3.5rem', marginBottom: '1rem' }}
                >
                  {selectedFiles.length > 0 ? '✅' : '📂'}
                </motion.div>
                {selectedFiles.length > 0 ? (
                  <>
                    <p style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--success)', marginBottom: '0.4rem' }}>
                      {selectedFiles.length} files selected
                    </p>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {(selectedFiles.reduce((sum, f) => sum + f.size, 0) / 1024 / 1024).toFixed(2)} MB — click to change
                    </p>
                    <div style={{ marginTop: '1rem', maxHeight: '150px', overflowY: 'auto', textAlign: 'left', padding: '0 1rem' }}>
                      {selectedFiles.slice(0, 10).map((file, i) => (
                        <div key={i} style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', padding: '0.25rem 0' }}>
                          📄 {file.webkitRelativePath || file.name}
                        </div>
                      ))}
                      {selectedFiles.length > 10 && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', padding: '0.25rem 0' }}>
                          ... and {selectedFiles.length - 10} more files
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    <p style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
                      Drop your src folder here or click to browse
                    </p>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                      Max total size: 50MB · Supports .js, .ts, .py, .java, .cs, .php, .rb, .go, .cpp and more
                    </p>
                    <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', marginTop: '1.5rem' }}>
                      <label 
                        htmlFor="folder-upload" 
                        style={{
                          padding: '0.625rem 1.25rem',
                          background: 'var(--accent-gradient)',
                          color: 'white',
                          borderRadius: 'var(--radius-md)',
                          fontSize: '0.875rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          border: 'none',
                        }}
                      >
                        📁 Select Folder
                      </label>
                      <label 
                        htmlFor="files-upload" 
                        style={{
                          padding: '0.625rem 1.25rem',
                          background: 'rgba(17,24,39,0.6)',
                          color: 'var(--text-secondary)',
                          border: '1px solid var(--border-primary)',
                          borderRadius: 'var(--radius-md)',
                          fontSize: '0.875rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        📄 Select Files
                      </label>
                    </div>
                  </>
                )}
              </label>
            </div>
          </motion.div>
        )}

        {/* GitHub URL */}
        {uploadMethod === 'github' && (
          <motion.div
            key="github"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <input
              type="text"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              className="form-input"
              style={{ fontSize: '1rem' }}
            />
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>💡</span> Enter a public GitHub repository URL (supports repos up to 500MB)
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            style={{
              marginTop: '1.25rem',
              padding: '1rem 1.25rem',
              background: 'var(--error-bg)',
              border: '1px solid rgba(248,113,113,0.3)',
              borderLeft: '4px solid var(--error)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--error)',
              fontSize: '0.875rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <span>❌</span> {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Architecture Generation Option */}
      <div style={{
        marginTop: '1.5rem',
        padding: '1.25rem',
        background: 'rgba(59,130,246,0.06)',
        border: '1px solid rgba(59,130,246,0.18)',
        borderRadius: 'var(--radius-lg)',
      }}>
        <label style={{ 
          display: 'flex', 
          alignItems: 'flex-start', 
          gap: '0.75rem', 
          cursor: 'pointer',
          fontSize: '0.9rem',
          lineHeight: 1.6
        }}>
          <input
            type="checkbox"
            checked={generateArchitecture}
            onChange={(e) => setGenerateArchitecture(e.target.checked)}
            style={{
              width: '18px',
              height: '18px',
              marginTop: '2px',
              accentColor: 'var(--accent-primary)',
              cursor: 'pointer'
            }}
          />
          <div>
            <div style={{ 
              color: 'var(--text-primary)', 
              fontWeight: 600,
              marginBottom: '0.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <span>🏗️</span>
              Generate Architecture Diagram
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Let AI automatically analyze your codebase and create an interactive architecture diagram showing components, databases, and services. You can edit and customize it afterwards.
            </div>
          </div>
        </label>
      </div>

      {/* Submit button */}
      <motion.button
        whileHover={{ scale: 1.02, boxShadow: 'var(--shadow-glow)' }}
        whileTap={{ scale: 0.98 }}
        onClick={handleUpload}
        disabled={uploading || (uploadMethod === 'files' && selectedFiles.length === 0) || (uploadMethod === 'zip' && !selectedFile) || (uploadMethod === 'github' && !githubUrl)}
        className="btn btn-primary"
        style={{ width: '100%', marginTop: '1.5rem', padding: '1rem', fontSize: '1.05rem' }}
      >
        {uploading ? (
          <motion.span
            animate={{ opacity: [1, 0.4, 1] }}
            transition={{ duration: 1.2, repeat: Infinity }}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite', border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%', width: 18, height: 18 }} />
            Uploading & Analyzing…
          </motion.span>
        ) : (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🚀</span> Start AI Analysis
          </span>
        )}
      </motion.button>

      {/* Info box */}
      <div style={{
        marginTop: '1.5rem',
        padding: '1.25rem',
        background: 'rgba(234,88,12,0.06)',
        border: '1px solid rgba(234,88,12,0.18)',
        borderRadius: 'var(--radius-lg)',
      }}>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.65 }}>
          <strong style={{ color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '0.4rem' }}>
            <span>✨</span> What happens next:
          </strong>
          Our AI will scan your code, detect all API endpoints, extract parameters, identify authentication requirements, and create ready-to-test endpoint documentation.
        </p>
      </div>
    </div>
  )
}

export default ProjectUpload
