# review_test_coverage.py
# Agent 2: Reviews generated tests for coverage based on API documentation
# Uses Playwright MCP patterns for coverage analysis

import requests
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Get project root and add to path BEFORE importing scripts module
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import config_loader (after adding project root to path)
from scripts.config_loader import get_swagger_url, load_config

# Paths and configuration
config = load_config()

SWAGGER_URL = get_swagger_url()
TEST_FILE = config.get("test_file", str(project_root / "tests" / "petstore.spec.ts"))


def load_swagger_spec(url=SWAGGER_URL):
    """Load Swagger/OpenAPI specification"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def load_generated_tests(test_file=TEST_FILE):
    """Load the generated test file"""
    # Ensure absolute path
    if not os.path.isabs(test_file):
        test_file = project_root / test_file
    else:
        test_file = Path(test_file)
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return None
    
    with open(test_file, "r") as f:
        return f.read()


def extract_endpoints_from_spec(spec):
    """Extract all endpoints from Swagger spec"""
    paths = spec.get("paths", {})
    endpoints = []
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "operationId": details.get("operationId", ""),
                    "tags": details.get("tags", []),
                    "parameters": details.get("parameters", []),
                    "responses": details.get("responses", {}),
                    "consumes": details.get("consumes", [])
                })
    
    return endpoints


def extract_tests_from_file(test_content):
    """Extract test information from generated test file"""
    tests = []
    
    # Pattern to match test() calls
    test_pattern = r"test\(['\"]([^'\"]+)['\"],\s*async"
    test_matches = re.finditer(test_pattern, test_content)
    
    for match in test_matches:
        test_name = match.group(1)
        
        # Extract method and path from test name
        # Format: "METHOD /path - description" or "METHOD /path"
        method_path_match = re.match(r"^(\w+)\s+([^\s-]+)", test_name)
        if method_path_match:
            method = method_path_match.group(1).upper()
            path = method_path_match.group(2)
            
            tests.append({
                "name": test_name,
                "method": method,
                "path": path,
                "full_name": test_name
            })
    
    # Also look for request calls to find actual endpoints being tested
    request_pattern = r"request\.(get|post|put|delete|patch)\([`'\"]([^`'\"]+)[`'\"]"
    request_matches = re.finditer(request_pattern, test_content, re.IGNORECASE)
    
    tested_endpoints = set()
    for match in request_matches:
        method = match.group(1).upper()
        url = match.group(2)
        
        # Extract path from URL (remove BASE_URL and query params)
        if "${BASE_URL}" in url:
            path = url.split("${BASE_URL}")[-1].split("?")[0]
        elif "BASE_URL" in url:
            # Handle template literals
            path_match = re.search(r'`\$\{BASE_URL\}([^`]+)`', url)
            if path_match:
                path = path_match.group(1).split("?")[0]
            else:
                path = url.split("?")[0]
        else:
            path = url.split("?")[0]
        
        tested_endpoints.add((method, path))
    
    return tests, tested_endpoints


def normalize_path(path):
    """Normalize path for comparison (remove trailing slashes, handle parameters)"""
    # Remove trailing slash
    path = path.rstrip('/')
    if not path:
        path = '/'
    
    # Normalize parameter formats: {id} vs ${resourceIds['id']}
    # We'll compare the base path structure
    normalized = re.sub(r'\{[^}]+\}', '{param}', path)
    normalized = re.sub(r'\$\{[^}]+\}', '{param}', normalized)
    
    return normalized


def analyze_coverage(spec_endpoints, tested_endpoints):
    """Analyze test coverage"""
    coverage_report = {
        "total_endpoints": len(spec_endpoints),
        "tested_endpoints": len(tested_endpoints),
        "missing_tests": [],
        "covered_endpoints": [],
        "coverage_percentage": 0,
        "by_method": {},
        "by_tag": {}
    }
    
    # Group endpoints by method
    spec_by_method = {}
    for ep in spec_endpoints:
        method = ep["method"]
        if method not in spec_by_method:
            spec_by_method[method] = []
        spec_by_method[method].append(ep)
    
    # Check coverage
    tested_set = set()
    for method, path in tested_endpoints:
        normalized = normalize_path(path)
        tested_set.add((method, normalized))
    
    covered = []
    missing = []
    
    for ep in spec_endpoints:
        method = ep["method"]
        path = ep["path"]
        normalized = normalize_path(path)
        
        # Skip problematic endpoints
        consumes = ep.get("consumes", [])
        if "multipart/form-data" in consumes or "application/x-www-form-urlencoded" in consumes:
            continue
        
        # Skip bulk endpoints
        if path in ["/user/createWithList", "/user/createWithArray"]:
            continue
        
        if (method, normalized) in tested_set:
            covered.append(ep)
            coverage_report["covered_endpoints"].append({
                "method": method,
                "path": path,
                "summary": ep.get("summary", "")
            })
        else:
            missing.append(ep)
            coverage_report["missing_tests"].append({
                "method": method,
                "path": path,
                "summary": ep.get("summary", ""),
                "description": ep.get("description", ""),
                "tags": ep.get("tags", [])
            })
    
    # Calculate coverage percentage
    total_testable = len(covered) + len(missing)
    if total_testable > 0:
        coverage_report["coverage_percentage"] = round((len(covered) / total_testable) * 100, 2)
    
    # Coverage by method
    for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
        method_endpoints = [ep for ep in spec_endpoints if ep["method"] == method]
        method_tested = [ep for ep in covered if ep["method"] == method]
        method_missing = [ep for ep in missing if ep["method"] == method]
        
        if method_endpoints:
            method_coverage = round((len(method_tested) / len(method_endpoints)) * 100, 2)
            coverage_report["by_method"][method] = {
                "total": len(method_endpoints),
                "tested": len(method_tested),
                "missing": len(method_missing),
                "coverage": method_coverage
            }
    
    # Coverage by tag
    tags_dict = {}
    for ep in spec_endpoints:
        tags = ep.get("tags", ["untagged"])
        for tag in tags:
            if tag not in tags_dict:
                tags_dict[tag] = {"total": 0, "tested": 0, "missing": 0}
            tags_dict[tag]["total"] += 1
            
            normalized = normalize_path(ep["path"])
            if (ep["method"], normalized) in tested_set:
                tags_dict[tag]["tested"] += 1
            else:
                tags_dict[tag]["missing"] += 1
    
    for tag, stats in tags_dict.items():
        if stats["total"] > 0:
            stats["coverage"] = round((stats["tested"] / stats["total"]) * 100, 2)
    
    coverage_report["by_tag"] = tags_dict
    
    return coverage_report


def generate_coverage_report(coverage_report, output_file="reports/coverage_report.json"):
    """Generate a detailed coverage report"""
    report_text = f"""
{'='*80}
📊 TEST COVERAGE ANALYSIS REPORT
{'='*80}

