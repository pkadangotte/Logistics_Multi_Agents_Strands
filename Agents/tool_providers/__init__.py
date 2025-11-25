"""
Tool Providers Package

This package contains Strands tool definitions for different agent domains:
- approval_tools: Tools for approval workflow management
- fleet_tools: Tools for fleet operations and vehicle management
- inventory_tools: Tools for inventory and product management

Each module provides domain-specific tools that can be used by agents
to perform operations through the Strands framework.
"""

# Import tool functions from each module for easy access
from . import approval_tools
from . import fleet_tools  
from . import inventory_tools

__all__ = [
    'approval_tools',
    'fleet_tools',
    'inventory_tools'
]