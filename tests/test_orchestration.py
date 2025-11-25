"""
Test orchestration and integration functionality.
"""

import pytest
# conftest.py is automatically imported by pytest


def assert_agent_valid(agent):
    """Helper function to validate an agent."""
    assert agent is not None
    assert hasattr(agent, 'name')
    assert hasattr(agent, 'send_message')
    assert hasattr(agent, 'get_info')
    
    info = agent.get_info()
    assert isinstance(info, dict)
    assert 'name' in info
    assert 'type' in info
    assert 'total_tools' in info


def assert_response_valid(response):
    """Helper function to validate agent responses."""
    assert response is not None
    assert isinstance(response, str)
    assert len(response.strip()) > 0


class TestOrchestration:
    """Test orchestration agent functionality."""
    
    def test_orchestrator_agent_info(self, orchestrator_agent):
        """Test orchestrator agent info retrieval."""
        assert_agent_valid(orchestrator_agent)
        
        info = orchestrator_agent.get_info()
        assert info['type'] == 'orchestrator'
        assert info['total_tools'] > 0
    
    def test_complex_logistics_query(self, orchestrator_agent):
        """Test complex logistics orchestration."""
        complex_queries = [
            "Plan a complete delivery from warehouse A to customer location B",
            "Coordinate inventory check, vehicle assignment, and route planning",
            "Handle a high-priority delivery request with approval workflow"
        ]
        
        for query in complex_queries:
            response = orchestrator_agent.send_message(query)
            assert_response_valid(response)
    
    def test_multi_agent_coordination(self, test_agents):
        """Test coordination between multiple agents."""
        # Verify all agents are available for coordination
        assert test_agents['inventory'] is not None
        assert test_agents['fleet'] is not None
        assert test_agents['approval'] is not None
        assert test_agents['orchestrator'] is not None
        
        # Test orchestrator can handle multi-step processes
        orchestrator = test_agents['orchestrator']
        response = orchestrator.send_message(
            "Check inventory for item SKU001, then assign a vehicle if available"
        )
        assert_response_valid(response)


class TestIntegration:
    """Test integration between different agents."""
    
    def test_inventory_fleet_integration(self, test_agents):
        """Test integration between inventory and fleet agents."""
        inventory_agent = test_agents['inventory']
        fleet_agent = test_agents['fleet']
        
        assert inventory_agent is not None
        assert fleet_agent is not None
        
        # Test inventory check
        inventory_response = inventory_agent.send_message("Check stock for SKU001")
        assert_response_valid(inventory_response)
        
        # Test fleet availability
        fleet_response = fleet_agent.send_message("Check available vehicles")
        assert_response_valid(fleet_response)
    
    def test_approval_workflow_integration(self, test_agents):
        """Test approval workflow integration with other agents."""
        approval_agent = test_agents['approval']
        orchestrator_agent = test_agents['orchestrator']
        
        assert approval_agent is not None
        assert orchestrator_agent is not None
        
        # Test approval status check
        approval_response = approval_agent.send_message("Check pending approvals")
        assert_response_valid(approval_response)
        
        # Test orchestrator can handle approval-dependent workflows  
        orchestrator_response = orchestrator_agent.send_message(
            "Process a delivery that requires approval"
        )
        assert_response_valid(orchestrator_response)
    
    def test_end_to_end_workflow(self, test_agents):
        """Test complete end-to-end logistics workflow."""
        orchestrator = test_agents['orchestrator']
        
        # Simulate a complete logistics request
        workflow_response = orchestrator.send_message(
            "I need to deliver 100 units of SKU001 to location XYZ. "
            "Please check inventory, get approval if needed, assign a vehicle, and plan the route."
        )
        assert_response_valid(workflow_response)
    
    def test_error_handling_across_agents(self, test_agents):
        """Test error handling in multi-agent scenarios."""
        for agent_type, agent in test_agents.items():
            if agent is not None:
                # Test with invalid/unclear request
                response = agent.send_message("This is an unclear request with no clear action")
                assert_response_valid(response)
                # Agent should respond gracefully even to unclear requests