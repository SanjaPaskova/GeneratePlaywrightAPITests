import { useState } from 'react'
import ConnectAPI from './steps/ConnectAPI'
import GenerateTests from './steps/GenerateTests'
import RunTests from './steps/RunTests'
import Reports from './steps/Reports'

import ViewTests from './steps/ViewTests'

interface WorkspaceProps {
  currentStep: 'connect' | 'generate' | 'view-tests' | 'run' | 'reports'
  onStepChange: (step: 'connect' | 'generate' | 'view-tests' | 'run' | 'reports') => void
  apiSpec: any
  onApiSpecLoaded: (spec: any) => void
  testsGenerated: boolean
  onTestsGenerated: (testCode: string, fileName: string) => void
  testRuns: any[]
  selectedRunId: string | null
  onSelectRun: (runId: string | null) => void
  onTestResults: (results: any) => void
  testCode: string | null
  testFileName: string
}

export default function Workspace({
  currentStep,
  onStepChange,
  apiSpec,
  onApiSpecLoaded,
  testsGenerated,
  onTestsGenerated,
  testRuns,
  selectedRunId,
  onSelectRun,
  onTestResults,
  testCode,
  testFileName,
}: WorkspaceProps) {
  return (
    <div className="flex-1 overflow-auto">
      {currentStep === 'connect' && (
        <ConnectAPI
          onApiSpecLoaded={(spec) => {
            onApiSpecLoaded(spec)
            onStepChange('generate')
          }}
        />
      )}
      
      {currentStep === 'generate' && (
        <GenerateTests
          apiSpec={apiSpec}
          onTestsGenerated={(code, fileName) => {
            onTestsGenerated(code, fileName)
          }}
          onViewTests={() => onStepChange('view-tests')}
        />
      )}
      
      {currentStep === 'view-tests' && (
        <ViewTests
          testCode={testCode}
          fileName={testFileName}
        />
      )}
      
      {currentStep === 'run' && (
        <RunTests
          onTestResults={onTestResults}
          testRuns={testRuns}
        />
      )}
      
      {currentStep === 'reports' && (
        <Reports 
          testRuns={testRuns}
          selectedRunId={selectedRunId}
          onSelectRun={onSelectRun}
        />
      )}
    </div>
  )
}

