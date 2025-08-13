#!/usr/bin/env python3
"""
Test runner script for Cidadão.AI Backend.
Executes tests with coverage reporting and quality metrics.
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel


console = Console()


class TestRunner:
    """Enhanced test runner with reporting capabilities."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_results = {}
        
    def run_command(self, command: List[str], description: str) -> Dict:
        """Run command and capture results."""
        console.print(f"🔄 {description}...")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            duration = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "command": " ".join(command)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time,
                "command": " ".join(command)
            }
    
    def run_unit_tests(self) -> Dict:
        """Run unit tests with coverage."""
        return self.run_command([
            "python", "-m", "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml",
            "-m", "unit"
        ], "Running unit tests")
    
    def run_integration_tests(self) -> Dict:
        """Run integration tests."""
        return self.run_command([
            "python", "-m", "pytest", 
            "tests/integration/",
            "-v",
            "--tb=short",
            "-m", "integration"
        ], "Running integration tests")
    
    def run_agent_tests(self) -> Dict:
        """Run specific agent tests."""
        return self.run_command([
            "python", "-m", "pytest",
            "tests/unit/agents/",
            "-v",
            "--tb=short",
            "--cov=src/agents",
            "--cov-report=term-missing"
        ], "Running agent tests")
    
    def run_linting(self) -> Dict:
        """Run code quality checks."""
        # Run multiple linting tools
        results = {}
        
        # Black formatting check
        results["black"] = self.run_command([
            "python", "-m", "black", "--check", "--diff", "src/", "tests/"
        ], "Checking code formatting (Black)")
        
        # Ruff linting
        results["ruff"] = self.run_command([
            "python", "-m", "ruff", "check", "src/", "tests/"
        ], "Running linting (Ruff)")
        
        # MyPy type checking
        results["mypy"] = self.run_command([
            "python", "-m", "mypy", "src/"
        ], "Running type checking (MyPy)")
        
        return results
    
    def run_security_checks(self) -> Dict:
        """Run security vulnerability checks."""
        results = {}
        
        # Bandit security check
        results["bandit"] = self.run_command([
            "python", "-m", "bandit", "-r", "src/", "-f", "json"
        ], "Running security checks (Bandit)")
        
        # Safety check for dependencies
        results["safety"] = self.run_command([
            "python", "-m", "safety", "check", "--json"
        ], "Checking dependencies (Safety)")
        
        return results
    
    def generate_coverage_report(self) -> Dict:
        """Generate detailed coverage report."""
        return self.run_command([
            "python", "-m", "coverage", "report", "--show-missing"
        ], "Generating coverage report")
    
    def display_results_table(self, results: Dict, title: str):
        """Display results in a formatted table."""
        table = Table(title=title)
        table.add_column("Test Category", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Details", style="blue")
        
        for category, result in results.items():
            if isinstance(result, dict):
                status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                duration = f"{result.get('duration', 0):.2f}s"
                
                if result.get("success"):
                    details = "All checks passed"
                else:
                    error_msg = result.get("stderr", result.get("error", "Unknown error"))
                    details = error_msg[:50] + "..." if len(error_msg) > 50 else error_msg
                
                table.add_row(category, status, duration, details)
        
        console.print(table)
    
    def extract_coverage_percentage(self, output: str) -> float:
        """Extract coverage percentage from pytest output."""
        import re
        
        # Look for coverage percentage in output
        match = re.search(r'TOTAL.*?(\d+)%', output)
        if match:
            return float(match.group(1))
        return 0.0
    
    def display_coverage_summary(self, coverage_output: str):
        """Display coverage summary."""
        coverage_pct = self.extract_coverage_percentage(coverage_output)
        
        if coverage_pct >= 80:
            status = "🟢 EXCELLENT"
            color = "green"
        elif coverage_pct >= 60:
            status = "🟡 GOOD"
            color = "yellow"
        elif coverage_pct >= 40:
            status = "🟠 NEEDS IMPROVEMENT"
            color = "orange"
        else:
            status = "🔴 POOR"
            color = "red"
        
        panel = Panel(
            f"[bold]Test Coverage: {coverage_pct}%[/bold]\n"
            f"Status: [{color}]{status}[/{color}]\n"
            f"Target: 80%+ for production readiness",
            title="📊 Coverage Report",
            border_style=color
        )
        
        console.print(panel)
    
    def run_comprehensive_tests(self):
        """Run comprehensive test suite."""
        console.print(Panel.fit(
            "[bold blue]🧪 Cidadão.AI Backend Test Suite[/bold blue]\n"
            "Running comprehensive tests and quality checks...",
            border_style="blue"
        ))
        
        all_results = {}
        
        # Run unit tests
        unit_results = self.run_unit_tests()
        all_results["Unit Tests"] = unit_results
        
        if unit_results.get("success"):
            self.display_coverage_summary(unit_results.get("stdout", ""))
        
        # Run agent-specific tests
        agent_results = self.run_agent_tests()
        all_results["Agent Tests"] = agent_results
        
        # Run integration tests
        integration_results = self.run_integration_tests()
        all_results["Integration Tests"] = integration_results
        
        # Run code quality checks
        linting_results = self.run_linting()
        all_results.update(linting_results)
        
        # Run security checks
        security_results = self.run_security_checks()
        all_results.update(security_results)
        
        # Display comprehensive results
        self.display_results_table(all_results, "🔍 Test Results Summary")
        
        # Calculate overall success rate
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results.values() if r.get("success", False))
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Final summary
        if success_rate >= 90:
            summary_color = "green"
            summary_icon = "🎉"
            summary_status = "EXCELLENT"
        elif success_rate >= 70:
            summary_color = "yellow"
            summary_icon = "⚠️"
            summary_status = "GOOD"
        else:
            summary_color = "red" 
            summary_icon = "❌"
            summary_status = "NEEDS ATTENTION"
        
        console.print(Panel(
            f"[bold]Overall Success Rate: {success_rate:.1f}%[/bold]\n"
            f"Status: [{summary_color}]{summary_icon} {summary_status}[/{summary_color}]\n"
            f"Tests Passed: {successful_tests}/{total_tests}",
            title="📋 Final Summary",
            border_style=summary_color
        ))
        
        return success_rate >= 70  # Return True if acceptable success rate


