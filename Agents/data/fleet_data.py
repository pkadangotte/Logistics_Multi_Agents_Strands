"""
Fleet Data Module
Contains AGV fleet and routing data definitions and access functions.
"""

import pandas as pd

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
    "Central Warehouse|Production Line B": {"distance_m": 200, "time_minutes": 5.5},
    "Warehouse A|Manufacturing Plant Delta": {"distance_m": 350, "time_minutes": 9},
    "Warehouse B|Manufacturing Plant Delta": {"distance_m": 420, "time_minutes": 11},
    "Central Warehouse|Manufacturing Plant Delta": {"distance_m": 380, "time_minutes": 10},
    "Inventory Warehouse|Manufacturing Plant Delta": {"distance_m": 320, "time_minutes": 8.5},
    "AGV_BASE|Manufacturing Plant Delta": {"distance_m": 300, "time_minutes": 8}
}


def get_fleet_dataframes():
    """Initialize and return AGV and routes DataFrames."""
    agv_df = pd.DataFrame.from_dict(agv_data, orient='index')
    routes_df = pd.DataFrame.from_dict(routes_data, orient='index')
    
    print(f"🚛 AGV Fleet DataFrame loaded with shape: {agv_df.shape}")
    print(f"🛣️ Routes DataFrame loaded with shape: {routes_df.shape}")
    
    return agv_df, routes_df


def demo_fleet_access(agv_df, routes_df):
    """Demonstrate fleet data access examples."""
    print("🔍 FLEET DATA ACCESS EXAMPLES:")
    print("=" * 35)

    # Filter available AGVs
    print("1. Available AGVs:")
    available_agvs = agv_df[agv_df['status'] == 'AVAILABLE']
    print(f"   Count: {len(available_agvs)}")
    print(f"   IDs: {list(available_agvs.index)}")

    # Route analysis
    print("\n2. Fastest routes (under 5 minutes):")
    fast_routes = routes_df[routes_df['time_minutes'] < 5]
    print(f"   Count: {len(fast_routes)}")
    for route in fast_routes.index:
        print(f"   - {route}: {fast_routes.loc[route, 'time_minutes']} min")

    # AGV capacity analysis
    print("\n3. AGV capacity summary:")
    total_capacity = agv_df['capacity_pieces'].sum()
    avg_battery = agv_df['battery_level'].mean()
    print(f"   Total fleet capacity: {total_capacity} pieces")
    print(f"   Average battery level: {avg_battery:.1f}%")

    # High capacity AGVs
    print("\n4. High-capacity AGVs (>50 pieces):")
    high_cap = agv_df[agv_df['capacity_pieces'] > 50]
    for agv in high_cap.index:
        cap = high_cap.loc[agv, 'capacity_pieces']
        agv_type = high_cap.loc[agv, 'type']
        print(f"   - {agv}: {cap} pieces ({agv_type})")

    print("\n✅ Fleet DataFrames are ready for use!")


if __name__ == "__main__":
    # Test fleet data when run directly
    agv_df, routes_df = get_fleet_dataframes()
    demo_fleet_access(agv_df, routes_df)