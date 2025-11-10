#!/usr/bin/env python3
"""
AI-Powered Inventory Agent - Part of Manufacturing Replenishment System
======================================================================

REFACTORED VERSION - Now uses InventoryService for business logic separation.

This intelligent agent manages inventory operations including:
- AI-driven stock level monitoring and predictions
- Intelligent availability checking with demand forecasting
- Smart reservation management
- Cost optimization analysis
- Lead time estimation with AI insights
- Inventory optimization recommendations

Architecture:
- InventoryAgent: Strands framework wrapper (this file)
- InventoryService: Core business logic (extracted to service layer)
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Strands Agent imports
from strands import Agent, tool

# Import the new service layer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.logistics_system.core.inventory_service import InventoryService, get_inventory_service
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    print(f"Warning: InventoryService not available - {e}")

# Fallback imports for backward compatibility
try:
    import requests
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

from config.config_loader import get_inventory_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InventoryAgent:
    """
    AI-Powered Inventory Agent - Strands Framework Wrapper.
    
    REFACTORED: Now delegates business logic to InventoryService for better separation
    of concerns. This class focuses on Strands framework integration while the service
    handles core inventory operations.
    
    Architecture:
    - This class: Strands agent wrapper, tool registration, API compatibility
    - InventoryService: Core business logic, AI integration, data management
    """
    
    def __init__(self, llm_model: str = None):
        self.llm_model = llm_model or os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
        
        # Initialize the service layer (new architecture)
        if SERVICE_AVAILABLE:
            self.service = get_inventory_service()
            logger.info("✅ Using new InventoryService architecture")
            
            # For backward compatibility, expose service data
            self.inventory_data = getattr(self.service, 'parts_inventory', {})
            self.demand_history = getattr(self.service, 'demand_history', {})
            self.llm_enabled = getattr(self.service, 'llm_enabled', False)
        else:
            # Fallback to legacy implementation
            logger.warning("⚠️ InventoryService not available - using legacy implementation")
            self._init_legacy_implementation()
        
        logger.info(f"🧠 InventoryAgent initialized - Service: {SERVICE_AVAILABLE}, Parts: {len(self.inventory_data)}")

    def _init_legacy_implementation(self):
        """Fallback to legacy implementation if service is unavailable"""
        # Load configuration from .env file
        import os
        llm_backend = os.getenv('LLM_BACKEND', 'ollama').lower()
        self.llm_enabled = LLM_AVAILABLE and (llm_backend == 'ollama')
        
        # Get Ollama URL from .env with fallback
        ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_url = f"{ollama_base_url}/api/generate" if not ollama_base_url.endswith('/api/generate') else ollama_base_url
        
        # Test LLM connection
        if self.llm_enabled and llm_backend == 'ollama':
            try:
                test_response = requests.post(
                    self.ollama_url,
                    json={"model": self.llm_model, "prompt": "Hello", "stream": False},
                    timeout=15
                )
                if test_response.status_code == 200:
                    logger.info(f"🧠 Ollama connected (legacy mode) with model: {self.llm_model}")
                else:
                    self.llm_enabled = False
                    logger.warning(f"🧠 Ollama connection failed - using rule-based inventory management")
            except Exception as e:
                self.llm_enabled = False
                logger.warning(f"🧠 Ollama not available ({str(e)}) - using rule-based inventory management")
        
        # Load legacy configuration
        self._load_inventory_configuration()
        self.service = None

    def _load_inventory_configuration(self):
        """Load inventory data from configuration files"""
        try:
            inventory_config = get_inventory_config()
            
            # Load parts catalog with timestamp updates
            self.inventory_data = {}
            parts_catalog = inventory_config.get('parts_catalog', {})
            
            for part_number, part_data in parts_catalog.items():
                # Add timestamp to each part
                inventory_entry = part_data.copy()
                inventory_entry['last_updated'] = datetime.now().isoformat()
                self.inventory_data[part_number] = inventory_entry
            
            # Load demand history
            self.demand_history = inventory_config.get('demand_history', {})
            
            # Load warehouse locations
            self.warehouse_locations = inventory_config.get('warehouse_locations', [])
            
            logger.info(f"📋 Loaded inventory config: {len(self.inventory_data)} parts, {len(self.demand_history)} demand histories")
            
        except Exception as e:
            logger.error(f"❌ Failed to load inventory configuration: {e}")
            # Fallback to minimal default configuration
            self.inventory_data = {
                "PART-DEFAULT": {
                    "available_quantity": 10,
                    "reserved_quantity": 0,
                    "warehouse_location": "Central Warehouse",
                    "cost_per_unit": 10.0,
                    "lead_time_days": 1,
                    "supplier": "Default Supplier",
                    "last_updated": datetime.now().isoformat(),
                    "description": "Default part (config loading failed)",
                    "category": "Default"
                }
            }
            self.demand_history = {}
            self.warehouse_locations = ["Central Warehouse"]

    async def llm_inventory_decision(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Use Ollama LLM for intelligent inventory management decisions.
        
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

Provide clear, actionable inventory recommendations with reasoning. Be concise and specific."""
            
            # Make request to Ollama
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.llm_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 150
                    }
                },
                timeout=120
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

    async def analyze_demand_patterns(self, part_number: str) -> Dict[str, Any]:
        """
        Use AI to analyze demand patterns and predict future needs.
        
        Args:
            part_number: Part to analyze
            
        Returns:
            AI-powered demand analysis
        """
        try:
            demand_data = self.demand_history.get(part_number, [])
            current_stock = self.inventory_data.get(part_number, {})
            
            analysis_context = {
                "part_number": part_number,
                "current_stock": current_stock.get("available_quantity", 0),
                "reserved_stock": current_stock.get("reserved_quantity", 0),
                "recent_demand": demand_data[-5:],  # Last 5 days
                "lead_time": current_stock.get("lead_time_days", 0),
                "cost_per_unit": current_stock.get("cost_per_unit", 0)
            }
            
            demand_prompt = f"""
Analyze the demand pattern for {part_number} and provide:
1. Predicted demand for next 3 days
2. Recommended reorder point
3. Optimal reorder quantity
4. Risk assessment (stockout probability)
5. Cost optimization suggestions

Consider seasonality, trends, and priority patterns in the historical data.
"""
            
            llm_analysis = await self.llm_inventory_decision(demand_prompt, analysis_context)
            
            return {
                "success": True,
                "part_number": part_number,
                "ai_analysis": llm_analysis,
                "demand_data": analysis_context,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Demand pattern analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def check_availability(
        self, 
        part_number: str, 
        quantity_needed: int,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Check if requested quantity is available in inventory.
        REFACTORED: Delegates to InventoryService for business logic.
        
        Args:
            part_number: Part number to check
            quantity_needed: Required quantity
            priority: Request priority (affects reservation logic)
            
        Returns:
            Dict with availability status and details
        """
        if self.service and SERVICE_AVAILABLE:
            # Use new service architecture
            return await self.service.check_availability(part_number, quantity_needed, priority)
        else:
            # Fallback to legacy implementation
            return await self._legacy_check_availability(part_number, quantity_needed, priority)

    async def _legacy_check_availability(
        self, 
        part_number: str, 
        quantity_needed: int,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """Legacy implementation for backward compatibility"""
        logger.info(f"📦 [LEGACY] Checking availability for {part_number} (qty: {quantity_needed})")
        
        try:
            # Simulate processing time
            await asyncio.sleep(0.2)
            
            # Check if part exists
            if part_number not in self.inventory_data:
                return {
                    "available": False,
                    "error": f"Part {part_number} not found in inventory",
                    "suggestions": self.get_alternative_parts(part_number)
                }
            
            part_data = self.inventory_data[part_number]
            available_qty = part_data["available_quantity"]
            
            # Use AI to make intelligent availability decisions
            availability_context = {
                "part_number": part_number,
                "requested_quantity": quantity_needed,
                "available_stock": available_qty,
                "reserved_stock": part_data["reserved_quantity"],
                "priority": priority,
                "cost_per_unit": part_data["cost_per_unit"],
                "lead_time": part_data["lead_time_days"],
                "recent_demand": self.demand_history.get(part_number, [])[-3:]
            }
            
            availability_prompt = f"""
Should we fulfill a request for {quantity_needed} units of {part_number} with {priority} priority?
Current stock: {available_qty} available, {part_data["reserved_quantity"]} reserved
Consider:
1. Stock levels vs demand
2. Priority level impact
3. Reserved stock management
4. Reorder recommendations

Provide recommendation: APPROVE, APPROVE_PARTIAL, or DECLINE with reasoning.
"""
            
            ai_recommendation = await self.llm_inventory_decision(availability_prompt, availability_context)
            
            # Check basic availability
            is_available = available_qty >= quantity_needed
            
            result = {
                "available": is_available,
                "part_number": part_number,
                "requested_quantity": quantity_needed,
                "available_quantity": available_qty,
                "reserved_quantity": part_data["reserved_quantity"],
                "warehouse_location": part_data["warehouse_location"],
                "cost_per_unit": part_data["cost_per_unit"],
                "total_cost": part_data["cost_per_unit"] * quantity_needed,
                "lead_time_days": part_data["lead_time_days"],
                "supplier": part_data["supplier"],
                "ai_recommendation": ai_recommendation,
                "check_timestamp": datetime.now().isoformat()
            }
            
            # Add shortage info if not fully available
            if not is_available:
                shortage = quantity_needed - available_qty
                result.update({
                    "shortage_quantity": shortage,
                    "partial_fulfillment": available_qty > 0,
                    "estimated_restock_date": (datetime.now() + timedelta(days=part_data["lead_time_days"])).isoformat(),
                    "ai_shortage_advice": ai_recommendation
                })
            
            logger.info(f"📦 Availability check complete: {is_available} ({available_qty}/{quantity_needed})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Availability check failed: {str(e)}")
            return {
                "available": False,
                "error": str(e)
            }

    async def reserve_inventory(
        self,
        part_number: str,
        quantity: int,
        request_id: str,
        duration_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Reserve inventory for a specific request.
        REFACTORED: Delegates to InventoryService for business logic.
        
        Args:
            part_number: Part to reserve
            quantity: Quantity to reserve
            request_id: Associated request ID
            duration_hours: Reservation duration
            
        Returns:
            Dict with reservation details
        """
        if self.service and SERVICE_AVAILABLE:
            # Use new service architecture
            return await self.service.reserve_inventory(part_number, quantity, request_id, f"Request: {request_id}")
        else:
            # Fallback to legacy implementation
            return await self._legacy_reserve_inventory(part_number, quantity, request_id, duration_hours)

    async def _legacy_reserve_inventory(
        self,
        part_number: str,
        quantity: int,
        request_id: str,
        duration_hours: int = 24
    ) -> Dict[str, Any]:
        """Legacy reservation implementation"""
        logger.info(f"🔒 [LEGACY] Reserving {quantity} of {part_number} for {request_id}")
        
        try:
            await asyncio.sleep(0.1)
            
            if part_number not in self.inventory_data:
                return {
                    "reserved": False,
                    "error": f"Part {part_number} not found"
                }
            
            part_data = self.inventory_data[part_number]
            
            if part_data["available_quantity"] < quantity:
                return {
                    "reserved": False,
                    "error": "Insufficient inventory",
                    "available_quantity": part_data["available_quantity"]
                }
            
            # Update inventory (simulate reservation)
            part_data["available_quantity"] -= quantity
            part_data["reserved_quantity"] += quantity
            
            reservation = {
                "reserved": True,
                "reservation_id": f"RES-{request_id}-{int(datetime.now().timestamp())}",
                "part_number": part_number,
                "quantity": quantity,
                "request_id": request_id,
                "expires_at": (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
                "reserved_at": datetime.now().isoformat()
            }
            
            logger.info(f"🔒 Reservation successful: {reservation['reservation_id']}")
            return reservation
            
        except Exception as e:
            logger.error(f"❌ Reservation failed: {str(e)}")
            return {
                "reserved": False,
                "error": str(e)
            }

    async def get_inventory_status(self, part_numbers: List[str] = None) -> Dict[str, Any]:
        """
        Get current inventory status for specified parts or all parts.
        REFACTORED: Delegates to InventoryService for business logic.
        
        Args:
            part_numbers: List of specific parts to check (optional)
            
        Returns:
            Dict with inventory status
        """
        if self.service and SERVICE_AVAILABLE:
            # Use new service architecture
            return await self.service.get_inventory_status(part_numbers)
        else:
            # Fallback to legacy implementation
            return await self._legacy_get_inventory_status(part_numbers)

    async def _legacy_get_inventory_status(self, part_numbers: List[str] = None) -> Dict[str, Any]:
        """Legacy status implementation"""
        logger.info(f"📊 [LEGACY] Getting inventory status")
        
        try:
            await asyncio.sleep(0.1)
            
            parts_to_check = part_numbers or list(self.inventory_data.keys())
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "parts_count": len(parts_to_check),
                "parts": {}
            }
            
            for part_number in parts_to_check:
                if part_number in self.inventory_data:
                    part_data = self.inventory_data[part_number]
                    status["parts"][part_number] = {
                        "available": part_data["available_quantity"],
                        "reserved": part_data["reserved_quantity"],
                        "location": part_data["warehouse_location"],
                        "cost_per_unit": part_data["cost_per_unit"],
                        "status": "IN_STOCK" if part_data["available_quantity"] > 0 else "OUT_OF_STOCK"
                    }
                else:
                    status["parts"][part_number] = {
                        "status": "NOT_FOUND"
                    }
            
            return {
                "success": True,
                "inventory_status": status
            }
            
        except Exception as e:
            logger.error(f"❌ Status check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_inventory_info(self, part_number: str) -> Dict[str, Any]:
        """
        Get direct inventory information for a specific part.
        
        Args:
            part_number: Part number to look up
            
        Returns:
            Dict with inventory data or None if part not found
        """
        return self.inventory_data.get(part_number)

    def get_alternative_parts(self, part_number: str) -> List[str]:
        """Get alternative/similar parts"""
        # Simple logic - return other parts from same category
        alternatives = []
        
        if "ABC" in part_number:
            alternatives = ["PART-ABC124", "PART-ABC125"]
        elif "XYZ" in part_number:
            alternatives = ["PART-XYZ790", "PART-XYZ791"]
        elif "DEF" in part_number:
            alternatives = ["PART-DEF457", "PART-DEF458"]
        
        return alternatives

    async def run_inventory_monitoring(self):
        """
        Main inventory monitoring loop
        """
        logger.info(f"🔄 Starting InventoryAgent monitoring loop")
        
        while True:
            try:
                # Monitor inventory levels
                for part_number, part_data in self.inventory_data.items():
                    available = part_data["available_quantity"]
                    reserved = part_data["reserved_quantity"]
                    
                    # Check for low stock
                    if available < 10:
                        logger.warning(f"⚠️  Low stock alert: {part_number} ({available} available)")
                    
                    # Check for expired reservations (simplified)
                    if reserved > 0:
                        logger.info(f"🔒 Active reservations: {part_number} ({reserved} reserved)")
                
                # Wait before next check
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                logger.info(f"🛑 Inventory monitoring stopped")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def get_ai_inventory_recommendations(self) -> Dict[str, Any]:
        """
        Get AI-powered recommendations for inventory optimization.
        
        Returns:
            Dict with LLM-generated inventory optimization recommendations
        """
        logger.info(f"🧠 Getting AI inventory optimization recommendations")
        
        try:
            # Gather comprehensive inventory data for analysis
            inventory_context = {
                "total_parts": len(self.inventory_data),
                "inventory_summary": {},
                "low_stock_items": [],
                "high_stock_items": [],
                "demand_patterns": self.demand_history
            }
            
            # Analyze each part
            for part_number, part_data in self.inventory_data.items():
                available = part_data["available_quantity"]
                reserved = part_data["reserved_quantity"]
                cost = part_data["cost_per_unit"]
                
                inventory_context["inventory_summary"][part_number] = {
                    "available": available,
                    "reserved": reserved,
                    "total_value": available * cost,
                    "lead_time": part_data["lead_time_days"],
                    "location": part_data["warehouse_location"]
                }
                
                # Flag low/high stock items
                if available < 20:
                    inventory_context["low_stock_items"].append(part_number)
                elif available > 100:
                    inventory_context["high_stock_items"].append(part_number)
            
            optimization_prompt = """
Analyze the current inventory status and provide optimization recommendations:

1. REORDER STRATEGY: Which parts need immediate reordering and optimal quantities?
2. COST OPTIMIZATION: Opportunities to reduce inventory carrying costs?
3. DEMAND FORECASTING: Predicted demand patterns and stock level recommendations?
4. RISK MANAGEMENT: Items at risk of stockout and mitigation strategies?
5. WAREHOUSE EFFICIENCY: Location and distribution improvements?

Provide specific, actionable recommendations with priorities.
"""
            
            llm_analysis = await self.llm_inventory_decision(optimization_prompt, inventory_context)
            
            return {
                "success": True,
                "ai_recommendations": llm_analysis,
                "inventory_metrics": inventory_context,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI inventory recommendations failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def predict_demand_with_ai(self, part_number: str, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Use AI to predict future demand for a specific part.
        
        Args:
            part_number: Part to analyze
            days_ahead: Number of days to predict
            
        Returns:
            Dict with AI-powered demand predictions
        """
        logger.info(f"🔮 Predicting demand for {part_number} ({days_ahead} days ahead)")
        
        try:
            demand_analysis = await self.analyze_demand_patterns(part_number)
            
            if demand_analysis.get("success"):
                prediction_context = demand_analysis["demand_data"]
                
                prediction_prompt = f"""
Based on the historical demand data, predict the daily demand for {part_number} over the next {days_ahead} days.

Provide:
1. Daily demand predictions (quantities)
2. Confidence levels for each prediction
3. Factors influencing demand (trends, seasonality, priority patterns)
4. Recommended safety stock levels
5. Optimal reorder timing

Format as specific daily predictions with reasoning.
"""
                
                llm_prediction = await self.llm_inventory_decision(prediction_prompt, prediction_context)
                
                return {
                    "success": True,
                    "part_number": part_number,
                    "prediction_period_days": days_ahead,
                    "ai_demand_forecast": llm_prediction,
                    "historical_context": prediction_context,
                    "predicted_at": datetime.now().isoformat()
                }
            else:
                return demand_analysis
                
        except Exception as e:
            logger.error(f"❌ Demand prediction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global InventoryAgent instance for tools to use
# REFACTORED: Now uses service layer architecture
_inventory_agent = InventoryAgent(llm_model="qwen2.5:7b")  # Use qwen2.5:7b model for better performance

# Strands Agent Tools - Explicitly registered functions with @tool decorator

@tool
async def check_availability(
    part_number: str, 
    quantity_needed: int,
    priority: str = "MEDIUM"
) -> Dict[str, Any]:
    """
    Check if requested quantity is available in inventory with AI-powered analysis.
    
    Args:
        part_number: Part number to check (e.g., 'HYDRAULIC-PUMP-HP450', 'PART-ABC123')
        quantity_needed: Required quantity in units
        priority: Request priority (LOW, MEDIUM, HIGH, URGENT) - affects allocation logic
        
    Returns:
        Dict with availability status, costs, lead times, and AI recommendations
    """
    return await _inventory_agent.check_availability(part_number, quantity_needed, priority)

@tool
async def reserve_inventory(
    part_number: str,
    quantity: int,
    request_id: str,
    duration_hours: int = 24
) -> Dict[str, Any]:
    """
    Reserve inventory for a specific replenishment request.
    
    Args:
        part_number: Part to reserve from inventory
        quantity: Quantity to reserve in units
        request_id: Associated request ID for tracking purposes
        duration_hours: Reservation duration in hours (default: 24)
        
    Returns:
        Dict with reservation details including reservation ID and expiration
    """
    return await _inventory_agent.reserve_inventory(part_number, quantity, request_id, duration_hours)

@tool
async def get_inventory_status(part_numbers: List[str] = None) -> Dict[str, Any]:
    """
    Get current inventory status for specified parts or all parts in system.
    
    Args:
        part_numbers: List of specific parts to check (optional, defaults to all parts)
        
    Returns:
        Dict with comprehensive inventory status including stock levels and locations
    """
    return await _inventory_agent.get_inventory_status(part_numbers)

@tool
async def predict_demand_with_ai(part_number: str, days_ahead: int = 7) -> Dict[str, Any]:
    """
    Use AI to predict future demand patterns for inventory planning.
    
    Args:
        part_number: Part to analyze for demand forecasting
        days_ahead: Number of days to predict ahead (default: 7)
        
    Returns:
        Dict with AI-powered demand predictions and recommendations
    """
    return await _inventory_agent.predict_demand_with_ai(part_number, days_ahead)

@tool
async def get_ai_inventory_recommendations() -> Dict[str, Any]:
    """
    Get AI-powered recommendations for inventory optimization and management.
    
    Returns:
        Dict with LLM-generated inventory optimization recommendations and strategies
    """
    return await _inventory_agent.get_ai_inventory_recommendations()

def create_inventory_agent(use_local_model: bool = False, hooks=None) -> Agent:
    """
    Factory function to create Strands Agent with InventoryAgent tools.
    
    Args:
        use_local_model: If True, uses a local Ollama model instead of AWS Bedrock
    
    Returns:
        Strands Agent configured with inventory management tools
    """
    system_prompt = """You are an AI-powered Inventory Manager for a manufacturing facility's supply chain operations.

Your responsibilities include:
- Monitoring and managing stock levels for manufacturing parts and components
- Checking availability and processing inventory reservations
- Analyzing demand patterns and predicting future inventory needs
- Providing cost optimization and reorder recommendations
- Managing warehouse locations and supplier relationships

You have access to advanced inventory management tools that use AI/LLM capabilities for:
- Intelligent availability checking with priority-based allocation
- AI-powered demand forecasting and trend analysis
- Smart inventory reservation and optimization
- Predictive reorder point calculations
- Cost analysis and supplier performance insights

Key inventory capabilities:
- Manage diverse parts catalog including hydraulic components, standard parts, and specialized equipment
- Handle multi-location inventory across Central Warehouse, Warehouse A, and Warehouse B
- Process reservations with flexible duration and automatic expiration
- Provide real-time stock level monitoring and alerts
- Generate AI-driven recommendations for inventory optimization

Inventory data includes:
- HYDRAULIC-PUMP-HP450: High-value hydraulic components for CNC machinery
- PART-ABC123, PART-XYZ789, PART-DEF456: Standard manufacturing parts
- Historical demand patterns for accurate forecasting
- Supplier information and lead time management

Be precise, cost-conscious, and always optimize for both availability and efficiency.
Prioritize preventing stockouts while minimizing carrying costs."""

    # Configure model based on preference
    agent_kwargs = {
        "system_prompt": system_prompt,
        "tools": [
            check_availability,
            reserve_inventory,
            get_inventory_status,
            predict_demand_with_ai,
            get_ai_inventory_recommendations
        ]
    }
    
    # Add hooks if provided
    if hooks:
        agent_kwargs["hooks"] = hooks
        logger.info("🪝 Adding observability hooks to inventory agent")
    
    if use_local_model:
        # Use direct OllamaModel for proper tool execution
        try:
            from strands.models.ollama import OllamaModel
            agent_kwargs["model"] = OllamaModel(
                host="http://localhost:11434",
                model_id="qwen2.5:7b",
                keep_alive=300
            )

        except ImportError:
            logger.warning("⚠️  OllamaModel not available, using default model")

    return Agent(**agent_kwargs)

if __name__ == "__main__":
    # Test the inventory agent
    import asyncio
    
    async def main():
        # Create agent
        agent = create_inventory_agent(use_local_model=True)
        
        # Test availability check
        result = await check_availability("HYDRAULIC-PUMP-HP450", 15, "HIGH")
        print(f"Availability check result: {result}")
    
    asyncio.run(main())
