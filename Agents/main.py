"""
Enhanced Main Entry Point for Logistics Multi-Agent System
Provides options for different testing modes including agent discovery functionality.
"""

from requirements import *
from data_setup import initialize_dataframes
from agent_factory import initialize_agent_factory
from test_agents import main_enhanced_testing, run_test_suite, display_test_menu
from inventory_data_provider import InventoryDataProvider
from fleet_data_provider import FleetDataProvider
from approval_data_provider import ApprovalDataProvider


def display_main_menu():
    """Display main application menu."""
    print("🚀 LOGISTICS MULTI-AGENT SYSTEM")
    print("=" * 70)
    print("Main Menu Options:")
    print("1. Run Original Test Suite (Legacy)")
    print("2. Run Enhanced Test Suite (Interactive)")
    print("3. Quick Agent Creation Test")
    print("4. Agent Discovery & Communication Test")
    print("5. Complex Orchestration Test")
    print("6. Emergency Simulation Test") 
    print("7. Custom Test Menu")
    print("8. Production Mode (Create Agents Only)")
    print("0. Exit")
    print("=" * 70)


def run_original_tests(factory):
    """Run the original test suite (now using enhanced system)."""
    print("\n🧪 RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    # Run full integration tests using the enhanced system
    agents = run_test_suite(factory, 6)  # Full Integration Test Suite
    
    return agents


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


def run_single_test(factory, test_number: int):
    """Run a specific test by number."""
    if test_number in [4, 5, 6]:
        # These are enhanced tests
        return run_test_suite(factory, test_number - 3)
    else:
        print(f"❌ Invalid test number: {test_number}")
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


def main():
    """Enhanced main function with menu options."""
    print("🌟 INITIALIZING LOGISTICS MULTI-AGENT SYSTEM")
    print("=" * 70)
    
    # Setup data and factory
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
        
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        return
    
    # Main menu loop
    while True:
        display_main_menu()
        
        try:
            choice = int(input("Enter your choice (0-8): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            continue
        
        if choice == 0:
            print("👋 Goodbye! Thanks for using the Logistics Multi-Agent System!")
            break
            
        elif choice == 1:
            run_original_tests(factory)
            
        elif choice == 2:
            main_enhanced_testing(factory)
            
        elif choice == 3:
            run_quick_creation_test(factory)
            
        elif choice == 4:
            run_test_suite(factory, 3)  # Agent Discovery Test
            
        elif choice == 5:
            run_test_suite(factory, 4)  # Complex Orchestration Test
            
        elif choice == 6:
            run_test_suite(factory, 5)  # Emergency Simulation Test
            
        elif choice == 7:
            # Show enhanced test menu and let user choose
            display_test_menu()
            try:
                test_choice = int(input("Enter enhanced test choice (0-7): "))
                run_test_suite(factory, test_choice)
            except ValueError:
                print("❌ Invalid test choice.")
                
        elif choice == 8:
            create_production_agents(factory)
            
        else:
            print("❌ Invalid choice. Please select 0-8.")
        
        # Ask if user wants to continue
        print("\n" + "=" * 70)
        continue_choice = input("Return to main menu? (y/n): ").lower().strip()
        if continue_choice not in ['y', 'yes']:
            print("👋 Goodbye!")
            break


if __name__ == "__main__":
    main()