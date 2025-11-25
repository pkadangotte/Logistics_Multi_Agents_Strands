"""
Logistics Data Setup Module
Contains all the initial data definitions for inventory, AGV fleet, routes, and approval thresholds.
"""

import pandas as pd

# Data for Inventory, AGV and Approvers
inventory_data = {
    "HYDRAULIC-PUMP-HP450": {
        "available_quantity": 24,
        "reserved_quantity": 2,
        "warehouse_location": "Central Warehouse",
        "cost_per_unit": 245.00,
        "lead_time_days": 1,
        "supplier": "HydroTech Systems",
        "description": "Heavy-duty hydraulic pump for CNC machinery",
        "category": "Hydraulic Components",
        "reorder_point": 10,
        "maximum_stock": 50
    },
    "PART-ABC123": {
        "available_quantity": 85,
        "reserved_quantity": 15,
        "warehouse_location": "Warehouse A",
        "cost_per_unit": 12.50,
        "lead_time_days": 2,
        "supplier": "Supplier Corp",
        "description": "Standard production part",
        "category": "Standard Components",
        "reorder_point": 25,
        "maximum_stock": 150
    },
    "PART-XYZ789": {
        "available_quantity": 42,
        "reserved_quantity": 8,
        "warehouse_location": "Warehouse B",
        "cost_per_unit": 18.75,
        "lead_time_days": 1,
        "supplier": "Parts Inc",
        "description": "Specialized part",
        "category": "Specialized Components",
        "reorder_point": 15,
        "maximum_stock": 75
    },
    "PART-DEF456": {
        "available_quantity": 120,
        "reserved_quantity": 25,
        "warehouse_location": "Warehouse A",
        "cost_per_unit": 8.25,
        "lead_time_days": 3,
        "supplier": "FastParts Ltd",
        "description": "Common component",
        "category": "Standard Components",
        "reorder_point": 40,
        "maximum_stock": 200
    }
}

# AGV Fleet data
agv_data = {
    "AGV-001": {
        "type": "heavy_duty_agv",
        "capacity_pieces": 100,
        "current_location": "AGV_BASE",
        "status": "AVAILABLE",
        "battery_level": 85,
        "cost_per_trip": 5.00,
        "max_speed_mps": 1.5,
        "charging_status": "not_charging"
    },
    "AGV-002": {
        "type": "standard_agv",
        "capacity_pieces": 50,
        "current_location": "AGV_BASE",
        "status": "AVAILABLE",
        "battery_level": 92,
        "cost_per_trip": 3.50,
        "max_speed_mps": 1.2,
        "charging_status": "not_charging"
    },
    "AGV-003": {
        "type": "heavy_duty_agv",
        "capacity_pieces": 100,
        "current_location": "AGV_BASE",
        "status": "AVAILABLE",
        "battery_level": 87,
        "cost_per_trip": 5.00,
        "max_speed_mps": 1.5,
        "charging_status": "not_charging"
    },
    "AGV-004": {
        "type": "light_duty_agv",
        "capacity_pieces": 25,
        "current_location": "AGV_BASE",
        "status": "AVAILABLE",
        "battery_level": 82,
        "cost_per_trip": 2.50,
        "max_speed_mps": 1.0,
        "charging_status": "not_charging"
    }
}

# Routes data
routes_data = {
    "Warehouse A|Production Line A": {"distance_m": 150, "time_minutes": 4},
    "Warehouse B|Production Line A": {"distance_m": 220, "time_minutes": 6},
    "Warehouse A|Production Line B": {"distance_m": 180, "time_minutes": 5},
    "Warehouse B|Production Line B": {"distance_m": 240, "time_minutes": 6.5},
    "Central Warehouse|Production Line A": {"distance_m": 180, "time_minutes": 5},
    "Central Warehouse|Production Line B": {"distance_m": 200, "time_minutes": 5.5}
}

# Approval thresholds data
approval_thresholds = {
    "low_value": {"max_cost": 1000, "auto_approve": True},
    "medium_value": {"max_cost": 5000, "requires_manager": True},
    "high_value": {"max_cost": 999999, "requires_director": True}
}


def initialize_dataframes():
    """Initialize and return all DataFrames for the logistics system."""
    # Convert to DataFrames immediately
    inventory_df = pd.DataFrame.from_dict(inventory_data, orient='index')
    agv_df = pd.DataFrame.from_dict(agv_data, orient='index')
    routes_df = pd.DataFrame.from_dict(routes_data, orient='index')
    approval_df = pd.DataFrame.from_dict(approval_thresholds, orient='index')
    
    print("✅ Data loaded and converted to DataFrames successfully!")
    print(f"📦 Inventory DataFrame shape: {inventory_df.shape}")
    print(f"🚛 AGV Fleet DataFrame shape: {agv_df.shape}")
    print(f"🛣️ Routes DataFrame shape: {routes_df.shape}")
    print(f"✅ Approval Thresholds DataFrame shape: {approval_df.shape}")
    
    return inventory_df, agv_df, routes_df, approval_df


def demo_data_access(inventory_df, agv_df, routes_df):
    """Demonstrate data access examples."""
    print("🔍 DATA ACCESS EXAMPLES:")
    print("=" * 50)

    # Query specific inventory items
    print("1. Get HYDRAULIC-PUMP-HP450 details:")
    pump_info = inventory_df.loc['HYDRAULIC-PUMP-HP450']
    print(f"   Available: {pump_info['available_quantity']} units")
    print(f"   Location: {pump_info['warehouse_location']}")
    print(f"   Cost: ${pump_info['cost_per_unit']}")

    # Filter available AGVs
    print("\n2. Available AGVs:")
    available_agvs = agv_df[agv_df['status'] == 'AVAILABLE']
    print(f"   Count: {len(available_agvs)}")
    print(f"   IDs: {list(available_agvs.index)}")

    # Find low stock items
    print("\n3. Low stock items (below reorder point):")
    low_stock = inventory_df[inventory_df['available_quantity'] <= inventory_df['reorder_point']]
    if len(low_stock) > 0:
        print(f"   Items: {list(low_stock.index)}")
    else:
        print("   No items below reorder point")

    # Route analysis
    print("\n4. Fastest routes (under 5 minutes):")
    fast_routes = routes_df[routes_df['time_minutes'] < 5]
    print(f"   Count: {len(fast_routes)}")
    for route in fast_routes.index:
        print(f"   - {route}: {fast_routes.loc[route, 'time_minutes']} min")

    # Cost analysis
    print("\n5. High-value inventory items (>$100):")
    high_value = inventory_df[inventory_df['cost_per_unit'] > 100]
    print(f"   Count: {len(high_value)}")
    for item in high_value.index:
        cost = high_value.loc[item, 'cost_per_unit']
        print(f"   - {item}: ${cost}")

    print("\n✅ DataFrames are ready for use in your logistics agents!")


if __name__ == "__main__":
    # Initialize dataframes when run as main module
    inventory_df, agv_df, routes_df, approval_df = initialize_dataframes()
    demo_data_access(inventory_df, agv_df, routes_df)