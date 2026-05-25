import { useState, useCallback, useMemo } from 'react'
import { motion } from 'framer-motion'
import ReactFlow, {
  Background,
  Controls,
  addEdge,
  useNodesState,
  useEdgesState,
  MarkerType,
  MiniMap,
} from 'reactflow'
import 'reactflow/dist/style.css'
import axios from 'axios'
import { toast } from 'react-toastify'
import './EditorTabs.css'

// Component type order for auto-edge generation (data flows left to right / top to bottom)
const COMPONENT_TYPE_ORDER = [
  'frontend', 'api_gateway', 'backend', 'middleware', 'cache', 'database', 'external_service', 'message_queue'
]

const NODE_STYLES = {
  frontend: {
    bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: '#5a67d8',
    shadow: 'rgba(102,126,234,0.4)',
    icon: '🖥️',
  },
  backend: {
    bg: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    border: '#059669',
    shadow: 'rgba(16,185,129,0.4)',
    icon: '⚙️',
  },
  database: {
    bg: 'linear-gradient(135deg, #f59e0b 0%, #dc2626 100%)',
    border: '#dc2626',
    shadow: 'rgba(245,158,11,0.4)',
    icon: '🗄️',
  },
  cache: {
    bg: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
    border: '#f59e0b',
    shadow: 'rgba(251,191,36,0.4)',
    icon: '⚡',
  },
  middleware: {
    bg: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
    border: '#db2777',
    shadow: 'rgba(236,72,153,0.4)',
    icon: '🔒',
  },
  external_service: {
    bg: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
    border: '#0891b2',
    shadow: 'rgba(6,182,212,0.4)',
    icon: '🌐',
  },
  api_gateway: {
    bg: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
    border: '#6d28d9',
    shadow: 'rgba(139,92,246,0.4)',
    icon: '🔀',
  },
  message_queue: {
    bg: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
    border: '#ea580c',
    shadow: 'rgba(249,115,22,0.4)',
    icon: '📨',
  },
  default: {
    bg: 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
    border: '#4b5563',
    shadow: 'rgba(107,114,128,0.4)',
    icon: '📦',
  },
}

const getNodeType = (technology = '', name = '') => {
  const t = (technology + ' ' + name).toLowerCase()
  if (t.includes('react') || t.includes('vue') || t.includes('angular') || t.includes('frontend') || t.includes('html') || t.includes('next')) return 'frontend'
  if (t.includes('redis') || t.includes('cache') || t.includes('memcache')) return 'cache'
  if (t.includes('postgres') || t.includes('mysql') || t.includes('mongo') || t.includes('sqlite') || t.includes('database') || t.includes('db')) return 'database'
  if (t.includes('middleware') || t.includes('auth') || t.includes('jwt') || t.includes('oauth')) return 'middleware'
  if (t.includes('gateway') || t.includes('nginx') || t.includes('proxy')) return 'api_gateway'
  if (t.includes('queue') || t.includes('kafka') || t.includes('rabbitmq') || t.includes('celery')) return 'message_queue'
  if (t.includes('aws') || t.includes('stripe') || t.includes('sendgrid') || t.includes('twilio') || t.includes('firebase') || t.includes('external')) return 'external_service'
  if (t.includes('express') || t.includes('django') || t.includes('flask') || t.includes('fastapi') || t.includes('nest') || t.includes('api') || t.includes('server') || t.includes('backend')) return 'backend'
  return 'default'
}

const buildNodeStyle = (nodeType) => {
  const s = NODE_STYLES[nodeType] || NODE_STYLES.default
  return {
    background: s.bg,
    color: 'white',
    border: `2px solid ${s.border}`,
    boxShadow: `0 6px 20px ${s.shadow}`,
    padding: '14px 18px',
    borderRadius: '14px',
    fontSize: '13px',
    fontWeight: '600',
    minWidth: '160px',
    textAlign: 'center',
  }
}

