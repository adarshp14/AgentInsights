import { useState } from 'react'
import { X, Save } from 'lucide-react'

interface SettingsModalProps {
  onClose: () => void
}

const SettingsModal = ({ onClose }: SettingsModalProps) => {
  const [model, setModel] = useState('gemini-1.5-pro')
  const [debugMode, setDebugMode] = useState(true)
  const [apiKey, setApiKey] = useState('')

  const handleSave = () => {
    localStorage.setItem('insightflow-settings', JSON.stringify({
      model,
      debugMode,
      apiKey
    }))
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full m-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Model Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Model
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="input"
            >
              <option value="gemini-1.5-pro">Gemini 1.5 Pro (Active)</option>
              <option value="gemini-pro">Gemini Pro</option>
              <option value="gpt-4" disabled>GPT-4 (Not configured)</option>
              <option value="claude-3" disabled>Claude 3 (Not configured)</option>
            </select>
          </div>
          
          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Google API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Configure in backend .env file..."
              className="input"
              disabled
            />
            <p className="text-xs text-gray-500 mt-1">
              API key is configured server-side for security
            </p>
          </div>
          
          {/* Debug Mode */}
          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Debug Mode
              </label>
              <p className="text-xs text-gray-500">
                Show detailed agent reasoning and performance metrics
              </p>
            </div>
            <button
              onClick={() => setDebugMode(!debugMode)}
              className={`
                relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                ${debugMode ? 'bg-primary-600' : 'bg-gray-200'}
              `}
            >
              <span
                className={`
                  inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                  ${debugMode ? 'translate-x-6' : 'translate-x-1'}
                `}
              />
            </button>
          </div>
        </div>
        
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={handleSave} className="btn-primary flex items-center space-x-2">
            <Save size={16} />
            <span>Save</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsModal