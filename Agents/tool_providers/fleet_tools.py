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
        """
        Get AGV details. Don't call after find_optimal_agv - you already have the info.
        """
        result = self.fleet_manager.get_agv_info(agv_id)
        return json.dumps(result, indent=2)
    
    @tool(name="get_available_agvs")
    def get_available_agvs(self, min_battery: int = 20, location: str = None) -> str:
        """
        List available AGVs. For reporting only. Use find_optimal_agv for deliveries.
        """
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
        """
        PRIMARY TOOL for deliveries. Finds best AGV considering capacity, battery, cost, route.
        Returns optimal_agv object. Extract agv_id: result["optimal_agv"]["agv_id"]
        
        CRITICAL - USE EXACT LOCATION NAMES (copy from check_availability result):
        FROM locations: "Central Warehouse", "Warehouse A", "Warehouse B"
        TO locations: "Production Line A", "Production Line B", "Manufacturing Plant Delta"
        
        DO NOT modify location names (no "A1", "warehouse a", etc.). Use EXACT strings.
        Call ONCE per delivery. DO NOT call again.
        """
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
    def dispatch_agv(self, agv_id: str, task_description: str, from_location: str, to_location: str, quantity: int, priority: str = "normal") -> str:
        """
        Dispatch AGV. Use agv_id from find_optimal_agv result["optimal_agv"]["agv_id"].
        Once this returns success → STOP and write Summary. DO NOT call again.
        DO NOT call complete_agv_task or get_agv_info after this.
        """
        task_details = {
            "description": task_description,
            "from_location": from_location,
            "to_location": to_location,
            "quantity": quantity,
            "priority": priority
        }
        result = self.fleet_manager.dispatch_agv(agv_id, task_details, "FleetAgent")
        return json.dumps(result, indent=2)
    
    @tool(name="complete_agv_task")
    def complete_agv_task(self, agv_id: str, completion_notes: str = "") -> str:
        """
        DO NOT USE. Completion is automatic. For testing only.
        """
        completion_details = {"notes": completion_notes} if completion_notes else None
        result = self.fleet_manager.complete_task(agv_id, completion_details)
        return json.dumps(result, indent=2)
    
    @tool(name="get_fleet_status")
    def get_fleet_status(self) -> str:
        """
        Get fleet overview. For reporting only, not needed in workflows.
        """
        result = self.fleet_manager.get_fleet_status()
        return json.dumps(result, indent=2)
    
    @tool(name="get_route_info")
    def get_route_info(self, from_location: str, to_location: str) -> str:
        """
        Get route details. Redundant if you used find_optimal_agv (includes route_info).
        """
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