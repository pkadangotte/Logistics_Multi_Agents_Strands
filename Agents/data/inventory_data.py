"""
Inventory Data Module
Contains inventory definitions and data access functions.
"""

import pandas as pd

# Data for Inventory
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


def get_inventory_dataframe():
    """Initialize and return inventory DataFrame."""
    inventory_df = pd.DataFrame.from_dict(inventory_data, orient='index')
    print(f"📦 Inventory DataFrame loaded with shape: {inventory_df.shape}")
    return inventory_df


def demo_inventory_access(inventory_df):
    """Demonstrate inventory data access examples."""
    print("🔍 INVENTORY DATA ACCESS EXAMPLES:")
    print("=" * 40)

    # Query specific inventory items
    print("1. Get HYDRAULIC-PUMP-HP450 details:")
    pump_info = inventory_df.loc['HYDRAULIC-PUMP-HP450']
    print(f"   Available: {pump_info['available_quantity']} units")
    print(f"   Location: {pump_info['warehouse_location']}")
    print(f"   Cost: ${pump_info['cost_per_unit']}")

    # Find low stock items
    print("\n2. Low stock items (below reorder point):")
    low_stock = inventory_df[inventory_df['available_quantity'] <= inventory_df['reorder_point']]
    if len(low_stock) > 0:
        print(f"   Items: {list(low_stock.index)}")
    else:
        print("   No items below reorder point")

    # Cost analysis
    print("\n3. High-value inventory items (>$100):")
    high_value = inventory_df[inventory_df['cost_per_unit'] > 100]
    print(f"   Count: {len(high_value)}")
    for item in high_value.index:
        cost = high_value.loc[item, 'cost_per_unit']
        print(f"   - {item}: ${cost}")

    print("\n✅ Inventory DataFrame is ready for use!")


if __name__ == "__main__":
    # Test inventory data when run directly
    inventory_df = get_inventory_dataframe()
    demo_inventory_access(inventory_df)