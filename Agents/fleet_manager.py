"""
Fleet Data Manager Module
Provides the FleetDataManager class for AGV fleet management operations.
"""

from datetime import datetime, timedelta
import json
from typing import Dict, List, Union


class FleetDataManager:
    """
    Data access class for AGV fleet management operations.
    Provides methods to query, schedule, and manage AGV fleet data.
    """
    
    def __init__(self, agv_df, routes_df):
        """Initialize with AGV and routes DataFrames"""
        self.agv_df = agv_df.copy()
        self.routes_df = routes_df.copy()
        self.dispatch_log = []
        self.current_assignments = {}
    
    def _convert_to_json_serializable(self, obj):
        """Convert pandas types to JSON-serializable types."""
        if hasattr(obj, 'item'):  # numpy/pandas scalar
            return obj.item()
        elif isinstance(obj, dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(v) for v in obj]
        else:
            return obj
        
    def get_agv_info(self, agv_id: str) -> dict:
        """
        Get complete information for a specific AGV.
        
        Args:
            agv_id: The AGV ID to query
            
        Returns:
            Dictionary with AGV information or error if not found
        """
        try:
            if agv_id not in self.agv_df.index:
                return {"error": f"AGV '{agv_id}' not found"}
                
            agv_info = self.agv_df.loc[agv_id].to_dict()
            agv_info['agv_id'] = agv_id
            agv_info['is_available'] = agv_info['status'] == 'AVAILABLE'
            agv_info['current_assignment'] = self.current_assignments.get(agv_id, None)
            
            return agv_info
        except Exception as e:
            return {"error": f"Error retrieving AGV info: {str(e)}"}
    
    def get_available_agvs(self, min_capacity: int = 0, agv_type: str = None) -> Union[List[Dict], Dict]:
        """
        Get list of available AGVs, optionally filtered by capacity and type.
        
        Args:
            min_capacity: Minimum capacity required
            agv_type: Specific AGV type filter
            
        Returns:
            List of available AGVs matching criteria
        """
        try:
            available_agvs = self.agv_df[self.agv_df['status'] == 'AVAILABLE']
            
            if min_capacity > 0:
                available_agvs = available_agvs[available_agvs['capacity_pieces'] >= min_capacity]
            
            if agv_type:
                available_agvs = available_agvs[available_agvs['type'] == agv_type]
            
            result = [
                {
                    "agv_id": idx,
                    "type": row['type'],
                    "capacity_pieces": row['capacity_pieces'],
                    "current_location": row['current_location'],
                    "battery_level": row['battery_level'],
                    "cost_per_trip": row['cost_per_trip'],
                    "max_speed_mps": row['max_speed_mps']
                }
                for idx, row in available_agvs.iterrows()
            ]
            return self._convert_to_json_serializable(result)
            
        except Exception as e:
            return {"error": f"Error getting available AGVs: {str(e)}"}
    
    def find_optimal_agv(self, quantity: int, from_location: str, to_location: str) -> dict:
        """
        Find the most suitable AGV for a delivery task.
        
        Args:
            quantity: Number of pieces to transport
            from_location: Source location
            to_location: Destination location
            
        Returns:
            Dictionary with optimal AGV recommendation
        """
        try:
            # Get route information
            route_key = f"{from_location}|{to_location}"
            if route_key not in self.routes_df.index:
                return {"error": f"Route '{route_key}' not found"}
            
            route_info = self.routes_df.loc[route_key]
            
            # Get available AGVs with sufficient capacity
            suitable_agvs = self.get_available_agvs(min_capacity=quantity)
            
            if not suitable_agvs or "error" in suitable_agvs:
                return {"error": "No suitable AGVs available for this task"}
            
            # Score AGVs based on efficiency (cost, battery, capacity utilization)
            scored_agvs = []
            for agv in suitable_agvs:
                capacity_utilization = quantity / agv['capacity_pieces']
                efficiency_score = (
                    (agv['battery_level'] / 100) * 0.4 +  # Battery weight: 40%
                    (1 / agv['cost_per_trip']) * 0.3 +    # Cost efficiency: 30%
                    capacity_utilization * 0.3             # Capacity utilization: 30%
                )
                
                scored_agvs.append({
                    **agv,
                    "efficiency_score": efficiency_score,
                    "capacity_utilization": capacity_utilization,
                    "estimated_trip_time": route_info['time_minutes'],
                    "estimated_cost": agv['cost_per_trip'],
                    "route_distance": route_info['distance_m']
                })
            
            # Sort by efficiency score (descending)
            scored_agvs.sort(key=lambda x: x['efficiency_score'], reverse=True)
            
            result = {
                "optimal_agv": scored_agvs[0],
                "alternatives": scored_agvs[1:3],  # Top 2 alternatives
                "route_info": {
                    "from": from_location,
                    "to": to_location,
                    "distance_m": route_info['distance_m'],
                    "time_minutes": route_info['time_minutes']
                }
            }
            return self._convert_to_json_serializable(result)
            
        except Exception as e:
            return {"error": f"Error finding optimal AGV: {str(e)}"}
    
    def dispatch_agv(self, agv_id: str, task_details: dict, requester: str = "system") -> dict:
        """
        Dispatch an AGV for a specific task.
        
        Args:
            agv_id: The AGV to dispatch
            task_details: Dictionary with task information (from, to, quantity, etc.)
            requester: Who is dispatching the AGV
            
        Returns:
            Dictionary with dispatch result
        """
        try:
            # Check if AGV exists and is available
            agv_info = self.get_agv_info(agv_id)
            if "error" in agv_info:
                return agv_info
                
            if not agv_info['is_available']:
                return {"error": f"AGV '{agv_id}' is not available (status: {agv_info['status']})"}
            
            # Validate task details
            required_fields = ['from_location', 'to_location', 'quantity']
            for field in required_fields:
                if field not in task_details:
                    return {"error": f"Missing required field: {field}"}
            
            # Check capacity
            if task_details['quantity'] > agv_info['capacity_pieces']:
                return {
                    "error": f"Task quantity ({task_details['quantity']}) exceeds AGV capacity ({agv_info['capacity_pieces']})"
                }
            
            # Update AGV status
            self.agv_df.loc[agv_id, 'status'] = 'DISPATCHED'
            self.agv_df.loc[agv_id, 'current_location'] = task_details['from_location']
            
            # Create dispatch record
            dispatch_record = {
                "dispatch_id": len(self.dispatch_log) + 1,
                "timestamp": datetime.now().isoformat(),
                "agv_id": agv_id,
                "task_details": task_details,
                "requester": requester,
                "status": "DISPATCHED",
                "estimated_completion": (datetime.now() + timedelta(minutes=10)).isoformat()  # Placeholder
            }
            
            self.dispatch_log.append(dispatch_record)
            self.current_assignments[agv_id] = dispatch_record
            
            return {
                "success": True,
                "dispatch_id": dispatch_record["dispatch_id"],
                "agv_id": agv_id,
                "estimated_cost": agv_info['cost_per_trip'],
                "estimated_completion": dispatch_record["estimated_completion"],
                "task_details": task_details
            }
            
        except Exception as e:
            return {"error": f"Dispatch failed: {str(e)}"}
    
    def complete_task(self, agv_id: str, completion_details: dict = None) -> dict:
        """
        Mark an AGV task as completed and return AGV to available status.
        
        Args:
            agv_id: The AGV completing the task
            completion_details: Optional details about task completion
            
        Returns:
            Dictionary with completion result
        """
        try:
            if agv_id not in self.current_assignments:
                return {"error": f"No active assignment found for AGV '{agv_id}'"}
            
            # Update AGV status back to available
            self.agv_df.loc[agv_id, 'status'] = 'AVAILABLE'
            
            # Get the assignment
            assignment = self.current_assignments[agv_id]
            assignment['status'] = 'COMPLETED'
            assignment['completion_time'] = datetime.now().isoformat()
            
            if completion_details:
                assignment['completion_details'] = completion_details
            
            # Remove from current assignments
            del self.current_assignments[agv_id]
            
            return {
                "success": True,
                "agv_id": agv_id,
                "dispatch_id": assignment['dispatch_id'],
                "completion_time": assignment['completion_time'],
                "task_duration": "calculated_duration"  # Could calculate actual duration
            }
            
        except Exception as e:
            return {"error": f"Task completion failed: {str(e)}"}
    
    def get_fleet_status(self) -> dict:
        """Get overall fleet status and statistics"""
        try:
            status_counts = self.agv_df['status'].value_counts().to_dict()
            
            result = {
                "total_agvs": len(self.agv_df),
                "available_agvs": status_counts.get('AVAILABLE', 0),
                "dispatched_agvs": status_counts.get('DISPATCHED', 0),
                "maintenance_agvs": status_counts.get('MAINTENANCE', 0),
                "average_battery_level": self.agv_df['battery_level'].mean(),
                "total_capacity": self.agv_df['capacity_pieces'].sum(),
                "active_dispatches": len(self.current_assignments),
                "total_completed_tasks": len([log for log in self.dispatch_log if log.get('status') == 'COMPLETED'])
            }
            return self._convert_to_json_serializable(result)
            
        except Exception as e:
            return {"error": f"Error getting fleet status: {str(e)}"}
    
    def get_route_info(self, from_location: str, to_location: str) -> dict:
        """Get route information between two locations"""
        try:
            route_key = f"{from_location}|{to_location}"
            if route_key not in self.routes_df.index:
                return {"error": f"Route '{route_key}' not found"}
            
            route_info = self.routes_df.loc[route_key].to_dict()
            route_info['route'] = route_key
            
            return route_info
            
        except Exception as e:
            return {"error": f"Error getting route info: {str(e)}"}
    
    def get_dispatch_history(self, agv_id: str = None) -> list:
        """Get dispatch history, optionally filtered by AGV ID"""
        if agv_id:
            return [log for log in self.dispatch_log if log['agv_id'] == agv_id]
        return self.dispatch_log


def initialize_fleet_manager(agv_df, routes_df):
    """Initialize the fleet manager with the provided DataFrames."""
    manager = FleetDataManager(agv_df, routes_df)
    
    print("✅ Fleet Data Manager initialized!")
    print(f"🚛 Managing {len(agv_df)} AGVs")
    print(f"🛣️ Managing {len(routes_df)} routes")
    
    return manager