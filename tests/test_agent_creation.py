"""
Test agent creation and basic functionality.
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


class TestAgentCreation:
    """Test agent creation functionality."""
    
    def test_create_inventory_agent(self, agent_factory):
        """Test creating an inventory agent."""
        agent = agent_factory.create_agent(
            agent_type="inventory",
            name="TestInventoryAgent"
        )
        assert_agent_valid(agent)
        
        info = agent.get_info()
        assert info['type'] == 'inventory'
        assert 'TestInventoryAgent' in info['name']
    
    def test_create_fleet_agent(self, agent_factory):
        """Test creating a fleet agent."""
        agent = agent_factory.create_agent(
            agent_type="fleet",
            name="TestFleetAgent"
        )
        assert_agent_valid(agent)
        
        info = agent.get_info()
        assert info['type'] == 'fleet'
        assert 'TestFleetAgent' in info['name']
    
    def test_create_approval_agent(self, agent_factory):
        """Test creating an approval agent."""
        agent = agent_factory.create_agent(
            agent_type="approval", 
            name="TestApprovalAgent"
        )
        assert_agent_valid(agent)
        
        info = agent.get_info()
        assert info['type'] == 'approval'
        assert 'TestApprovalAgent' in info['name']
    
    def test_create_orchestrator_agent(self, agent_factory):
        """Test creating an orchestrator agent."""
        agent = agent_factory.create_agent(
            agent_type="orchestrator",
            name="TestOrchestratorAgent"
        )
        assert_agent_valid(agent)
        
        info = agent.get_info()
        assert info['type'] == 'orchestrator'
        assert 'TestOrchestratorAgent' in info['name']
    
    def test_invalid_agent_type(self, agent_factory, capsys):
        """Test creating an invalid agent type defaults to orchestrator with warning."""
        agent = agent_factory.create_agent(
            agent_type="invalid_type",
            name="InvalidAgent"
        )
        
        # Should successfully create agent (graceful fallback)
        assert_agent_valid(agent)
        
        # Should capture warning message
        captured = capsys.readouterr()
        assert "Warning: Unknown agent type 'invalid_type'" in captured.out
        assert "using orchestrator configuration" in captured.out
        
        # Should default to orchestrator behavior (has all tools)
        info = agent.get_info()
        assert info['total_tools'] > 0  # Should have tools from orchestrator config
    
    def test_all_agents_created_successfully(self, test_agents):
        """Test that all test agents are created successfully."""
        required_agents = ['inventory', 'fleet', 'approval', 'orchestrator']
        
        for agent_type in required_agents:
            assert test_agents[agent_type] is not None, f"{agent_type} agent was not created"
            assert_agent_valid(test_agents[agent_type])