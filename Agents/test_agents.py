"""
Enhanced Logistics Agent Testing Module
Provides options to run different test scenarios with agent discovery functionality.
"""

import json
from typing import Dict, List, Optional


def display_test_menu():
    """Display available test options."""
    print("🧪 ENHANCED LOGISTICS AGENT TESTING SUITE")
    print("=" * 70)
    print("Available Test Options:")
    print("1. Basic Agent Creation Tests (Quick)")
    print("2. Individual Agent Function Tests")
    print("3. Agent Discovery & Communication Tests")
    print("4. Complex Orchestration with Discovery")
    print("5. Urgent Request Simulation")
    print("6. Full Integration Test Suite")
    print("7. Run All Tests")
    print("0. Exit")
    print("=" * 70)


def run_test_suite(factory, test_choice: int = None):
    """Run tests based on user choice."""
    if test_choice is None:
        display_test_menu()
        try:
            test_choice = int(input("Enter your choice (0-7): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            return None
    
    print(f"\n🚀 Running Test Option {test_choice}...")
    
    # Create agents first (needed for all tests)
    agents = create_test_agents(factory)
    
    if test_choice == 1:
        run_basic_creation_tests(agents)
    elif test_choice == 2:
        run_individual_function_tests(agents)
    elif test_choice == 3:
        run_agent_discovery_tests(agents)
    elif test_choice == 4:
        run_complex_orchestration_with_discovery(agents)
    elif test_choice == 5:
        run_urgent_request_simulation(agents)
    elif test_choice == 6:
        run_full_integration_tests(agents)
    elif test_choice == 7:
        run_all_tests(agents)
    elif test_choice == 0:
        print("👋 Exiting test suite.")
        return None
    else:
        print("❌ Invalid choice. Please select 0-7.")
    
    return agents


def create_test_agents(factory):
    """Create all test agents."""
    print("🚀 CREATING ENHANCED TEST AGENTS")
    print("=" * 70)

    # Check Ollama connection
    print("🔧 Checking Ollama connection...")
    try:
        test_model = factory.create_ollama_model()
        print("✅ Ollama model created successfully")
    except Exception as e:
        print(f"⚠️ Ollama connection issue: {str(e)}")
        print("   Make sure Ollama is running: ollama serve")
        print("   And model is available: ollama pull qwen2.5:7b")

    agents = {}
    agent_configs = [
        ("inventory", "SmartInventoryAgent", "📦"),
        ("fleet", "IntelligentFleetAgent", "🚛"),
        ("approval", "ComplianceApprovalAgent", "⚖️"),
        ("orchestrator", "MasterLogisticsOrchestrator", "🎯")
    ]

    for agent_type, name, icon in agent_configs:
        try:
            agents[agent_type] = factory.create_agent(
                agent_type=agent_type,
                name=name
            )
            print(f"✅ {icon} {name} created successfully")
        except Exception as e:
            print(f"❌ Failed to create {name}: {str(e)}")
            agents[agent_type] = None

    print("\n📊 Agent Summary:")
    for agent_type, agent in agents.items():
        if agent:
            info = agent.get_info()
            print(f"   {agent_type.title()}: {info['data_manager_tools']} domain + 3 A2A = {info['total_tools']} total tools")

    return agents


def run_basic_creation_tests(agents):
    """Test 1: Basic agent creation validation."""
    print("\n" + "=" * 70)
    print("🧪 TEST 1: BASIC AGENT CREATION VALIDATION")
    print("=" * 70)
    
    for agent_type, agent in agents.items():
        if agent:
            info = agent.get_info()
            print(f"✅ {agent_type.title()} Agent:")
            print(f"   Name: {info['name']}")
            print(f"   Type: {info['type']}")
            print(f"   Domain Tools: {info['data_manager_tools']}")
            print(f"   Total Tools: {info['total_tools']}")
            print(f"   A2A Enabled: {info['a2a_enabled']}")
        else:
            print(f"❌ {agent_type.title()} Agent: Creation Failed")
        print()


def run_individual_function_tests(agents):
    """Test 2: Individual agent function tests."""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: INDIVIDUAL AGENT FUNCTION TESTS")
    print("=" * 70)
    
    # Test each agent individually
    test_inventory_functions(agents.get('inventory'))
    test_fleet_functions(agents.get('fleet'))
    test_approval_functions(agents.get('approval'))


def run_agent_discovery_tests(agents):
    """Test 3: Agent discovery and communication tests."""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: AGENT DISCOVERY & COMMUNICATION TESTS")
    print("=" * 70)
    
    orchestrator = agents.get('orchestrator')
    if not orchestrator:
        print("❌ Cannot run discovery tests - orchestrator not available")
        return
    
    # Test agent discovery capabilities
    print("1. 🔍 Agent Discovery Test:")
    discovery_query = """
    Can you tell me what agents are available in this system? 
    What capabilities does each agent have?
    List all the tools you have access to.
    """
    print(f"   Query: {discovery_query.strip()}")
    print(f"   Agent: {orchestrator.name}")
    print()
    
    try:
        response = orchestrator.send_message(discovery_query)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\n" + "-" * 50)
    
    # Test inter-agent communication
    print("2. 🤝 Inter-Agent Communication Test:")
    comm_query = """
    I want to understand how agents work together. 
    Can you demonstrate how you would coordinate with other agents 
    to handle a logistics request?
    """
    print(f"   Query: {comm_query.strip()}")
    print(f"   Agent: {orchestrator.name}")
    print()
    
    try:
        response = orchestrator.send_message(comm_query)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {str(e)}")


def run_complex_orchestration_with_discovery(agents):
    """Test 4: Complex orchestration with agent discovery."""
    print("\n" + "=" * 70)
    print("🧪 TEST 4: COMPLEX ORCHESTRATION WITH DISCOVERY")
    print("=" * 70)
    
    orchestrator = agents.get('orchestrator')
    if not orchestrator:
        print("❌ Cannot run orchestration tests - orchestrator not available")
        return
    
    print("🌟 Complex Multi-Phase Logistics Operation:")
    
    # Phase 1: Discovery and Planning
    print("\n📋 PHASE 1: Agent Discovery & Task Planning")
    print("-" * 50)
    
    discovery_task = """
    I have a complex logistics request. Before we start, I need you to:
    
    1. Discover what agents and tools are available
    2. Analyze what capabilities we have for:
       - Inventory management
       - Fleet operations  
       - Approval workflows
    3. Create a plan for handling multi-domain requests
    
    Please provide a comprehensive overview of our system capabilities.
    """
    print(f"Query: {discovery_task.strip()}")
    print(f"Agent: {orchestrator.name}")
    print()
    
    try:
        discovery_response = orchestrator.send_message(discovery_task)
        print(f"Discovery Response: {discovery_response}")
    except Exception as e:
        print(f"Discovery Error: {str(e)}")
        return
    
    # Phase 2: Complex Task Execution
    print("\n\n🚀 PHASE 2: Complex Task Execution")
    print("-" * 50)
    
    complex_task = """
    Now that you know our capabilities, please handle this complex request:
    
    PRODUCTION ORDER: PO-2024-URGENT-001
    Requirements:
    - 25 units of HYDRAULIC-PUMP-HP450 (check availability)
    - Transport from Central Warehouse to Production Line C
    - Estimated total cost: $6,750
    - Priority: HIGH
    
    Based on your agent discovery, coordinate this entire operation:
    1. Check inventory and reserve items
    2. Find optimal AGV for transport
    3. Handle any required approvals
    4. Provide status updates throughout
    
    Use your knowledge of available agents and tools to complete this efficiently.
    """
    print(f"Query: {complex_task.strip()}")
    print(f"Agent: {orchestrator.name}")
    print()
    
    try:
        execution_response = orchestrator.send_message(complex_task)
        print(f"Execution Response: {execution_response}")
    except Exception as e:
        print(f"Execution Error: {str(e)}")


def run_urgent_request_simulation(agents):
    """Test 5: Urgent request simulation."""
    print("\n" + "=" * 70)
    print("🧪 TEST 5: URGENT REQUEST SIMULATION")
    print("=" * 70)
    
    orchestrator = agents.get('orchestrator')
    if not orchestrator:
        print("❌ Cannot run urgent simulation - orchestrator not available")
        return
    
    print("🚨 Emergency Logistics Situation:")
    
    urgent_task = """
    URGENT EMERGENCY SITUATION:
    
    Production Line A is down due to a failed HYDRAULIC-PUMP-HP450.
    We need immediate replacement to avoid production loss.
    
    Requirements:
    - 1 unit of HYDRAULIC-PUMP-HP450 ASAP
    - Emergency transport to Production Line A
    - Fast-track any approvals needed
    - Estimated cost: $270 (emergency rate)
    
    This is production-critical. Use all available agents and tools 
    to resolve this as quickly as possible.
    
    Please coordinate the emergency response.
    """
    print(f"Query: {urgent_task.strip()}")
    print(f"Agent: {orchestrator.name}")
    print()
    
    try:
        response = orchestrator.send_message(urgent_task)
        print(f"Emergency Response: {response}")
    except Exception as e:
        print(f"Emergency Error: {str(e)}")


def run_full_integration_tests(agents):
    """Test 6: Full integration test suite."""
    print("\n" + "=" * 70)
    print("🧪 TEST 6: FULL INTEGRATION TEST SUITE")
    print("=" * 70)
    
    print("Running comprehensive integration tests...")
    
    # Run all individual tests
    run_basic_creation_tests(agents)
    run_individual_function_tests(agents)
    run_agent_discovery_tests(agents)
    run_complex_orchestration_with_discovery(agents)
    run_urgent_request_simulation(agents)
    
    print("\n" + "=" * 70)
    print("✅ FULL INTEGRATION TEST SUITE COMPLETED!")
    print("=" * 70)


def run_all_tests(agents):
    """Test 7: Run all available tests."""
    print("\n" + "=" * 70)
    print("🧪 TEST 7: RUNNING ALL AVAILABLE TESTS")
    print("=" * 70)
    
    run_full_integration_tests(agents)


# Individual agent test functions (enhanced versions)
def test_inventory_functions(inventory_agent):
    """Enhanced inventory agent testing."""
    print("\n📦 TESTING INVENTORY AGENT FUNCTIONS")
    print("-" * 50)
    
    if not inventory_agent:
        print("❌ Inventory agent not available")
        return
    
    agent_name = inventory_agent.name
    
    tests = [
        ("Part Availability Check", "Check availability for HYDRAULIC-PUMP-HP450. How many do we have?"),
        ("Inventory Reservation", "Reserve 3 units of PART-ABC123 for order PO-2024-TEST"),
        ("Low Stock Analysis", "What items are below reorder point? Show me our critical stock levels."),
        ("Stock Value Report", "What's the total value of our current inventory?")
    ]
    
    for test_name, query in tests:
        print(f"\n🔍 {test_name}:")
        print(f"   Query: {query}")
        print(f"   Agent: {agent_name}")
        print()
        
        try:
            response = inventory_agent.send_message(query)
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   Error: {str(e)}")


def test_fleet_functions(fleet_agent):
    """Enhanced fleet agent testing."""
    print("\n🚛 TESTING FLEET AGENT FUNCTIONS")
    print("-" * 50)
    
    if not fleet_agent:
        print("❌ Fleet agent not available")
        return
    
    agent_name = fleet_agent.name
    
    tests = [
        ("Optimal AGV Selection", "Find the best AGV to transport 50 units from Warehouse B to Line A"),
        ("Fleet Status Check", "What's the current status of all AGVs? Show availability and capacity."),
        ("Route Optimization", "Optimize route for AGV-003 from Central to Production Line C"),
        ("Fleet Performance", "Show me AGV utilization and efficiency metrics")
    ]
    
    for test_name, query in tests:
        print(f"\n🎯 {test_name}:")
        print(f"   Query: {query}")
        print(f"   Agent: {agent_name}")
        print()
        
        try:
            response = fleet_agent.send_message(query)
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   Error: {str(e)}")


def test_approval_functions(approval_agent):
    """Enhanced approval agent testing."""
    print("\n⚖️ TESTING APPROVAL AGENT FUNCTIONS")
    print("-" * 50)
    
    if not approval_agent:
        print("❌ Approval agent not available")
        return
    
    agent_name = approval_agent.name
    
    tests = [
        ("Threshold Check", "Check approval requirements for a $2,500 procurement request"),
        ("Compliance Validation", "Validate compliance for 'AGV maintenance contract - $1,800'"),
        ("Approval Submission", "Submit approval request for $4,200 emergency parts order"),
        ("Approval Status", "Check status of all pending approval requests")
    ]
    
    for test_name, query in tests:
        print(f"\n💰 {test_name}:")
        print(f"   Query: {query}")
        print(f"   Agent: {agent_name}")
        print()
        
        try:
            response = approval_agent.send_message(query)
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   Error: {str(e)}")


# Interactive test runner
def run_interactive_tests(factory):
    """Run tests interactively with user choices."""
    while True:
        agents = run_test_suite(factory)
        if agents is None:  # User chose to exit
            break
            
        print("\n" + "=" * 70)
        continue_choice = input("Run another test? (y/n): ").lower().strip()
        if continue_choice not in ['y', 'yes']:
            break
    
    print("\n✅ Enhanced testing session completed!")
    return True


# Main execution function
def main_enhanced_testing(factory):
    """Main function to run enhanced testing."""
    print("🚀 ENHANCED LOGISTICS TESTING SYSTEM")
    print("=" * 70)
    print("This enhanced test suite provides:")
    print("- Multiple test scenarios")
    print("- Agent discovery capabilities") 
    print("- Complex orchestration testing")
    print("- Interactive test selection")
    print("=" * 70)
    
    return run_interactive_tests(factory)


if __name__ == "__main__":
    print("This module should be imported and used with an AgentFactory instance.")
    print("Example usage:")
    print("from enhanced_test_agents import main_enhanced_testing")
    print("main_enhanced_testing(your_factory)")