"""
Test fleet agent functionality.
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


class TestFleetAgent:
    """Test fleet agent functionality."""
    
    def test_fleet_agent_info(self, fleet_agent):
        """Test fleet agent info retrieval."""
        assert_agent_valid(fleet_agent)
        
        info = fleet_agent.get_info()
        assert info['type'] == 'fleet'
        assert info['total_tools'] > 0
    
    def test_agv_status_query(self, fleet_agent):
        """Test AGV status checking functionality."""
        test_queries = [
            "What is the status of all AGVs?",
            "Check AGV001 status",
            "Show me available vehicles"
        ]
        
        for query in test_queries:
            response = fleet_agent.send_message(query)
            assert_response_valid(response)
    
    def test_route_optimization(self, fleet_agent):
        """Test route optimization functionality."""
        response = fleet_agent.send_message("Optimize route from A to B")
        assert_response_valid(response)
    
    def test_vehicle_assignment(self, fleet_agent):
        """Test vehicle assignment functionality."""
        response = fleet_agent.send_message("Assign an available AGV for delivery")
        assert_response_valid(response)
    
    def test_fleet_capacity_check(self, fleet_agent):
        """Test fleet capacity checking."""
        response = fleet_agent.send_message("Check total fleet capacity")
        assert_response_valid(response)
    
    def test_route_planning(self, fleet_agent):
        """Test route planning functionality."""
        response = fleet_agent.send_message("Plan optimal routes for all active deliveries")
        assert_response_valid(response)
    
    def test_vehicle_maintenance_status(self, fleet_agent):
        """Test vehicle maintenance status."""
        response = fleet_agent.send_message("Check maintenance status of all vehicles")
        assert_response_valid(response)