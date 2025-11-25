"""
Test package for the Logistics Multi-Agent System.

This package contains comprehensive tests for:
- Agent creation and functionality
- Multi-agent orchestration
- Tool execution and validation
- System integration tests

Usage:
    from tests.test_agents import main_enhanced_testing
    main_enhanced_testing(factory)
"""

from .test_agents import (
    main_enhanced_testing,
    run_test_suite,
    create_test_agents,
    run_interactive_tests
)

__all__ = [
    'main_enhanced_testing',
    'run_test_suite', 
    'create_test_agents',
    'run_interactive_tests'
]