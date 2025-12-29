# Frontend Development Plan
## GeneratePlaywrightAPITests - Web Interface

---

## 📋 Project Understanding

### Current State
- **Backend**: Python scripts that generate Playwright API tests from Swagger/OpenAPI specs
- **Workflow**: 
  1. User configures `config.json` with Swagger URL and LLM settings
  2. Python script fetches OpenAPI spec
  3. Script generates Playwright test files (`.spec.ts`)
  4. Tests are run via `npm run test`
  5. Reports generated via Playwright

### Key Features
- ✅ Schema-based test generation (free, no API keys)
- ✅ Optional AI-powered test generation (OpenAI/Anthropic)
- ✅ Test coverage analysis
- ✅ Test debugging and failure analysis
- ✅ Supports both Swagger 2.0 and OpenAPI 3.0

---

## 🎯 Frontend Goals

Create a modern, user-friendly web interface that:
1. **Simplifies configuration** - Visual config editor instead of editing JSON
2. **Visualizes API specs** - Show endpoints, methods, schemas
3. **Generates tests on-demand** - One-click test generation
4. **Runs and monitors tests** - Real-time test execution and results
5. **Shows reports** - Test coverage, debug reports, test results

---

## 🏗️ Architecture Overview

### Recommended Stack
- **Frontend Framework**: React + TypeScript (or Vue.js, or Next.js)
- **UI Library**: 
  - Material-UI / MUI (comprehensive components)
  - OR Tailwind CSS + shadcn/ui (modern, customizable)
  - OR Ant Design (enterprise-ready)
- **State Management**: React Query / TanStack Query (for API calls) + Zustand/Context (for UI state)
- **Build Tool**: Vite (fast, modern)
- **Backend API**: FastAPI (Python) or Express.js (Node.js) - to wrap existing Python scripts

### Architecture Pattern
```
┌─────────────────┐
│   React Frontend │
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│  Backend API    │
│  (Port 8000)    │
│  FastAPI/Express│
└────────┬────────┘
         │
         │ Subprocess/CLI
         │
┌────────▼────────┐
│  Python Scripts │
│  (Existing)     │
└─────────────────┘
```

---

## 📱 Pages & Features

### 1. **Dashboard / Home Page**
**Purpose**: Overview and quick actions

**Features**:
- Welcome message and project description
- Quick stats:
  - Last generated test count
  - Last test run status
  - API spec status
- Quick actions:
  - "Generate Tests" button
  - "Run Tests" button
  - "View Reports" button
- Recent activity feed

**Layout**:
```
┌─────────────────────────────────────┐
│  Header: Logo, Navigation          │
├─────────────────────────────────────┤
│  Hero: Welcome + Quick Actions      │
│  ┌──────────┐  ┌──────────┐        │
│  │ Generate │  │ Run Tests│        │
│  └──────────┘  └──────────┘        │
├─────────────────────────────────────┤
│  Stats Cards:                       │
│  [Tests] [Coverage] [Status]        │
├─────────────────────────────────────┤
│  Recent Activity                    │
└─────────────────────────────────────┘
```

---

### 2. **Configuration Page**
**Purpose**: Manage API and LLM settings

**Features**:
- **API Configuration Section**:
  - Swagger/OpenAPI URL input
  - URL validation and preview
  - "Load Spec" button to fetch and validate
  - Display spec info (title, version, base URL)
  
- **LLM Provider Selection**:
  - Radio buttons: None / OpenAI / Anthropic
  - Conditional fields based on selection:
    - OpenAI: API Key input, Model dropdown
    - Anthropic: API Key input, Model dropdown
  - "Test Connection" button
  
- **Generation Options**:
  - Toggle: "Use AI for tests"
  - Toggle: "Fallback to schema"
  - Model selection dropdown
  
- **Save & Load**:
  - "Save Configuration" button
  - "Reset to Defaults" button
  - Visual confirmation on save

