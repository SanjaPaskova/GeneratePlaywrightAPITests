# Data Sources - Real vs Mock

## Current Implementation Status

### ✅ **REAL DATA** (Uses Your API)

#### 1. **API Loading (ConnectAPI)**
- **Status**: ✅ **REAL** - Actually fetches from the URL you provide
- **How it works**: Uses `axios.get(url)` to fetch the Swagger/OpenAPI spec
- **What happens when you change URL**:
  - ✅ Fetches the new API specification
  - ✅ Shows real endpoints count
  - ✅ Displays real API title and version
  - ✅ Works with any valid Swagger/OpenAPI URL

**Code Location**: `src/components/steps/ConnectAPI.tsx` (line 27)
```typescript
const response = await axios.get(url)  // Real API call!
const apiSpec = response.data
```

#### 2. **Test Generation (GenerateTests)**
- **Status**: ✅ **REAL** - Uses actual endpoints from your API spec
- **How it works**: Reads `apiSpec.paths` and generates tests for each endpoint
- **What happens when you change URL**:
  - ✅ Generates tests for the new API's endpoints
  - ✅ Uses real endpoint paths (POST, GET, PUT, DELETE)
  - ✅ Extracts real base URL from the spec
  - ✅ Uses real API title in test file name

**Code Location**: `src/components/steps/GenerateTests.tsx` (line 62)
```typescript
Object.entries(apiSpec.paths || {}).forEach(([path, methods]) => {
  // Generates tests based on REAL endpoints from your API
})
```

### ❌ **MOCK DATA** (Fake/Demo)

#### 3. **Test Execution (RunTests)**
- **Status**: ❌ **MOCK** - Doesn't actually run tests
- **How it works**: Shows hardcoded fake results after a delay
- **What happens when you change URL**:
  - ❌ Still shows same mock results
  - ❌ Doesn't actually execute the generated tests
  - ❌ Results are randomly varied but not real

**Code Location**: `src/components/steps/RunTests.tsx` (line 43)
```typescript
const mockResults = {
  total: 20,
  passed: 18,
  failed: 2,
  // ... hardcoded test results
}
```

---

## Summary

| Feature | Status | Uses Your API? |
|---------|--------|----------------|
| Load API Spec | ✅ Real | Yes - Fetches from your URL |
| Generate Tests | ✅ Real | Yes - Based on your API endpoints |
| Run Tests | ❌ Mock | No - Shows fake results |
| View Reports | ❌ Mock | No - Based on fake test results |

---

## What This Means

### ✅ **Works with Any API**
- Change the URL → Loads that API's spec
- Different API → Generates tests for that API
- Real endpoints → Real test code generated

### ❌ **Test Execution is Demo Only**
- Tests are generated but not actually executed
- Results are simulated for demonstration
- To run real tests, you need backend integration

---

## Example: Changing the URL

1. **Enter new URL**: `https://api.example.com/swagger.json`
2. **Click "Load API"** → ✅ Fetches real spec from that URL
3. **Generate Tests** → ✅ Creates tests for that API's endpoints
4. **View Tests** → ✅ Shows real generated code for that API
5. **Run Tests** → ❌ Still shows mock results (not real execution)

---

## Next Steps for Full Integration

To make test execution real, you would need:

1. **Backend API** (FastAPI/Express) that:
   - Accepts the generated test code
   - Executes Playwright tests
   - Returns real results

2. **Update RunTests component** to:
   - Send test code to backend
   - Receive real execution results
   - Display actual test outcomes

---

**Current State**: Frontend is ready and uses real API data for loading and generation. Test execution needs backend integration to be fully functional.



