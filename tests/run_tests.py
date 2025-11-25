#!/usr/bin/env python3
"""
Test Runner for Logistics Multi-Agent System

This script provides an easy way to run the comprehensive test suite
for the logistics multi-agent system.

Usage:
    python run_tests.py

Or from the root directory:
    python tests/run_tests.py
"""

import sys
import os

# Add the Agents directory to the Python path
agents_dir = os.path.join(os.path.dirname(__file__), '..', 'Agents')
sys.path.insert(0, agents_dir)

def main():
    """Main test runner function."""
    try:
        # Import required modules
        from agent_factory import initialize_agent_factory
        from data_setup import setup_all_data_managers
        from test_agents import main_enhanced_testing
        
        print("🚀 LOGISTICS MULTI-AGENT SYSTEM - TEST RUNNER")
        print("=" * 60)
        print("Initializing system components...")
        
        # Setup data managers
        print("📊 Setting up data managers...")
        inv_mgr, fleet_mgr, approval_mgr = setup_all_data_managers()
        
        # Initialize agent factory
        print("🏭 Initializing agent factory...")
        factory = initialize_agent_factory(inv_mgr, fleet_mgr, approval_mgr)
        
        print("✅ System initialization complete!")
        print("🧪 Starting test suite...\n")
        
        # Run the comprehensive test suite
        result = main_enhanced_testing(factory)
        
        if result:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n⚠️ Some tests may have encountered issues.")
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nMake sure you're running from the correct directory and all dependencies are installed.")
        print("Required: pandas, strands, ollama")
        
    except Exception as e:
        print(f"❌ Error during test execution: {e}")
        print("\nPlease check:")
        print("1. Ollama is running: ollama serve")
        print("2. Model is available: ollama pull qwen2.5:7b")
        print("3. All dependencies are installed")
        
        return False
        
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)