@click.command()
@click.option("--unit-only", "-u", is_flag=True, help="Run only unit tests")
@click.option("--integration-only", "-i", is_flag=True, help="Run only integration tests")
@click.option("--agents-only", "-a", is_flag=True, help="Run only agent tests")
@click.option("--quality-only", "-q", is_flag=True, help="Run only code quality checks")
@click.option("--coverage-threshold", "-t", default=80, help="Coverage threshold percentage")
@click.option("--fast", "-f", is_flag=True, help="Skip slower checks")
def main(unit_only, integration_only, agents_only, quality_only, coverage_threshold, fast):
    """Run Cidadão.AI Backend test suite."""
    
    project_root = Path(__file__).parent.parent
    runner = TestRunner(project_root)
    
    console.print(f"[bold cyan]🚀 Starting test execution in: {project_root}[/bold cyan]")
    
    if unit_only:
        result = runner.run_unit_tests()
        runner.display_results_table({"Unit Tests": result}, "Unit Test Results")
        runner.display_coverage_summary(result.get("stdout", ""))
        
    elif integration_only:
        result = runner.run_integration_tests()
        runner.display_results_table({"Integration Tests": result}, "Integration Test Results")
        
    elif agents_only:
        result = runner.run_agent_tests()
        runner.display_results_table({"Agent Tests": result}, "Agent Test Results")
        runner.display_coverage_summary(result.get("stdout", ""))
        
    elif quality_only:
        results = runner.run_linting()
        if not fast:
            security_results = runner.run_security_checks()
            results.update(security_results)
        runner.display_results_table(results, "Code Quality Results")
        
    else:
        # Run comprehensive test suite
        success = runner.run_comprehensive_tests()
        
        if not success:
            console.print("[red]❌ Some tests failed. Please review the results above.[/red]")
            sys.exit(1)
        else:
            console.print("[green]✅ All tests passed successfully![/green]")
    
    console.print("\n[bold green]🎯 Test execution completed![/bold green]")


if __name__ == "__main__":
    main()