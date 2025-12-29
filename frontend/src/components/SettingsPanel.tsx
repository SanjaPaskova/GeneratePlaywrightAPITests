import { X } from 'lucide-react'

interface SettingsPanelProps {
  onClose: () => void
}

export default function SettingsPanel({ onClose }: SettingsPanelProps) {
  return (
    <div className="w-96 glass-effect border-l border-dark-border flex flex-col">
      <div className="p-6 border-b border-dark-border flex items-center justify-between">
        <h2 className="text-lg font-semibold text-dark-text">Settings</h2>
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-dark-surfaceHover transition-colors"
        >
          <X className="w-5 h-5 text-dark-textMuted" />
        </button>
      </div>
      
      <div className="flex-1 p-6 overflow-auto">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-dark-text mb-2">
              LLM Provider
            </label>
            <select className="input-field w-full">
              <option value="none">None (Schema-based)</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-text mb-2">
              API Key
            </label>
            <input
              type="password"
              placeholder="Enter API key"
              className="input-field w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-text mb-2">
              Model
            </label>
            <select className="input-field w-full">
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4">GPT-4</option>
              <option value="claude-3.5">Claude 3.5</option>
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            <input type="checkbox" id="useAI" className="rounded" />
            <label htmlFor="useAI" className="text-sm text-dark-text">
              Use AI for test generation
            </label>
          </div>
          
          <div className="flex items-center gap-2">
            <input type="checkbox" id="fallback" className="rounded" defaultChecked />
            <label htmlFor="fallback" className="text-sm text-dark-text">
              Fallback to schema
            </label>
          </div>
        </div>
      </div>
      
      <div className="p-6 border-t border-dark-border">
        <button className="btn-primary w-full">
          Save Settings
        </button>
      </div>
    </div>
  )
}


