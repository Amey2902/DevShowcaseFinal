import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import ReactFlow, { Background, Controls, addEdge, useNodesState, useEdgesState } from 'reactflow'
import 'reactflow/dist/style.css'
import axios from 'axios'
import { toast } from 'react-toastify'
import './EditorTabs.css'

const ArchitectureTab = ({ project, onUpdate }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(
    project.architecture_nodes.map(node => ({
      id: node.id.toString(),
      position: { x: node.x_position, y: node.y_position },
      data: { label: `${node.name}\n${node.technology}` },
    }))
  )
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [formData, setFormData] = useState({ name: '', technology: '', description: '' })

  const onConnect = useCallback(params => setEdges(eds => addEdge(params, eds)), [])

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

  return (
    <div>
      <h3 className="editor-section-title">🏗 Architecture Diagram</h3>

      <div style={{
        height: '420px',
        marginBottom: '2rem',
        border: '1px solid var(--border-primary)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
        background: 'var(--bg-secondary)',
      }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeDragStop={handleNodeDragStop}
          fitView
        >
          <Background color="rgba(234,88,12,0.12)" gap={24} />
          <Controls />
        </ReactFlow>
      </div>

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
