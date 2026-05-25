import { useState, useEffect, useContext, useCallback, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import ReactFlow, { Background, Controls, MiniMap, MarkerType, useNodesState, useEdgesState, addEdge } from 'reactflow'
import 'reactflow/dist/style.css'
import APIPlayground from '../components/APIPlayground'
import { AuthContext } from '../context/AuthContext'
import AnimatedPage from '../components/AnimatedPage'
import './ProjectView.css'

// ── Architecture helpers (shared logic with ArchitectureTab) ──────────────────
const COMPONENT_TYPE_ORDER = ['frontend','api_gateway','backend','middleware','cache','database','external_service','message_queue']

const NODE_STYLES = {
  frontend:         { bg: 'linear-gradient(135deg,#667eea,#764ba2)', border: '#5a67d8', shadow: 'rgba(102,126,234,.4)', icon: '🖥️' },
  backend:          { bg: 'linear-gradient(135deg,#10b981,#059669)', border: '#059669', shadow: 'rgba(16,185,129,.4)',  icon: '⚙️' },
  database:         { bg: 'linear-gradient(135deg,#f59e0b,#dc2626)', border: '#dc2626', shadow: 'rgba(245,158,11,.4)',  icon: '🗄️' },
  cache:            { bg: 'linear-gradient(135deg,#fbbf24,#f59e0b)', border: '#f59e0b', shadow: 'rgba(251,191,36,.4)',  icon: '⚡' },
  middleware:       { bg: 'linear-gradient(135deg,#ec4899,#db2777)', border: '#db2777', shadow: 'rgba(236,72,153,.4)',  icon: '🔒' },
  external_service: { bg: 'linear-gradient(135deg,#06b6d4,#0891b2)', border: '#0891b2', shadow: 'rgba(6,182,212,.4)',   icon: '🌐' },
  api_gateway:      { bg: 'linear-gradient(135deg,#8b5cf6,#6d28d9)', border: '#6d28d9', shadow: 'rgba(139,92,246,.4)', icon: '🔀' },
  message_queue:    { bg: 'linear-gradient(135deg,#f97316,#ea580c)', border: '#ea580c', shadow: 'rgba(249,115,22,.4)',  icon: '📨' },
  default:          { bg: 'linear-gradient(135deg,#6b7280,#4b5563)', border: '#4b5563', shadow: 'rgba(107,114,128,.4)', icon: '📦' },
}

const getNodeType = (technology = '', name = '') => {
  const t = (technology + ' ' + name).toLowerCase()
  if (t.includes('react')||t.includes('vue')||t.includes('angular')||t.includes('frontend')||t.includes('html')||t.includes('next')) return 'frontend'
  if (t.includes('redis')||t.includes('cache')||t.includes('memcache')) return 'cache'
  if (t.includes('postgres')||t.includes('mysql')||t.includes('mongo')||t.includes('sqlite')||t.includes('database')||t.includes('db')) return 'database'
  if (t.includes('middleware')||t.includes('auth')||t.includes('jwt')||t.includes('oauth')) return 'middleware'
  if (t.includes('gateway')||t.includes('nginx')||t.includes('proxy')) return 'api_gateway'
  if (t.includes('queue')||t.includes('kafka')||t.includes('rabbitmq')||t.includes('celery')) return 'message_queue'
  if (t.includes('aws')||t.includes('stripe')||t.includes('sendgrid')||t.includes('twilio')||t.includes('firebase')||t.includes('external')) return 'external_service'
  if (t.includes('express')||t.includes('django')||t.includes('flask')||t.includes('fastapi')||t.includes('nest')||t.includes('api')||t.includes('server')||t.includes('backend')) return 'backend'
  return 'default'
}

const buildArchNodes = (archNodes) => archNodes.map(node => {
  const nodeType = getNodeType(node.technology, node.name)
  const s = NODE_STYLES[nodeType] || NODE_STYLES.default
  return {
    id: node.id.toString(),
    _nodeType: nodeType,
    position: { x: node.x_position, y: node.y_position },
    data: {
      label: (
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:'4px' }}>
          <span style={{ fontSize:'20px' }}>{s.icon}</span>
          <span style={{ fontWeight:700, fontSize:'13px' }}>{node.name}</span>
          <span style={{ fontSize:'11px', opacity:.85, fontWeight:400 }}>{node.technology}</span>
        </div>
      )
    },
    style: {
      background: s.bg, color:'white', border:`2px solid ${s.border}`,
      boxShadow:`0 6px 20px ${s.shadow}`, padding:'14px 18px',
      borderRadius:'14px', fontSize:'13px', fontWeight:'600',
      minWidth:'160px', textAlign:'center',
    },
  }
})

