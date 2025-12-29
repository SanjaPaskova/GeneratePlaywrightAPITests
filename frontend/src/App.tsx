import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Workspace from './components/Workspace'
import SettingsPanel from './components/SettingsPanel'
import { Settings } from 'lucide-react'

function App() {
  const [showSettings, setShowSettings] = useState(false)
  const [currentStep, setCurrentStep] = useState<'connect' | 'generate' | 'view-tests' | 'run' | 'reports'>('connect')
  const [apiSpec, setApiSpec] = useState<any>(null)
  const [testsGenerated, setTestsGenerated] = useState(false)
  const [testRuns, setTestRuns] = useState<any[]>([])
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const [testCode, setTestCode] = useState<string | null>(null)
  const [testFileName, setTestFileName] = useState('')

  return (
    <div className="flex h-screen overflow-hidden bg-dark-bg">
      <Sidebar 
        currentStep={currentStep}
        onStepChange={setCurrentStep}
        apiSpec={apiSpec}
        testsGenerated={testsGenerated}
        testRuns={testRuns}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="glass-effect border-b border-dark-border px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-dark-primary to-dark-accent flex items-center justify-center">
              <span className="text-xl font-bold text-white">AI</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-dark-text">API Pronouts</h1>
              <p className="text-sm text-dark-textMuted">AI-Powered API Test Generator</p>
            </div>
          </div>
          
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-lg hover:bg-dark-surfaceHover transition-colors"
            title="Settings"
          >
            <Settings className="w-5 h-5 text-dark-textMuted hover:text-dark-text" />
          </button>
        </header>

        {/* Main Workspace */}
        <Workspace
          currentStep={currentStep}
          onStepChange={setCurrentStep}
          apiSpec={apiSpec}
          onApiSpecLoaded={setApiSpec}
          testsGenerated={testsGenerated}
          onTestsGenerated={(code, fileName) => {
            setTestCode(code)
            setTestFileName(fileName)
            setTestsGenerated(true)
          }}
          testRuns={testRuns}
          selectedRunId={selectedRunId}
          onSelectRun={setSelectedRunId}
          onTestResults={(results) => {
            const newRun = {
              id: `run-${Date.now()}`,
              timestamp: new Date().toISOString(),
              runNumber: testRuns.length + 1,
              ...results
            }
            setTestRuns([newRun, ...testRuns])
            setSelectedRunId(newRun.id)
          }}
          testCode={testCode}
          testFileName={testFileName}
        />
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <SettingsPanel onClose={() => setShowSettings(false)} />
      )}
    </div>
  )
}

export default App

