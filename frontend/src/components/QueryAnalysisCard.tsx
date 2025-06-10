import { useState, useEffect } from 'react'
import { Brain, Search, FileText, Calculator, Target, Clock, CheckCircle, AlertCircle } from 'lucide-react'

interface QueryAnalysisCardProps {
  step: {
    node: string
    status: string
    timestamp: number
    data: Record<string, any>
  }
  index: number
}

const QueryAnalysisCard = ({ step, index }: QueryAnalysisCardProps) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), index * 300)
    return () => clearTimeout(timer)
  }, [index])

  const getIcon = () => {
    switch (step.node) {
      case 'QueryClassifier':
        return <Brain className="w-5 h-5" />
      case 'DocumentRetriever':
        return <Search className="w-5 h-5" />
      case 'ContextAnalyzer':
        return <FileText className="w-5 h-5" />
      case 'ToolUser':
        return <Calculator className="w-5 h-5" />
      case 'ResponseGenerator':
        return <Target className="w-5 h-5" />
      default:
        return <CheckCircle className="w-5 h-5" />
    }
  }

  const getStatusIcon = () => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-yellow-500 animate-spin" />
    }
  }

  const getBorderColor = () => {
    switch (step.status) {
      case 'completed':
        return 'border-green-200 bg-green-50'
      case 'error':
        return 'border-red-200 bg-red-50'
      default:
        return 'border-blue-200 bg-blue-50'
    }
  }

  const getNodeDescription = () => {
    switch (step.node) {
      case 'QueryClassifier':
        return 'Analyzing query type and determining optimal processing path'
      case 'DocumentRetriever':
        return 'Searching document store for relevant information'
      case 'ContextAnalyzer':
        return 'Analyzing retrieved documents and extracting insights'
      case 'ToolUser':
        return 'Executing specialized tools for calculations or data retrieval'
      case 'ResponseGenerator':
        return 'Generating comprehensive response based on gathered information'
      default:
        return 'Processing...'
    }
  }

  const formatTime = (ms: number) => {
    if (ms < 1000) return `${Math.round(ms)}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  return (
    <div
      className={`border rounded-lg p-4 transition-all duration-500 transform ${
        isVisible ? 'translate-x-0 opacity-100' : 'translate-x-10 opacity-0'
      } ${getBorderColor()}`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            {getIcon()}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{step.node}</h3>
            <p className="text-sm text-gray-600">{getNodeDescription()}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className="text-xs text-gray-500">
            {formatTime(step.data.processing_time_ms || 0)}
          </span>
        </div>
      </div>

      {/* Step-specific details */}
      <div className="space-y-2 text-sm">
        {step.node === 'QueryClassifier' && step.data.query_type && (
          <div className="bg-white rounded p-2 border">
            <div className="flex justify-between items-center">
              <span className="font-medium">Classification:</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                step.data.query_type === 'retrieval' ? 'bg-purple-100 text-purple-800' :
                step.data.query_type === 'tool_use' ? 'bg-orange-100 text-orange-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {step.data.query_type}
              </span>
            </div>
            {step.data.classification_reasoning && (
              <div className="mt-1 text-xs text-gray-600">
                <strong>Reasoning:</strong> {step.data.classification_reasoning}
              </div>
            )}
          </div>
        )}

        {step.node === 'DocumentRetriever' && (
          <div className="bg-white rounded p-2 border space-y-1">
            <div className="flex justify-between">
              <span className="font-medium">Documents Found:</span>
              <span className="text-blue-600 font-bold">{step.data.documents_found || 0}</span>
            </div>
            {step.data.avg_similarity_score && (
              <div className="flex justify-between">
                <span className="font-medium">Avg Similarity:</span>
                <span className="text-green-600 font-bold">
                  {Math.round(step.data.avg_similarity_score * 100)}%
                </span>
              </div>
            )}
            {step.data.sources && step.data.sources.length > 0 && (
              <div>
                <span className="font-medium">Sources:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {step.data.sources.slice(0, 2).map((source: string, idx: number) => (
                    <span key={idx} className="bg-gray-100 px-2 py-1 rounded text-xs">
                      {source.replace('.pdf', '')}
                    </span>
                  ))}
                  {step.data.sources.length > 2 && (
                    <span className="text-xs text-gray-500">+{step.data.sources.length - 2} more</span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {step.node === 'ContextAnalyzer' && (
          <div className="bg-white rounded p-2 border space-y-1">
            <div className="flex justify-between">
              <span className="font-medium">Analysis Type:</span>
              <span className="text-purple-600">{step.data.analysis_type || 'Standard'}</span>
            </div>
            {step.data.documents_analyzed && (
              <div className="flex justify-between">
                <span className="font-medium">Documents Analyzed:</span>
                <span className="text-blue-600 font-bold">{step.data.documents_analyzed}</span>
              </div>
            )}
            {step.data.analysis_length && (
              <div className="flex justify-between">
                <span className="font-medium">Analysis Length:</span>
                <span className="text-gray-600">{step.data.analysis_length} chars</span>
              </div>
            )}
          </div>
        )}

        {step.node === 'ToolUser' && (
          <div className="bg-white rounded p-2 border space-y-1">
            <div className="flex justify-between">
              <span className="font-medium">Tool Used:</span>
              <span className="text-orange-600 font-bold">{step.data.tool_selected || 'N/A'}</span>
            </div>
            {step.data.tool_result && (
              <div>
                <span className="font-medium">Result:</span>
                <div className="mt-1 p-2 bg-gray-50 rounded text-xs font-mono">
                  {typeof step.data.tool_result === 'string' 
                    ? step.data.tool_result.substring(0, 100) + (step.data.tool_result.length > 100 ? '...' : '')
                    : JSON.stringify(step.data.tool_result).substring(0, 100)
                  }
                </div>
              </div>
            )}
          </div>
        )}

        {step.node === 'ResponseGenerator' && (
          <div className="bg-white rounded p-2 border space-y-1">
            <div className="flex justify-between">
              <span className="font-medium">Response Length:</span>
              <span className="text-green-600 font-bold">{step.data.response_length || 0} chars</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Word Count:</span>
              <span className="text-blue-600">{step.data.word_count || 0} words</span>
            </div>
            {step.data.sources_referenced !== undefined && (
              <div className="flex justify-between">
                <span className="font-medium">Sources Referenced:</span>
                <span className="text-purple-600">{step.data.sources_referenced}</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="mt-3 text-xs text-gray-400 text-right">
        {new Date(step.timestamp).toLocaleTimeString()}
      </div>
    </div>
  )
}

export { QueryAnalysisCard }
export default QueryAnalysisCard