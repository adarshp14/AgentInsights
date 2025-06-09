import React from 'react'
import { motion } from 'framer-motion'
import { 
  FileText, 
  Search, 
  Brain, 
  MessageSquare, 
  Tool,
  CheckCircle,
  Circle,
  Clock
} from 'lucide-react'

interface AgentStep {
  node: string
  status: string
  timestamp: number
  data: Record<string, any>
}

interface AgentFlowVisualizerProps {
  steps: AgentStep[]
}

const nodeIcons = {
  InputProcessor: FileText,
  Retriever: Search,
  Analyzer: Brain,
  Responder: MessageSquare,
  ToolCaller: Tool,
}

const nodeColors = {
  completed: 'bg-green-100 text-green-700 border-green-200',
  in_progress: 'bg-blue-100 text-blue-700 border-blue-200',
  pending: 'bg-gray-100 text-gray-500 border-gray-200',
}

const AgentFlowVisualizer: React.FC<AgentFlowVisualizerProps> = ({ steps }) => {
  const getNodeStatus = (nodeName: string) => {
    const step = steps.find(s => s.node === nodeName)
    return step?.status || 'pending'
  }

  const getNodeData = (nodeName: string) => {
    const step = steps.find(s => s.node === nodeName)
    return step?.data || {}
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return CheckCircle
      case 'in_progress':
        return Clock
      default:
        return Circle
    }
  }

  const nodes = [
    { name: 'InputProcessor', label: 'Input Processing' },
    { name: 'Retriever', label: 'Document Retrieval' },
    { name: 'Analyzer', label: 'Context Analysis' },
    { name: 'Responder', label: 'Response Generation' },
  ]

  return (
    <div className="h-full p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">Agent Flow</h2>
      
      <div className="space-y-4">
        {nodes.map((node, index) => {
          const status = getNodeStatus(node.name)
          const data = getNodeData(node.name)
          const NodeIcon = nodeIcons[node.name as keyof typeof nodeIcons]
          const StatusIcon = getStatusIcon(status)
          
          return (
            <div key={node.name} className="relative">
              {/* Connection Line */}
              {index < nodes.length - 1 && (
                <div className="absolute left-6 top-12 w-0.5 h-8 bg-gray-200" />
              )}
              
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`
                  p-4 rounded-lg border-2 transition-all duration-300
                  ${nodeColors[status as keyof typeof nodeColors]}
                `}
              >
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <NodeIcon size={20} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-sm">{node.label}</h3>
                    {status === 'completed' && data && Object.keys(data).length > 0 && (
                      <div className="mt-2 text-xs opacity-80">
                        {Object.entries(data).map(([key, value]) => (
                          <div key={key}>
                            <span className="font-medium">{key}:</span> {String(value)}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex-shrink-0">
                    <StatusIcon size={16} />
                  </div>
                </div>
                
                {status === 'in_progress' && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1">
                      <motion.div
                        className="bg-blue-500 h-1 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: '100%' }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
                    </div>
                  </div>
                )}
              </motion.div>
            </div>
          )
        })}
      </div>
      
      {steps.length > 0 && (
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-sm text-gray-900 mb-2">Debug Info</h3>
          <div className="text-xs text-gray-600 space-y-1">
            <div>Total steps: {steps.length}</div>
            <div>Completed: {steps.filter(s => s.status === 'completed').length}</div>
            {steps.length > 0 && (
              <div>
                Duration: {Math.round(steps[steps.length - 1].timestamp - steps[0].timestamp)}ms
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentFlowVisualizer