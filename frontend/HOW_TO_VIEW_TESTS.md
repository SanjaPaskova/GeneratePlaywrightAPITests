# How to View Generated Tests

## Overview
After generating tests, you can now view the complete generated test code in a beautiful code viewer!

## How to Access

### Method 1: From Generate Tests Page
1. **Generate Tests** → Click "Generate Tests" button
2. After generation completes, click **"View Tests"** button
3. You'll see the full generated test code

### Method 2: From Sidebar
1. After generating tests, go to **Sidebar**
2. Click **"View Tests"** (becomes available after generation)
3. View the complete test code

## Features in View Tests Page

### Code Display
- ✅ **Syntax Highlighting** - TypeScript/JavaScript syntax
- ✅ **Line Numbers** - Toggle on/off with "Lines" button
- ✅ **Full Code** - Complete generated `.spec.ts` file
- ✅ **File Info** - Shows filename, line count, character count

### Actions Available
- 📋 **Copy** - Copy entire test code to clipboard
- 💾 **Download** - Download as `.spec.ts` file
- 👁️ **Toggle Line Numbers** - Show/hide line numbers

## What You'll See

The generated test code includes:
- Import statements for Playwright
- BASE_URL configuration
- Resource ID tracking
- Test describe block
- Individual test cases for each endpoint:
  - POST requests (create resources)
  - GET requests (retrieve resources)
  - PUT requests (update resources)
  - DELETE requests (remove resources)

## Example Generated Code Structure

```typescript
import { test, expect } from '@playwright/test';

const BASE_URL = 'https://api.example.com';

let resourceIds: Record<string, any> = {};

test.describe('API Name - API Tests', () => {
  test('POST /endpoint', async ({ request }) => {
    // Test code...
  });
  
  test('GET /endpoint/{id}', async ({ request }) => {
    // Test code...
  });
  
  // More tests...
});
```

## Next Steps

After viewing the tests:
1. **Copy** the code to use in your project
2. **Download** the file to save locally
3. **Run Tests** to execute them
4. **View Reports** to see results

---

**Note**: The generated code is based on your OpenAPI specification and includes proper test structure, assertions, and resource management.


