import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import { QueryAnalysisCard } from './QueryAnalysisCard';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  steps?: any[];
  metadata?: any;
  isStreaming?: boolean;
}

interface StreamingChatInterfaceProps {
  conversationId?: string;
}

export const StreamingChatInterface: React.FC<StreamingChatInterfaceProps> = ({
  conversationId: providedConversationId
}) => {
  // Generate unique session ID if not provided
  const [sessionId] = useState(() => {
    if (providedConversationId && providedConversationId !== 'default') {
      return providedConversationId;
    }
    
    // Try to get existing session from localStorage
    const existing = localStorage.getItem('insightflow_session_id');
    if (existing) {
      return existing;
    }
    
    // Generate new unique session ID
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('insightflow_session_id', newSessionId);
    return newSessionId;
  });

  const [messages, setMessages] = useState<Message[]>(() => {
    // Load conversation history from localStorage
    try {
      const saved = localStorage.getItem(`insightflow_messages_${sessionId}`);
      if (saved) {
        const parsedMessages = JSON.parse(saved);
        // Convert timestamp strings back to Date objects
        return parsedMessages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
      }
      return [];
    } catch {
      return [];
    }
  });
  
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('');
  const [currentSteps, setCurrentSteps] = useState<any[]>([]);
  const [progress, setProgress] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`insightflow_messages_${sessionId}`, JSON.stringify(messages));
    }
  }, [messages, sessionId]);

  const handleStreamingQuery = async (question: string) => {
    if (!question.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setCurrentStreamingMessage('');
    setCurrentSteps([]);
    setProgress(0);

    try {
      // Close any existing EventSource
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Create streaming request
      const response = await fetch('/api/query/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          conversation_id: sessionId,
          stream: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      let assistantMessageId = (Date.now() + 1).toString();
      let fullResponse = '';
      let finalSteps: any[] = [];
      let finalMetadata: any = {};

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              let dataStr = line.slice(6).trim();
              if (!dataStr) continue;
              
              // Handle nested "data: data: {...}" format from backend
              if (dataStr.startsWith('data: ')) {
                dataStr = dataStr.slice(6).trim();
              }
              
              const data = JSON.parse(dataStr);
              
              switch (data.type) {
                case 'step':
                  // Hide technical steps for clean UI
                  setProgress(data.progress || 0);
                  break;
                
                case 'token':
                  fullResponse += data.content;
                  setCurrentStreamingMessage(fullResponse);
                  setProgress(data.progress || 0);
                  break;
                
                case 'complete':
                  finalMetadata = data.metadata;
                  setProgress(100);
                  break;
                
                case 'error':
                  throw new Error(data.error);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }

      // Add final assistant message
      const assistantMessage: Message = {
        id: assistantMessageId,
        type: 'assistant',
        content: fullResponse,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setCurrentStreamingMessage('');
      setCurrentSteps([]);

    } catch (error) {
      console.error('Streaming error:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
      setCurrentStreamingMessage('');
    } finally {
      setIsLoading(false);
      setProgress(0);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && !isLoading) {
      handleStreamingQuery(inputMessage.trim());
    }
  };

  const formatTimestamp = (date: Date | string) => {
    try {
      const dateObj = date instanceof Date ? date : new Date(date);
      return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  };

  const clearConversation = () => {
    setMessages([]);
    localStorage.removeItem(`insightflow_messages_${sessionId}`);
  };

  return (
    <div className="flex flex-col h-full max-h-screen bg-white">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto" style={{ height: 'calc(100vh - 140px)' }}>
        <div className="max-w-4xl mx-auto px-4 py-6">
          {messages.length === 0 && !currentStreamingMessage && (
            <div className="text-center py-12">
              <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Welcome to InsightFlow</h3>
              <p className="text-gray-500 max-w-md mx-auto mb-4">
                Ask me anything about taxes, business regulations, or general knowledge. 
                I'll provide real-time streaming responses with intelligent routing.
              </p>
              <div className="text-xs text-gray-400 bg-gray-50 px-3 py-2 rounded-lg inline-block">
                Session: {sessionId.slice(-8)}...
              </div>
            </div>
          )}

          <div className="space-y-6">
            {messages.map((message) => (
              <div key={message.id} className="group">
                <div className={`flex items-start gap-4 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.type === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-800 text-white'
                  }`}>
                    {message.type === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  {/* Message content */}
                  <div className={`flex-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                    <div className={`inline-block max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
                        {message.content}
                      </div>
                    </div>
                    <div className={`text-xs text-gray-500 mt-1 px-2 ${
                      message.type === 'user' ? 'text-right' : 'text-left'
                    }`}>
                      {formatTimestamp(message.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Streaming message */}
            {currentStreamingMessage && (
              <div className="group">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-800 text-white">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <div className="inline-block max-w-[80%] bg-gray-100 text-gray-900 rounded-2xl px-4 py-3">
                      <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
                        {currentStreamingMessage}
                        <span className="inline-block w-2 h-5 bg-gray-600 animate-pulse ml-0.5"></span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

          </div>
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit}>
            <div className="relative flex items-center gap-3">
              <div className="flex-1">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Message InsightFlow..."
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-sm"
                  disabled={isLoading}
                />
              </div>
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="flex-shrink-0 w-10 h-10 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-full flex items-center justify-center transition-colors"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
            
          </form>
        </div>
      </div>
    </div>
  );
};