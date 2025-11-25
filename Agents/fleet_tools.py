"""
Fleet Agent Tool Provider
Contains tool provider class for fleet management operations.
"""

import json
from strands import tool


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