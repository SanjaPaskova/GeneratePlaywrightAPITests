import { useState } from 'react'
import { Loader2, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react'
import axios from 'axios'

interface ConnectAPIProps {
  onApiSpecLoaded: (spec: any) => void
}

export default function ConnectAPI({ onApiSpecLoaded }: ConnectAPIProps) {
  const [url, setUrl] = useState('https://petstore.swagger.io/v2/swagger.json')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [spec, setSpec] = useState<any>(null)

  const handleLoad = async () => {
    if (!url.trim()) {
      setError('Please enter a Swagger/OpenAPI URL')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // In production, this would call the backend API
      // For now, we'll fetch directly (CORS permitting)
      const response = await axios.get(url)
      const apiSpec = response.data
      
      setSpec(apiSpec)
      setTimeout(() => {
        onApiSpecLoaded(apiSpec)
      }, 500)
    } catch (err: any) {
      setError(err.message || 'Failed to load API specification')
    } finally {
      setLoading(false)
    }
  }

  const handleQuickStart = () => {
    setUrl('https://petstore.swagger.io/v2/swagger.json')
    handleLoad()
  }

  return (
    <div className="h-full flex items-center justify-center p-8">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-dark-primary to-dark-accent flex items-center justify-center shadow-2xl">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-dark-text">
            Connect Your API
          </h2>
          <p className="text-dark-textMuted">
            Enter your Swagger/OpenAPI specification URL to get started
          </p>
        </div>

        {/* Input Card */}
        <div className="card space-y-6">
          <div>
            <label className="block text-sm font-medium text-dark-text mb-2">
              Swagger/OpenAPI URL
            </label>
            <div className="flex gap-3">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://api.example.com/swagger.json"
                className="input-field flex-1"
                onKeyDown={(e) => e.key === 'Enter' && handleLoad()}
              />
              <button
                onClick={handleLoad}
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Loading...
                  </>
                ) : (
                  'Load API'
                )}
              </button>
            </div>
          </div>

          {/* Quick Start */}
          <div className="pt-4 border-t border-dark-border">
            <p className="text-sm text-dark-textMuted mb-3">Or try our demo:</p>
            <button
              onClick={handleQuickStart}
              disabled={loading}
              className="btn-secondary w-full disabled:opacity-50"
            >
              Try Petstore Demo API
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-3 p-4 bg-dark-error/10 border border-dark-error/30 rounded-lg">
              <AlertCircle className="w-5 h-5 text-dark-error flex-shrink-0" />
              <p className="text-sm text-dark-error">{error}</p>
            </div>
          )}

          {/* Success Message */}
          {spec && !loading && (
            <div className="flex items-center gap-3 p-4 bg-dark-success/10 border border-dark-success/30 rounded-lg">
              <CheckCircle2 className="w-5 h-5 text-dark-success flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-dark-success">
                  API loaded successfully!
                </p>
                <p className="text-xs text-dark-textMuted mt-1">
                  {spec.info?.title || 'API'} - {Object.keys(spec.paths || {}).length} endpoints found
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card text-center">
            <div className="text-2xl font-bold text-dark-primary mb-1">
              {spec ? Object.keys(spec.paths || {}).length : '0'}
            </div>
            <div className="text-sm text-dark-textMuted">Endpoints</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-dark-accent mb-1">
              {spec ? (spec.info?.version || 'N/A') : 'N/A'}
            </div>
            <div className="text-sm text-dark-textMuted">API Version</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-dark-success mb-1">
              ✓
            </div>
            <div className="text-sm text-dark-textMuted">Ready</div>
          </div>
        </div>
      </div>
    </div>
  )
}



