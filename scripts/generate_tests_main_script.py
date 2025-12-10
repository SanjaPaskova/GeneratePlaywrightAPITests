# Main test generation script
# Generates Playwright API tests from Swagger/OpenAPI specs (optional LLM)

import requests
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Get project root (one level up from scripts/)
project_root = Path(__file__).parent.parent

# Add project root to Python path BEFORE importing scripts module
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import config_loader (this will work from any directory)
from scripts.config_loader import load_config, get_swagger_url

# Load configuration
config = load_config()

SWAGGER_URL = get_swagger_url()
API_KEY = config.get("api_key", "special-key")
LLM_PROVIDER = config.get("llm_provider", "openai")
OPENAI_API_KEY = config.get("openai_api_key")
ANTHROPIC_API_KEY = config.get("anthropic_api_key")
MODEL = config.get("model", "gpt-4o")
FALLBACK_TO_SCHEMA = config.get("fallback_to_schema", True)

# Debug: Print config status
if LLM_PROVIDER != "none":
    print(f"🔧 Config: LLM Provider = {LLM_PROVIDER}")
    print(f"🔧 Config: OpenAI API Key present = {bool(OPENAI_API_KEY)}")
    print(f"🔧 Config: Anthropic API Key present = {bool(ANTHROPIC_API_KEY)}")

