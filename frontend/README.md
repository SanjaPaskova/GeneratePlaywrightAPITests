# GeneratePlaywrightAPITests - Frontend

Modern, dark-themed web interface for generating Playwright API tests from Swagger/OpenAPI specifications.

## Features

- 🎨 **Dark AI Theme** - Modern, sleek interface with AI aesthetics
- 🚀 **3-Step Workflow** - Connect → Generate → Run
- ⚡ **Real-time Progress** - Live updates during test generation and execution
- 🎯 **Smart Defaults** - Zero configuration needed for basic usage
- ⚙️ **Settings Panel** - Advanced configuration when needed

## Tech Stack

- **React 19** + **TypeScript**
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will open at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── steps/
│   │   │   ├── ConnectAPI.tsx      # Step 1: Load API spec
│   │   │   ├── GenerateTests.tsx   # Step 2: Generate tests
│   │   │   └── RunTests.tsx        # Step 3: Run tests
│   │   ├── Sidebar.tsx             # Navigation sidebar
│   │   ├── Workspace.tsx           # Main workspace container
│   │   └── SettingsPanel.tsx       # Settings panel
│   ├── App.tsx                     # Main app component
│   ├── main.tsx                    # Entry point
│   └── index.css                   # Global styles + Tailwind
├── index.html
└── package.json
```

## Next Steps

1. **Backend Integration** - Connect to FastAPI backend
2. **Real WebSocket** - Real-time test execution logs
3. **Test Preview** - Code editor for generated tests
4. **Reports Page** - Coverage and debug reports
5. **Test History** - Previous test runs

## Notes

Currently uses mock data for demonstration. Backend API integration needed for production use.


