"""
Agent Tool Providers Module
Contains tool provider classes that wrap data manager functions as Strands tools.
"""

import json
from typing import Dict, Any, Optional
from strands import tool


class InventoryAgentToolProvider:
    """Tool provider for inventory management operations."""
    
    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager
    
    @tool(name="get_part_info")
    def get_part_info(self, part_number: str) -> str:
        result = self.inventory_manager.get_part_info(part_number)
        return json.dumps(result, indent=2)
    
    @tool(name="check_availability")
    def check_availability(self, part_number: str, quantity: int) -> str:
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
        result = self.inventory_manager.search_parts(search_term, search_field)
        return json.dumps(result, indent=2)
    
    @tool(name="get_low_stock_items")
    def get_low_stock_items(self) -> str:
        result = self.inventory_manager.get_low_stock_items()
        return json.dumps(result, indent=2)
    
    @tool(name="get_inventory_summary")
    def get_inventory_summary(self) -> str:
        result = self.inventory_manager.get_inventory_summary()
        return json.dumps(result, indent=2)
    
    @tool(name="get_reservation_history")
    def get_reservation_history(self, part_number: str = None) -> str:
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


class FleetAgentToolProvider:
    """Tool provider for fleet management operations."""
    
    def __init__(self, fleet_manager):
        self.fleet_manager = fleet_manager
    
    @tool(name="get_agv_info")
    def get_agv_info(self, agv_id: str) -> str:
        result = self.fleet_manager.get_agv_info(agv_id)
        return json.dumps(result, indent=2)
    
    @tool(name="get_available_agvs")
    def get_available_agvs(self, min_battery: int = 20, location: str = None) -> str:
        try:
            min_battery = int(min_battery)
            result = self.fleet_manager.get_available_agvs(min_battery, location)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid min_battery parameter: {min_battery}. Must be an integer.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Get available AGVs failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="find_optimal_agv")
    def find_optimal_agv(self, quantity: int, from_location: str, to_location: str) -> str:
        try:
            quantity = int(quantity)
            result = self.fleet_manager.find_optimal_agv(quantity, from_location, to_location)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid quantity parameter: {quantity}. Must be an integer.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Find optimal AGV failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="dispatch_agv")
    def dispatch_agv(self, agv_id: str, task_description: str, from_location: str, to_location: str, priority: str = "normal") -> str:
        task_details = {
            "description": task_description,
            "from_location": from_location,
            "to_location": to_location,
            "priority": priority
        }
        result = self.fleet_manager.dispatch_agv(agv_id, task_details, "FleetAgent")
        return json.dumps(result, indent=2)
    
    @tool(name="complete_agv_task")
    def complete_agv_task(self, agv_id: str, completion_notes: str = "") -> str:
        completion_details = {"notes": completion_notes} if completion_notes else None
        result = self.fleet_manager.complete_task(agv_id, completion_details)
        return json.dumps(result, indent=2)
    
    @tool(name="get_fleet_status")
    def get_fleet_status(self) -> str:
        result = self.fleet_manager.get_fleet_status()
        return json.dumps(result, indent=2)
    
    @tool(name="get_route_info")
    def get_route_info(self, from_location: str, to_location: str) -> str:
        result = self.fleet_manager.get_route_info(from_location, to_location)
        return json.dumps(result, indent=2)

    @property
    def tools(self):
        return [
            self.get_agv_info,
            self.get_available_agvs,
            self.find_optimal_agv,
            self.dispatch_agv,
            self.complete_agv_task,
            self.get_fleet_status,
            self.get_route_info
        ]


class ApprovalAgentToolProvider:
    """Tool provider for approval workflow operations."""
    
    def __init__(self, approval_manager):
        self.approval_manager = approval_manager
    
    @tool(name="check_approval_threshold")
    def check_approval_threshold(self, cost: float) -> str:
        try:
            cost = float(cost)
            result = self.approval_manager.get_approval_threshold(cost)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid cost parameter: {cost}. Must be a number.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Approval threshold check failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="create_approval_request")
    def create_approval_request(self, cost: float, description: str, request_type: str, requester: str = "ApprovalAgent") -> str:
        try:
            cost = float(cost)
            request_details = {
                "cost": cost,
                "description": description,
                "request_type": request_type
            }
            result = self.approval_manager.create_approval_request(request_details, requester)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid cost parameter: {cost}. Must be a number.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Create approval request failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="process_approval")
    def process_approval(self, request_id: str, decision: str, approver: str, comments: str = "") -> str:
        result = self.approval_manager.process_approval(request_id, decision, approver, comments)
        return json.dumps(result, indent=2)
    
    @tool(name="get_pending_approvals")
    def get_pending_approvals(self, approver_type: str = None) -> str:
        result = self.approval_manager.get_pending_approvals(approver_type)
        return json.dumps(result, indent=2)
    
    @tool(name="check_compliance")
    def check_compliance(self, cost: float, description: str, request_type: str) -> str:
        try:
            cost = float(cost)
            request_details = {
                "cost": cost,
                "description": description,
                "request_type": request_type
            }
            result = self.approval_manager.check_compliance(request_details)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid cost parameter: {cost}. Must be a number.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Compliance check failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="get_approval_statistics")
    def get_approval_statistics(self) -> str:
        result = self.approval_manager.get_approval_statistics()
        return json.dumps(result, indent=2)

    @property
    def tools(self):
        return [
            self.check_approval_threshold,
            self.create_approval_request,
            self.process_approval,
            self.get_pending_approvals,
            self.check_compliance,
            self.get_approval_statistics
        ]


def initialize_tool_providers(inventory_manager=None, fleet_manager=None, approval_manager=None):
    """Initialize all tool providers with their respective managers."""
    providers = {}
    
    if inventory_manager:
        providers['inventory'] = InventoryAgentToolProvider(inventory_manager)
        print("⚖️ Approval Agent Tools: 6 functions available")
    
    if fleet_manager:
        providers['fleet'] = FleetAgentToolProvider(fleet_manager)
        print("🚛 Fleet Agent Tools: 7 functions available")
    
    if approval_manager:
        providers['approval'] = ApprovalAgentToolProvider(approval_manager)
        print("📦 Inventory Agent Tools: 8 functions available")
    
    print("✅ Data Manager Tool Providers created!")
    
    return providers