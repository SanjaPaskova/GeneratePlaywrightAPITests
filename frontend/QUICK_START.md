# Quick Start Guide

## 🚀 Getting Started

1. **Navigate to frontend folder:**
   ```bash
   cd frontend
   ```

2. **Install dependencies (if not already done):**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   - The app should automatically open at `http://localhost:3000`
   - If not, manually navigate to that URL

## 🎨 Features

### Current Implementation
- ✅ Dark AI-themed interface
- ✅ 3-step workflow (Connect → Generate → Run)
- ✅ Sidebar navigation
- ✅ Settings panel
- ✅ Progress indicators
- ✅ Mock data for demonstration

### Next Steps (Backend Integration)
- Connect to Python backend API
- Real test generation
- Real test execution
- WebSocket for live logs
- Test preview/editor
- Reports and analytics

## 📝 Notes

- Currently uses **mock data** for demonstration
- Backend API integration needed for production
- All UI components are functional and styled
- Ready for backend connection

## 🐛 Troubleshooting

**Port already in use?**
- Change port in `vite.config.ts` or kill the process using port 3000

**Styles not loading?**
- Make sure Tailwind CSS is properly configured
- Check `tailwind.config.js` and `postcss.config.js`

**TypeScript errors?**
- Run `npm install` to ensure all types are installed
- Check `tsconfig.json` configuration


