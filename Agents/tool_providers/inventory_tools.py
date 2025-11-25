"""
Inventory Agent Tool Provider
Contains tool provider class for inventory management operations.
"""

import json
from strands import tool


class InventoryAgentToolProvider:
    """Tool provider for inventory management operations."""
    
    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager
    
    @tool(name="get_part_info")
    def get_part_info(self, part_number: str) -> str:
        """
        Get part details: warehouse_location, available_quantity, cost_per_unit, supplier.
        Use warehouse_location as from_location in find_optimal_agv.
        """
        result = self.inventory_manager.get_part_info(part_number)
        return json.dumps(result, indent=2)
    
    @tool(name="check_availability")
    def check_availability(self, part_number: str, quantity: int) -> str:
        """
        Check stock availability. Returns: available (true/false), warehouse_location, available_quantity.
        If available=true, use EXACT warehouse_location value for find_optimal_agv. If false, STOP.
        DO NOT call get_part_info after this - you already have warehouse_location.
        CRITICAL: Use the EXACT warehouse_location string from response - don't modify or shorten it.
        """
        try:
            quantity = int(quantity)
            result = self.inventory_manager.check_availability(part_number, quantity)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid quantity parameter: {quantity}. Must be an integer.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Availability check failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="reserve_inventory")
    def reserve_inventory(self, part_number: str, quantity: int, requester: str = "InventoryAgent") -> str:
        """
        Reserve inventory. RARELY NEEDED - skip in normal workflows.
        """
        try:
            quantity = int(quantity)
            result = self.inventory_manager.reserve_quantity(part_number, quantity, requester)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid quantity parameter: {quantity}. Must be an integer.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Reservation failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="release_reservation")
    def release_reservation(self, part_number: str, quantity: int, requester: str = "InventoryAgent") -> str:
        """
        Release reservation. DO NOT USE in normal workflows. Only for error recovery.
        """
        try:
            quantity = int(quantity)
            result = self.inventory_manager.release_reservation(part_number, quantity, requester)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid quantity parameter: {quantity}. Must be an integer.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Release failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="search_parts")
    def search_parts(self, search_term: str, search_field: str = "description") -> str:
        """
        Search parts by keyword. Use when you don't have exact part_number.
        """
        result = self.inventory_manager.search_parts(search_term, search_field)
        return json.dumps(result, indent=2)
    
    @tool(name="get_low_stock_items")
    def get_low_stock_items(self) -> str:
        """
        Get low stock items. For reporting only, not needed in delivery workflows.
        """
        result = self.inventory_manager.get_low_stock_items()
        return json.dumps(result, indent=2)
    
    @tool(name="get_inventory_summary")
    def get_inventory_summary(self) -> str:
        """
        Get inventory overview. For reporting only, not needed in delivery workflows.
        """
        result = self.inventory_manager.get_inventory_summary()
        return json.dumps(result, indent=2)
    
    @tool(name="get_reservation_history")
    def get_reservation_history(self, part_number: str = None) -> str:
        """
        Get reservation history. For auditing only, NEVER use in workflows.
        """
        result = self.inventory_manager.get_reservation_history(part_number)
        return json.dumps(result, indent=2)

    @property
    def tools(self):
        return [
            self.get_part_info,
            self.check_availability,
            self.reserve_inventory,
            self.release_reservation,
            self.search_parts,
            self.get_low_stock_items,
            self.get_inventory_summary,
            self.get_reservation_history
        ]