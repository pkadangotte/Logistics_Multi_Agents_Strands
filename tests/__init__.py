"""
Test package for the Logistics Multi-Agent System.

This package contains comprehensive pytest-based tests for:
- Agent creation and functionality (test_agent_creation.py)
- Individual agent testing (test_inventory_agent.py, test_fleet_agent.py, test_approval_agent.py)
- Multi-agent orchestration and integration (test_orchestration.py)
- Shared fixtures and utilities (conftest.py)

Usage:
    # Run individual test modules
    python -m pytest tests/test_agent_creation.py -v
    
    # Run all tests
    python -m pytest tests/ -v
    
    # Run with coverage
    python -m pytest tests/ --cov=Agents
"""

# Test package initialization - no specific imports needed for pytest