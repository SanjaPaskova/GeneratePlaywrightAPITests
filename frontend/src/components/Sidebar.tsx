import { Home, FileText, TestTube, BarChart3, Code2 } from 'lucide-react'
import { clsx } from 'clsx'

interface SidebarProps {
  currentStep: 'connect' | 'generate' | 'view-tests' | 'run' | 'reports'
  onStepChange: (step: 'connect' | 'generate' | 'view-tests' | 'run' | 'reports') => void
  apiSpec: any
  testsGenerated: boolean
  testRuns: any[]
}

export default function Sidebar({ currentStep, onStepChange, apiSpec, testsGenerated, testRuns }: SidebarProps) {
  const menuItems = [
    { id: 'connect' as const, icon: Home, label: 'Connect API', step: 1 },
    { id: 'generate' as const, icon: FileText, label: 'Generate Tests', step: 2, disabled: !apiSpec },
    { id: 'view-tests' as const, icon: Code2, label: 'View Tests', step: 3, disabled: !testsGenerated },
    { id: 'run' as const, icon: TestTube, label: 'Run Tests', step: 4, disabled: !testsGenerated },
    { id: 'reports' as const, icon: BarChart3, label: 'Reports', step: 5, disabled: testRuns.length === 0 },
  ]

  return (
    <aside className="w-64 glass-effect border-r border-dark-border flex flex-col">
      <div className="p-6 border-b border-dark-border">
        <h2 className="text-sm font-semibold text-dark-textMuted uppercase tracking-wider">
          Workflow
        </h2>
      </div>
      
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = currentStep === item.id
          const isDisabled = item.disabled
          
          return (
            <button
              key={`${item.id}-${item.step}`}
              onClick={() => !isDisabled && onStepChange(item.id)}
              disabled={isDisabled}
              className={clsx(
                'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all',
                'text-left',
                isActive
                  ? 'bg-gradient-to-r from-dark-primary/20 to-dark-accent/20 text-dark-text border border-dark-primary/50'
                  : 'text-dark-textMuted hover:text-dark-text hover:bg-dark-surfaceHover',
                isDisabled && 'opacity-50 cursor-not-allowed'
              )}
            >
              <Icon className={clsx(
                'w-5 h-5',
                isActive && 'text-dark-primary'
              )} />
              <div className="flex-1">
                <div className="font-medium">{item.label}</div>
                <div className="text-xs opacity-70">Step {item.step}</div>
              </div>
              {isActive && (
                <div className="w-2 h-2 rounded-full bg-dark-primary animate-pulse" />
              )}
            </button>
          )
        })}
      </nav>

      <div className="p-4 border-t border-dark-border">
        <div className="card p-4 bg-gradient-to-br from-dark-primary/10 to-dark-accent/10">
          <div className="text-xs text-dark-textMuted mb-2">Status</div>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-dark-textMuted">API Loaded</span>
              <span className={apiSpec ? 'text-dark-success' : 'text-dark-textMuted'}>
                {apiSpec ? '✓' : '○'}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-dark-textMuted">Tests Ready</span>
              <span className={testsGenerated ? 'text-dark-success' : 'text-dark-textMuted'}>
                {testsGenerated ? '✓' : '○'}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-dark-textMuted">Test Runs</span>
              <span className={testRuns.length > 0 ? 'text-dark-success' : 'text-dark-textMuted'}>
                {testRuns.length > 0 ? `${testRuns.length} runs` : '0 runs'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}

