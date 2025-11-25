"""
Data Providers Package

This package contains data access layer classes for different domains:
- ApprovalDataProvider: Handles approval workflow data operations
- FleetDataProvider: Manages fleet and vehicle data operations  
- InventoryDataProvider: Handles inventory and product data operations
"""

from .approval_data_provider import ApprovalDataProvider
from .fleet_data_provider import FleetDataProvider
from .inventory_data_provider import InventoryDataProvider

__all__ = [
    'ApprovalDataProvider',
    'FleetDataProvider', 
    'InventoryDataProvider'
]