Overall Coverage: {coverage_report['coverage_percentage']}%
Total Endpoints: {coverage_report['total_endpoints']}
Tested Endpoints: {len(coverage_report['covered_endpoints'])}
Missing Tests: {len(coverage_report['missing_tests'])}

{'='*80}
COVERAGE BY HTTP METHOD
{'='*80}
"""
    
    for method, stats in coverage_report["by_method"].items():
        report_text += f"""
{method}:
  Total: {stats['total']}
  Tested: {stats['tested']} ({stats['coverage']}%)
  Missing: {stats['missing']}
"""
    
    report_text += f"""
{'='*80}
COVERAGE BY TAG
{'='*80}
"""
    
    for tag, stats in sorted(coverage_report["by_tag"].items()):
        if stats["total"] > 0:
            report_text += f"""
{tag}:
  Total: {stats['total']}
  Tested: {stats['tested']} ({stats.get('coverage', 0)}%)
  Missing: {stats['missing']}
"""
    
    if coverage_report["missing_tests"]:
        report_text += f"""
{'='*80}
MISSING TESTS
{'='*80}
"""
        for missing in coverage_report["missing_tests"]:
            report_text += f"""
❌ {missing['method']} {missing['path']}
   Summary: {missing.get('summary', 'No summary')}
   Tags: {', '.join(missing.get('tags', []))}
