import { useState } from 'react'
import { Loader2, CheckCircle2, XCircle, Play, AlertCircle } from 'lucide-react'

interface RunTestsProps {
  onTestResults: (results: any) => void
  testRuns: any[]
}

export default function RunTests({ onTestResults, testRuns }: RunTestsProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<any>(null)
  const [progress, setProgress] = useState(0)

  const handleRun = async () => {
    setLoading(true)
    setError(null)
    setProgress(0)

    // Simulate progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval)
          return 90
        }
        return prev + Math.random() * 15
      })
    }, 500)

    try {
      // In production, this would call the backend API
      // POST /api/tests/run
      await new Promise((resolve) => setTimeout(resolve, 4000))
      
      // Mock results - expanded list for better visibility
      // Add some variation to make runs different
      const randomVariation = Math.random() * 0.1 - 0.05 // -5% to +5%
      const basePassed = 18
      const passed = Math.max(0, Math.min(20, Math.round(basePassed + (randomVariation * 20))))
      const failed = 20 - passed
      
      const mockResults = {
        total: 20,
        passed: passed,
        failed: failed,
        skipped: 0,
        duration: 4500 + Math.random() * 1000,
        tests: [
          { name: 'POST /pet', status: 'passed', duration: 234 },
          { name: 'GET /pet/{petId}', status: 'passed', duration: 156 },
          { name: 'PUT /pet', status: 'failed', duration: 189, error: 'Expected 200, got 404' },
          { name: 'DELETE /pet/{petId}', status: 'passed', duration: 145 },
          { name: 'GET /pet/findByStatus', status: 'failed', duration: 203, error: 'Timeout after 2000ms' },
          { name: 'POST /store/order', status: 'passed', duration: 178 },
          { name: 'GET /store/order/{orderId}', status: 'passed', duration: 134 },
          { name: 'DELETE /store/order/{orderId}', status: 'passed', duration: 112 },
          { name: 'GET /store/inventory', status: 'passed', duration: 198 },
          { name: 'POST /user', status: 'passed', duration: 167 },
          { name: 'GET /user/{username}', status: 'passed', duration: 145 },
          { name: 'PUT /user/{username}', status: 'passed', duration: 156 },
          { name: 'DELETE /user/{username}', status: 'passed', duration: 123 },
          { name: 'POST /user/createWithArray', status: 'passed', duration: 234 },
          { name: 'POST /user/createWithList', status: 'passed', duration: 245 },
          { name: 'GET /user/login', status: 'passed', duration: 189 },
          { name: 'GET /user/logout', status: 'passed', duration: 134 },
          { name: 'GET /pet/findByTags', status: 'passed', duration: 167 },
          { name: 'POST /pet/{petId}/uploadImage', status: 'passed', duration: 198 },
          { name: 'PUT /pet/{petId}', status: 'passed', duration: 156 },
        ]
      }
      
      setProgress(100)
      setResults(mockResults)
      onTestResults(mockResults)
    } catch (err: any) {
      setError(err.message || 'Failed to run tests')
      clearInterval(interval)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex items-center justify-center p-8">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-dark-primary to-dark-accent flex items-center justify-center shadow-2xl">
              <Play className="w-10 h-10 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-dark-text">
            Run Tests
          </h2>
          <p className="text-dark-textMuted">
            Execute your generated Playwright tests and view results
          </p>
        </div>

        {/* Run Card */}
        <div className="card space-y-6">
          {!results ? (
            <>
              <div>
                <h3 className="font-semibold text-dark-text mb-4">
                  Test Configuration
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-dark-surface rounded-lg">
                    <span className="text-sm text-dark-text">Browser</span>
                    <span className="text-sm font-medium text-dark-textMuted">Chromium (Headless)</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-dark-surface rounded-lg">
                    <span className="text-sm text-dark-text">Test File</span>
                    <span className="text-sm font-medium text-dark-textMuted">petstore.spec.ts</span>
                  </div>
                </div>
              </div>

              {/* Progress */}
              {loading && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-dark-textMuted">Running tests...</span>
                    <span className="text-dark-primary font-medium">{Math.round(progress)}%</span>
                  </div>
                  <div className="w-full bg-dark-surface rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-dark-primary to-dark-accent transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}

              <button
                onClick={handleRun}
                disabled={loading}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Running Tests...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Run Tests
                  </>
                )}
              </button>
            </>
          ) : (
            <div className="space-y-6">
              {/* Summary */}
              <div className="grid grid-cols-4 gap-4">
                <div className="card text-center bg-dark-surface/50">
                  <div className="text-2xl font-bold text-dark-text mb-1">{results.total}</div>
                  <div className="text-xs text-dark-textMuted">Total</div>
                </div>
                <div className="card text-center bg-dark-success/10 border-dark-success/30">
                  <div className="text-2xl font-bold text-dark-success mb-1">{results.passed}</div>
                  <div className="text-xs text-dark-textMuted">Passed</div>
                </div>
                <div className="card text-center bg-dark-error/10 border-dark-error/30">
                  <div className="text-2xl font-bold text-dark-error mb-1">{results.failed}</div>
                  <div className="text-xs text-dark-textMuted">Failed</div>
                </div>
                <div className="card text-center bg-dark-surface/50">
                  <div className="text-2xl font-bold text-dark-text mb-1">
                    {(results.duration / 1000).toFixed(1)}s
                  </div>
                  <div className="text-xs text-dark-textMuted">Duration</div>
                </div>
              </div>

              {/* Test Results */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-dark-text">
                    Test Results
                  </h3>
                  <span className="text-sm text-dark-textMuted">
                    {results.tests?.length || 0} tests
                  </span>
                </div>
                <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar border border-dark-border rounded-lg p-2 bg-dark-surface/30">
                  {results.tests && results.tests.length > 0 ? (
                    results.tests.map((test: any, index: number) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border transition-all hover:scale-[1.01] ${
                        test.status === 'passed'
                          ? 'bg-dark-success/10 border-dark-success/30 hover:bg-dark-success/15'
                          : 'bg-dark-error/10 border-dark-error/30 hover:bg-dark-error/15'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          {test.status === 'passed' ? (
                            <CheckCircle2 className="w-5 h-5 text-dark-success flex-shrink-0" />
                          ) : (
                            <XCircle className="w-5 h-5 text-dark-error flex-shrink-0" />
                          )}
                          <span className="font-medium text-dark-text truncate">{test.name}</span>
                        </div>
                        <span className="text-xs text-dark-textMuted ml-2 flex-shrink-0">{test.duration}ms</span>
                      </div>
                      {test.error && (
                        <div className="mt-2 p-2 bg-dark-error/20 rounded text-xs text-dark-error break-words">
                          {test.error}
                        </div>
                      )}
                    </div>
                    ))
                  ) : (
                    <div className="p-8 text-center text-dark-textMuted">
                      <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p>No test results available</p>
                    </div>
                  )}
                </div>
              </div>

              <button
                onClick={() => {
                  setResults(null)
                  setProgress(0)
                }}
                className="btn-secondary w-full"
              >
                Run Again
              </button>
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
      </div>
    </div>
  )
}

