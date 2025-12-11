# debug_test_results.py
# Script: Debug the results of the automated regression suite using Playwright

import subprocess
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Ensure we can import project modules when running from any cwd
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.config_loader import load_config

# Uses Playwright test runner directly

config = load_config()

# Optional LLM setup
LLM_PROVIDER = config.get("llm_provider", "openai")
OPENAI_API_KEY = config.get("openai_api_key")
ANTHROPIC_API_KEY = config.get("anthropic_api_key")
MODEL = config.get("model", "gpt-4o")

client = None
if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        client = None
elif LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception:
        client = None

TEST_FILE = sys.argv[1] if len(sys.argv) > 1 else str(project_root / "tests" / "spec.ts")
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
        """Run Playwright tests and collect results"""
        print("=" * 80)
        print("🐛 Test Results Debugger")
        print("=" * 80)
        
        print(f"\n📋 Running tests from: {TEST_FILE}")
        print(f"🎯 Project: {PROJECT}")
        print("🔧 Using Playwright test runner...\n")

        try:
            # Use Playwright test runner directly (MCP patterns)
            return self.run_tests_direct()
        except subprocess.TimeoutExpired:
            return self.analyze_error_output("Test execution timed out", None)
        except Exception as e:
            return self.analyze_error_output(str(e), e)
    
    def run_tests_direct(self):
        """Run tests directly with Playwright JSON reporter"""
        print("▶️  Running Playwright tests directly...\n")
        try:
            # Ensure TEST_FILE is absolute or relative to project root
            test_file_path = TEST_FILE if os.path.isabs(TEST_FILE) else str(project_root / TEST_FILE)
            # If the path doesn't exist, default to the tests/ folder
            if not os.path.exists(test_file_path):
                test_file_path = str(project_root / "tests")
            cmd = ["npx", "playwright", "test", test_file_path, "--reporter=json"]
            # Only add project flag if explicitly provided
            if PROJECT:
                cmd.append(f"--project={PROJECT}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )

            try:
                json_output = json.loads(result.stdout)
                # If no suites/specs found, treat as discovery failure
                if not json_output.get("suites") and not json_output.get("specs"):
                    return self.analyze_error_output("No tests discovered. Check file path or Playwright configuration.", None)
                return self.analyze_results(json_output)
            except json.JSONDecodeError:
                # Fallback: analyze raw text output
                output_text = (result.stdout or "") + (result.stderr or "")
                if not output_text.strip():
                    return self.analyze_error_output("No output from Playwright. Ensure Playwright is installed and tests exist.", None)
                return self.analyze_text_output(output_text)
        except Exception as e:
            return self.analyze_error_output(str(e), e)

    def analyze_results(self, json_results):
        """Analyze JSON test results and produce a friendly report"""
        print("📊 Analyzing test results...\n")

        if "suites" in json_results:
            for suite in json_results["suites"]:
                self.process_suite(suite)
        elif "specs" in json_results:
            for spec in json_results["specs"]:
                self.process_spec(spec)

        # Optionally use LLM to summarize and suggest fixes
        self.apply_llm_analysis()
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

        self.apply_llm_analysis()
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

        self.apply_llm_analysis()
        self.generate_report()
        return self.results

    def apply_llm_analysis(self):
        """Use LLM (if configured) to provide deeper insights and suggestions."""
        if not client:
            return

        try:
            summary = {
                "total": self.results["total"],
                "passed": self.results["passed"],
                "failed": self.results["failed"],
                "skipped": self.results["skipped"],
            }
            failures = self.results.get("failures", [])
            errors = self.results.get("errors", [])

            # Limit payload size
            failures_brief = [
                {
                    "test": f.get("test"),
                    "file": f.get("file"),
                    "status": f.get("status"),
                    "errorMessage": (f.get("errorMessage") or "")[:800],
                }
                for f in failures[:30]
            ]
            errors_brief = [
                {
                    "message": e.get("message"),
                    "output": (e.get("output") or "")[:800],
                }
                for e in errors[:10]
            ]

            system = (
                "You are an expert Playwright API test debugger. "
                "Analyze failures and propose concrete, actionable fixes. "
                "Classify issues (network, endpoint, auth, request schema, server, assertion, dependency). "
                "Suggest code changes (timeouts, headers, payloads), test sequencing, and config tweaks."
            )
            user = (
                f"Summary: {json.dumps(summary)}\n\n"
                f"Failures: {json.dumps(failures_brief, indent=2)}\n\n"
                f"Errors: {json.dumps(errors_brief, indent=2)}\n\n"
                "Return a concise analysis with bullets: Root Cause, Evidence, Fixes, Next Checks."
            )

            ai_text = None
            if LLM_PROVIDER == "anthropic":
                try:
                    resp = client.messages.create(
                        model=MODEL,
                        max_tokens=1200,
                        temperature=0,
                        system=system,
                        messages=[{"role": "user", "content": user}],
                    )
                    ai_text = resp.content[0].text
                except Exception:
                    ai_text = None
            elif LLM_PROVIDER == "openai":
                try:
                    resp = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        temperature=0,
                        max_tokens=1200,
                    )
                    ai_text = resp.choices[0].message.content
                except Exception:
                    ai_text = None

            if ai_text:
                # Attach AI analysis to results for inclusion in report
                self.results.setdefault("aiAnalysis", ai_text)
        except Exception:
            # Non-blocking
            pass

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
            "toolName": "Playwright Test Debugger",
            "ai": self.results.get("aiAnalysis")
        }

        # Generate text report
        text_report = f"""
{'='*80}
🐛 TEST DEBUG REPORT
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

    🔍 Debugging Suggestions:
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

        # Only show "ALL TESTS PASSED" when at least one test ran
        if report["summary"]["failed"] == 0 and not report["errors"] and report["summary"]["total"] > 0:
            text_report += f"""
{'='*80}
✅ ALL TESTS PASSED!
{'='*80}
"""

        # AI section
        if report.get("ai"):
            text_report += f"""
{'='*80}
RECOMMENDATIONS
{'='*80}
    {report.get("ai")}
    """
        
        recommendations = []

        # If no tests were discovered, provide discovery guidance and skip pass-rate warning
        if report["summary"]["total"] == 0:
            recommendations.append("❗ No tests discovered. Verify the test file path and Playwright configuration.")
            recommendations.append("• Ensure the file exists and matches Playwright's test patterns.")
            recommendations.append("• Try running: npx playwright test tests --reporter=json")
            recommendations.append("• If using TypeScript, ensure ts-node is not required for API tests.")
        else:
            if report["summary"]["passRate"] < 50:
                recommendations.append("⚠️  Less than 50% of tests are passing. Review test suite configuration.")

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

