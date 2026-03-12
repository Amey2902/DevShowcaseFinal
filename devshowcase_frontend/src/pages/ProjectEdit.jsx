import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { toast } from 'react-toastify'
import OverviewTab from '../components/editor/OverviewTab'
import TechStackTab from '../components/editor/TechStackTab'
import ArchitectureTab from '../components/editor/ArchitectureTab'
import EndpointsTab from '../components/editor/EndpointsTab'
import TimelineTab from '../components/editor/TimelineTab'
import PublishTab from '../components/editor/PublishTab'
import ProjectUpload from '../components/ProjectUpload'
import AnalysisProgress from '../components/AnalysisProgress'
import APITranslator from '../components/APITranslator'

const ProjectEdit = () => {
  const { slug } = useParams()
  const [activeTab, setActiveTab] = useState('overview')
  const [project, setProject] = useState(null)
  const [uploadId, setUploadId] = useState(null)

  useEffect(() => { fetchProject() }, [slug])

  const fetchProject = async () => {
    try {
      const { data } = await axios.get(`/api/projects/${slug}/full/`)
      setProject(data)
    } catch {
      toast.error('Failed to load project')
    }
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'techstack', label: 'Tech Stack', icon: '🛠' },
    { id: 'architecture', label: 'Architecture', icon: '🏗' },
    { id: 'endpoints', label: 'Endpoints', icon: '🔌' },
    { id: 'upload', label: 'Auto-Detect', icon: '🤖' },
    { id: 'translate', label: 'Translate API', icon: '🔄' },
    { id: 'timeline', label: 'Timeline', icon: '📅' },
    { id: 'publish', label: 'Publish', icon: '📢' },
  ]

  if (!project) return (
    <div className="loading">
      <div className="loading-spinner" />
      Loading project…
    </div>
  )

  return (
    <div className="container" style={{ paddingTop: '2.5rem', paddingBottom: '4rem' }}>

      {/* ─── Page Header ─── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
        style={{ marginBottom: '2rem' }}
      >
        {/* Breadcrumb */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          <Link to="/dashboard" style={{ color: 'var(--text-tertiary)', textDecoration: 'none' }}>Dashboard</Link>
          <span>›</span>
          <Link to={`/project/${slug}`} style={{ color: 'var(--text-tertiary)', textDecoration: 'none' }}>{project.title}</Link>
          <span>›</span>
          <span style={{ color: 'var(--text-secondary)' }}>Edit</span>
        </div>

        <div style={{
          background: 'linear-gradient(135deg, rgba(234,88,12,0.10), rgba(219,39,119,0.07))',
          border: '1px solid rgba(234,88,12,0.18)',
          borderRadius: 'var(--radius-xl)',
          padding: '1.75rem 2.25rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1.5rem',
          flexWrap: 'wrap',
          position: 'relative',
          overflow: 'hidden',
        }}>
          {/* Glow */}
          <div style={{ position: 'absolute', right: -60, top: -60, width: 200, height: 200, borderRadius: '50%', background: 'rgba(219,39,119,0.12)', filter: 'blur(50px)', pointerEvents: 'none' }} />

          <div style={{ position: 'relative', zIndex: 1 }}>
            <p style={{ fontSize: '0.78rem', color: 'var(--accent-primary)', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
              ✏ EDITING PROJECT
            </p>
            <h1 style={{ fontSize: '1.875rem', fontWeight: '900', letterSpacing: '-0.025em', margin: 0 }}>
              {project.title}
            </h1>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', flexShrink: 0, position: 'relative', zIndex: 1 }}>
            <Link to={`/project/${slug}`}>
              <motion.button whileHover={{ scale: 1.04 }} className="btn btn-ghost" style={{ padding: '0.6rem 1.25rem', fontSize: '0.875rem' }}>
                👁 Preview
              </motion.button>
            </Link>
            <span className={project.is_published ? 'badge badge-success' : 'badge badge-gray'} style={{ alignSelf: 'center', fontSize: '0.8rem' }}>
              {project.is_published ? '✓ Published' : 'Draft'}
            </span>
          </div>
        </div>
      </motion.div>

      {/* ─── Tabs Card ─── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.45 }}
        style={{
          background: 'var(--bg-glass)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: '1px solid var(--border-glass)',
          borderRadius: 'var(--radius-xl)',
          overflow: 'hidden',
        }}
      >
        {/* Tab bar */}
        <div className="tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            >
              <span style={{ marginRight: '5px' }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.22 }}
            style={{ padding: '2rem' }}
          >
            {activeTab === 'overview' && <OverviewTab project={project} onUpdate={fetchProject} />}
            {activeTab === 'techstack' && <TechStackTab project={project} onUpdate={fetchProject} />}
            {activeTab === 'architecture' && <ArchitectureTab project={project} onUpdate={fetchProject} />}
            {activeTab === 'endpoints' && <EndpointsTab project={project} onUpdate={fetchProject} />}
            {activeTab === 'upload' && (
              !uploadId ? (
                <ProjectUpload
                  projectId={project.id}
                  onUploadStart={(id) => {
                    setUploadId(id)
                    toast.success('Upload started! AI is analyzing your code…')
                  }}
                />
              ) : (
                <AnalysisProgress
                  uploadId={uploadId}
                  onComplete={(data) => {
                    toast.success(`Analysis complete! Found ${data.endpoints_found} endpoints`)
                    fetchProject()
                    setTimeout(() => setUploadId(null), 3000)
                  }}
                />
              )
            )}
            {activeTab === 'translate' && <APITranslator projectId={project.id} endpoints={project.endpoints} />}
            {activeTab === 'timeline' && <TimelineTab project={project} onUpdate={fetchProject} />}
            {activeTab === 'publish' && <PublishTab project={project} onUpdate={fetchProject} />}
          </motion.div>
        </AnimatePresence>
      </motion.div>
    </div>
  )
}

export default ProjectEdit
