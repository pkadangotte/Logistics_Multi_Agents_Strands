"""
Inventory Data Provider Module
Provides the InventoryDataProvider class for inventory management operations.
"""

from datetime import datetime
import json
from typing import Dict, List, Union


class InventoryDataProvider:
    """
    Data access class for inventory management operations.
    Provides methods to query, reserve, and manage inventory data.
    """
    
    def __init__(self, inventory_df):
        """Initialize with inventory DataFrame"""
        self.inventory_df = inventory_df.copy()
        self.reservation_log = []
    
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
        
    def get_part_info(self, part_number: str) -> dict:
        """
        Get complete information for a specific part number.
        
        Args:
            part_number: The part number to query
            
        Returns:
            Dictionary with part information or None if not found
        """
        try:
            if part_number not in self.inventory_df.index:
                return {"error": f"Part number '{part_number}' not found"}
                
            part_info = self.inventory_df.loc[part_number].to_dict()
            part_info['part_number'] = part_number
            part_info['net_available'] = part_info['available_quantity'] - part_info['reserved_quantity']
            
            return self._convert_to_json_serializable(part_info)
        except Exception as e:
            return {"error": f"Error retrieving part info: {str(e)}"}
    
    def check_availability(self, part_number: str, quantity: int) -> dict:
        """
        Check if requested quantity is available for a part.
        
        Args:
            part_number: The part number to check
            quantity: Requested quantity
            
        Returns:
            Dictionary with availability status and details
        """
        part_info = self.get_part_info(part_number)
        
        if "error" in part_info:
            return part_info
            
        net_available = part_info['net_available']
        
        result = {
            "part_number": part_number,
            "requested_quantity": quantity,
            "available_quantity": part_info['available_quantity'],
            "reserved_quantity": part_info['reserved_quantity'],
            "net_available": net_available,
            "can_fulfill": quantity <= net_available,
            "shortage": max(0, quantity - net_available),
            "lead_time_days": part_info['lead_time_days'],
            "cost_per_unit": part_info['cost_per_unit'],
            "total_cost": quantity * part_info['cost_per_unit']
        }
        return self._convert_to_json_serializable(result)
    
    def reserve_quantity(self, part_number: str, quantity: int, requester: str = "system") -> dict:
        """
        Reserve a specified quantity for a part number.
        
        Args:
            part_number: The part number to reserve
            quantity: Quantity to reserve
            requester: Who is making the reservation
            
        Returns:
            Dictionary with reservation result
        """
        # Check availability first
        availability = self.check_availability(part_number, quantity)
        
        if "error" in availability:
            return availability
            
        if not availability["can_fulfill"]:
            return {
                "success": False,
                "error": f"Insufficient inventory. Requested: {quantity}, Available: {availability['net_available']}",
                "shortage": availability["shortage"]
            }
        
        # Perform reservation
        try:
            self.inventory_df.loc[part_number, 'reserved_quantity'] += quantity
            
            # Log the reservation
            reservation_record = {
                "timestamp": datetime.now().isoformat(),
                "part_number": part_number,
                "quantity_reserved": int(quantity),
                "requester": requester,
                "total_reserved": int(self.inventory_df.loc[part_number, 'reserved_quantity']),
                "remaining_available": int(self.inventory_df.loc[part_number, 'available_quantity'] - self.inventory_df.loc[part_number, 'reserved_quantity'])
            }
            
            self.reservation_log.append(reservation_record)
            
            return {
                "success": True,
                "reservation_id": len(self.reservation_log),
                "part_number": part_number,
                "quantity_reserved": int(quantity),
                "total_cost": float(quantity * availability["cost_per_unit"]),
                "remaining_available": reservation_record["remaining_available"],
                "timestamp": reservation_record["timestamp"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Reservation failed: {str(e)}"}
    
    def release_reservation(self, part_number: str, quantity: int, requester: str = "system") -> dict:
        """
        Release a reserved quantity back to available inventory.
        
        Args:
            part_number: The part number
            quantity: Quantity to release
            requester: Who is releasing the reservation
            
        Returns:
            Dictionary with release result
        """
        try:
            if part_number not in self.inventory_df.index:
                return {"error": f"Part number '{part_number}' not found"}
            
            current_reserved = self.inventory_df.loc[part_number, 'reserved_quantity']
            
            if quantity > current_reserved:
                return {
                    "success": False,
                    "error": f"Cannot release {quantity} units. Only {current_reserved} units are reserved."
                }
            
            # Perform release
            self.inventory_df.loc[part_number, 'reserved_quantity'] -= quantity
            
            # Log the release
            release_record = {
                "timestamp": datetime.now().isoformat(),
                "part_number": part_number,
                "quantity_released": quantity,
                "requester": requester,
                "total_reserved": self.inventory_df.loc[part_number, 'reserved_quantity'],
                "total_available": self.inventory_df.loc[part_number, 'available_quantity'] - self.inventory_df.loc[part_number, 'reserved_quantity']
            }
            
            self.reservation_log.append(release_record)
            
            return {
                "success": True,
                "part_number": part_number,
                "quantity_released": quantity,
                "remaining_reserved": release_record["total_reserved"],
                "net_available": release_record["total_available"],
                "timestamp": release_record["timestamp"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Release failed: {str(e)}"}
    
    def get_low_stock_items(self) -> list:
        """Get list of items below reorder point"""
        low_stock = self.inventory_df[
            (self.inventory_df['available_quantity'] - self.inventory_df['reserved_quantity']) 
            <= self.inventory_df['reorder_point']
        ]
        
        return [
            {
                "part_number": idx,
                "net_available": row['available_quantity'] - row['reserved_quantity'],
                "reorder_point": row['reorder_point'],
                "supplier": row['supplier'],
                "lead_time_days": row['lead_time_days']
            }
            for idx, row in low_stock.iterrows()
        ]
    
    def get_inventory_summary(self) -> dict:
        """Get overall inventory summary statistics"""
        df = self.inventory_df
        
        return {
            "total_parts": len(df),
            "total_inventory_value": (df['available_quantity'] * df['cost_per_unit']).sum(),
            "total_reserved_value": (df['reserved_quantity'] * df['cost_per_unit']).sum(),
            "low_stock_count": len(self.get_low_stock_items()),
            "categories": df['category'].value_counts().to_dict(),
            "warehouses": df['warehouse_location'].value_counts().to_dict(),
            "total_reservations": len(self.reservation_log)
        }
    
    def get_reservation_history(self, part_number: str = None) -> list:
        """Get reservation history, optionally filtered by part number"""
        if part_number:
            return [log for log in self.reservation_log if log['part_number'] == part_number]
        return self.reservation_log
    
    def search_parts(self, search_term: str, search_field: str = "description") -> Union[List[Dict], Dict]:
        """
        Search for parts by description, category, or supplier.
        
        Args:
            search_term: Term to search for
            search_field: Field to search in ('description', 'category', 'supplier')
        """
        try:
            if search_field not in ['description', 'category', 'supplier']:
                return {"error": "Invalid search field. Use 'description', 'category', or 'supplier'"}
            
            mask = self.inventory_df[search_field].str.contains(search_term, case=False, na=False)
            results = self.inventory_df[mask]
            
            return [
                {
                    "part_number": idx,
                    "description": row['description'],
                    "category": row['category'],
                    "supplier": row['supplier'],
                    "net_available": row['available_quantity'] - row['reserved_quantity'],
                    "cost_per_unit": row['cost_per_unit']
                }
                for idx, row in results.iterrows()
            ]
            
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}


def initialize_inventory_manager(inventory_df):
    """Initialize the inventory manager with the provided DataFrame."""
    manager = InventoryDataProvider(inventory_df)
    
    print("✅ Inventory Data Manager initialized!")
    print(f"📊 Managing {len(inventory_df)} parts")
    print(f"💰 Total inventory value: ${manager.get_inventory_summary()['total_inventory_value']:,.2f}")
    
    return manager