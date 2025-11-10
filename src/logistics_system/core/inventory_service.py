#!/usr/bin/env python3
"""
Inventory Service - Core Business Logic
======================================

Extracted business logic from InventoryAgent for better separation of concerns.
This service handles all inventory operations independent of the Strands framework.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

# LLM Integration for AI capabilities (using Ollama)
try:
    import requests
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Configuration loader import
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config_loader import get_inventory_config, get_system_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InventoryService:
    """
    Core inventory business logic service.
    
    This class contains all the business logic for inventory operations,
    separated from Strands framework concerns. Can be used independently
    or wrapped by InventoryAgent.
    """
    
    def __init__(self, llm_model: str = None):
        # Load configuration from central config system with .env overrides
        system_config = get_system_config()
        ai_config = system_config.get('system_settings', {}).get('ai_config', {})
        
        # Environment variables override central config
        llm_backend = os.getenv('LLM_BACKEND', 'ollama').lower()
        self.llm_model = llm_model or os.getenv('OLLAMA_MODEL', ai_config.get('default_model', 'qwen2.5:7b'))
        self.llm_enabled = LLM_AVAILABLE and (llm_backend == 'ollama')
        
        # Get Ollama URL from env first, then central config
        ollama_base_url = os.getenv('OLLAMA_BASE_URL', ai_config.get('ollama_url', 'http://localhost:11434/api/generate'))
        self.ollama_url = ollama_base_url if ollama_base_url.endswith('/api/generate') else f"{ollama_base_url}/api/generate"
        
        # AI parameters from env with central config fallbacks
        self.temperature = float(os.getenv('OLLAMA_TEMPERATURE', str(ai_config.get('temperature', 0.1))))
        self.num_predict = int(os.getenv('OLLAMA_NUM_PREDICT', '200'))
        self.timeout = int(os.getenv('OLLAMA_TIMEOUT', str(ai_config.get('timeout_seconds', 60))))
        
        # Test LLM connection based on backend
        if self.llm_enabled and llm_backend == 'ollama':
            try:
                # Test if Ollama is running
                test_response = requests.post(
                    self.ollama_url,
                    json={"model": self.llm_model, "prompt": "Hello", "stream": False},
                    timeout=15
                )
                if test_response.status_code == 200:
                    logger.info(f"🧠 Ollama connected successfully for inventory AI with model: {self.llm_model}")
                else:
                    self.llm_enabled = False
                    logger.warning(f"🧠 Ollama connection failed - using rule-based inventory logic")
            except Exception as e:
                self.llm_enabled = False
                logger.warning(f"🧠 Ollama not available ({str(e)}) - using rule-based inventory logic")
        else:
            logger.warning("🧠 Requests library not available - using rule-based inventory logic")
        
        # Load inventory configuration from config files
        self._load_inventory_configuration()

    def _load_inventory_configuration(self):
        """Load inventory data from configuration files"""
        try:
            inventory_config = get_inventory_config()
            
            # Load parts data from parts_catalog (dictionary with part_number as keys)
            self.parts_inventory = {}
            parts_catalog = inventory_config.get('parts_catalog', {})
            
            for part_number, part_data in parts_catalog.items():
                self.parts_inventory[part_number] = {
                    "name": part_data.get('description', f'Part {part_number}'),
                    "current_stock": part_data.get('available_quantity', 0) + part_data.get('reserved_quantity', 0),
                    "reserved_quantity": part_data.get('reserved_quantity', 0),
                    "available_quantity": part_data.get('available_quantity', 0),
                    "minimum_stock": part_data.get('reorder_point', 10),
                    "maximum_stock": part_data.get('maximum_stock', 100),
                    "location": part_data.get('warehouse_location', 'Unknown Location'),
                    "cost_per_unit": part_data.get('cost_per_unit', 100.0),
                    "supplier": part_data.get('supplier', 'Unknown Supplier'),
                    "lead_time_days": part_data.get('lead_time_days', 7),
                    "last_updated": datetime.now().isoformat()
                }
            
            # Load demand history from demand_history (dictionary with part_number as keys)
            self.demand_history = {}
            demand_history_data = inventory_config.get('demand_history', {})
            
            for part_number, demand_list in demand_history_data.items():
                self.demand_history[part_number] = []
                
                for demand in demand_list:
                    self.demand_history[part_number].append({
                        "date": demand.get('date', datetime.now().isoformat()),
                        "quantity": demand.get('quantity', 0),
                        "priority": demand.get('priority', 'MEDIUM'),
                        "reason": demand.get('reason', 'Historical demand'),
                        "machine": demand.get('machine', 'Unknown')
                    })
            
            logger.info(f"📋 Loaded inventory config: {len(self.parts_inventory)} parts, {len(self.demand_history)} demand histories")
            
        except Exception as e:
            logger.error(f"❌ Failed to load inventory configuration: {e}")
            # Fallback to minimal default data
            self.parts_inventory = {
                "HYDRAULIC-PUMP-HP450": {
                    "name": "Hydraulic Pump HP450",
                    "current_stock": 24,
                    "reserved_quantity": 2,
                    "available_quantity": 22,
                    "minimum_stock": 5,
                    "maximum_stock": 50,
                    "location": "Central Warehouse",
                    "cost_per_unit": 245.00,
                    "supplier": "HydroTech Systems",
                    "lead_time_days": 1,
                    "last_updated": datetime.now().isoformat()
                }
            }
            self.demand_history = {}
        
        logger.info(f"🧠 AI InventoryService initialized with {len(self.parts_inventory)} parts and demand history")

    async def llm_inventory_decision(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Use Ollama LLM for intelligent inventory decisions and recommendations.
        
        Args:
            prompt: Decision prompt for the LLM
            context: Additional inventory context data
            
        Returns:
            LLM response for inventory decision-making
        """
        if not self.llm_enabled:
            return "LLM not available - using rule-based inventory logic"
        
        try:
            # Prepare context for LLM
            context_str = ""
            if context:
                context_str = f"\nInventory Context: {json.dumps(context, indent=2)}"
            
            full_prompt = f"""You are an AI Inventory Manager for a manufacturing facility.
Make intelligent inventory decisions based on the following:

{prompt}{context_str}

Provide clear recommendations with reasoning, cost analysis, and urgency levels. Be specific and actionable."""
            
            # Make request to Ollama
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.llm_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.num_predict
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from Ollama").strip()
            else:
                logger.error(f"❌ Ollama API error: {response.status_code}")
                return f"Ollama API error - using rule-based inventory logic"
            
        except Exception as e:
            logger.error(f"❌ Inventory LLM decision failed: {str(e)}")
            return f"LLM error: {str(e)} - using rule-based inventory logic"

    async def check_availability(
        self,
        part_number: str,
        quantity_needed: int,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Check inventory availability for a specific part with AI-powered recommendations.
        
        Args:
            part_number: Part number to check
            quantity_needed: Quantity requested
            priority: Request priority (URGENT, HIGH, MEDIUM, LOW)
            
        Returns:
            Dict with availability status, recommendations, and AI insights
        """
        logger.info(f"📦 Checking availability for {part_number} (qty: {quantity_needed})")
        
        try:
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Get part info
            part_info = self.get_inventory_info(part_number)
            
            if not part_info:
                return {
                    "available": False,
                    "part_number": part_number,
                    "error": f"Part {part_number} not found in inventory",
                    "alternatives": self.get_alternative_parts(part_number)
                }
            
            available_qty = part_info["available_quantity"]
            current_stock = part_info["current_stock"]
            
            # Basic availability check
            is_available = available_qty >= quantity_needed
            
            # Get AI-powered analysis
            analysis_context = {
                "part_info": part_info,
                "quantity_needed": quantity_needed,
                "priority": priority,
                "demand_history": self.demand_history.get(part_number, [])
            }
            
            ai_analysis = await self.llm_inventory_decision(
                f"Analyze availability request for {quantity_needed} units of {part_number} "
                f"with {priority} priority. Current stock: {current_stock}, Available: {available_qty}",
                analysis_context
            )
            
            result = {
                "available": is_available,
                "part_number": part_number,
                "part_name": part_info["name"],
                "quantity_needed": quantity_needed,
                "quantity_available": available_qty,
                "current_stock": current_stock,
                "reserved_quantity": part_info["reserved_quantity"],
                "location": part_info["location"],
                "cost_per_unit": part_info["cost_per_unit"],
                "total_cost": part_info["cost_per_unit"] * quantity_needed,
                "supplier": part_info["supplier"],
                "lead_time_days": part_info["lead_time_days"],
                "priority": priority,
                "ai_analysis": ai_analysis,
                "checked_at": datetime.now().isoformat()
            }
            
            # Add recommendations based on availability
            if is_available:
                result["recommendation"] = "Sufficient stock available for immediate fulfillment"
                result["action"] = "APPROVE"
            else:
                shortage = quantity_needed - available_qty
                result["shortage"] = shortage
                result["recommendation"] = f"Insufficient stock - short by {shortage} units"
                result["action"] = "BACKORDER" if priority in ["LOW", "MEDIUM"] else "EXPEDITE"
                result["alternatives"] = self.get_alternative_parts(part_number)
            
            logger.info(f"📦 Availability check complete: {is_available} ({available_qty}/{quantity_needed})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Availability check failed: {str(e)}")
            return {
                "available": False,
                "part_number": part_number,
                "error": str(e)
            }

    def get_inventory_info(self, part_number: str) -> Dict[str, Any]:
        """Get complete inventory information for a part"""
        if part_number in self.parts_inventory:
            return self.parts_inventory[part_number].copy()
        return None

    def get_alternative_parts(self, part_number: str) -> List[str]:
        """
        Get alternative parts that could substitute for the requested part.
        Currently returns similar parts - could be enhanced with AI recommendations.
        """
        alternatives = []
        
        # Simple pattern matching for alternatives
        if "HYDRAULIC-PUMP" in part_number:
            alternatives = [p for p in self.parts_inventory.keys() if "HYDRAULIC" in p and p != part_number]
        elif "MOTOR" in part_number:
            alternatives = [p for p in self.parts_inventory.keys() if "MOTOR" in p and p != part_number]
        elif "VALVE" in part_number:
            alternatives = [p for p in self.parts_inventory.keys() if "VALVE" in p and p != part_number]
        
        return alternatives[:3]  # Return max 3 alternatives

    async def reserve_inventory(
        self,
        part_number: str,
        quantity: int,
        requester: str = "Unknown",
        reason: str = "Production request"
    ) -> Dict[str, Any]:
        """Reserve inventory for a specific request"""
        logger.info(f"📦 Reserving {quantity} units of {part_number} for {requester}")
        
        try:
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Check if part exists and has sufficient stock
            part_info = self.get_inventory_info(part_number)
            if not part_info:
                return {
                    "reserved": False,
                    "error": f"Part {part_number} not found in inventory"
                }
            
            available_qty = part_info["available_quantity"]
            if available_qty < quantity:
                return {
                    "reserved": False,
                    "error": f"Insufficient stock: need {quantity}, available {available_qty}"
                }
            
            # Update inventory (simulate - in real system this would update database)
            self.parts_inventory[part_number]["reserved_quantity"] += quantity
            self.parts_inventory[part_number]["available_quantity"] -= quantity
            
            reservation_id = f"RES-{part_number}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            return {
                "reserved": True,
                "reservation_id": reservation_id,
                "part_number": part_number,
                "quantity_reserved": quantity,
                "requester": requester,
                "reason": reason,
                "reserved_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Reservation failed: {str(e)}")
            return {
                "reserved": False,
                "error": str(e)
            }

    async def get_inventory_status(self, part_numbers: List[str] = None) -> Dict[str, Any]:
        """Get comprehensive inventory status"""
        logger.info(f"📊 Getting inventory status for {len(part_numbers) if part_numbers else 'all'} parts")
        
        try:
            await asyncio.sleep(0.2)  # Simulate processing time
            
            # Default to all parts if none specified
            if part_numbers is None:
                part_numbers = list(self.parts_inventory.keys())
            
            status_data = {}
            total_value = 0.0
            low_stock_items = []
            
            for part_number in part_numbers:
                part_info = self.get_inventory_info(part_number)
                if part_info:
                    part_value = part_info["current_stock"] * part_info["cost_per_unit"]
                    total_value += part_value
                    
                    status_data[part_number] = {
                        "name": part_info["name"],
                        "current_stock": part_info["current_stock"],
                        "available_quantity": part_info["available_quantity"],
                        "reserved_quantity": part_info["reserved_quantity"],
                        "minimum_stock": part_info["minimum_stock"],
                        "stock_level": "OK" if part_info["current_stock"] >= part_info["minimum_stock"] else "LOW",
                        "location": part_info["location"],
                        "value": part_value,
                        "last_updated": part_info["last_updated"]
                    }
                    
                    # Track low stock items
                    if part_info["current_stock"] <= part_info["minimum_stock"]:
                        low_stock_items.append(part_number)
            
            return {
                "success": True,
                "total_parts": len(status_data),
                "total_inventory_value": total_value,
                "low_stock_count": len(low_stock_items),
                "low_stock_items": low_stock_items,
                "parts_status": status_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Status check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global service instance
_inventory_service = None

def get_inventory_service() -> InventoryService:
    """Get or create global inventory service instance"""
    global _inventory_service
    if _inventory_service is None:
        _inventory_service = InventoryService()
    return _inventory_service