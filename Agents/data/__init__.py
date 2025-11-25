"""
Data Package

This package contains data definitions for the logistics system:
- inventory_data: Product inventory definitions and configurations
- fleet_data: AGV fleet and routing information  
- approver_data: Approval workflow thresholds and rules
"""

from .inventory_data import inventory_data, get_inventory_dataframe
from .fleet_data import agv_data, routes_data, get_fleet_dataframes
from .approver_data import approval_thresholds, get_approval_dataframe

__all__ = [
    'inventory_data',
    'agv_data', 
    'routes_data',
    'approval_thresholds',
    'get_inventory_dataframe',
    'get_fleet_dataframes',
    'get_approval_dataframe'
]