import { useState, useMemo } from 'react'
import { Code2, Download, Copy, CheckCircle2, Eye, EyeOff, FileText } from 'lucide-react'

interface ViewTestsProps {
  testCode: string | null
  fileName: string
}

export default function ViewTests({ testCode, fileName }: ViewTestsProps) {
  const [copied, setCopied] = useState(false)
  const [showLineNumbers, setShowLineNumbers] = useState(true)
  const [activeTab, setActiveTab] = useState<'typescript' | 'gherkin'>('typescript')

  // Mock test code if none provided
  const code = testCode || `import { test, expect } from '@playwright/test';

const BASE_URL = 'https://petstore.swagger.io/v2';

let resourceIds: Record<string, any> = {};

test.describe('Swagger Petstore - API Tests', () => {
  test('POST /pet', async ({ request }) => {
    const response = await request.post(\`\${BASE_URL}/pet\`, {
      headers: {
        'Content-Type': 'application/json',
      },
      data: { 
        id: 1,
        name: 'Test Pet',
        status: 'available'
      },
    });
    
    expect(response.status()).toBe(200);
    
    if (response.ok()) {
      const body = await response.json();
      if (body.id !== undefined) {
        resourceIds['pet'] = body.id;
      }
    }
  });

  test('GET /pet/{petId}', async ({ request }) => {
    const response = await request.get(\`\${BASE_URL}/pet/\${resourceIds['pet'] || 1}\`);
    expect(response.status()).toBe(200);
  });

  test('PUT /pet', async ({ request }) => {
    const response = await request.put(\`\${BASE_URL}/pet\`, {
      headers: {
        'Content-Type': 'application/json',
      },
      data: { 
        id: resourceIds['pet'] || 1,
        name: 'Updated Pet',
        status: 'sold'
      },
    });
    expect(response.status()).toBe(200);
  });

  test('DELETE /pet/{petId}', async ({ request }) => {
    const response = await request.delete(\`\${BASE_URL}/pet/\${resourceIds['pet'] || 1}\`);
    expect(response.status()).toBe(200);
  });
});`

  const handleCopy = async () => {
    await navigator.clipboard.writeText(currentCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const extension = activeTab === 'typescript' ? '.spec.ts' : '.feature'
    const mimeType = activeTab === 'typescript' ? 'text/typescript' : 'text/plain'
    const blob = new Blob([currentCode], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = (fileName || 'tests').replace('.spec.ts', '') + extension
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Convert TypeScript tests to Gherkin format
  const gherkinCode = useMemo(() => {
    if (!code) return ''
    
    const lines = code.split('\n')
    let gherkin = ''
    let currentFeature = ''
    let scenarios: string[] = []
    
    // Extract feature name from describe
    const describeMatch = code.match(/test\.describe\(['"]([^'"]+)['"]/)
    if (describeMatch) {
      currentFeature = describeMatch[1]
    }
    
    // Extract all test cases
    const testMatches = [...code.matchAll(/test\(['"]([^'"]+)['"]/g)]
    
    testMatches.forEach((match) => {
      const testName = match[1]
      const parts = testName.split(' ')
      const method = parts[0]
      const path = parts.slice(1).join(' ')
      
      let scenario = `  Scenario: ${testName}\n`
      
      // Extract resource name from path
      const resourceMatch = path.match(/\/(\w+)/)
      const resourceName = resourceMatch ? resourceMatch[1] : 'resource'
      
      if (method === 'POST') {
        scenario += `    Given I want to create a new ${resourceName}\n`
        scenario += `    When I send a POST request to "${path}" with valid data\n`
        scenario += `    Then the response status should be 200\n`
        scenario += `    And the ${resourceName} should be created successfully\n`
      } else if (method === 'GET') {
        scenario += `    Given a ${resourceName} exists\n`
        scenario += `    When I send a GET request to "${path}"\n`
        scenario += `    Then the response status should be 200\n`
        scenario += `    And the ${resourceName} data should be returned\n`
      } else if (method === 'PUT') {
        scenario += `    Given a ${resourceName} exists\n`
        scenario += `    When I send a PUT request to "${path}" with updated data\n`
        scenario += `    Then the response status should be 200\n`
        scenario += `    And the ${resourceName} should be updated successfully\n`
      } else if (method === 'DELETE') {
        scenario += `    Given a ${resourceName} exists\n`
        scenario += `    When I send a DELETE request to "${path}"\n`
        scenario += `    Then the response status should be 200\n`
        scenario += `    And the ${resourceName} should be deleted successfully\n`
      } else {
        scenario += `    Given the API endpoint "${path}" is available\n`
        scenario += `    When I send a ${method} request to "${path}"\n`
        scenario += `    Then the response status should be 200\n`
        scenario += `    And the request should be processed successfully\n`
      }
      
      scenarios.push(scenario)
    })
    
    // Build final Gherkin
    gherkin = `Feature: ${currentFeature || 'API Tests'}\n`
    gherkin += `  As a developer or tester\n`
    gherkin += `  I want to verify API endpoints work correctly\n`
    gherkin += `  So that I can ensure the API meets requirements\n\n`
    gherkin += scenarios.join('\n')
    
    return gherkin || `Feature: API Tests
  As a developer or tester
  I want to verify API endpoints work correctly
  So that I can ensure the API meets requirements

  Scenario: Create a new resource
    Given I want to create a new resource
    When I send a POST request with valid data
    Then the response status should be 200
    And the resource should be created successfully

  Scenario: Retrieve an existing resource
    Given a resource exists
    When I send a GET request to retrieve it
    Then the response status should be 200
    And the resource data should be returned

  Scenario: Update an existing resource
    Given a resource exists
    When I send a PUT request to update it
    Then the response status should be 200
    And the resource should be updated successfully

  Scenario: Delete an existing resource
    Given a resource exists
    When I send a DELETE request to remove it
    Then the response status should be 200
    And the resource should be deleted successfully`
  }, [code])
  
  const lines = (activeTab === 'typescript' ? code : gherkinCode).split('\n')
  const currentCode = activeTab === 'typescript' ? code : gherkinCode

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-dark-primary to-dark-accent flex items-center justify-center">
                <Code2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-dark-text">Generated Test Code</h2>
                <p className="text-sm text-dark-textMuted">
                  {activeTab === 'typescript' ? (fileName || 'tests.spec.ts') : (fileName?.replace('.spec.ts', '.feature') || 'tests.feature')}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowLineNumbers(!showLineNumbers)}
                className="btn-secondary flex items-center gap-2"
                title={showLineNumbers ? 'Hide line numbers' : 'Show line numbers'}
              >
                {showLineNumbers ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                Lines
              </button>
              <button
                onClick={handleCopy}
                className="btn-secondary flex items-center gap-2"
                title="Copy to clipboard"
              >
                {copied ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-dark-success" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    Copy
                  </>
                )}
              </button>
              <button
                onClick={handleDownload}
                className="btn-primary flex items-center gap-2"
                title="Download file"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-dark-border">
            <button
              onClick={() => setActiveTab('typescript')}
              className={activeTab === 'typescript' 
                ? 'px-4 py-2 border-b-2 border-dark-primary text-dark-text font-medium'
                : 'px-4 py-2 text-dark-textMuted hover:text-dark-text'}
            >
              <div className="flex items-center gap-2">
                <Code2 className="w-4 h-4" />
                TypeScript
              </div>
            </button>
            <button
              onClick={() => setActiveTab('gherkin')}
              className={activeTab === 'gherkin' 
                ? 'px-4 py-2 border-b-2 border-dark-primary text-dark-text font-medium'
                : 'px-4 py-2 text-dark-textMuted hover:text-dark-text'}
            >
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Gherkin (BDD)
              </div>
            </button>
          </div>

          {/* Code Editor */}
          <div className="card p-0 overflow-hidden">
            <div className="bg-dark-surface border-b border-dark-border px-4 py-2 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-dark-textMuted">
                {activeTab === 'typescript' ? (
                  <>
                    <Code2 className="w-4 h-4" />
                    <span>TypeScript</span>
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4" />
                    <span>Gherkin (BDD Format)</span>
                  </>
                )}
                <span className="text-dark-textMuted/50">•</span>
                <span>{lines.length} lines</span>
                <span className="text-dark-textMuted/50">•</span>
                <span>{currentCode.length} characters</span>
              </div>
            </div>
            
            <div className="relative">
              <pre className="p-4 overflow-x-auto bg-dark-bg text-sm">
                <code className="text-dark-text font-mono">
                  {lines.map((line, index) => (
                    <div key={index} className="flex hover:bg-dark-surface/30 transition-colors">
                      {showLineNumbers && (
                        <span className="text-dark-textMuted/50 pr-4 text-right select-none min-w-[3rem]">
                          {index + 1}
                        </span>
                      )}
                      <span className="flex-1">
                        {line || '\u00A0'}
                      </span>
                    </div>
                  ))}
                </code>
              </pre>
            </div>
          </div>

          {/* Info */}
          <div className="card bg-dark-surface/50">
            <div className="flex items-start gap-3">
              {activeTab === 'typescript' ? (
                <>
                  <Code2 className="w-5 h-5 text-dark-primary flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-dark-textMuted">
                    <p className="font-medium text-dark-text mb-1">About this test file</p>
                    <p>
                      This is the generated Playwright test file in TypeScript. You can copy it, download it, or use it directly in your project.
                      The tests are ready to run with <code className="text-dark-primary">npm run test</code>.
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5 text-dark-primary flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-dark-textMuted">
                    <p className="font-medium text-dark-text mb-1">About Gherkin (BDD) Format</p>
                    <p>
                      This is the same test suite in Gherkin format - a human-readable, business-friendly language for describing tests.
                      Perfect for non-technical stakeholders to understand what the tests do. Gherkin uses keywords like <strong>Given</strong>, <strong>When</strong>, and <strong>Then</strong> to describe test scenarios in plain English.
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

