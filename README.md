# GenerateAPITests Agent

This project automatically generates Playwright API tests from a Swagger/OpenAPI specification. It uses a schema-based approach (no API keys required) for realistic test data generation.

## Features
- Generates Playwright tests for all API endpoints
- Creates, retrieves, and deletes resources in correct order
- Uses OpenAPI schema to generate realistic test data
- No LLM/API key required (completely free)
- Tests run in serial mode so resource IDs are shared

## Quick Start

### 1. Set up Python virtual environment

**First time setup:**
```bash
# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

**Every time you work on this project:**
```bash
# Activate virtual environment before running Python scripts
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

You should see `(venv)` at the start of your terminal prompt when activated.

### 2. Install dependencies
```bash
# Make sure venv is activated first (see step 1)
pip install requests
npm install
npx playwright install
```

### 3. Generate Playwright tests

**Option A: Advanced Generator (Recommended)**
```bash
# Ensure venv is activated
python scripts/generate_tests_main_script.py
```

**Option B: Basic Generator**
```bash
# Ensure venv is activated
python scripts/generate_playwright_tests.py
```

Both options generate `tests/{api_name}.spec.ts` (generated output, not tracked by git), where `{api_name}` is derived from the API specification title.

### 4. Run the tests
```bash
npm run test
```
- View the report:
```bash
npx playwright show-report
```

## Configuration
Edit `config.json` to set your Swagger/OpenAPI URL and LLM provider:

**Free Mode (No API Key Required):**
```json
{
  "swagger_url": "https://petstore.swagger.io/v2/swagger.json",
  "llm_provider": "none",
  "model": "gpt-4o",
   "fallback_to_schema": true,
   "use_ai_for_tests": false
}
```

**With AI Agent (Requires API Key):**
```json
{
  "swagger_url": "https://petstore.swagger.io/v2/swagger.json",
  "llm_provider": "openai",
  "openai_api_key": "your-api-key-here",
  "model": "gpt-4o",
   "fallback_to_schema": true,
   "use_ai_for_tests": true
}
```

**Anthropic (Claude) Example:**
```json
{
   "swagger_url": "https://petstore.swagger.io/v2/swagger.json",
   "llm_provider": "anthropic",
   "anthropic_api_key": "your-api-key-here",
   "model": "claude-3.5",
   "fallback_to_schema": true,
   "use_ai_for_tests": true
}
```

Notes:
- Set `use_ai_for_tests` to `true` to enable AI-generated tests. If the AI client isn’t available or the provider package isn’t installed, the generator falls back to basic schema-based tests.
- Supported providers: `none`, `openai`, `anthropic`.
- Ensure you `pip install openai` or `pip install anthropic` when using AI.

## How it works
- The agent parses the OpenAPI spec and generates tests for each endpoint.
- For POST/PUT requests, it creates resources and stores their IDs.
- For GET/DELETE requests, it uses the stored IDs to test resource retrieval and deletion.
- Test data is generated from the schema, so no LLM or API key is needed.

## Scripts Available

### npm scripts
- **`npm run test`**: Run all Playwright tests
- **`npm run test:debug`**: Run tests in debug mode

### Python scripts
1. **`scripts/generate_tests_main_script.py`** – Advanced generator with optional AI
   ```bash
   python scripts/generate_tests_main_script.py
   ```
2. **`scripts/generate_playwright_tests.py`** – Basic schema-only generator
   ```bash
   python scripts/generate_playwright_tests.py
   ```
3. **`scripts/review_test_coverage.py`** – Coverage analysis and gap report
   ```bash
   python scripts/review_test_coverage.py
   ```
4. **`scripts/debug_test_results.py`** – Failure analysis and debug report
   ```bash
   python scripts/debug_test_results.py tests/{api_name}.spec.ts chromium
   ```

## Troubleshooting

### ModuleNotFoundError: No module named 'requests'
If you see this error, you need to activate the virtual environment first:
```bash
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```
Then install dependencies:
```bash
pip install requests
```

### Other common issues
- **No API key needed**: Set `"llm_provider": "none"` for free schema-based generation
- **Want AI-powered tests**: Add your OpenAI/Anthropic API key to `config.json`
- **Tests failing**: Check that your API endpoints are accessible and match the Swagger spec

## Outputs and Git Ignore
- Generated tests: `tests/` (ignored)
- Reports: `reports/`, `playwright-report/`, `test-results/` (ignored)
- Caches and deps: `node_modules/`, `__pycache__/`, virtualenvs (ignored)

If you previously committed any of these, untrack them:
```bash
git rm -r --cached tests/ reports/ playwright-report/ test-results/ node_modules/
git add .
git commit -m "chore: untrack generated outputs and deps"
```

## License
MIT
