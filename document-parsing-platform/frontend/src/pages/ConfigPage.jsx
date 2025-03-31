import { useState } from 'react'
import { FaSave, FaSpinner } from 'react-icons/fa'

const providers = [
  { id: 'google-ai', name: 'Google AI Studio' },
  { id: 'awan', name: 'Awan LLM' },
  { id: 'ollama', name: 'Ollama (Local)' },
  { id: 'openrouter', name: 'OpenRouter' },
  { id: 'togetherai', name: 'TogetherAI' },
  { id: 'litellm', name: 'LiteLLM' },
  { id: 'lmstudio', name: 'LMStudio' }
]

export default function ConfigPage() {
  const [selectedProvider, setSelectedProvider] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [localPath, setLocalPath] = useState('')
  const [modelParams, setModelParams] = useState({
    temperature: 0.7,
    maxTokens: 2048,
    topP: 0.9
  })
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    setIsSaving(true)
    try {
      // TODO: Implement actual save logic
      await new Promise(resolve => setTimeout(resolve, 1500))
      alert('Configuration saved successfully!')
    } catch (error) {
      console.error('Save failed:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const isLocalProvider = selectedProvider === 'ollama' || selectedProvider === 'lmstudio'

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">LLM Configuration</h1>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Provider
            </label>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Select a provider</option>
              {providers.map((provider) => (
                <option key={provider.id} value={provider.id}>
                  {provider.name}
                </option>
              ))}
            </select>
          </div>

          {selectedProvider && !isLocalProvider && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your API key"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          )}

          {isLocalProvider && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Local Model Path
              </label>
              <input
                type="text"
                value={localPath}
                onChange={(e) => setLocalPath(e.target.value)}
                placeholder="Enter model path (e.g. /models/llama2)"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          )}

          {selectedProvider && (
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h3 className="font-medium text-gray-700">Model Parameters</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Temperature: {modelParams.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={modelParams.temperature}
                  onChange={(e) => setModelParams({...modelParams, temperature: parseFloat(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Tokens: {modelParams.maxTokens}
                </label>
                <input
                  type="range"
                  min="256"
                  max="4096"
                  step="256"
                  value={modelParams.maxTokens}
                  onChange={(e) => setModelParams({...modelParams, maxTokens: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Top P: {modelParams.topP}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={modelParams.topP}
                  onChange={(e) => setModelParams({...modelParams, topP: parseFloat(e.target.value)})}
                  className="w-full"
                />
              </div>
            </div>
          )}
        </div>

        <div className="mt-6">
          <button
            onClick={handleSave}
            disabled={!selectedProvider || isSaving}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
              !selectedProvider || isSaving
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isSaving ? (
              <span className="flex items-center">
                <FaSpinner className="animate-spin mr-2" />
                Saving...
              </span>
            ) : (
              <span className="flex items-center">
                <FaSave className="mr-2" />
                Save Configuration
              </span>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}