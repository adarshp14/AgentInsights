import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import AgentFlowVisualizer from './components/AgentFlowVisualizer'
import SettingsModal from './components/SettingsModal'
import { Settings } from 'lucide-react'

interface AgentStep {
  node: string
  status: string
  timestamp: number
  data: Record<string, any>
}

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: number
  steps?: AgentStep[]
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [currentSteps, setCurrentSteps] = useState<AgentStep[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: Date.now()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setCurrentSteps([])

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: content,
          conversation_id: 'default'
        })
      })

      const data = await response.json()
      
      setCurrentSteps(data.steps)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.answer,
        timestamp: Date.now(),
        steps: data.steps
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend is running.',
        timestamp: Date.now()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="h-screen bg-gray-50 flex">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">InsightFlow</h1>
          <button
            onClick={() => setShowSettings(true)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Settings size={20} />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex pt-20">
        {/* Chat Interface */}
        <div className="flex-1 flex flex-col">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>

        {/* Agent Flow Visualizer */}
        <div className="w-96 border-l border-gray-200 bg-white">
          <AgentFlowVisualizer steps={currentSteps} />
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal onClose={() => setShowSettings(false)} />
      )}
    </div>
  )
}

export default App