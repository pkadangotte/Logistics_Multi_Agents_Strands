#!/usr/bin/env python3
"""
AI-Powered Inventory Agent - Part of Manufacturing Replenishment System
======================================================================

This intelligent agent manages inventory operations including:
- AI-driven stock level monitoring and predictions
- Intelligent availability checking with demand forecasting
- Smart reservation management
- Cost optimization analysis
- Lead time estimation with AI insights
- Inventory optimization recommendations
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# LLM Integration for AI capabilities (using Ollama)
try:
    import requests
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Requests not installed. Run: pip install requests")

# Placeholder for Strands imports (will work when properly installed)
try:
    from strands_agents import Agent, tool
except ImportError:
    # Fallback for development/testing
    class Agent:
        def __init__(self, name: str):
            self.name = name
    
    def tool(func):
        """Decorator placeholder"""
        return func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InventoryAgent(Agent):
    """
    AI-Powered Inventory Agent that manages stock operations with intelligent decision-making.
    Uses LLM for demand forecasting, reorder optimization, and inventory strategy decisions.
    """
    
    def __init__(self, name: str = "InventoryAgent", llm_model: str = "llama3:latest"):
        super().__init__(name=name)
        self.llm_model = llm_model
        self.llm_enabled = LLM_AVAILABLE
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Test Ollama connection
        if self.llm_enabled:
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
                    logger.warning(f"🧠 Ollama connection failed - using rule-based inventory management")
            except Exception as e:
                self.llm_enabled = False
                logger.warning(f"🧠 Ollama not available ({str(e)}) - using rule-based inventory management")
        else:
            logger.warning("🧠 Requests library not available - using rule-based inventory management")
        
        # Mock inventory database
        self.inventory_data = {
            "HYDRAULIC-PUMP-HP450": {
                "available_quantity": 24,
                "reserved_quantity": 2,
                "warehouse_location": "Central Warehouse",
                "cost_per_unit": 245.00,
                "lead_time_days": 1,
                "supplier": "HydroTech Systems",
                "last_updated": datetime.now().isoformat(),
                "description": "Heavy-duty hydraulic pump for CNC machinery",
                "category": "Hydraulic Components"
            },
            "PART-ABC123": {
                "available_quantity": 85,
                "reserved_quantity": 15,
                "warehouse_location": "Warehouse A",
                "cost_per_unit": 12.50,
                "lead_time_days": 2,
                "supplier": "Supplier Corp",
                "last_updated": datetime.now().isoformat()
            },
            "PART-XYZ789": {
                "available_quantity": 42,
                "reserved_quantity": 8,
                "warehouse_location": "Warehouse B", 
                "cost_per_unit": 18.75,
                "lead_time_days": 1,
                "supplier": "Parts Inc",
                "last_updated": datetime.now().isoformat()
            },
            "PART-DEF456": {
                "available_quantity": 120,
                "reserved_quantity": 25,
                "warehouse_location": "Warehouse A",
                "cost_per_unit": 8.25,
                "lead_time_days": 3,
                "supplier": "FastParts Ltd",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        # Historical demand data for AI analysis
        self.demand_history = {
            "HYDRAULIC-PUMP-HP450": [
                {"date": "2025-10-15", "quantity": 8, "priority": "HIGH", "machine": "CNC-007"},
                {"date": "2025-10-28", "quantity": 4, "priority": "MEDIUM", "machine": "CNC-003"},
                {"date": "2025-11-01", "quantity": 12, "priority": "HIGH", "machine": "CNC-007"},
                {"date": "2025-11-03", "quantity": 6, "priority": "URGENT", "machine": "CNC-005"},
                {"date": "2025-11-05", "quantity": 10, "priority": "HIGH", "machine": "CNC-007"}
            ],
            "PART-ABC123": [
                {"date": "2025-11-01", "quantity": 45, "priority": "HIGH"},
                {"date": "2025-11-02", "quantity": 30, "priority": "MEDIUM"},
                {"date": "2025-11-03", "quantity": 55, "priority": "URGENT"},
                {"date": "2025-11-04", "quantity": 20, "priority": "LOW"},
                {"date": "2025-11-05", "quantity": 40, "priority": "HIGH"}
            ],
            "PART-XYZ789": [
                {"date": "2025-11-01", "quantity": 15, "priority": "MEDIUM"},
                {"date": "2025-11-02", "quantity": 25, "priority": "HIGH"},
                {"date": "2025-11-03", "quantity": 10, "priority": "LOW"},
                {"date": "2025-11-04", "quantity": 35, "priority": "URGENT"},
                {"date": "2025-11-05", "quantity": 20, "priority": "MEDIUM"}
            ]
        }
        
        logger.info(f"🧠 AI InventoryAgent initialized with {len(self.inventory_data)} parts and demand history")

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
                timeout=60
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

    @tool
    async def check_availability(
        self, 
        part_number: str, 
        quantity_needed: int,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Check if requested quantity is available in inventory.
        
        Args:
            part_number: Part number to check
            quantity_needed: Required quantity
            priority: Request priority (affects reservation logic)
            
        Returns:
            Dict with availability status and details
        """
        logger.info(f"📦 Checking availability for {part_number} (qty: {quantity_needed})")
        
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

    @tool
    async def reserve_inventory(
        self,
        part_number: str,
        quantity: int,
        request_id: str,
        duration_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Reserve inventory for a specific request.
        
        Args:
            part_number: Part to reserve
            quantity: Quantity to reserve
            request_id: Associated request ID
            duration_hours: Reservation duration
            
        Returns:
            Dict with reservation details
        """
        logger.info(f"🔒 Reserving {quantity} of {part_number} for {request_id}")
        
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

    @tool
    async def get_inventory_status(self, part_numbers: List[str] = None) -> Dict[str, Any]:
        """
        Get current inventory status for specified parts or all parts.
        
        Args:
            part_numbers: List of specific parts to check (optional)
            
        Returns:
            Dict with inventory status
        """
        logger.info(f"📊 Getting inventory status")
        
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

    @tool
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

    @tool
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

def create_inventory_agent() -> InventoryAgent:
    """Factory function to create AI-powered InventoryAgent with Ollama"""
    return InventoryAgent(name="AI_InventoryAgent", llm_model="llama3:latest")

if __name__ == "__main__":
    # Test the AI-powered inventory agent
    async def test_ai_inventory_agent():
        agent = create_inventory_agent()
        
        print("🧠 Testing AI-Powered Inventory Agent")
        print("=" * 50)
        
        # Test AI-enhanced availability check
        print("\n📦 Testing AI availability check...")
        result = await agent.check_availability("PART-ABC123", 50, "HIGH")
        print(f"Availability: {result.get('available', False)}")
        print(f"AI Recommendation: {result.get('ai_recommendation', 'N/A')[:100]}...")
        
        # Test reservation with AI insights
        if result.get("available"):
            reservation = await agent.reserve_inventory("PART-ABC123", 25, "TEST-REQ-001")
            print(f"\n🔒 Reservation: {reservation.get('reserved', False)}")
        
        # Test AI demand prediction
        print("\n🔮 Testing AI demand prediction...")
        demand_forecast = await agent.predict_demand_with_ai("PART-ABC123", 5)
        if demand_forecast.get("success"):
            print(f"Demand Forecast: {demand_forecast['ai_demand_forecast'][:150]}...")
        
        # Test AI inventory optimization
        print("\n🧠 Testing AI inventory recommendations...")
        ai_recommendations = await agent.get_ai_inventory_recommendations()
        if ai_recommendations.get("success"):
            print(f"AI Analysis: {ai_recommendations['ai_recommendations'][:200]}...")
        
        # Test status with AI insights
        print("\n📊 Testing inventory status...")
        status = await agent.get_inventory_status()
        print(f"Total parts: {status.get('parts_count', 0)}")
    
    asyncio.run(test_ai_inventory_agent())
