#!/usr/bin/env python3
"""
Script to run comprehensive security tests for Cidadão.AI
Tests OAuth, audit logging, security middleware, and more
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and capture output."""
    print(f"\n🔍 {description}")
    print(f"Running: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {str(e)}")
        return False


def main():
    """Run security tests."""
    
    parser = argparse.ArgumentParser(description="Run Cidadão.AI security tests")
    parser.add_argument(
        "--test-type",
        choices=["unit", "integration", "security", "all"],
        default="security",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    
    args = parser.parse_args()
    
    # Set up environment
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🛡️  Cidadão.AI Security Test Suite")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print(f"Test type: {args.test_type}")
    print(f"Verbose: {args.verbose}")
    print(f"Coverage: {args.coverage}")
    
    # Check if virtual environment is activated
    if not os.getenv("VIRTUAL_ENV"):
        print("⚠️  Warning: No virtual environment detected")
        print("   Consider activating a virtual environment first")
    
    success_count = 0
    total_tests = 0
    
    # Base pytest command
    pytest_cmd = "python -m pytest"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    if args.coverage:
        pytest_cmd += " --cov=src --cov-report=html --cov-report=term"
    
    # Security tests
    if args.test_type in ["security", "all"]:
        print("\n🔐 SECURITY TESTS")
        print("=" * 40)
        
        # OAuth security tests
        total_tests += 1
        if run_command(
            f"{pytest_cmd} tests/security/test_oauth.py",
            "OAuth2 Security Tests"
        ):
            success_count += 1
        
        # Audit logging tests
        total_tests += 1
        if run_command(
            f"{pytest_cmd} tests/security/test_audit.py",
            "Audit Logging Tests"
        ):
            success_count += 1
        
        # Security middleware tests
        total_tests += 1
        if run_command(
            f"{pytest_cmd} tests/security/test_security_middleware.py",
            "Security Middleware Tests"
        ):
            success_count += 1
    
    # Unit tests
    if args.test_type in ["unit", "all"]:
        print("\n🧪 UNIT TESTS")
        print("=" * 40)
        
        total_tests += 1
        if run_command(
            f"{pytest_cmd} tests/unit/",
            "Unit Tests"
        ):
            success_count += 1
    
    # Integration tests
    if args.test_type in ["integration", "all"]:
        print("\n🔗 INTEGRATION TESTS")
        print("=" * 40)
        
        total_tests += 1
        if run_command(
            f"{pytest_cmd} tests/integration/",
            "Integration Tests"
        ):
            success_count += 1
    
    # Security tools
    if args.test_type in ["security", "all"]:
        print("\n🔍 SECURITY ANALYSIS")
        print("=" * 40)
        
        # Safety check for known vulnerabilities
        total_tests += 1
        if run_command(
            "python -m safety check",
            "Safety - Known Vulnerabilities Check"
        ):
            success_count += 1
        
        # Bandit security linting
        total_tests += 1
        if run_command(
            "python -m bandit -r src/ -f json -o bandit-report.json",
            "Bandit - Security Issues Scan"
        ):
            success_count += 1
        
        # Type checking with MyPy
        total_tests += 1
        if run_command(
            "python -m mypy src/ --ignore-missing-imports",
            "MyPy - Type Checking"
        ):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total test suites: {total_tests}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_tests - success_count}")
    print(f"Success rate: {(success_count/total_tests*100):.1f}%" if total_tests > 0 else "0%")
    
    if success_count == total_tests:
        print("\n🎉 All security tests passed!")
        if args.coverage:
            print("📈 Coverage report generated in htmlcov/")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_tests - success_count} test suite(s) failed")
        print("🔧 Please review the failures above and fix the issues")
        sys.exit(1)


if __name__ == "__main__":
    main()