**Layout**:
```
┌─────────────────────────────────────┐
│  Configuration                      │
├─────────────────────────────────────┤
│  API Settings                       │
│  ┌───────────────────────────────┐ │
│  │ Swagger URL: [____________]   │ │
│  │ [Load Spec] [Validate]       │ │
│  │ ✓ Spec loaded: Petstore API   │ │
│  └───────────────────────────────┘ │
├─────────────────────────────────────┤
│  LLM Provider                       │
│  ○ None  ● OpenAI  ○ Anthropic     │
│  ┌───────────────────────────────┐ │
│  │ API Key: [************]        │ │
│  │ Model: [gpt-4o ▼]             │ │
│  │ [Test Connection]              │ │
│  └───────────────────────────────┘ │
├─────────────────────────────────────┤
│  Options                            │
│  ☑ Use AI for tests                │
│  ☑ Fallback to schema              │
├─────────────────────────────────────┤
│  [Save Config] [Reset]              │
└─────────────────────────────────────┘
```

---

### 3. **API Spec Viewer**
**Purpose**: Visualize the loaded OpenAPI specification

**Features**:
- **Spec Overview**:
  - API title, version, description
  - Base URL, schemes
  - Server information
  
- **Endpoints List**:
  - Grouped by tags/categories
  - Filter by HTTP method (GET, POST, PUT, DELETE)
  - Search/filter endpoints
  - Expandable cards showing:
    - Path, method, summary
    - Parameters (query, path, body)
    - Request body schema
    - Response schemas
    - Example requests/responses
  
- **Schema Viewer**:
  - Expandable definitions/schemas
  - JSON schema visualization
  - Type information

**Layout**:
```
┌─────────────────────────────────────┐
│  API Specification                  │
├─────────────────────────────────────┤
│  Overview                           │
│  Title: Petstore API                │
│  Version: 1.0.0                     │
│  Base URL: https://petstore...      │
├─────────────────────────────────────┤
│  Filters: [All] [GET] [POST] [PUT] │
│  Search: [____________]             │
├─────────────────────────────────────┤
│  Endpoints                          │
│  ▼ Pet Operations                   │
│    ✓ POST /pet - Add new pet        │
│    ✓ GET /pet/{petId} - Get pet    │
│    ✓ PUT /pet - Update pet          │
│  ▼ Store Operations                 │
│    ...                              │
└─────────────────────────────────────┘
```

---

### 4. **Test Generation Page**
**Purpose**: Generate Playwright tests from the API spec

**Features**:
- **Generation Options**:
  - Select generation mode (Basic / AI-powered)
  - Select endpoints to include (checkboxes or "Select All")
  - Preview generation settings
  
- **Generation Process**:
  - "Generate Tests" button
  - Progress indicator (loading spinner)
  - Real-time log output (stdout from Python script)
  - Success/error messages
  
- **Generated Tests Preview**:
  - Code editor (Monaco/CodeMirror) showing generated `.spec.ts`
  - Syntax highlighting
  - Line numbers
  - Download button
  - "Regenerate" button

**Layout**:
```
┌─────────────────────────────────────┐
│  Generate Tests                     │
├─────────────────────────────────────┤
│  Options                            │
│  Mode: [Basic ▼]                    │
│  ☑ Include all endpoints            │
│  ☑ Pet operations                   │
│  ☐ Store operations                 │
├─────────────────────────────────────┤
│  [Generate Tests]                   │
│  ⏳ Generating... (3/15 endpoints)  │
│  ┌───────────────────────────────┐ │
│  │ > Loading spec...             │ │
│  │ > Generating tests...         │ │
│  │ > Writing file...             │ │
│  └───────────────────────────────┘ │
├─────────────────────────────────────┤
│  Generated Test File                │
│  ┌───────────────────────────────┐ │
│  │ 1  import { test, expect }... │ │
│  │ 2  const BASE_URL = '...'     │ │
│  │ 3  ...                        │ │
│  └───────────────────────────────┘ │
│  [Download] [Regenerate]            │
└─────────────────────────────────────┘
```

---

### 5. **Test Runner Page**
**Purpose**: Execute tests and view results

**Features**:
- **Run Configuration**:
  - Select test file(s) to run
  - Select browser(s): Chromium, Firefox, WebKit
  - Run mode: Headless / Headed / Debug
  - "Run Tests" button
  
- **Test Execution**:
  - Real-time test progress
  - Live log output
  - Test status indicators (running, passed, failed)
  - Cancel button
  
- **Results Display**:
  - Test summary (total, passed, failed, skipped)
  - Test list with status icons
  - Expandable test details:
    - Test name, duration
    - Assertions
    - Error messages (if failed)
    - Screenshots (if available)
  - "View Full Report" link

