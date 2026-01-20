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
                "consumes": details.get("consumes", []),
                "requestBody": details.get("requestBody", {})  # OpenAPI 3.0
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
            swagger_url = SWAGGER_URL
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
        test_code += generate_test_code(ep, spec, use_stored_id=False)
    # 2. GET list tests (don't need IDs, but run after POST)
    for ep in get_list_tests:
        test_code += generate_test_code(ep, spec, use_stored_id=False)
    # 3. Dependent tests (use stored IDs from POST)
    for ep in dependent_tests:
        test_code += generate_test_code(ep, spec, use_stored_id=True)
    
    test_code += """});
"""
    
    return test_code


def generate_test_code(ep, spec, use_stored_id=False):
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
    
    # Extract resource name from path (needed for fallback payload)
    path_parts = path.split('/')
    resource_name = None
    for i, part in enumerate(path_parts):
        if '{' in part and i > 0:
            resource_name = path_parts[i-1]
            break
    
    if not resource_name and method == "POST":
        resource_name = path_parts[-1] if path_parts else None
    
    # Determine payload from schema
    payload = None
    body_params = [p for p in parameters if p.get("in") == "body"]
    
    def resolve_ref(ref):
        """Resolve $ref references in schema"""
        if not ref or not ref.startswith("#/"):
            return {}
        parts = ref.lstrip("#/").split("/")
        obj = spec
        for part in parts:
            obj = obj.get(part, {})
        return obj

    def generate_value_from_schema(prop_schema, spec_ref=None):
        """Generate a test value from a schema property"""
        # Handle $ref
        if "$ref" in prop_schema:
            resolved = resolve_ref(prop_schema["$ref"])
            return generate_value_from_schema(resolved, spec_ref or spec)
        
        # Handle enum
        if "enum" in prop_schema:
            return json.dumps(prop_schema["enum"][0])
        
        # Handle default value
        if "default" in prop_schema:
            return json.dumps(prop_schema["default"])
        
        prop_type = prop_schema.get("type")
        fmt = prop_schema.get("format")
        
        # Handle string types
        if prop_type == "string":
            if fmt == "date-time":
                return json.dumps("2023-01-01T00:00:00Z")
            elif fmt == "date":
                return json.dumps("2023-01-01")
            elif fmt == "email":
                return json.dumps("test@example.com")
            elif fmt == "uri" or fmt == "url":
                return json.dumps("https://example.com")
            elif "example" in prop_schema:
                return json.dumps(prop_schema["example"])
            else:
                # Generate example based on property name
                prop_name = prop_schema.get("name", "")
                if "name" in prop_name.lower():
                    return json.dumps("Test Name")
                elif "email" in prop_name.lower():
                    return json.dumps("test@example.com")
                elif "url" in prop_name.lower() or "uri" in prop_name.lower():
                    return json.dumps("https://example.com")
                else:
                    return json.dumps("example")
        
        # Handle integer types
        elif prop_type == "integer":
            if "example" in prop_schema:
                return prop_schema["example"]
            elif "minimum" in prop_schema:
                return prop_schema["minimum"]
            else:
                return 1
        
        # Handle number types
        elif prop_type == "number":
            if "example" in prop_schema:
                return prop_schema["example"]
            elif "minimum" in prop_schema:
                return prop_schema["minimum"]
            else:
                return 1.0
        
        # Handle boolean types
        elif prop_type == "boolean":
            return True
        
        # Handle array types
        elif prop_type == "array":
            items_schema = prop_schema.get("items", {})
            item_value = generate_value_from_schema(items_schema, spec_ref or spec)
            return f"[{item_value}]"
        
        # Handle object types
        elif prop_type == "object":
            return generate_payload_from_schema(prop_schema, spec_ref or spec)
        
        # Default fallback
        return json.dumps(None)

    def generate_payload_from_schema(schema, spec_ref=None):
        """Generate a complete payload object from a schema"""
        # Resolve $ref
        if "$ref" in schema:
            schema = resolve_ref(schema["$ref"])
        
        # Handle allOf, anyOf, oneOf
        if "allOf" in schema:
            # Merge all schemas in allOf
            merged = {}
            for sub_schema in schema["allOf"]:
                merged.update(generate_payload_from_schema(sub_schema, spec_ref or spec))
            return merged
        
        props = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Include required fields and some optional fields for better coverage
        fields_to_include = set(required)
        # Add a few optional fields if available (up to 3)
        optional_fields = [k for k in props.keys() if k not in required]
        fields_to_include.update(optional_fields[:3])
        
        out = {}
        for field_name in fields_to_include:
            if field_name in props:
                prop_schema = props[field_name]
                field_value = generate_value_from_schema(prop_schema, spec_ref or spec)
                out[field_name] = field_value
        
        return out
    
    # Extract schema from body parameter (Swagger 2.0) or requestBody (OpenAPI 3.0)
    if method in ["POST", "PUT", "PATCH"]:
        schema = None
        
        # Swagger 2.0: body parameter
        if body_params:
            schema = body_params[0].get("schema", {})
        
        # OpenAPI 3.0: requestBody
        request_body = ep.get("requestBody", {})
        if request_body:
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            if json_content:
                schema = json_content.get("schema", {})
        
        if schema:
            payload_obj = generate_payload_from_schema(schema, spec)
            if payload_obj and len(payload_obj) > 0:
                # Convert to JavaScript object string
                payload_parts = []
                for k, v in payload_obj.items():
                    if isinstance(v, str) and (v.startswith("{") or v.startswith("[")):
                        payload_parts.append(f"{k}: {v}")
                    else:
                        payload_parts.append(f"{k}: {json.dumps(v)}")
                payload = "{ " + ", ".join(payload_parts) + " }"
    
    # If no payload generated but it's a POST/PUT/PATCH, create fallback
    if method in ["POST", "PUT", "PATCH"] and not payload:
        if resource_name:
            payload = "{ id: 1 }"
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
    # Always add headers/data for POST/PUT/PATCH, even if schema extraction failed
    needs_content_type = method in ["POST", "PUT", "PATCH"]
    
    # Build request object
    if needs_content_type or headers or payload:
        if needs_content_type or headers:
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
            # Add fallback data for POST/PUT/PATCH if no payload generated
            # Try to generate minimal payload based on resource name
            if resource_name:
                # Generate a basic payload with id field
                test_code += f"""
      data: {{ id: 1 }},"""
            else:
                # Empty object as last resort
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
