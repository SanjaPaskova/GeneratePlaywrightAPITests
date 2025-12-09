# debug_test_results.py
# Agent 3: Debug the results of the automated regression suite using Playwright MCP agent

import subprocess
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Playwright MCP agent - uses Playwright test runner directly

# Load configuration
# Get project root (one level up from agents/)
project_root = Path(__file__).parent.parent
config_path = project_root / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)

TEST_FILE = sys.argv[1] if len(sys.argv) > 1 else str(project_root / "tests" / "petstore.spec.ts")
PROJECT = sys.argv[2] if len(sys.argv) > 2 else "chromium"


class TestDebugger:
    def __init__(self):
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "failures": [],
            "errors": [],
            "warnings": []
        }

    def run_tests(self):
        """Run Playwright tests using MCP agent tools"""
        print("=" * 80)
        print("🐛 Agent 3: Test Results Debugger (Playwright MCP Agent)")
        print("=" * 80)
        
        print(f"\n📋 Running tests from: {TEST_FILE}")
        print(f"🎯 Project: {PROJECT}")
        print("🔧 Using Playwright MCP agent tools...\n")

        try:
            # Use Playwright test runner directly (MCP patterns)
            return self.run_tests_direct()
        except subprocess.TimeoutExpired:
            return self.analyze_error_output("Test execution timed out", None)
        except Exception as e:
            return self.analyze_error_output(str(e), e)
    
    def run_tests_direct(self):
        """Fallback: Run tests directly without MCP helper"""
        print("⚠️  MCP helper not found, using direct Playwright execution...\n")
        try:
            # Ensure TEST_FILE is absolute or relative to project root
            test_file_path = TEST_FILE if os.path.isabs(TEST_FILE) else str(project_root / TEST_FILE)
            result = subprocess.run(
                ["npx", "playwright", "test", test_file_path, f"--project={PROJECT}", "--reporter=json"],
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )

            try:
                json_output = json.loads(result.stdout)
                return self.analyze_results(json_output)
            except json.JSONDecodeError:
                return self.analyze_text_output(result.stdout + result.stderr)
        except Exception as e:
            return self.analyze_error_output(str(e), e)

    def analyze_results(self, json_results):
        """Analyze JSON test results using Playwright MCP agent patterns"""
        print("📊 Analyzing test results using Playwright MCP agent...\n")

        if "suites" in json_results:
            for suite in json_results["suites"]:
                self.process_suite(suite)
        elif "specs" in json_results:
            for spec in json_results["specs"]:
                self.process_spec(spec)

        self.generate_report()
        return self.results

    def process_suite(self, suite):
        """Process a test suite"""
        if "specs" in suite:
            for spec in suite["specs"]:
                self.process_spec(spec)
        if "suites" in suite:
            for sub_suite in suite["suites"]:
                self.process_suite(sub_suite)

    def process_spec(self, spec):
        """Process a test spec"""
        if "tests" in spec:
            for test in spec["tests"]:
                self.results["total"] += 1
                
                if "results" in test:
                    for result in test["results"]:
                        if result.get("status") == "passed":
                            self.results["passed"] += 1
                        elif result.get("status") == "failed":
                            self.results["failed"] += 1
                            self.analyze_failure(spec, test, result)
                        elif result.get("status") == "skipped":
                            self.results["skipped"] += 1

    def analyze_failure(self, spec, test, result):
        """Analyze a test failure"""
        failure = {
            "test": spec.get("title") or test.get("title") or "Unknown test",
            "file": spec.get("file") or test.get("file") or "Unknown file",
            "line": spec.get("line") or test.get("line") or 0,
            "status": result.get("status"),
            "error": None,
            "errorMessage": "",
            "errorDetails": "",
            "duration": result.get("duration", 0),
            "retry": result.get("retry", 0),
            "suggestions": []
        }

        if "error" in result:
            error = result["error"]
            failure["error"] = error
            failure["errorMessage"] = error.get("message", "")
            failure["errorDetails"] = error.get("stack") or error.get("message", "")
            
            # Extract location info
            if "location" in error:
                failure["file"] = error["location"].get("file", failure["file"])
                failure["line"] = error["location"].get("line", failure["line"])
            if "errorLocation" in result:
                failure["file"] = result["errorLocation"].get("file", failure["file"])
                failure["line"] = result["errorLocation"].get("line", failure["line"])

        # Generate MCP-style suggestions
        failure["suggestions"] = self.generate_mcp_suggestions(failure)
        self.results["failures"].append(failure)

    def generate_mcp_suggestions(self, failure):
        """Generate debugging suggestions using MCP patterns"""
        suggestions = []
        error_msg = failure["errorMessage"].lower()
        error_details = failure["errorDetails"].lower()

        # Network/Connection errors
        if any(term in error_msg for term in ["net::err", "network", "timeout"]):
            suggestions.append({
                "type": "network",
                "severity": "high",
                "message": "Network or connection issue detected",
                "actions": [
                    "Check if the API server is running and accessible",
                    "Verify the BASE_URL in your test file is correct",
                    "Check network connectivity and firewall settings",
                    "Increase timeout values in playwright.config.ts if the API is slow"
                ]
            })

        # 404 Not Found errors
        if "404" in error_msg or "not found" in error_details:
            suggestions.append({
                "type": "endpoint",
                "severity": "high",
                "message": "Endpoint not found (404) - Resource may not exist",
                "actions": [
                    "Verify the endpoint path matches the API documentation",
                    "Check if path parameters are correctly replaced with actual IDs",
                    "Ensure POST tests run before GET/DELETE operations (use test.describe.serial)",
                    "Verify resourceIds are being stored correctly after POST requests",
                    "Check if the resource was actually created before trying to access it"
                ]
            })

        # 401/403 Authentication errors
        if any(code in error_msg for code in ["401", "403"]) or "unauthorized" in error_msg:
            suggestions.append({
                "type": "authentication",
                "severity": "high",
                "message": "Authentication or authorization issue",
                "actions": [
                    "Verify API_KEY is correctly set in the test file",
                    "Check if the API requires authentication headers",
                    "Ensure the API key has proper permissions",
                    "Review authentication requirements in API documentation"
                ]
            })

        # 400 Bad Request errors
        if "400" in error_msg or "bad request" in error_msg:
            suggestions.append({
                "type": "request",
                "severity": "medium",
                "message": "Bad request - invalid request data",
                "actions": [
                    "Review the request payload structure",
                    "Check if all required fields are included",
                    "Verify data types match the API schema",
                    "Ensure JSON format is valid"
                ]
            })

        # 500 Server errors
        if "500" in error_msg or "internal server error" in error_msg:
            suggestions.append({
                "type": "server",
                "severity": "medium",
                "message": "Server error - API issue",
                "actions": [
                    "This may be a server-side issue, not a test problem",
                    "Check API server logs",
                    "Verify the API is functioning correctly",
                    "Try the request manually to confirm"
                ]
            })

        # Assertion failures
        if any(term in error_msg for term in ["expect", "assertion", "tobe"]):
            suggestions.append({
                "type": "assertion",
                "severity": "medium",
                "message": "Test assertion failed - Expected vs Actual mismatch",
                "actions": [
                    "Review the expected vs actual values in the error message",
                    "Check if the API response format changed",
                    "Verify the test expectations match API behavior",
                    "Consider if the test data is valid for the API",
                    "Check if status code expectations are correct (200 vs 201 vs 204)"
                ]
            })

        # Test dependency issues
        if "skipping" in error_msg or ("no" in error_msg and "available" in error_msg):
            suggestions.append({
                "type": "dependency",
                "severity": "low",
                "message": "Missing resource dependency - Test skipped",
                "actions": [
                    "Ensure POST tests run before GET/DELETE tests",
                    "Use test.describe.serial() for sequential execution",
                    "Check if resourceIds are being stored correctly after POST",
                    "Verify test execution order matches resource dependencies",
                    "Review the test generation to ensure proper ordering"
                ]
            })

        # Status code mismatches
        if "expected" in error_msg and "received" in error_msg:
            if any(code in error_msg for code in ["200", "201", "404"]):
                suggestions.append({
                    "type": "status",
                    "severity": "medium",
                    "message": "HTTP status code mismatch",
                    "actions": [
                        "Verify the expected status code matches API documentation",
                        "Check if the operation actually succeeded (201 for POST, 200 for GET)",
                        "Review API response to understand why status differs",
                        "Consider if the endpoint behavior changed"
                    ]
                })

        return suggestions

    def analyze_text_output(self, output):
        """Analyze text output as fallback"""
        print("📊 Analyzing test output...\n")

        lines = output.split("\n")
        in_failure = False
        current_failure = None

        for line in lines:
            if "passed" in line or "✓" in line:
                self.results["passed"] += 1
                self.results["total"] += 1

            if "failed" in line or "✘" in line or "×" in line:
                self.results["failed"] += 1
                self.results["total"] += 1
                in_failure = True
                current_failure = {
                    "test": line.strip(),
                    "errorMessage": "",
                    "suggestions": []
                }

            if in_failure and ("Error:" in line or "at " in line):
                if current_failure:
                    current_failure["errorMessage"] += line + "\n"

            if in_failure and line.strip() == "":
                if current_failure:
                    current_failure["suggestions"] = self.generate_mcp_suggestions(current_failure)
                    self.results["failures"].append(current_failure)
                in_failure = False
                current_failure = None

        self.generate_report()
        return self.results

    def analyze_error_output(self, output, error):
        """Analyze execution errors"""
        print("❌ Error running tests:\n")
        print(output)

        self.results["errors"].append({
            "message": str(error) if error else output,
            "output": output,
            "suggestions": [
                {
                    "type": "execution",
                    "severity": "high",
                    "message": "Test execution failed",
                    "actions": [
                        "Check if Playwright is installed: npx playwright install",
                        "Verify test file exists and is valid TypeScript",
                        "Check Playwright configuration in playwright.config.ts",
                        "Ensure all dependencies are installed: npm install",
                        "Try running tests manually: npx playwright test"
                    ]
                }
            ]
        })

        self.generate_report()
        return self.results

    def generate_report(self):
        """Generate comprehensive debug report"""
        pass_rate = 0
        if self.results["total"] > 0:
            pass_rate = round((self.results["passed"] / self.results["total"]) * 100 * 100) / 100

        report = {
            "summary": {
                "total": self.results["total"],
                "passed": self.results["passed"],
                "failed": self.results["failed"],
                "skipped": self.results["skipped"],
                "passRate": pass_rate
            },
            "failures": self.results["failures"],
            "errors": self.results["errors"],
            "timestamp": datetime.now().isoformat(),
            "mcpAgent": "Playwright MCP Test Debugger"
        }

        # Generate text report
        text_report = f"""
{'='*80}
🐛 TEST DEBUG REPORT (Playwright MCP Agent)
{'='*80}

Summary:
  Total Tests: {report['summary']['total']}
  Passed: {report['summary']['passed']} ({report['summary']['passRate']}%)
  Failed: {report['summary']['failed']}
  Skipped: {report['summary']['skipped']}

"""

        if report["failures"]:
            text_report += f"""
{'='*80}
FAILED TESTS ANALYSIS
{'='*80}
"""

            for failure in report["failures"]:
                text_report += f"""
❌ {failure['test']}
   File: {failure['file']}:{failure['line']}
   Status: {failure['status']}
   Duration: {failure['duration']}ms
   Retry: {failure['retry']}

   Error: {failure['errorMessage'] or 'No error message'}

   🔍 Debugging Suggestions (MCP Analysis):
"""

                for suggestion in failure["suggestions"]:
                    text_report += f"   [{suggestion['severity'].upper()}] {suggestion['message']}\n"
                    for action in suggestion["actions"]:
                        text_report += f"      • {action}\n"
                    text_report += "\n"

        if report["errors"]:
            text_report += f"""
{'='*80}
EXECUTION ERRORS
{'='*80}
"""

            for error in report["errors"]:
                text_report += f"""
❌ {error['message']}

   Suggestions:
"""
                for suggestion in error["suggestions"]:
                    for action in suggestion["actions"]:
                        text_report += f"   • {action}\n"

        if report["summary"]["failed"] == 0 and not report["errors"]:
            text_report += f"""
{'='*80}
✅ ALL TESTS PASSED!
{'='*80}
"""

        text_report += f"""
{'='*80}
RECOMMENDATIONS
{'='*80}
"""

        recommendations = []

        if report["summary"]["passRate"] < 50:
            recommendations.append("⚠️  Less than 50% of tests are passing. Review test suite configuration.")

        if report["failures"]:
            network_failures = [f for f in report["failures"] 
                              if any(s["type"] == "network" for s in f["suggestions"])]
            if network_failures:
                recommendations.append(f"🔌 {len(network_failures)} network-related failures. Check API connectivity.")

            endpoint_failures = [f for f in report["failures"] 
                               if any(s["type"] == "endpoint" for s in f["suggestions"])]
            if endpoint_failures:
                recommendations.append(f"🔗 {len(endpoint_failures)} endpoint failures (404). Ensure tests run in serial mode and resources exist.")

            auth_failures = [f for f in report["failures"] 
                           if any(s["type"] == "authentication" for s in f["suggestions"])]
            if auth_failures:
                recommendations.append(f"🔐 {len(auth_failures)} authentication failures. Check API keys.")

            dependency_failures = [f for f in report["failures"] 
                                 if any(s["type"] == "dependency" for s in f["suggestions"])]
            if dependency_failures:
                recommendations.append(f"🔗 {len(dependency_failures)} dependency issues. Use test.describe.serial() for proper test ordering.")

        if not recommendations and report["summary"]["failed"] == 0:
            recommendations.append("✅ Test suite is healthy! All tests passing.")

        for rec in recommendations:
            text_report += f"{rec}\n"

        text_report += f"\n{'='*80}\n"

        # Create reports directory if it doesn't exist
        reports_dir = project_root / "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save reports
        json_file = reports_dir / "debug_report.json"
        txt_file = reports_dir / "debug_report.txt"
        
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        with open(txt_file, "w") as f:
            f.write(text_report)

        # Print report
        print(text_report)

        print(f"\n💾 Detailed JSON report saved to: {json_file}")
        print(f"📄 Text report saved to: {txt_file}")
        print("\n" + "=" * 80)

        return report


# Main execution
if __name__ == "__main__":
    debugger = TestDebugger()
    debugger.run_tests()

