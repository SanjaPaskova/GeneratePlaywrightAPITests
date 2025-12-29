import { useState } from 'react'
import { BarChart3, TrendingUp, AlertTriangle, CheckCircle2, XCircle, Clock, ChevronRight, History } from 'lucide-react'
import { clsx } from 'clsx'

interface ReportsProps {
  testRuns: any[]
  selectedRunId: string | null
  onSelectRun: (runId: string | null) => void
}

export default function Reports({ testRuns, selectedRunId, onSelectRun }: ReportsProps) {
  const selectedRun = testRuns.find(run => run.id === selectedRunId) || testRuns[0] || null

  if (testRuns.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-8">
        <div className="max-w-2xl w-full text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-dark-primary to-dark-accent flex items-center justify-center shadow-2xl">
              <BarChart3 className="w-10 h-10 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-dark-text">Reports</h2>
          <p className="text-dark-textMuted">
            Run tests first to view reports and analytics
          </p>
        </div>
      </div>
    )
  }

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  if (!selectedRun) {
    return null
  }

  const passRate = ((selectedRun.passed / selectedRun.total) * 100).toFixed(1)
  const failRate = ((selectedRun.failed / selectedRun.total) * 100).toFixed(1)

  // Calculate trends if we have multiple runs
  const previousRun = testRuns.length > 1 ? testRuns[1] : null
  const passRateChange = previousRun 
    ? ((selectedRun.passed / selectedRun.total) * 100) - ((previousRun.passed / previousRun.total) * 100)
    : 0

  return (
    <div className="h-full overflow-auto p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header with Run Selector */}
        <div className="flex items-center justify-between">
          <div className="text-center flex-1">
            <h2 className="text-3xl font-bold text-dark-text">Test Reports & Analytics</h2>
            <p className="text-dark-textMuted mt-1">
              Comprehensive analysis of your test execution
            </p>
          </div>
        </div>

        {/* Run History Sidebar */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Run History List */}
          <div className="lg:col-span-1">
            <div className="card">
              <div className="flex items-center gap-2 mb-4 pb-4 border-b border-dark-border">
                <History className="w-5 h-5 text-dark-primary" />
                <h3 className="font-semibold text-dark-text">Run History</h3>
                <span className="ml-auto text-xs text-dark-textMuted bg-dark-surface px-2 py-1 rounded">
                  {testRuns.length} runs
                </span>
              </div>
              
              <div className="space-y-2 max-h-[600px] overflow-y-auto custom-scrollbar">
                {testRuns.map((run) => {
                  const runPassRate = ((run.passed / run.total) * 100).toFixed(0)
                  const isSelected = run.id === selectedRunId
                  
                  return (
                    <button
                      key={run.id}
                      onClick={() => onSelectRun(run.id)}
                      className={clsx(
                        'w-full text-left p-3 rounded-lg border transition-all',
                        isSelected
                          ? 'bg-gradient-to-r from-dark-primary/20 to-dark-accent/20 border-dark-primary/50'
                          : 'bg-dark-surface border-dark-border hover:border-dark-primary/30 hover:bg-dark-surfaceHover'
                      )}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className={clsx(
                            'w-2 h-2 rounded-full',
                            isSelected ? 'bg-dark-primary' : 'bg-dark-textMuted'
                          )} />
                          <span className="font-medium text-dark-text">
                            Run {run.runNumber}
                          </span>
                        </div>
                        <span className={clsx(
                          'text-xs font-medium',
                          run.failed === 0 ? 'text-dark-success' : 'text-dark-error'
                        )}>
                          {runPassRate}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-dark-textMuted">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>{formatTime(run.timestamp)}</span>
                        </div>
                        <span>{formatDate(run.timestamp)}</span>
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-xs">
                        <span className="text-dark-success">✓ {run.passed}</span>
                        {run.failed > 0 && (
                          <span className="text-dark-error">✗ {run.failed}</span>
                        )}
                        <span className="text-dark-textMuted ml-auto">
                          {(run.duration / 1000).toFixed(1)}s
                        </span>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Main Report Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Run Header */}
            <div className="card bg-gradient-to-br from-dark-primary/10 to-dark-accent/10 border-dark-primary/30">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-dark-text mb-1">
                    Run {selectedRun.runNumber} Report
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-dark-textMuted">
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      <span>{formatDate(selectedRun.timestamp)}</span>
                    </div>
                    {passRateChange !== 0 && previousRun && (
                      <div className={clsx(
                        'flex items-center gap-1',
                        passRateChange > 0 ? 'text-dark-success' : 'text-dark-error'
                      )}>
                        <TrendingUp className={clsx('w-4 h-4', passRateChange < 0 && 'rotate-180')} />
                        <span>
                          {passRateChange > 0 ? '+' : ''}{passRateChange.toFixed(1)}% vs previous
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-dark-primary">{passRate}%</div>
                  <div className="text-xs text-dark-textMuted">Pass Rate</div>
                </div>
              </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="card text-center">
                <div className="text-3xl font-bold text-dark-text mb-2">{selectedRun.total}</div>
                <div className="text-sm text-dark-textMuted">Total Tests</div>
              </div>
              <div className="card text-center bg-dark-success/10 border-dark-success/30">
                <div className="text-3xl font-bold text-dark-success mb-2">{selectedRun.passed}</div>
                <div className="text-sm text-dark-textMuted">Passed</div>
                <div className="text-xs text-dark-textMuted mt-1">{passRate}%</div>
              </div>
              <div className="card text-center bg-dark-error/10 border-dark-error/30">
                <div className="text-3xl font-bold text-dark-error mb-2">{selectedRun.failed}</div>
                <div className="text-sm text-dark-textMuted">Failed</div>
                <div className="text-xs text-dark-textMuted mt-1">{failRate}%</div>
              </div>
              <div className="card text-center">
                <div className="text-3xl font-bold text-dark-text mb-2">
                  {(selectedRun.duration / 1000).toFixed(1)}s
                </div>
                <div className="text-sm text-dark-textMuted">Duration</div>
              </div>
            </div>

            {/* Pass Rate Visualization */}
            <div className="card">
              <h3 className="font-semibold text-dark-text mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-dark-primary" />
                Pass Rate
              </h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-dark-textMuted">Overall Success Rate</span>
                  <span className="font-medium text-dark-text">{passRate}%</span>
                </div>
                <div className="w-full bg-dark-surface rounded-full h-4 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-dark-success to-dark-primary transition-all duration-500"
                    style={{ width: `${passRate}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Test Breakdown */}
            <div className="card">
              <h3 className="font-semibold text-dark-text mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-dark-primary" />
                Test Breakdown
              </h3>
              <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
                {selectedRun.tests.map((test: any, index: number) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border ${
                      test.status === 'passed'
                        ? 'bg-dark-success/10 border-dark-success/30'
                        : 'bg-dark-error/10 border-dark-error/30'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {test.status === 'passed' ? (
                          <CheckCircle2 className="w-5 h-5 text-dark-success flex-shrink-0" />
                        ) : (
                          <XCircle className="w-5 h-5 text-dark-error flex-shrink-0" />
                        )}
                        <div>
                          <div className="font-medium text-dark-text">{test.name}</div>
                          {test.error && (
                            <div className="text-xs text-dark-error mt-1">{test.error}</div>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-dark-text">{test.duration}ms</div>
                        <div className="text-xs text-dark-textMuted">
                          {test.status === 'passed' ? 'Passed' : 'Failed'}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Insights */}
            <div className="card bg-gradient-to-br from-dark-primary/10 to-dark-accent/10 border-dark-primary/30">
              <h3 className="font-semibold text-dark-text mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-dark-warning" />
                Insights
              </h3>
              <div className="space-y-2 text-sm text-dark-textMuted">
                {selectedRun.failed > 0 ? (
                  <>
                    <p>• {selectedRun.failed} test(s) failed and may need attention</p>
                    <p>• Review failed tests above for error details</p>
                    <p>• Consider checking API endpoints and test data</p>
                  </>
                ) : (
                  <>
                    <p>• All tests passed successfully! 🎉</p>
                    <p>• Your API is working as expected</p>
                    <p>• Test coverage looks good</p>
                  </>
                )}
                {previousRun && (
                  <>
                    <p className="pt-2 border-t border-dark-border/50">
                      • Comparison with Run {previousRun.runNumber}: {
                        passRateChange > 0 
                          ? `Improved by ${passRateChange.toFixed(1)}%` 
                          : passRateChange < 0 
                          ? `Declined by ${Math.abs(passRateChange).toFixed(1)}%`
                          : 'No change'
                      }
                    </p>
                  </>
                )}
                <p>• Total execution time: {(selectedRun.duration / 1000).toFixed(2)} seconds</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
