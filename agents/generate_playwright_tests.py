# generate_playwright_tests.py
import requests
import json
import os
from pathlib import Path

# Load configuration
# Get project root (one level up from agents/)
project_root = Path(__file__).parent.parent
config_path = project_root / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)

SWAGGER_URL = config.get("swagger_url", "https://fakerestapi.azurewebsites.net/swagger/v1/swagger.json")
API_KEY = config.get("api_key", "special-key")


def load_swagger_spec(url=SWAGGER_URL):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_endpoints(spec):
    paths = spec.get("paths", {})
    endpoints = []
    for path, methods in paths.items():
        for method, details in methods.items():
            endpoints.append({
                "path": path,
                "method": method.upper(),
                "summary": details.get("summary", ""),
                "parameters": details.get("parameters", []),
                "responses": details.get("responses", {}),
                "consumes": details.get("consumes", [])
            })
    return endpoints


def generate_playwright_tests(spec, endpoints):
    base_url = spec.get("host", "petstore.swagger.io")
    base_path = spec.get("basePath", "")
    scheme = spec.get("schemes", ["https"])[0]
    full_base_url = f"{scheme}://{base_url}{base_path}"
    
    test_code = f"""import {{ test, expect }} from '@playwright/test';

const BASE_URL = '{full_base_url}';
const API_KEY = '{API_KEY}';

// Store created resource IDs for reuse in later tests
const resourceIds = {{}};

test.describe('API Tests - Generated from Swagger', () => {{
"""

    # Separate tests into two groups
    post_tests = []  # Create resources first
    dependent_tests = []  # Tests that need resource IDs
    
    for ep in endpoints:
        path = ep['path']
        method = ep['method']
        consumes = ep.get("consumes", [])
        
        # Skip form-data and multipart uploads
        if "multipart/form-data" in consumes or "application/x-www-form-urlencoded" in consumes:
            continue
        
        # Skip bulk user creation endpoints
        if path in ["/user/createWithList", "/user/createWithArray"]:
            continue
        
        # Categorize tests
        if method == "POST" and "{" not in path:
            post_tests.append(ep)
        elif method == "GET" and "{" not in path:
            post_tests.insert(0, ep)  # GET lists first
        elif "{" in path:
            dependent_tests.append(ep)
    
    # Generate POST tests first (to create resources)
    for ep in post_tests:
        test_code += generate_test_code(ep, use_stored_id=False)
    
    # Generate dependent tests (use stored IDs)
    for ep in dependent_tests:
        test_code += generate_test_code(ep, use_stored_id=True)
    
    test_code += """});
"""
    
    return test_code


def generate_test_code(ep, use_stored_id=False):
    path = ep['path']
    method = ep['method']
    summary = ep['summary']
    responses = ep['responses']
    parameters = ep['parameters']
    
    # Determine headers
    headers = {}
    for p in parameters:
        if p.get("name") == "api_key":
            headers["api_key"] = "API_KEY"
    
    # Determine payload
    payload = None
    body_params = [p for p in parameters if p.get("in") == "body"]
    if body_params and method in ["POST", "PUT", "PATCH"]:
        schema = body_params[0].get("schema", {})
        if schema.get("type") == "array":
            payload = "[{}]"
        else:
            payload = "{}"
    
    # Determine expected status
    expected_status = 200
    if "200" in responses:
        expected_status = 200
    elif "201" in responses:
        expected_status = 201
    elif "204" in responses:
        expected_status = 204
    else:
        for status in sorted(responses.keys()):
            if status.isdigit():
                status_int = int(status)
                if 200 <= status_int < 300:
                    expected_status = status_int
                    break
    
    if not any(str(s).startswith('2') for s in responses.keys() if str(s).isdigit()):
        if method in ["POST", "PUT", "PATCH", "GET"]:
            expected_status = 200
    
    # Generate test name
    test_name = f"{method} {path}"
    if summary:
        test_name = f"{method} {path} - {summary}"
    
    # Extract resource name from path
    path_parts = path.split('/')
    resource_name = None
    for i, part in enumerate(path_parts):
        if '{' in part and i > 0:
            resource_name = path_parts[i-1]
            break
    
    if not resource_name and method == "POST":
        resource_name = path_parts[-1]
    
    # Build test code
    test_code = f"""
  test('{test_name}', async ({{ request }}) => {{"""
    
    if use_stored_id and resource_name:
        test_code += f"""
    // Skip if resource ID not available
    if (!resourceIds['{resource_name}']) {{
      console.log('Skipping - no {resource_name} ID available');
      return;
    }}"""
        
        # Replace path parameters with stored IDs
        dynamic_path = path.replace('{id}', '${resourceIds[\'' + resource_name + '\']}')
        dynamic_path = dynamic_path.replace('{idBook}', '${resourceIds[\'Books\']}')
        
        test_code += f"""
    
    const response = await request.{method.lower()}(`${{BASE_URL}}{dynamic_path}`, {{"""
    else:
        test_code += f"""
    const response = await request.{method.lower()}(`${{BASE_URL}}{path}`, {{"""
    
    if headers:
        test_code += f"""
      headers: {{
        'api_key': API_KEY,
      }},"""
    
    if payload:
        test_code += f"""
      data: {payload},"""
    
    test_code += f"""
    }});
    
    expect(response.status()).toBe({expected_status});"""
    
    # Store ID if this is a POST request
    if method == "POST" and not use_stored_id and resource_name:
        test_code += f"""
    
    // Store the created resource ID for later tests
    if (response.ok()) {{
      const body = await response.json();
      if (body.id !== undefined) {{
        resourceIds['{resource_name}'] = body.id;
        console.log('Created {resource_name} with ID:', body.id);
      }}
    }}"""
    
    test_code += """
  });
"""
    
    return test_code


# Generate tests
spec = load_swagger_spec()
endpoints = get_endpoints(spec)
playwright_tests = generate_playwright_tests(spec, endpoints)

# Save to file
output_file = project_root / "tests" / "petstore.spec.ts"
os.makedirs(output_file.parent, exist_ok=True)
with open(output_file, "w") as f:
    f.write(playwright_tests)

test_count = len([line for line in playwright_tests.split('\n') if 'test(' in line])
print(f"✅ Playwright tests generated: {output_file}")
print(f"📝 Generated {test_count} test cases")
print(f"\n🔄 Test Strategy:")
print(f"   1. POST requests create resources and store their IDs")
print(f"   2. GET/PUT/DELETE requests use stored IDs")
print(f"   3. Tests with missing IDs are skipped gracefully")
print(f"\nTo run the tests:")
print(f"  npx playwright test")
print(f"  npx playwright show-report")