"""
    
    report_text += f"""
{'='*80}
COVERED ENDPOINTS
{'='*80}
"""
    
    for covered in coverage_report["covered_endpoints"]:
        report_text += f"""
✅ {covered['method']} {covered['path']}
   {covered.get('summary', '')}
"""
    
    report_text += f"""
{'='*80}
RECOMMENDATIONS
{'='*80}
"""
    
    # Generate recommendations
    recommendations = []
    
    if coverage_report["coverage_percentage"] < 50:
        recommendations.append("⚠️  Coverage is below 50%. Consider adding more tests.")
    
    if coverage_report["by_method"].get("POST", {}).get("missing", 0) > 0:
        recommendations.append("📝 Missing POST tests - these are critical for creating test data.")
    
    if coverage_report["by_method"].get("GET", {}).get("missing", 0) > 0:
        recommendations.append("🔍 Missing GET tests - these verify data retrieval.")
    
    if coverage_report["by_method"].get("DELETE", {}).get("missing", 0) > 0:
        recommendations.append("🗑️  Missing DELETE tests - these verify cleanup.")
    
    # Find endpoints with parameters that might not be tested
    param_endpoints_missing = [ep for ep in coverage_report["missing_tests"] if "{" in ep["path"]]
    if param_endpoints_missing:
        recommendations.append(f"🔗 {len(param_endpoints_missing)} endpoints with path parameters are missing tests.")
    
    if not recommendations:
        recommendations.append("✅ Excellent coverage! All critical endpoints are tested.")
    
    for rec in recommendations:
        report_text += f"{rec}\n"
    
    report_text += f"\n{'='*80}\n"
    
    # Create reports directory if it doesn't exist
    if not os.path.isabs(output_file):
        reports_dir = project_root / "reports"
    else:
        reports_dir = Path(output_file).parent
    
    os.makedirs(reports_dir, exist_ok=True)
    
    # Save text report
    txt_file = reports_dir / "coverage_report.txt"
    with open(txt_file, "w") as f:
        f.write(report_text)
    
    # Save JSON report
    json_file = reports_dir / "coverage_report.json"
    with open(json_file, "w") as f:
        json.dump(coverage_report, f, indent=2)
    
    return report_text, str(json_file)


def main():
    """Main execution"""
    print("=" * 80)
    print("🔍 Agent 2: Test Coverage Reviewer")
    print("=" * 80)
    
    # Load API specification
    print(f"\n📡 Loading API specification from: {SWAGGER_URL}")
    try:
        spec = load_swagger_spec()
        print("✅ API specification loaded")
    except Exception as e:
        print(f"❌ Error loading API spec: {e}")
        return
    
    # Extract endpoints from spec
    print("📋 Extracting endpoints from API documentation...")
    spec_endpoints = extract_endpoints_from_spec(spec)
    print(f"✅ Found {len(spec_endpoints)} endpoints in API documentation")
    
    # Load generated tests
    print(f"\n📄 Loading generated tests from: {TEST_FILE}")
    test_content = load_generated_tests()
    if not test_content:
        return
    
    print("✅ Test file loaded")
    
    # Extract tests
    print("🔍 Analyzing test file...")
    tests, tested_endpoints = extract_tests_from_file(test_content)
    print(f"✅ Found {len(tests)} test cases")
    print(f"✅ Found {len(tested_endpoints)} unique endpoint calls")
    
    # Analyze coverage
    print("\n📊 Analyzing coverage...")
    coverage_report = analyze_coverage(spec_endpoints, tested_endpoints)
    
    # Generate report
    print("📝 Generating coverage report...")
    report_text, json_file = generate_coverage_report(coverage_report, str(project_root / "reports" / "coverage_report.json"))
    
    # Print report
    print(report_text)
    
    txt_file = json_file.replace(".json", ".txt")
    print(f"\n💾 Detailed JSON report saved to: {json_file}")
    print(f"📄 Text report saved to: {txt_file}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

