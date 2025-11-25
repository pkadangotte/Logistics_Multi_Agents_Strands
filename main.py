#!/usr/bin/env python3
"""
Main Entry Point for Logistics Multi-Agent System
Provides options for different testing modes including agent discovery functionality.
"""

import sys
import os

# Add the Agents directory to the Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'Agents'))

from data_setup import initialize_dataframes
from agent_factory import initialize_agent_factory
from data_providers.inventory_data_provider import InventoryDataProvider
from data_providers.fleet_data_provider import FleetDataProvider
from data_providers.approval_data_provider import ApprovalDataProvider

# Import test functions
sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
from test_agents import main_enhanced_testing, run_test_suite, display_test_menu


def display_main_menu():
    """Display main application menu."""
    print("🚀 LOGISTICS MULTI-AGENT SYSTEM")
    print("=" * 70)
    print("Main Menu Options:")
    print("1. Run Enhanced Test Suite (Interactive)")
    print("2. Quick Agent Creation Test")
    print("3. Agent Discovery & Communication Test")
    print("4. Complex Orchestration Test")
    print("5. Emergency Simulation Test") 
    print("6. Full Integration Test Suite")
    print("7. Production Mode (Create Agents Only)")
    print("0. Exit")
    print("=" * 70)


def run_quick_creation_test(factory):
    """Quick test of agent creation only."""
    print("\n⚡ QUICK AGENT CREATION TEST")
    print("=" * 70)
    
    try:
        # Test model creation
        print("1. Testing Ollama Model Creation...")
        model = factory.create_ollama_model()
        print("   ✅ Model created successfully")
        
        # Test each agent type
        agent_types = [
            ("inventory", "TestInventoryAgent"),
            ("fleet", "TestFleetAgent"), 
            ("approval", "TestApprovalAgent"),
            ("orchestrator", "TestOrchestratorAgent")
        ]
        
        created_agents = {}
        for agent_type, name in agent_types:
            print(f"2. Testing {agent_type.title()} Agent Creation...")
            try:
                agent = factory.create_agent(agent_type=agent_type, name=name)
                created_agents[agent_type] = agent
                info = agent.get_info()
                print(f"   ✅ {name} - {info['total_tools']} tools")
            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")
                created_agents[agent_type] = None
        
        print(f"\n✅ Quick test completed! {len([a for a in created_agents.values() if a])} agents created successfully.")
        return created_agents
        
    except Exception as e:
        print(f"❌ Quick test failed: {str(e)}")
        return None


def create_production_agents(factory):
    """Create agents for production use without testing."""
    print("\n🏭 PRODUCTION MODE - Creating Agents")
    print("=" * 70)
    
    production_agents = {}
    
    # Production agent configurations
    configs = [
        ("inventory", "ProductionInventoryAgent", "📦 Inventory Management Agent"),
        ("fleet", "ProductionFleetAgent", "🚛 Fleet Management Agent"),
        ("approval", "ProductionApprovalAgent", "⚖️ Approval Workflow Agent"),
        ("orchestrator", "ProductionOrchestrator", "🎯 Master Logistics Orchestrator")
    ]
    
    for agent_type, name, description in configs:
        try:
            agent = factory.create_agent(agent_type=agent_type, name=name)
            production_agents[agent_type] = agent
            info = agent.get_info()
            print(f"✅ {description}")
            print(f"   Name: {info['name']}")
            print(f"   Tools: {info['total_tools']}")
            print()
        except Exception as e:
            print(f"❌ Failed to create {description}: {str(e)}")
            production_agents[agent_type] = None
    
    print("🎯 Production agents ready for logistics operations!")
    return production_agents


def initialize_system():
    """Initialize the logistics system components."""
    print("🌟 INITIALIZING LOGISTICS MULTI-AGENT SYSTEM")
    print("=" * 70)
    
    try:
        print("📊 Setting up logistics data...")
        inventory_df, agv_df, routes_df, approval_df = initialize_dataframes()
        
        # Create data managers
        inventory_manager = InventoryDataProvider(inventory_df)
        fleet_manager = FleetDataProvider(agv_df, routes_df)
        approval_manager = ApprovalDataProvider(approval_df)
        print("✅ Data setup completed")
        
        print("🏭 Initializing agent factory...")
        factory = initialize_agent_factory(inventory_manager, fleet_manager, approval_manager)
        print("✅ Agent factory initialized")
        
        return factory
        
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        print("\nPlease ensure:")
        print("1. All dependencies are installed: pip install -r requirements.txt")
        print("2. Ollama is running: ollama serve")
        print("3. Required model is available: ollama pull qwen2.5:7b")
        raise


def main():
    """Main function with menu options."""
    
    # Initialize system
    try:
        factory = initialize_system()
    except Exception:
        return 1
    
    # Main menu loop
    while True:
        display_main_menu()
        
        try:
            choice = int(input("Enter your choice (0-7): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            continue
        
        if choice == 0:
            print("👋 Goodbye! Thanks for using the Logistics Multi-Agent System!")
            break
            
        elif choice == 1:
            main_enhanced_testing(factory)
            
        elif choice == 2:
            run_quick_creation_test(factory)
            
        elif choice == 3:
            run_test_suite(factory, 3)  # Agent Discovery Test
            
        elif choice == 4:
            run_test_suite(factory, 4)  # Complex Orchestration Test
            
        elif choice == 5:
            run_test_suite(factory, 5)  # Emergency Simulation Test
            
        elif choice == 6:
            run_test_suite(factory, 6)  # Full Integration Test Suite
            
        elif choice == 7:
            create_production_agents(factory)
            
        else:
            print("❌ Invalid choice. Please select 0-7.")
        
        # Ask if user wants to continue
        print("\n" + "=" * 70)
        continue_choice = input("Return to main menu? (y/n): ").lower().strip()
        if continue_choice not in ['y', 'yes']:
            print("👋 Goodbye!")
            break
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)