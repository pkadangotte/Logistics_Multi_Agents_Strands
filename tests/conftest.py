"""
Shared test fixtures and utilities for the Logistics Multi-Agent System tests.
"""

import pytest
import sys
import os
from typing import Dict, Any

# Add the Agents directory to the Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Agents'))

from data_setup import initialize_dataframes
from agent_factory import initialize_agent_factory
from data_providers.inventory_data_provider import InventoryDataProvider
from data_providers.fleet_data_provider import FleetDataProvider
from data_providers.approval_data_provider import ApprovalDataProvider


@pytest.fixture(scope="session")
def data_managers():
    """Create data managers for testing."""
    inventory_df, agv_df, routes_df, approval_df = initialize_dataframes()
    
    inventory_manager = InventoryDataProvider(inventory_df)
    fleet_manager = FleetDataProvider(agv_df, routes_df)
    approval_manager = ApprovalDataProvider(approval_df)
    
    return {
        'inventory': inventory_manager,
        'fleet': fleet_manager,
        'approval': approval_manager
    }


@pytest.fixture(scope="session")
def agent_factory(data_managers):
    """Create agent factory for testing."""
    return initialize_agent_factory(
        data_managers['inventory'],
        data_managers['fleet'], 
        data_managers['approval']
    )


@pytest.fixture(scope="function")
def test_agents(agent_factory):
    """Create test agents for individual tests."""
    agents = {}
    agent_configs = [
        ("inventory", "TestInventoryAgent"),
        ("fleet", "TestFleetAgent"),
        ("approval", "TestApprovalAgent"),
        ("orchestrator", "TestOrchestratorAgent")
    ]
    
    for agent_type, name in agent_configs:
        try:
            agents[agent_type] = agent_factory.create_agent(
                agent_type=agent_type,
                name=name
            )
        except Exception as e:
            agents[agent_type] = None
            print(f"Warning: Failed to create {agent_type} agent: {e}")
    
    return agents


@pytest.fixture(scope="function")
def inventory_agent(agent_factory):
    """Create a single inventory agent for focused testing."""
    return agent_factory.create_agent(
        agent_type="inventory",
        name="TestInventoryAgent"
    )


@pytest.fixture(scope="function") 
def fleet_agent(agent_factory):
    """Create a single fleet agent for focused testing."""
    return agent_factory.create_agent(
        agent_type="fleet",
        name="TestFleetAgent"
    )


@pytest.fixture(scope="function")
def approval_agent(agent_factory):
    """Create a single approval agent for focused testing."""
    return agent_factory.create_agent(
        agent_type="approval", 
        name="TestApprovalAgent"
    )


@pytest.fixture(scope="function")
def orchestrator_agent(agent_factory):
    """Create a single orchestrator agent for focused testing."""
    return agent_factory.create_agent(
        agent_type="orchestrator",
        name="TestOrchestratorAgent"
    )


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