# Initialize LLM client based on provider
client = None
if LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        print(f"🤖 Using Anthropic Claude: {MODEL}")
    except ImportError:
        print("⚠️  Anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)
elif LLM_PROVIDER == "openai" and OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        print(f"🤖 Using OpenAI: {MODEL}")
    except ImportError as e:
        print(f"⚠️  OpenAI package not installed. Run: pip install openai")
        print(f"   Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️  Error initializing OpenAI client: {e}")
        sys.exit(1)
elif LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    print("⚠️  OpenAI provider selected but 'openai_api_key' not found in config.json")
    print("   Please add 'openai_api_key' to your config.json")
elif LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
    print("⚠️  Anthropic provider selected but 'anthropic_api_key' not found in config.json")
    print("   Please add 'anthropic_api_key' to your config.json")


def load_swagger_spec(url=SWAGGER_URL):
    """Load Swagger/OpenAPI specification"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_endpoints(spec):
    """Extract endpoints from Swagger spec"""
    paths = spec.get("paths", {})
    definitions = spec.get("definitions", {})
    endpoints = []
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "parameters": details.get("parameters", []),
                    "responses": details.get("responses", {}),
                    "consumes": details.get("consumes", []),
                    "definitions": definitions
                })
    return endpoints


def call_llm(system_prompt, user_prompt, temperature=0.5):
    """Universal LLM caller that works with multiple providers"""
    if not client:
        return None
    
    try:
        if LLM_PROVIDER == "anthropic":
            response = client.messages.create(
                model=MODEL,
                max_tokens=4000,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        elif LLM_PROVIDER == "openai":
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=4000
            )
            return response.choices[0].message.content
    except Exception as e:
        print(f"   ⚠️  LLM Error: {e}")
        return None


def generate_test_plan_with_agent(spec, endpoints):
    """Use LLM agent to analyze API and create a test generation plan"""
    if not client:
        return None
    
    endpoint_summary = []
    for ep in endpoints[:20]:  # Limit for token efficiency
        endpoint_summary.append(f"- {ep['method']} {ep['path']}: {ep['summary']}")
    
    system_prompt = """You are an expert API test generator using Playwright. 
Analyze the API specification and create a comprehensive test generation plan.
Focus on:
1. Test execution order (POST before GET/DELETE)
2. Resource dependencies
3. Test data requirements
4. Expected responses"""
    
    user_prompt = f"""Analyze this API specification and create a test generation plan:

API Title: {spec.get('info', {}).get('title', 'Unknown')}
Base URL: {spec.get('schemes', ['https'])[0]}://{spec.get('host', 'unknown')}{spec.get('basePath', '')}

Endpoints:
{chr(10).join(endpoint_summary)}

Create a detailed plan for generating Playwright API tests that:
1. Creates resources first (POST)
2. Tests retrieval (GET) using created IDs
3. Tests updates (PUT) using created IDs  
4. Tests deletion (DELETE) using created IDs
5. Handles resource dependencies correctly
6. Uses serial test execution mode
7. Stores resource IDs for dependent tests

Return a structured plan in JSON format."""
    
    response = call_llm(system_prompt, user_prompt, temperature=0.3)
    return response


def generate_test_with_agent(endpoint_info, test_plan=None):
    """Use LLM agent to generate a single Playwright test"""
    if not client:
        return None
    
    # Extract schema information
    body_params = [p for p in endpoint_info['parameters'] if p.get('in') == 'body']
    schema_info = {}
    if body_params:
        schema = body_params[0].get('schema', {})
        if '$ref' in schema:
            ref_name = schema['$ref'].split('/')[-1]
            schema_info = endpoint_info.get('definitions', {}).get(ref_name, {})
        else:
            schema_info = schema
    
    system_prompt = """You are an expert at generating Playwright API tests.
Generate complete, working Playwright test code that:
- Uses proper TypeScript/JavaScript syntax
- Handles resource IDs correctly
- Uses serial test execution
- Includes proper error handling
- Stores created resource IDs for later tests"""
    
    user_prompt = f"""Generate a Playwright test for this API endpoint:

Method: {endpoint_info['method']}
Path: {endpoint_info['path']}
Summary: {endpoint_info['summary']}
Parameters: {json.dumps(endpoint_info['parameters'], indent=2)}
Schema: {json.dumps(schema_info, indent=2) if schema_info else 'None'}

Requirements:
- Use Playwright's request API
- Store resource IDs in a shared resourceIds object
- Use test.describe.serial for sequential execution
- Handle path parameters like {{petId}} by replacing with ${{resourceIds['pet']}}
- Generate realistic test data based on the schema
- Include proper assertions

Return ONLY the test code, no explanations."""
    
    response = call_llm(system_prompt, user_prompt, temperature=0.5)
    return response


def get_base_url_from_spec(spec, swagger_url=None):
    """Extract base URL from OpenAPI/Swagger spec"""
    # Try OpenAPI 3.0 format first (uses 'servers' array)
    if "servers" in spec and spec["servers"]:
        server_url = spec["servers"][0].get("url", "")
        if server_url:
            # Remove trailing slash
            return server_url.rstrip("/")
    
    # Try Swagger 2.0 format (uses 'host', 'basePath', 'schemes')
    host = spec.get("host", "")
    base_path = spec.get("basePath", "")
    schemes = spec.get("schemes", ["https"])
    scheme = schemes[0] if schemes else "https"
    
    if host:
        full_url = f"{scheme}://{host}{base_path}".rstrip("/")
        return full_url
    
    # Fallback: extract from swagger_url if provided
    if swagger_url:
        from urllib.parse import urlparse
        parsed = urlparse(swagger_url)
        # Remove /swagger/v1/swagger.json or similar paths
        base = f"{parsed.scheme}://{parsed.netloc}"
        # Try to remove common swagger paths
        path_parts = parsed.path.split("/")
        if "swagger" in path_parts:
            swagger_idx = path_parts.index("swagger")
            base_path = "/".join(path_parts[:swagger_idx])
            if base_path:
                return f"{base}{base_path}".rstrip("/")
        return base.rstrip("/")
    
    # Last resort fallback
    return "https://api.example.com"


def use_playwright_mcp_tools(spec, endpoints):
    """Use Playwright MCP tools programmatically to generate tests"""
    # This would require connecting to Playwright MCP server
    # For now, we'll use the LLM agent approach with Playwright test patterns
    print("🔧 Generating tests using local patterns...")
    
    # Get base URL from spec (handles both OpenAPI 3.0 and Swagger 2.0)
    full_base_url = get_base_url_from_spec(spec, SWAGGER_URL)
    print(f"📍 Using base URL: {full_base_url}")
    
    # Get API name for test suite naming
    api_info = spec.get("info", {})
    api_title = api_info.get("title", "API")
    
    # Generate test plan with agent
    print("📋 Generating test plan with AI agent...")
    test_plan = generate_test_plan_with_agent(spec, endpoints)
    if test_plan:
        print(f"\n📝 Test Plan:\n{test_plan}\n")
    
    # Generate tests using agent
    test_code = f"""import {{ test, expect }} from '@playwright/test';

const BASE_URL = '{full_base_url}';
const API_KEY = '{API_KEY}';

// Store created resource IDs for reuse in later tests
let resourceIds: Record<string, any> = {{}};

/*
AI-Generated Test Plan:
{test_plan if test_plan else 'Basic strategy: POST resources first, then test GET/PUT/DELETE using created IDs.'}
*/

// Use serial mode to run tests sequentially and share state
test.describe.serial('{api_title} - API Tests', () => {{
"""
    
    # Group endpoints by resource and method
    resource_groups = {
        'pet': {'post': [], 'get': [], 'put': [], 'delete': []},
        'order': {'post': [], 'get': [], 'put': [], 'delete': []},
        'user': {'post': [], 'get': [], 'put': [], 'delete': []},
        'other': []
    }
    
    for ep in endpoints:
        path = ep['path']
        method = ep['method']
        consumes = ep.get("consumes", [])
        
        # Skip problematic endpoints
        if "multipart/form-data" in consumes or "application/x-www-form-urlencoded" in consumes:
            continue
        if path in ["/user/createWithList", "/user/createWithArray"]:
            continue
        
        # Categorize by resource
        if 'pet' in path.lower():
            if method == 'POST' and '{' not in path:
                resource_groups['pet']['post'].append(ep)
            elif method == 'GET':
                resource_groups['pet']['get'].append(ep)
            elif method == 'PUT':
                resource_groups['pet']['put'].append(ep)
            elif method == 'DELETE':
                resource_groups['pet']['delete'].append(ep)
        elif 'order' in path.lower() or 'store' in path.lower():
            if method == 'POST' and '{' not in path:
                resource_groups['order']['post'].append(ep)
            elif method == 'GET':
                resource_groups['order']['get'].append(ep)
            elif method == 'PUT':
                resource_groups['order']['put'].append(ep)
            elif method == 'DELETE':
                resource_groups['order']['delete'].append(ep)
        elif 'user' in path.lower():
            if method == 'POST' and '{' not in path:
                resource_groups['user']['post'].append(ep)
            elif method == 'GET':
                resource_groups['user']['get'].append(ep)
            elif method == 'PUT':
                resource_groups['user']['put'].append(ep)
            elif method == 'DELETE':
                resource_groups['user']['delete'].append(ep)
        else:
            resource_groups['other'].append(ep)
    
    # Generate tests in order: POST → GET → PUT → DELETE
    for resource in ['pet', 'order', 'user']:
        for ep in resource_groups[resource]['post']:
            print(f"🤖 Generating test with agent: {ep['method']} {ep['path']}...")
            agent_test = generate_test_with_agent(ep)
            if agent_test:
                # Clean and integrate agent-generated test
                test_code += agent_test + "\n"
            else:
                # Fallback to basic test generation
                test_code += generate_basic_test(ep, use_stored_id=False)
        
        for ep in resource_groups[resource]['get']:
            needs_id = '{' in ep['path']
            if needs_id:
                print(f"🤖 Generating test with agent: {ep['method']} {ep['path']}...")
                agent_test = generate_test_with_agent(ep)
                if agent_test:
                    test_code += agent_test + "\n"
                else:
                    test_code += generate_basic_test(ep, use_stored_id=True)
            else:
                test_code += generate_basic_test(ep, use_stored_id=False)
        
        for ep in resource_groups[resource]['put']:
            needs_id = '{' in ep['path']
            print(f"🤖 Generating test with agent: {ep['method']} {ep['path']}...")
            agent_test = generate_test_with_agent(ep)
            if agent_test:
                test_code += agent_test + "\n"
            else:
                test_code += generate_basic_test(ep, use_stored_id=needs_id)
        
        for ep in resource_groups[resource]['delete']:
            needs_id = '{' in ep['path']
            print(f"🤖 Generating test with agent: {ep['method']} {ep['path']}...")
            agent_test = generate_test_with_agent(ep)
            if agent_test:
                test_code += agent_test + "\n"
            else:
                test_code += generate_basic_test(ep, use_stored_id=needs_id)
    
    # Add other tests
    for ep in resource_groups['other']:
        test_code += generate_basic_test(ep, use_stored_id=False)
    
    test_code += """});
"""
    
    return test_code


def generate_basic_test(ep, use_stored_id=False):
    """Fallback basic test generation"""
    path = ep['path']
    method = ep['method']
    summary = ep['summary']
    responses = ep['responses']
    
    expected_status = 200
    if "200" in responses:
        expected_status = 200
    elif "201" in responses:
        expected_status = 201
    elif "204" in responses:
        expected_status = 204
    
    test_name = f"{method} {path}"
    if summary:
        test_name = f"{method} {path} - {summary}"
    
    # Extract resource name
    path_parts = path.split('/')
    resource_name = None
    for i, part in enumerate(path_parts):
        if '{' in part and i > 0:
            resource_name = path_parts[i-1]
            break
    
    if not resource_name and method == "POST":
        resource_name = path_parts[-1]
    
    test_code = f"""
  test('{test_name}', async ({{ request }}) => {{"""
    
    if use_stored_id and resource_name:
        test_code += f"""
    if (!resourceIds['{resource_name}']) {{
      console.log('Skipping - no {resource_name} ID available');
      return;
    }}"""
        
        dynamic_path = path.replace('{petId}', '${resourceIds[\'pet\']}')
        dynamic_path = dynamic_path.replace('{orderId}', '${resourceIds[\'order\']}')
        dynamic_path = dynamic_path.replace('{username}', '${resourceIds[\'user\']}')
        dynamic_path = dynamic_path.replace('{id}', '${resourceIds[\'' + resource_name + '\']}')
        
        test_code += f"""
    const response = await request.{method.lower()}(`${{BASE_URL}}{dynamic_path}`);"""
    else:
        test_code += f"""
    const response = await request.{method.lower()}(`${{BASE_URL}}{path}`);"""
    
    test_code += f"""
    expect(response.status()).toBe({expected_status});"""
    
    if method == "POST" and not use_stored_id and resource_name:
        if resource_name == "user":
            test_code += f"""
    if (response.ok()) {{
      const body = await response.json();
      if (body.username !== undefined) {{
        resourceIds['{resource_name}'] = body.username;
      }}
    }}"""
        else:
            test_code += f"""
    if (response.ok()) {{
      const body = await response.json();
      if (body.id !== undefined) {{
        resourceIds['{resource_name}'] = body.id;
      }}
    }}"""
    
    test_code += """
  });
"""
    
    return test_code


# Main execution
print("=" * 80)
print("🚀 Playwright Test Generator")
print("=" * 80)

if LLM_PROVIDER == "none":
    print("\n⚠️  LLM provider set to 'none'. Using basic test generation.")
    print("   Set 'llm_provider' to 'openai' or 'anthropic' in config.json to use agent mode.\n")
    
    spec = load_swagger_spec()
    endpoints = get_endpoints(spec)
    # Use basic generation
    sys.path.insert(0, str(project_root))
    from generate_playwright_tests import generate_playwright_tests
    playwright_tests = generate_playwright_tests(spec, endpoints)
elif not client:
    print("\n❌ LLM provider configured but client initialization failed.")
    print("   Please check your API keys and ensure required packages are installed.\n")
    sys.exit(1)
else:
    print(f"\n🤖 Using {LLM_PROVIDER.upper()} agent: {MODEL}")
    print(f"📡 Loading API spec from: {SWAGGER_URL}\n")
    
    spec = load_swagger_spec()
    endpoints = get_endpoints(spec)
    playwright_tests = use_playwright_mcp_tools(spec, endpoints)

# Generate test file name from API spec
api_info = spec.get("info", {})
api_title = api_info.get("title", "API")
api_name = "".join(c.lower() if c.isalnum() else "_" for c in api_title).strip("_")
if not api_name:
    host = spec.get("host", "")
    api_name = host.split(".")[0] if host and "." in host else "api_tests"

test_filename = f"{api_name}.spec.ts"
output_file = project_root / "tests" / test_filename

os.makedirs(output_file.parent, exist_ok=True)
with open(output_file, "w") as f:
    f.write(playwright_tests)

test_count = len([line for line in playwright_tests.split('\n') if 'test(' in line])

print("\n" + "=" * 80)
print(f"✅ Playwright tests generated: {output_file}")
print(f"📝 Generated {test_count} test cases")
print(f"\n🤖 Agent Features Used:")
print(f"   • AI-powered test plan generation")
print(f"   • Intelligent test code generation")
print(f"   • Playwright MCP patterns")
print(f"   • Resource dependency handling")
print("\nTo run the tests:")
print("  npx playwright test")
print("  npx playwright show-report")
print("=" * 80)