**Layout**:
```
┌─────────────────────────────────────┐
│  Run Tests                          │
├─────────────────────────────────────┤
│  Configuration                      │
│  Test File: [petstore.spec.ts ▼]   │
│  Browsers: ☑ Chromium ☐ Firefox    │
│  Mode: [Headless ▼]                 │
│  [Run Tests]                        │
├─────────────────────────────────────┤
│  Execution                          │
│  ⏳ Running... (5/20 tests)         │
│  ┌───────────────────────────────┐ │
│  │ ✓ POST /pet                   │ │
│  │ ✓ GET /pet/{id}               │ │
│  │ ✗ PUT /pet/{id}               │ │
│  │ ⏳ DELETE /pet/{id}           │ │
│  └───────────────────────────────┘ │
├─────────────────────────────────────┤
│  Results                            │
│  Total: 20 | Passed: 18 | Failed: 2│
│  ┌───────────────────────────────┐ │
│  │ ✗ PUT /pet/{id}               │ │
│  │   Error: Expected 200, got 404│ │
│  │   [View Details] [Screenshot] │ │
│  └───────────────────────────────┘ │
│  [View Full Report]                │
└─────────────────────────────────────┘
```

---

### 6. **Reports & Analytics Page**
**Purpose**: View test coverage, debug reports, and analytics

**Features**:
- **Test Coverage Report**:
  - Coverage percentage
  - Endpoints covered vs. total
  - Visual coverage chart (bar/pie)
  - Missing endpoints list
  - "Generate Coverage Report" button
  
- **Debug Report**:
  - Failed tests analysis
  - Error patterns
  - Suggestions for fixes
  - "Generate Debug Report" button
  
- **Test History**:
  - List of previous test runs
  - Date, status, duration
  - Link to detailed report
  - Download reports

