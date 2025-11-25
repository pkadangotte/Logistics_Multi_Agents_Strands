"""
Test inventory agent functionality.
"""

import pytest
from conftest import assert_agent_valid, assert_response_valid


class TestInventoryAgent:
    """Test inventory agent functionality."""
    
    def test_inventory_agent_info(self, inventory_agent):
        """Test inventory agent info retrieval."""
        assert_agent_valid(inventory_agent)
        
        info = inventory_agent.get_info()
        assert info['type'] == 'inventory'
        assert info['total_tools'] > 0
    
    def test_inventory_check_query(self, inventory_agent):
        """Test inventory checking functionality."""
        test_queries = [
            "Check inventory levels for item SKU001",
            "What is the current stock for all warehouse items?",
            "Show me low stock items"
        ]
        
        for query in test_queries:
            response = inventory_agent.send_message(query)
            assert_response_valid(response)
    
    def test_inventory_item_lookup(self, inventory_agent):
        """Test specific inventory item lookup."""
        response = inventory_agent.send_message("Get details for item with SKU SKU001")
        assert_response_valid(response)
    
    def test_inventory_stock_levels(self, inventory_agent):
        """Test stock level checking."""
        response = inventory_agent.send_message("Check current stock levels in all warehouses")
        assert_response_valid(response)
    
    def test_inventory_low_stock_alert(self, inventory_agent):
        """Test low stock identification."""
        response = inventory_agent.send_message("Identify items with low stock levels")
        assert_response_valid(response)
    
    def test_inventory_warehouse_summary(self, inventory_agent):
        """Test warehouse summary functionality."""
        response = inventory_agent.send_message("Provide a summary of warehouse inventory")
        assert_response_valid(response)