const buildAutoEdges = (nodes) => {
  if (nodes.length < 2) return []
  const sorted = [...nodes].sort((a,b) => {
    const ai = COMPONENT_TYPE_ORDER.indexOf(a._nodeType)
    const bi = COMPONENT_TYPE_ORDER.indexOf(b._nodeType)
    return (ai===-1?99:ai)-(bi===-1?99:bi)
  })
  return sorted.slice(0,-1).map((n,i) => ({
    id: `e-${n.id}-${sorted[i+1].id}`,
    source: n.id, target: sorted[i+1].id,
    animated: true,
    style: { stroke:'#94a3b8', strokeWidth:2 },
    markerEnd: { type: MarkerType.ArrowClosed, color:'#94a3b8' },
  }))
}

const TECH_COLORS = [
  { bg:'#1e3a5f', border:'#3b82f6', text:'#93c5fd' },
  { bg:'#1a3a2a', border:'#10b981', text:'#6ee7b7' },
  { bg:'#3b1f1f', border:'#ef4444', text:'#fca5a5' },
  { bg:'#2d1f3d', border:'#8b5cf6', text:'#c4b5fd' },
  { bg:'#1f2d3d', border:'#06b6d4', text:'#67e8f9' },
  { bg:'#3d2d1f', border:'#f59e0b', text:'#fcd34d' },
  { bg:'#3d1f2d', border:'#ec4899', text:'#f9a8d4' },
]
// ─────────────────────────────────────────────────────────────────────────────

const ProjectView = ({ setErrorContext, setEndpointContext }) => {
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

  // Hooks must be called before any early return
  const archNodes = useMemo(() => project ? buildArchNodes(project.architecture_nodes) : [], [project])
  const archEdges = useMemo(() => buildAutoEdges(archNodes), [archNodes])
  const techItems = useMemo(() => {
    if (!project) return []
    if (project.tech_stack && project.tech_stack.length > 0) return project.tech_stack
    return project.architecture_nodes.map(n => ({ name: n.technology, purpose: n.name }))
  }, [project])

  if (!project) return (
    <div className="loading">
      <div className="loading-spinner" />
      Loading project…
    </div>
  )

  const isOwner = user && project.owner_username === user.username

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
                  <div className="architecture-diagram" style={{
                    background: 'linear-gradient(135deg,#0f172a,#1e293b)',
                    borderRadius: '16px',
                    border: '1px solid rgba(148,163,184,.15)',
                    boxShadow: '0 8px 32px rgba(0,0,0,.4)',
                    overflow: 'hidden',
                  }}>
                    <ReactFlow nodes={archNodes} edges={archEdges} fitView fitViewOptions={{ padding: 0.3 }}>
                      <Background color="rgba(148,163,184,.08)" gap={24} />
                      <Controls style={{ background:'rgba(15,23,42,.8)', border:'1px solid rgba(148,163,184,.2)', borderRadius:'8px' }} />
                      <MiniMap
                        nodeColor={n => (NODE_STYLES[n._nodeType] || NODE_STYLES.default).border}
                        style={{ background:'rgba(15,23,42,.8)', border:'1px solid rgba(148,163,184,.2)', borderRadius:'8px' }}
                      />
                    </ReactFlow>
                  </div>

                  {/* Tech Stack badges */}
                  {techItems.length > 0 && (
                    <div style={{ marginTop:'1.5rem' }}>
                      <h4 style={{ fontSize:'15px', fontWeight:700, color:'#e2e8f0', marginBottom:'1rem' }}>🛠 Tech Stack</h4>
                      <div style={{ display:'flex', flexWrap:'wrap', gap:'10px' }}>
                        {techItems.map((tech, i) => {
                          const c = TECH_COLORS[i % TECH_COLORS.length]
                          return (
                            <motion.div key={i}
                              initial={{ opacity:0, scale:.85 }}
                              animate={{ opacity:1, scale:1 }}
                              transition={{ delay: i * 0.05 }}
                              style={{
                                background: c.bg, border:`1px solid ${c.border}`,
                                borderRadius:'10px', padding:'8px 14px',
                                display:'flex', flexDirection:'column', gap:'2px', minWidth:'110px',
                              }}
                            >
                              <span style={{ color:c.text, fontWeight:700, fontSize:'13px' }}>{tech.name}</span>
                              {tech.purpose && <span style={{ color:'rgba(255,255,255,.5)', fontSize:'11px' }}>{tech.purpose}</span>}
                            </motion.div>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Playground Tab */}
              {activeTab === 'playground' && (
                <APIPlayground endpoints={project.endpoints} isOwner={isOwner} projectId={project.id} liveBaseUrl={project.live_base_url || ''} setErrorContext={setErrorContext} setEndpointContext={setEndpointContext} />
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