// Auto-generate edges: connect nodes in type-order sequence
const buildAutoEdges = (nodes) => {
  if (nodes.length < 2) return []

  // Sort nodes by their type order
  const sorted = [...nodes].sort((a, b) => {
    const ai = COMPONENT_TYPE_ORDER.indexOf(a._nodeType)
    const bi = COMPONENT_TYPE_ORDER.indexOf(b._nodeType)
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })

  const edges = []
  // Connect each node to the next in the sorted order
  for (let i = 0; i < sorted.length - 1; i++) {
    edges.push({
      id: `e-${sorted[i].id}-${sorted[i + 1].id}`,
      source: sorted[i].id,
      target: sorted[i + 1].id,
      animated: true,
      style: { stroke: '#94a3b8', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#94a3b8' },
    })
  }
  return edges
}

// Tech stack badge colors
const TECH_COLORS = [
  { bg: '#1e3a5f', border: '#3b82f6', text: '#93c5fd' },
  { bg: '#1a3a2a', border: '#10b981', text: '#6ee7b7' },
  { bg: '#3b1f1f', border: '#ef4444', text: '#fca5a5' },
  { bg: '#2d1f3d', border: '#8b5cf6', text: '#c4b5fd' },
  { bg: '#1f2d3d', border: '#06b6d4', text: '#67e8f9' },
  { bg: '#3d2d1f', border: '#f59e0b', text: '#fcd34d' },
  { bg: '#3d1f2d', border: '#ec4899', text: '#f9a8d4' },
]

const ArchitectureTab = ({ project, onUpdate }) => {
  const rawNodes = useMemo(() => project.architecture_nodes.map(node => {
    const nodeType = getNodeType(node.technology, node.name)
    const style = NODE_STYLES[nodeType] || NODE_STYLES.default
    return {
      id: node.id.toString(),
      _nodeType: nodeType,
      position: { x: node.x_position, y: node.y_position },
      data: {
        label: (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
            <span style={{ fontSize: '20px' }}>{style.icon}</span>
            <span style={{ fontWeight: 700, fontSize: '13px' }}>{node.name}</span>
            <span style={{ fontSize: '11px', opacity: 0.85, fontWeight: 400 }}>{node.technology}</span>
          </div>
        )
      },
      style: buildNodeStyle(nodeType),
    }
  }), [project.architecture_nodes])

  const [nodes, setNodes, onNodesChange] = useNodesState(rawNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(buildAutoEdges(rawNodes))
  const [formData, setFormData] = useState({ name: '', technology: '', description: '' })

  const onConnect = useCallback(params => setEdges(eds => addEdge({
    ...params,
    animated: true,
    style: { stroke: '#94a3b8', strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#94a3b8' },
  }, eds)), [])

  const handleNodeDragStop = async (event, node) => {
    const nodeData = project.architecture_nodes.find(n => n.id.toString() === node.id)
    if (nodeData) {
      try {
        await axios.put(`/api/architecture/${nodeData.id}/`, { ...nodeData, x_position: node.position.x, y_position: node.position.y })
      } catch { console.error('Failed to update node position') }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/architecture/', { ...formData, project: project.id, x_position: 100, y_position: 100 })
      toast.success('Architecture node added')
      setFormData({ name: '', technology: '', description: '' })
      onUpdate()
    } catch { toast.error('Failed to add architecture node') }
  }

  // Build tech stack list: prefer project.tech_stack, fallback to architecture nodes
  const techItems = useMemo(() => {
    if (project.tech_stack && project.tech_stack.length > 0) {
      return project.tech_stack.map(t => ({ name: t.name, purpose: t.purpose }))
    }
    // Fallback: derive from architecture nodes
    return project.architecture_nodes.map(n => ({ name: n.technology, purpose: n.name }))
  }, [project.tech_stack, project.architecture_nodes])

  return (
    <div>
      <h3 className="editor-section-title">🏗 Architecture Diagram</h3>

      {/* Diagram */}
      <div style={{
        height: '460px',
        marginBottom: '2rem',
        border: '1px solid rgba(148,163,184,0.15)',
        borderRadius: '16px',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
      }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeDragStop={handleNodeDragStop}
          fitView
          fitViewOptions={{ padding: 0.3 }}
        >
          <Background color="rgba(148,163,184,0.08)" gap={24} size={1} />
          <Controls style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(148,163,184,0.2)', borderRadius: '8px' }} />
          <MiniMap
            nodeColor={(n) => {
              const s = NODE_STYLES[n._nodeType] || NODE_STYLES.default
              return s.border
            }}
            style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(148,163,184,0.2)', borderRadius: '8px' }}
          />
        </ReactFlow>
      </div>

      {/* Tech Stack */}
      {techItems.length > 0 && (
        <div style={{ marginBottom: '2rem' }}>
          <h4 style={{
            fontSize: '15px',
            fontWeight: 700,
            color: '#e2e8f0',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            🛠 Tech Stack
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {techItems.map((tech, i) => {
              const c = TECH_COLORS[i % TECH_COLORS.length]
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.85 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                  style={{
                    background: c.bg,
                    border: `1px solid ${c.border}`,
                    borderRadius: '10px',
                    padding: '8px 14px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '2px',
                    minWidth: '110px',
                  }}
                >
                  <span style={{ color: c.text, fontWeight: 700, fontSize: '13px' }}>{tech.name}</span>
                  {tech.purpose && (
                    <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '11px' }}>{tech.purpose}</span>
                  )}
                </motion.div>
              )
            })}
          </div>
        </div>
      )}

      {/* Add Node Form */}
      <div className="editor-form">
        <h4 className="editor-form-title">+ Add Architecture Node</h4>
        <form onSubmit={handleSubmit}>
          {[
            { key: 'name', label: 'Node Name', type: 'input' },
            { key: 'technology', label: 'Technology', type: 'input' },
            { key: 'description', label: 'Description', type: 'textarea' },
          ].map(({ key, label, type }) => (
            <div key={key} className="form-group">
              <label className="form-label">{label}</label>
              {type === 'textarea' ? (
                <textarea className="form-textarea" rows={3} value={formData[key]} onChange={e => setFormData({ ...formData, [key]: e.target.value })} required />
              ) : (
                <input type="text" className="form-input" value={formData[key]} onChange={e => setFormData({ ...formData, [key]: e.target.value })} required />
              )}
            </div>
          ))}
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} type="submit" className="btn btn-primary">
            + Add Node
          </motion.button>
        </form>
      </div>
    </div>
  )
}

export default ArchitectureTab
