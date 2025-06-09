import { useState, useEffect } from 'react'
import { Brain, Search, Calculator, FileText, Clock, Target, TrendingUp, Activity } from 'lucide-react'
import QueryAnalysisCard from './QueryAnalysisCard'

interface AgentStep {
  node: string
  status: string
  timestamp: number
  data: Record<string, any>
}

interface RealtimeDashboardProps {
  steps: AgentStep[]
  isProcessing: boolean
  currentQuery: string
}

const RealtimeDashboard = ({ steps, isProcessing, currentQuery }: RealtimeDashboardProps) => {
  const [animatedSteps, setAnimatedSteps] = useState<AgentStep[]>([])
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [metrics, setMetrics] = useState({
    totalTime: 0,
    queryType: 'unknown',
    documentsFound: 0,
    confidence: 0
  })

  useEffect(() => {
    if (steps.length > 0) {
      // Animate steps appearing one by one
      const timer = setTimeout(() => {
        if (currentStepIndex < steps.length) {
          setAnimatedSteps(prev => [...prev, steps[currentStepIndex]])
          setCurrentStepIndex(prev => prev + 1)
        }
      }, 200)

      return () => clearTimeout(timer)
    }
  }, [steps, currentStepIndex])

  useEffect(() => {
    // Reset animation when new query starts
    if (isProcessing && steps.length === 0) {
      setAnimatedSteps([])
      setCurrentStepIndex(0)
    }
  }, [isProcessing, steps.length])

  useEffect(() => {
    // Calculate metrics from completed steps
    if (steps.length > 0) {
      const startTime = steps[0]?.timestamp || 0
      const endTime = steps[steps.length - 1]?.timestamp || 0
      const totalTime = endTime - startTime

      const classificationStep = steps.find(step => step.node === 'QueryClassifier')
      const retrievalStep = steps.find(step => step.node === 'DocumentRetriever')

      setMetrics({
        totalTime,
        queryType: classificationStep?.data.query_type || 'unknown',
        documentsFound: retrievalStep?.data.documents_found || 0,
        confidence: calculateConfidence(steps)
      })
    }
  }, [steps])

  const calculateConfidence = (steps: AgentStep[]) => {
    const retrievalStep = steps.find(step => step.node === 'DocumentRetriever')
    if (retrievalStep?.data.avg_similarity_score) {
      return Math.round(retrievalStep.data.avg_similarity_score * 100)
    }
    return steps.length > 0 ? 85 : 0
  }

  const getStepIcon = (nodeName: string) => {
    switch (nodeName) {
      case 'QueryClassifier':
        return <Brain className="w-4 h-4" />
      case 'DocumentRetriever':
        return <Search className="w-4 h-4" />
      case 'ContextAnalyzer':
        return <FileText className="w-4 h-4" />
      case 'ToolUser':
        return <Calculator className="w-4 h-4" />
      case 'ResponseGenerator':
        return <Target className="w-4 h-4" />
      default:
        return <Activity className="w-4 h-4" />
    }
  }

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 border-green-500 text-green-700'
      case 'error':
        return 'bg-red-100 border-red-500 text-red-700'
      case 'in_progress':
        return 'bg-blue-100 border-blue-500 text-blue-700'
      default:
        return 'bg-gray-100 border-gray-300 text-gray-600'
    }
  }

  const getQueryTypeColor = (type: string) => {
    switch (type) {
      case 'retrieval':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'tool_use':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'direct':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const formatProcessingTime = (ms: number) => {
    if (ms < 1000) return `${Math.round(ms)}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Real-time Query Analysis
        </h2>
        {isProcessing && (
          <div className="flex items-center text-blue-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            Processing...
          </div>
        )}
      </div>

      {/* Current Query */}
      {currentQuery && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-sm font-medium text-gray-700">Current Query</h3>
            {steps.length > 0 && steps[0].data.processing_time_ms < 1000 && (
              <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">
                Fast Response
              </span>
            )}
          </div>
          <p className="text-gray-900 italic">"{currentQuery}"</p>
          {steps.some(s => s.data.memory_context_used || s.data.memory_updated) && (
            <div className="mt-2 text-xs text-blue-600 flex items-center">
              <Brain className="w-3 h-3 mr-1" />
              Memory context active
            </div>
          )}
        </div>
      )}

      {/* Real-time Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Query Type</p>
              <p className="text-xl font-bold capitalize">{metrics.queryType}</p>
            </div>
            <Brain className="w-8 h-8 text-blue-200" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Processing Time</p>
              <p className="text-xl font-bold">{formatProcessingTime(metrics.totalTime)}</p>
            </div>
            <Clock className="w-8 h-8 text-green-200" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Documents Found</p>
              <p className="text-xl font-bold">{metrics.documentsFound}</p>
            </div>
            <FileText className="w-8 h-8 text-purple-200" />
          </div>
        </div>

        <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">
                {steps.some(s => s.data.memory_context_used || s.data.memory_updated) ? 'Memory Active' : 'Confidence'}
              </p>
              <p className="text-xl font-bold">
                {steps.some(s => s.data.memory_context_used || s.data.memory_updated) ? '✓' : `${metrics.confidence}%`}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-orange-200" />
          </div>
        </div>
      </div>

      {/* Process Flow Visualization */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Processing Pipeline</h3>
        
        {animatedSteps.length === 0 && !isProcessing && (
          <div className="text-center text-gray-500 py-8">
            <Activity className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>Send a query to see the real-time analysis</p>
          </div>
        )}

        <div className="space-y-4">
          {animatedSteps.map((step, index) => (
            <QueryAnalysisCard
              key={`${step.node}-${step.timestamp}`}
              step={step}
              index={index}
            />
          ))}
        </div>
      </div>

      {/* Add some custom animations */}
      <style jsx>{`
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  )
}

export default RealtimeDashboard