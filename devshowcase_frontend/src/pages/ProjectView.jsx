import { useState, useEffect, useContext } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import ReactFlow, { Background, Controls } from 'reactflow'
import 'reactflow/dist/style.css'
import APIPlayground from '../components/APIPlayground'
import { AuthContext } from '../context/AuthContext'
import AnimatedPage from '../components/AnimatedPage'
import './ProjectView.css'

const ProjectView = () => {
  const { slug } = useParams()
  const { user } = useContext(AuthContext)
  const [project, setProject] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [aiExplanation, setAiExplanation] = useState('')
  const [loadingAI, setLoadingAI] = useState(false)
  const [showAI, setShowAI] = useState(false)

  useEffect(() => { fetchProject() }, [slug])

  const fetchProject = async () => {
    try {
      const { data } = await axios.get(`/api/projects/${slug}/full/`)
      setProject(data)
    } catch {
      console.error('Failed to load project')
    }
  }

  const handleAIExplain = async () => {
    if (aiExplanation) { setShowAI(!showAI); return }
    setLoadingAI(true)
    setShowAI(true)
    try {
      const { data } = await axios.post(`/api/projects/${slug}/explain/`)
      setAiExplanation(data.explanation)
    } catch {
      setAiExplanation('Failed to generate explanation. Please try again.')
    } finally {
      setLoadingAI(false)
    }
  }

  if (!project) return (
    <div className="loading">
      <div className="loading-spinner" />
      Loading project…
    </div>
  )

  const isOwner = user && project.owner_username === user.username

  const nodes = project.architecture_nodes.map(node => ({
    id: node.id.toString(),
    position: { x: node.x_position, y: node.y_position },
    data: { label: `${node.name}\n${node.technology}` },
  }))

  const tabs = [
    { id: 'overview', label: '📋 Overview', icon: '📋' },
    { id: 'architecture', label: '🏗 Architecture', icon: '🏗' },
    { id: 'playground', label: '🧪 API Playground', icon: '🧪' },
    { id: 'timeline', label: '📅 Timeline', icon: '📅' },
  ]

  return (
    <AnimatedPage>
      <div className="container project-view-container">

        {/* ─── Project Hero Header ─── */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="project-header"
        >
          {/* Background glow orbs */}
          <div className="project-header-orb project-header-orb-1" />
          <div className="project-header-orb project-header-orb-2" />

          <div style={{ position: 'relative', zIndex: 1 }}>
            {/* Owner */}
            <div style={{ marginBottom: '1rem' }}>
              <span className="badge badge-primary">by {project.owner_username}</span>
            </div>

            <h1 className="project-title">{project.title}</h1>
            <p className="project-description">{project.short_description}</p>

            {/* Action buttons */}
            <div className="project-links">
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: 'var(--shadow-glow)' }}
                whileTap={{ scale: 0.96 }}
                onClick={handleAIExplain}
                className="btn btn-primary"
                style={{ padding: '0.75rem 1.5rem' }}
              >
                ✦ {showAI ? 'Hide AI' : 'AI Explain'}
              </motion.button>
              {project.github_url && (
                <motion.a
                  whileHover={{ scale: 1.05 }}
                  href={project.github_url}
                  target="_blank" rel="noopener noreferrer"
                  className="btn btn-secondary"
                  style={{ padding: '0.75rem 1.5rem' }}
                >
                  GitHub →
                </motion.a>
              )}
              {project.demo_url && (
                <motion.a
                  whileHover={{ scale: 1.05 }}
                  href={project.demo_url}
                  target="_blank" rel="noopener noreferrer"
                  className="btn btn-success"
                  style={{ padding: '0.75rem 1.5rem' }}
                >
                  Live Demo ↗
                </motion.a>
              )}
              {isOwner && (
                <Link to={`/project/edit/${slug}`}>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    className="btn btn-ghost"
                    style={{ padding: '0.75rem 1.5rem' }}
                  >
                    ✏ Edit
                  </motion.button>
                </Link>
              )}
            </div>
          </div>
        </motion.div>

        {/* ─── AI Explanation Panel ─── */}
        <AnimatePresence>
          {showAI && (
            <motion.div
              initial={{ opacity: 0, height: 0, marginBottom: 0 }}
              animate={{ opacity: 1, height: 'auto', marginBottom: '2rem' }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="ai-panel"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '1rem' }}>
                <motion.span
                  animate={{ rotate: loadingAI ? 360 : 0 }}
                  transition={{ duration: 1, repeat: loadingAI ? Infinity : 0, ease: 'linear' }}
                  style={{ fontSize: '1.25rem' }}
                >
                  🤖
                </motion.span>
                <h3 className="ai-panel-title">AI-Generated Explanation</h3>
              </div>
              {loadingAI ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div className="skeleton" style={{ height: '14px', width: '90%' }} />
                  <div className="skeleton" style={{ height: '14px', width: '75%' }} />
                  <div className="skeleton" style={{ height: '14px', width: '82%' }} />
                  <div className="skeleton" style={{ height: '14px', width: '60%' }} />
                </div>
              ) : (
                <p className="ai-panel-text">{aiExplanation}</p>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* ─── Tabs Card ─── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          style={{
            background: 'var(--bg-glass)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: '1px solid var(--border-glass)',
            borderRadius: 'var(--radius-xl)',
            overflow: 'hidden',
            marginBottom: '3rem',
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
              transition={{ duration: 0.25 }}
              style={{ padding: '2rem' }}
            >
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div>
                  <h3 className="section-title">Problem Statement</h3>
                  <p className="section-text">{project.problem_statement}</p>
                  <h3 className="section-title" style={{ marginTop: '2.5rem' }}>Tech Stack</h3>
                  <div className="tech-grid">
                    {project.tech_stack.map((tech, i) => (
                      <motion.div
                        key={tech.id}
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.07 }}
                        className="tech-card"
                      >
                        <h4 className="tech-name">{tech.name}</h4>
                        <p className="tech-purpose">{tech.purpose}</p>
                        <p className="tech-reason">{tech.reason}</p>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}

              {/* Architecture Tab */}
              {activeTab === 'architecture' && (
                <div>
                  <h3 className="section-title">Architecture Diagram</h3>
                  <div className="architecture-diagram">
                    <ReactFlow nodes={nodes} edges={[]} fitView>
                      <Background color="rgba(234,88,12,0.12)" gap={24} />
                      <Controls />
                    </ReactFlow>
                  </div>
                </div>
              )}

              {/* Playground Tab */}
              {activeTab === 'playground' && (
                <APIPlayground endpoints={project.endpoints} isOwner={isOwner} projectId={project.id} />
              )}

              {/* Timeline Tab */}
              {activeTab === 'timeline' && (
                <div>
                  <h3 className="section-title">Project Timeline</h3>
                  <div className="timeline-container">
                    {project.timeline_events.map((event, i) => (
                      <motion.div
                        key={event.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.08 }}
                        className="timeline-item"
                      >
                        <div className="timeline-date">{event.event_date}</div>
                        <div className="timeline-content">
                          <h4 className="timeline-title">{event.title}</h4>
                          <p className="timeline-description">{event.description}</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </motion.div>
      </div>
    </AnimatedPage>
  )
}

export default ProjectView
