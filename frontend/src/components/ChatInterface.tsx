import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

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

interface ChatInterfaceProps {
  messages: Message[]
  onSendMessage: (content: string) => void
  isLoading: boolean
}

const ChatInterface = ({
  messages,
  onSendMessage,
  isLoading
}: ChatInterfaceProps) => {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput('')
    }
  }

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <h3 className="text-lg font-medium mb-2">Welcome to InsightFlow</h3>
              <p>Ask me anything and watch the AI agent process your query in real-time!</p>
            </div>
          </div>
        )}
        
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-4xl px-4 py-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white border border-gray-200 shadow-sm'
              }`}
            >
              {message.type === 'user' ? (
                <div className="text-white">
                  <p className="mb-1">{message.content}</p>
                </div>
              ) : (
                <div className="prose prose-sm max-w-none text-gray-800">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => <h1 className="text-lg font-bold mb-2 text-gray-900">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-base font-semibold mb-2 text-gray-900">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-sm font-semibold mb-1 text-gray-900">{children}</h3>,
                      p: ({ children }) => <p className="mb-2 text-gray-700 leading-relaxed">{children}</p>,
                      ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="text-gray-700">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                      em: ({ children }) => <em className="italic text-gray-700">{children}</em>,
                      code: ({ children }) => <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-gray-800">{children}</code>,
                      pre: ({ children }) => <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto mb-2">{children}</pre>,
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              )}
              <div className={`text-xs mt-2 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-400'}`}>
                {formatTime(message.timestamp)}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-gray-600">Agent is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything..."
            className="input flex-1"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Send size={16} />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  )
}

export default ChatInterface