**Layout**:
```
┌─────────────────────────────────────┐
│  Reports & Analytics                │
├─────────────────────────────────────┤
│  Test Coverage                      │
│  ┌───────────────────────────────┐ │
│  │ Coverage: 85%                  │ │
│  │ ████████████░░░░               │ │
│  │ Covered: 17/20 endpoints       │ │
│  │ Missing: /pet/findByStatus     │ │
│  └───────────────────────────────┘ │
│  [Generate Coverage Report]         │
├─────────────────────────────────────┤
│  Debug Report                       │
│  ┌───────────────────────────────┐ │
│  │ Failed Tests: 2                │ │
│  │ Common Error: 404 Not Found    │ │
│  │ Suggestion: Check resource IDs │ │
│  └───────────────────────────────┘ │
│  [Generate Debug Report]            │
├─────────────────────────────────────┤
│  Test History                       │
│  ┌───────────────────────────────┐ │
│  │ 2024-01-15 10:30 | ✓ 18/20    │ │
│  │ 2024-01-14 15:20 | ✗ 12/20    │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 🔌 Backend API Design

### Required Endpoints

#### Configuration
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `POST /api/config/validate` - Validate configuration

#### API Spec
- `POST /api/spec/load` - Load spec from URL
- `POST /api/spec/upload` - Upload spec file
- `GET /api/spec` - Get loaded spec
- `GET /api/spec/endpoints` - Get endpoints list

#### Test Generation
- `POST /api/tests/generate` - Generate tests
  - Body: `{ mode: "basic" | "ai", endpoints?: string[] }`
  - Returns: `{ file: string, content: string, count: number }`
- `GET /api/tests/list` - List generated test files
- `GET /api/tests/:filename` - Get test file content

#### Test Execution
- `POST /api/tests/run` - Run tests
  - Body: `{ file: string, browsers: string[], mode: string }`
  - Returns: WebSocket connection for real-time logs
- `GET /api/tests/results/:runId` - Get test results
- `GET /api/tests/results` - List all test runs

#### Reports
- `POST /api/reports/coverage` - Generate coverage report
- `POST /api/reports/debug` - Generate debug report
- `GET /api/reports/:type/:id` - Get report

---

## 🎨 UI/UX Considerations

### Design Principles
1. **Clean & Modern**: Minimal, professional interface
2. **Progressive Disclosure**: Show details on demand
3. **Real-time Feedback**: Loading states, progress indicators
4. **Error Handling**: Clear error messages with suggestions
5. **Responsive**: Works on desktop and tablet

### Color Scheme
- Primary: Blue (trust, technology)
- Success: Green
- Error: Red
- Warning: Orange
- Neutral: Gray scale

### Components Needed
- Navigation bar / Sidebar
- Cards / Panels
- Forms (inputs, selects, toggles)
- Code editor
- Progress bars / Spinners
- Tables / Lists
- Charts / Graphs
- Modals / Dialogs
- Toast notifications

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Set up frontend project (React + Vite + TypeScript)
- [ ] Set up backend API (FastAPI or Express)
- [ ] Create basic routing and navigation
- [ ] Design system / UI library setup
- [ ] Configuration page (basic)

### Phase 2: Core Features (Week 3-4)
- [ ] API spec loading and validation
- [ ] API spec viewer
- [ ] Test generation integration
- [ ] Generated tests preview
- [ ] Basic test runner

### Phase 3: Advanced Features (Week 5-6)
- [ ] Real-time test execution with WebSockets
- [ ] Test results visualization
- [ ] Coverage reports
- [ ] Debug reports
- [ ] Test history

### Phase 4: Polish (Week 7-8)
- [ ] Error handling and validation
- [ ] Loading states and animations
- [ ] Responsive design
- [ ] Documentation
- [ ] Testing and bug fixes

---

## 🛠️ Technical Decisions Needed

### 1. Backend Framework
**Option A: FastAPI (Python)**
- ✅ Same language as existing scripts
- ✅ Easy integration with Python scripts
- ✅ Automatic API docs
- ✅ Async support

**Option B: Express.js (Node.js)**
- ✅ JavaScript ecosystem
- ✅ Easy WebSocket support
- ❌ Need to call Python scripts via subprocess

**Recommendation**: FastAPI (better integration)

### 2. Frontend Framework
**Option A: React**
- ✅ Most popular, large ecosystem
- ✅ Many UI libraries available

**Option B: Next.js**
- ✅ Server-side rendering
- ✅ Built-in routing
- ✅ Better for production

**Option C: Vue.js**
- ✅ Simpler learning curve
- ✅ Good documentation

**Recommendation**: React + Vite (fast development)

### 3. Code Editor
**Option A: Monaco Editor** (VS Code editor)
- ✅ Full-featured
- ✅ Syntax highlighting
- ✅ Large bundle size

**Option B: CodeMirror**
- ✅ Lighter weight
- ✅ Good features
- ✅ Customizable

**Recommendation**: Monaco Editor (better UX)

### 4. Real-time Communication
- **WebSockets**: For test execution logs
- **Server-Sent Events (SSE)**: Alternative, simpler
- **Polling**: Fallback option

**Recommendation**: WebSockets (bidirectional)

---

## 📦 Dependencies Estimate

### Frontend
```json
{
  "react": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "@tanstack/react-query": "^5.0.0",
  "@monaco-editor/react": "^4.6.0",
  "@mui/material": "^5.14.0", // or tailwindcss
  "axios": "^1.6.0",
  "recharts": "^2.10.0" // for charts
}
```

### Backend (FastAPI)
```python
fastapi==0.104.0
uvicorn==0.24.0
websockets==12.0
python-multipart==0.0.6
pydantic==2.5.0
```

---

## 🔒 Security Considerations

1. **API Keys**: Never expose in frontend, store securely in backend
2. **File Uploads**: Validate file types and sizes
3. **URL Validation**: Sanitize and validate Swagger URLs
4. **CORS**: Configure properly for development and production
5. **Rate Limiting**: Prevent abuse of test generation

---

## 📝 Next Steps

1. **Review this plan** with stakeholders
2. **Choose tech stack** (React vs Vue, FastAPI vs Express)
3. **Set up project structure**
4. **Create wireframes/mockups** (optional but recommended)
5. **Start with Phase 1** implementation

---

## ❓ Questions to Consider

1. **Deployment**: Where will this be hosted? (Local, cloud, Docker?)
2. **Authentication**: Do we need user accounts/login?
3. **Multi-tenancy**: Single user or multiple users/projects?
4. **Persistence**: Store configs and history in database or files?
5. **File Management**: How to handle multiple test files/projects?

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Status**: Planning Phase



