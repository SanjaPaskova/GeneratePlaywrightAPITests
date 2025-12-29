import { useState } from 'react'
import { Loader2, CheckCircle2, AlertCircle, Sparkles, Code2 } from 'lucide-react'

interface GenerateTestsProps {
  apiSpec: any
  onTestsGenerated: (testCode: string, fileName: string) => void
  onViewTests?: () => void
}

export default function GenerateTests({ apiSpec, onTestsGenerated, onViewTests }: GenerateTestsProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [generated, setGenerated] = useState(false)
  const [testCount, setTestCount] = useState(0)
  const [progress, setProgress] = useState(0)
  const [testCode, setTestCode] = useState<string | null>(null)
  const [fileName, setFileName] = useState('')

  const handleGenerate = async () => {
    if (!apiSpec) {
      setError('Please load an API specification first')
      return
    }

    setLoading(true)
    setError(null)
    setProgress(0)

    // Simulate progress (in production, this would be real-time updates)
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval)
          return 90
        }
        return prev + 10
      })
    }, 300)

    try {
      // In production, this would call the backend API
      // POST /api/tests/generate
      await new Promise((resolve) => setTimeout(resolve, 3000))
      
      // Count endpoints
      const endpoints = Object.keys(apiSpec.paths || {}).length
      setTestCount(endpoints)
      setProgress(100)
      
      // Generate mock test code
      const apiName = apiSpec.info?.title?.toLowerCase().replace(/\s+/g, '_') || 'api'
      const generatedFileName = `${apiName}.spec.ts`
      setFileName(generatedFileName)
      
      // Generate sample test code based on API spec
      const baseUrl = apiSpec.servers?.[0]?.url || 
                     `${apiSpec.schemes?.[0] || 'https'}://${apiSpec.host || 'api.example.com'}${apiSpec.basePath || ''}`
      
      // Generate test code based on API spec
      const testCases: string[] = []
      
      Object.entries(apiSpec.paths || {}).slice(0, 15).forEach(([path, methods]: [string, any]) => {
        const resourceName = path.split('/').filter(p => p && !p.startsWith('{'))[0] || 'resource'
        
        if (methods.post && !path.includes('{')) {
          testCases.push(`  test('POST ${path}', async ({ request }) => {
    const response = await request.post(\`\${BASE_URL}${path}\`, {
      headers: { 'Content-Type': 'application/json' },
      data: { id: 1 },
    });
    expect(response.status()).toBe(200);
    if (response.ok()) {
      const body = await response.json();
      if (body.id !== undefined) {
        resourceIds['${resourceName}'] = body.id;
      }
    }
  });`)
        }
        
        if (methods.get) {
          const testPath = path.includes('{') ? path.replace(/\{[^}]+\}/g, '${resourceIds[\'' + resourceName + '\'] || 1}') : path
          testCases.push(`  test('GET ${path}', async ({ request }) => {
    const response = await request.get(\`\${BASE_URL}${testPath}\`);
    expect(response.status()).toBe(200);
  });`)
        }
        
        if (methods.put) {
          testCases.push(`  test('PUT ${path}', async ({ request }) => {
    const response = await request.put(\`\${BASE_URL}${path}\`, {
      headers: { 'Content-Type': 'application/json' },
      data: { id: resourceIds['${resourceName}'] || 1 },
    });
    expect(response.status()).toBe(200);
  });`)
        }
        
        if (methods.delete) {
          const testPath = path.includes('{') ? path.replace(/\{[^}]+\}/g, '${resourceIds[\'' + resourceName + '\'] || 1}') : path
          testCases.push(`  test('DELETE ${path}', async ({ request }) => {
    const response = await request.delete(\`\${BASE_URL}${testPath}\`);
    expect(response.status()).toBe(200);
  });`)
        }
      })
      
      const generatedCode = `import { test, expect } from '@playwright/test';

const BASE_URL = '${baseUrl}';

let resourceIds: Record<string, any> = {};

test.describe('${(apiSpec.info?.title || 'API').replace(/'/g, "\\'")} - API Tests', () => {
${testCases.join('\n\n')}
});`
      
      setTestCode(generatedCode)
      setGenerated(true)
      
      setTimeout(() => {
        onTestsGenerated(generatedCode, generatedFileName)
      }, 1000)
    } catch (err: any) {
      setError(err.message || 'Failed to generate tests')
      clearInterval(interval)
    } finally {
      setLoading(false)
    }
  }

  const endpoints = apiSpec ? Object.keys(apiSpec.paths || {}).length : 0

  return (
    <div className="h-full flex items-center justify-center p-8">
      <div className="max-w-3xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-dark-primary to-dark-accent flex items-center justify-center shadow-2xl">
              <Code2 className="w-10 h-10 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-dark-text">
            Generate Tests
          </h2>
          <p className="text-dark-textMuted">
            Generate Playwright API tests from your OpenAPI specification
          </p>
        </div>

        {/* API Info Card */}
        {apiSpec && (
          <div className="card bg-gradient-to-br from-dark-primary/10 to-dark-accent/10 border-dark-primary/30">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-dark-text mb-1">
                  {apiSpec.info?.title || 'API'}
                </h3>
                <p className="text-sm text-dark-textMuted">
                  {endpoints} endpoints • {apiSpec.info?.version || 'N/A'}
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-dark-primary">{endpoints}</div>
                <div className="text-xs text-dark-textMuted">Endpoints</div>
              </div>
            </div>
          </div>
        )}

        {/* Generation Card */}
        <div className="card space-y-6">
          {!generated ? (
            <>
              <div>
                <h3 className="font-semibold text-dark-text mb-4">
                  Generation Options
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 bg-dark-surface rounded-lg">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-dark-text">
                        Schema-based generation (Recommended)
                      </div>
                      <div className="text-xs text-dark-textMuted">
                        Fast, free, no API keys required
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-dark-surface rounded-lg opacity-50">
                    <input type="checkbox" disabled className="rounded" />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-dark-textMuted">
                        AI-powered generation
                      </div>
                      <div className="text-xs text-dark-textMuted">
                        Configure in Settings
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Progress */}
              {loading && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-dark-textMuted">Generating tests...</span>
                    <span className="text-dark-primary font-medium">{progress}%</span>
                  </div>
                  <div className="w-full bg-dark-surface rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-dark-primary to-dark-accent transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={loading || !apiSpec}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating Tests...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Generate Tests
                  </>
                )}
              </button>
            </>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-dark-success/10 border border-dark-success/30 rounded-lg">
                <CheckCircle2 className="w-5 h-5 text-dark-success flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-dark-success">
                    Tests generated successfully!
                  </p>
                  <p className="text-xs text-dark-textMuted mt-1">
                    {testCount} test cases created
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setGenerated(false)
                    setProgress(0)
                    setTestCode(null)
                  }}
                  className="btn-secondary flex-1"
                >
                  Regenerate Tests
                </button>
                <button
                  onClick={() => {
                    if (testCode) {
                      onTestsGenerated(testCode, fileName)
                      onViewTests?.()
                    }
                  }}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  <Code2 className="w-4 h-4" />
                  View Tests
                </button>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-3 p-4 bg-dark-error/10 border border-dark-error/30 rounded-lg">
              <AlertCircle className="w-5 h-5 text-dark-error flex-shrink-0" />
              <p className="text-sm text-dark-error">{error}</p>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="card bg-dark-surface/50">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-dark-primary flex-shrink-0 mt-0.5" />
            <div className="text-sm text-dark-textMuted">
              <p className="font-medium text-dark-text mb-1">How it works</p>
              <p>
                Our AI analyzes your API specification and generates comprehensive Playwright tests
                that cover all endpoints with proper test data and assertions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

