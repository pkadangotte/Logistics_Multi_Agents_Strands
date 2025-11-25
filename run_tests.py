#!/usr/bin/env python3
"""
Test runner script for Logistics Multi-Agent System.
Allows running individual test modules or all tests.
"""

import sys
import os
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} FAILED (exit code: {result.returncode})")
        return False
    else:
        print(f"✅ {description} PASSED")
        return True


def main():
    """Main test runner function."""
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [test_module|all|coverage]")
        print("\nAvailable test modules:")
        print("  - agent_creation")
        print("  - inventory_agent") 
        print("  - fleet_agent")
        print("  - approval_agent")
        print("  - orchestration")
        print("  - all (run all tests)")
        print("  - coverage (run all tests with coverage)")
        return
    
    test_option = sys.argv[1].lower()
    
    # Test module mapping
    test_modules = {
        'agent_creation': 'tests/test_agent_creation.py',
        'inventory_agent': 'tests/test_inventory_agent.py', 
        'fleet_agent': 'tests/test_fleet_agent.py',
        'approval_agent': 'tests/test_approval_agent.py',
        'orchestration': 'tests/test_orchestration.py'
    }
    
    success = True
    
    if test_option == 'all':
        # Run all test modules individually
        for module_name, module_path in test_modules.items():
            cmd = ['python', '-m', 'pytest', module_path, '-v']
            if not run_command(cmd, f"{module_name.replace('_', ' ').title()} Tests"):
                success = False
    
    elif test_option == 'coverage':
        # Run all tests with coverage
        cmd = ['python', '-m', 'pytest', 'tests/', '--cov=Agents', '--cov-report=term-missing', '--cov-report=html']
        success = run_command(cmd, "All Tests with Coverage")
        
        if success:
            print(f"\n📊 Coverage report generated in htmlcov/index.html")
    
    elif test_option in test_modules:
        # Run specific test module
        module_path = test_modules[test_option]
        cmd = ['python', '-m', 'pytest', module_path, '-v']
        success = run_command(cmd, f"{test_option.replace('_', ' ').title()} Tests")
    
    else:
        print(f"❌ Unknown test option: {test_option}")
        success = False
    
    if success:
        print(f"\n🎉 All requested tests completed successfully!")
    else:
        print(f"\n💥 Some tests failed. Check output above for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()