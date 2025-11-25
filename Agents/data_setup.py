"""
Logistics Data Setup Module (Refactored)
Central coordinator that imports from modular data files.
Uses the new data package structure for better organization.
"""

from data.inventory_data import get_inventory_dataframe
from data.fleet_data import get_fleet_dataframes  
from data.approver_data import get_approval_dataframe


def initialize_dataframes():
    """Initialize and return all DataFrames for the logistics system."""
    print("🔄 Loading data from modular data files...")
    
    # Load data from separate modules
    inventory_df = get_inventory_dataframe()
    agv_df, routes_df = get_fleet_dataframes()
    approval_df = get_approval_dataframe()
    
    print("✅ Data loaded and converted to DataFrames successfully!")
    
    return inventory_df, agv_df, routes_df, approval_df


def demo_data_access(inventory_df, agv_df, routes_df):
    """Demonstrate data access examples using modular data structure."""
    print("🔍 INTEGRATED DATA ACCESS EXAMPLES:")
    print("=" * 50)

    # Import demo functions from individual modules
    from data.inventory_data import demo_inventory_access
    from data.fleet_data import demo_fleet_access
    from data.approver_data import demo_approval_access, get_approval_dataframe

    print("\n📦 INVENTORY MODULE DEMO:")
    demo_inventory_access(inventory_df)
    
    print("\n🚛 FLEET MODULE DEMO:")  
    demo_fleet_access(agv_df, routes_df)
    
    print("\n✅ APPROVAL MODULE DEMO:")
    approval_df = get_approval_dataframe()
    demo_approval_access(approval_df)

    print("\n🎉 All modular DataFrames are ready for use in your logistics agents!")
    print("📁 Data is now organized in separate modules under data/ directory!")


if __name__ == "__main__":
    # Initialize dataframes when run as main module
    inventory_df, agv_df, routes_df, approval_df = initialize_dataframes()
    demo_data_access(inventory_df, agv_df, routes_df)