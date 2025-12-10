# generate_playwright_tests.py
import requests
import json
import os
from pathlib import Path
import re

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


def generate_playwright_tests(spec, endpoints):
    # Get base URL from spec
    from urllib.parse import urlparse
    
    # Try OpenAPI 3.0 format first
    if "servers" in spec and spec["servers"]:
        full_base_url = spec["servers"][0].get("url", "").rstrip("/")
    else:
        # Swagger 2.0 format
        host = spec.get("host", "")
        base_path = spec.get("basePath", "")
        scheme = spec.get("schemes", ["https"])[0] if spec.get("schemes") else "https"
        if host:
            full_base_url = f"{scheme}://{host}{base_path}".rstrip("/")
        else:
            # Fallback: extract from config
            from scripts.config_loader import get_swagger_url
            swagger_url = get_swagger_url()
            parsed = urlparse(swagger_url)
            full_base_url = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    
    # Get API name
    api_info = spec.get("info", {})
    api_title = api_info.get("title", "API")
    
    test_code = f"""import {{ test, expect }} from '@playwright/test';

const BASE_URL = '{full_base_url}';
const API_KEY = '{API_KEY}';

let resourceIds: Record<string, any> = {{}};

test.describe.serial('{api_title} - API Tests', () => {{
"""

    # Separate tests into three groups for proper ordering
    post_tests = []  # POST endpoints - create resources first
    get_list_tests = []  # GET endpoints without IDs - can run after POST
    dependent_tests = []  # Tests that need resource IDs (GET/PUT/DELETE with {id})
    
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
        
        # Categorize tests properly
        if method == "POST" and "{" not in path:
            # POST endpoints create resources - run first
            post_tests.append(ep)
        elif method == "GET" and "{" not in path:
            # GET list endpoints - run after POST but before dependent tests
            get_list_tests.append(ep)
        elif "{" in path:
            # Tests that need resource IDs (GET /pet/{id}, PUT /pet/{id}, DELETE /pet/{id})
            dependent_tests.append(ep)
        else:
            # Other methods (PUT, DELETE without IDs) - add to dependent
            dependent_tests.append(ep)
    
    # Generate tests in correct order:
    # 1. POST tests first (to create resources)
    for ep in post_tests:
        test_code += generate_test_code(ep, use_stored_id=False)
    
    # 2. GET list tests (don't need IDs, but run after POST)
    for ep in get_list_tests:
        test_code += generate_test_code(ep, use_stored_id=False)
    
    # 3. Dependent tests (use stored IDs from POST)
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
        # Generate payload based on endpoint
        if "permission" in path.lower():
            payload = "{ id: 1, name: 'TestResource' }"
        else:
            payload = "{ id: 1 }"
    
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
        
        # Replace ALL path parameters with stored IDs dynamically
        dynamic_path = path
        
        # Find all path parameters like {petId}, {orderId}, {username}, {id}, etc.
        path_params = re.findall(r'\{(\w+)\}', path)
        
        for param in path_params:
            # Map parameter names to resource keys
            # Common patterns: {petId} -> 'pet', {orderId} -> 'order', {username} -> 'user'
            param_lower = param.lower()
            
            # Determine which resource key to use
            if 'pet' in param_lower:
                resource_key = 'pet'
            elif 'order' in param_lower:
                resource_key = 'order'
            elif 'user' in param_lower or 'username' in param_lower:
                resource_key = 'user'
            else:
                # Default to the resource_name we extracted from path
                resource_key = resource_name
            
            # Replace {paramName} with ${resourceIds['resourceKey']}
            dynamic_path = dynamic_path.replace(f'{{{param}}}', f'${{resourceIds[\'{resource_key}\']}}')
        
        test_code += f"""
    
    const response = await request.{method.lower()}(`${{BASE_URL}}{dynamic_path}`, {{"""
    else:
        test_code += f"""
    const response = await request.{method.lower()}(`${{BASE_URL}}{path}`, {{"""
    
    # Determine if we need Content-Type header (POST/PUT/PATCH with body)
    needs_content_type = body_params and method in ["POST", "PUT", "PATCH"]
    
    # Build request object
    if needs_content_type or headers or payload:
        test_code += f"""
      headers: {{
        'Content-Type': 'application/json',"""
        if headers:
            test_code += f"""
        'api_key': API_KEY,"""
        test_code += f"""
      }},"""
        
        if payload:
            test_code += f"""
      data: {payload},"""
        elif needs_content_type:
            # Add empty data object for POST/PUT/PATCH even if no payload generated
            test_code += f"""
      data: {{}},"""
    
    test_code += f"""
    }});
    
    expect(response.status()).toBe({expected_status});"""
    
    # Store ID if this is a POST request
    if method == "POST" and not use_stored_id and resource_name:
        # Handle different response structures
        if resource_name == "user":
            test_code += f"""
    
    // Store the created resource ID for later tests
    if (response.ok()) {{
      const body = await response.json();
      // User endpoints might return username instead of id
      if (body.username !== undefined) {{
        resourceIds['{resource_name}'] = body.username;
        console.log('Created {resource_name} with username:', body.username);
      }} else if (body.id !== undefined) {{
        resourceIds['{resource_name}'] = body.id;
        console.log('Created {resource_name} with ID:', body.id);
      }}
    }}"""
        else:
            test_code += f"""
    
    // Store the created resource ID for later tests
    if (response.ok()) {{
      const body = await response.json();
      if (body.id !== undefined) {{
        resourceIds['{resource_name}'] = body.id;
        console.log('Created {resource_name} with ID:', body.id);
      }} else {{
        console.warn('POST succeeded but no ID found in response:', body);
      }}
    }} else {{
      console.error('POST failed with status:', response.status());
      const errorBody = await response.text();
      console.error('Error response:', errorBody);
    }}"""
    
    test_code += """
  });
"""
    
    return test_code


# Generate tests
spec = load_swagger_spec()
endpoints = get_endpoints(spec)
playwright_tests = generate_playwright_tests(spec, endpoints)

# Generate test file name from API spec
api_info = spec.get("info", {})
api_title = api_info.get("title", "API")
api_name = "".join(c.lower() if c.isalnum() else "_" for c in api_title).strip("_")
if not api_name:
    host = spec.get("host", "")
    api_name = host.split(".")[0] if host and "." in host else "api_tests"

output_file = project_root / "tests" / f"{api_name}.spec.ts"

# Save to file
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
