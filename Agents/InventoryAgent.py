#!/usr/bin/env python3
"""
AI-Powered Inventory Agent - Strands Framework Wrapper
=====================================================

REFACTORED VERSION - Clean separation of concerns.

This is a thin wrapper around InventoryService that handles:
- Strands framework integration
- Tool registration with @tool decorators  
- Service initialization and delegation
- Backward compatibility interfaces

The actual business logic is in InventoryService.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

# Strands Agent imports
from strands import Agent, tool

# Import the service layer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.logistics_system.core.inventory_service import InventoryService, get_inventory_service
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    print(f"Warning: InventoryService not available - {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InventoryAgent:
    """
    Strands Framework Wrapper for InventoryService.
    
    This class is a thin wrapper that delegates all business logic to InventoryService
    while handling Strands framework concerns like tool registration and agent creation.
    
    Architecture:
    - InventoryAgent: Strands integration (this class - minimal code)
    - InventoryService: Business logic (separate service - core functionality)
    """
    
    def __init__(self, llm_model: str = None):
        self.llm_model = llm_model or os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
        
        if SERVICE_AVAILABLE:
            # Use the service layer for all business logic
            self.service = get_inventory_service()
            logger.info("✅ InventoryAgent using InventoryService architecture")
            
            # Expose service properties for backward compatibility
            self.inventory_data = getattr(self.service, 'parts_inventory', {})
            self.demand_history = getattr(self.service, 'demand_history', {})
            self.llm_enabled = getattr(self.service, 'llm_enabled', False)
        else:
            # Graceful degradation if service unavailable
            logger.error("❌ InventoryService not available - agent will not function properly")
            self.service = None
            self.inventory_data = {}
            self.demand_history = {}
            self.llm_enabled = False
        
        logger.info(f"🧠 InventoryAgent initialized - Service: {SERVICE_AVAILABLE}, Parts: {len(self.inventory_data)}")

    # =============================================================================
    # DELEGATION METHODS - All business logic delegated to InventoryService
    # =============================================================================

    async def check_availability(
        self, 
        part_number: str, 
        quantity_needed: int,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Check inventory availability - delegates to InventoryService.
        """
        if not self.service:
            return {
                "available": False,
                "error": "InventoryService not available",
                "part_number": part_number
            }
        
        return await self.service.check_availability(part_number, quantity_needed, priority)

    async def reserve_inventory(
        self,
        part_number: str,
        quantity: int,
        request_id: str,
        duration_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Reserve inventory - delegates to InventoryService.
        """
        if not self.service:
            return {
                "reserved": False,
                "error": "InventoryService not available"
            }
        
        return await self.service.reserve_inventory(
            part_number, 
            quantity, 
            request_id, 
            f"Request: {request_id} (Duration: {duration_hours}h)"
        )

    async def get_inventory_status(self, part_numbers: List[str] = None) -> Dict[str, Any]:
        """
        Get inventory status - delegates to InventoryService.
        """
        if not self.service:
            return {
                "success": False,
                "error": "InventoryService not available",
                "total_parts": 0
            }
        
        return await self.service.get_inventory_status(part_numbers)

    async def analyze_demand_patterns(self, part_number: str) -> Dict[str, Any]:
        """
        Analyze demand patterns - uses InventoryService LLM capabilities.
        """
        if not self.service:
            return {
                "success": False,
                "error": "InventoryService not available"
            }
        
        # Use service LLM for demand analysis
        try:
            demand_data = self.service.demand_history.get(part_number, [])
            part_info = self.service.get_inventory_info(part_number)
            
            if not part_info:
                return {
                    "success": False,
                    "error": f"Part {part_number} not found"
                }
            
            analysis_context = {
                "part_number": part_number,
                "current_stock": part_info.get("current_stock", 0),
                "recent_demand": demand_data[-5:],  # Last 5 entries
                "lead_time": part_info.get("lead_time_days", 0),
                "cost_per_unit": part_info.get("cost_per_unit", 0)
            }
            
            demand_prompt = f"""
Analyze demand pattern for {part_number} and provide:
1. Predicted demand for next 3 days
2. Recommended reorder point  
3. Optimal reorder quantity
4. Risk assessment (stockout probability)
5. Cost optimization suggestions

Consider trends and patterns in historical data.
"""
            
            llm_analysis = await self.service.llm_inventory_decision(demand_prompt, analysis_context)
            
            return {
                "success": True,
                "part_number": part_number,
                "ai_analysis": llm_analysis,
                "demand_data": analysis_context,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Demand analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def predict_demand_with_ai(self, part_number: str, days_ahead: int = 7) -> Dict[str, Any]:
        """
        AI-powered demand prediction - uses InventoryService capabilities.
        """
        if not self.service:
            return {
                "success": False,
                "error": "InventoryService not available"
            }
        
        try:
            # Get demand analysis first
            demand_analysis = await self.analyze_demand_patterns(part_number)
            
            if not demand_analysis.get("success"):
                return demand_analysis
            
            prediction_context = demand_analysis["demand_data"]
            
            prediction_prompt = f"""
Based on historical demand data, predict daily demand for {part_number} over next {days_ahead} days.

Provide:
1. Daily demand predictions (quantities)
2. Confidence levels for each prediction  
3. Factors influencing demand (trends, seasonality)
4. Recommended safety stock levels
5. Optimal reorder timing

Format as specific daily predictions with reasoning.
"""
            
            llm_prediction = await self.service.llm_inventory_decision(prediction_prompt, prediction_context)
            
            return {
                "success": True,
                "part_number": part_number,
                "prediction_period_days": days_ahead,
                "ai_demand_forecast": llm_prediction,
                "historical_context": prediction_context,
                "predicted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Demand prediction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_ai_inventory_recommendations(self) -> Dict[str, Any]:
        """
        Get AI-powered inventory optimization recommendations.
        """
        if not self.service:
            return {
                "success": False,
                "error": "InventoryService not available"
            }
        
        try:
            # Get current inventory status
            status = await self.service.get_inventory_status()
            
            if not status.get("success"):
                return status
            
            recommendations_context = {
                "total_parts": status["total_parts"],
                "total_value": status["total_inventory_value"],
                "low_stock_items": status["low_stock_items"],
                "parts_summary": {
                    part_id: {
                        "stock": data["current_stock"],
                        "available": data["available_quantity"],
                        "level": data["stock_level"]
                    }
                    for part_id, data in status["parts_status"].items()
                }
            }
            
            recommendations_prompt = f"""
Analyze current inventory status and provide optimization recommendations:

Current Status:
- Total parts managed: {status['total_parts']}
- Total inventory value: ${status['total_inventory_value']:.2f}
- Low stock items: {len(status['low_stock_items'])}

Provide recommendations for:
1. Immediate reorder priorities
2. Inventory optimization strategies
3. Cost reduction opportunities  
4. Risk mitigation for low stock items
5. Overall inventory health assessment

Be specific and actionable.
"""
            
            ai_recommendations = await self.service.llm_inventory_decision(
                recommendations_prompt, 
                recommendations_context
            )
            
            return {
                "success": True,
                "ai_recommendations": ai_recommendations,
                "inventory_context": recommendations_context,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI recommendations failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# =============================================================================
# GLOBAL AGENT INSTANCE - Used by Strands tools
# =============================================================================

# Global InventoryAgent instance for tools to use
_inventory_agent = InventoryAgent(llm_model="qwen2.5:7b")


# =============================================================================
# STRANDS TOOL FUNCTIONS - @tool decorated functions for Strands framework
# =============================================================================

@tool
async def check_availability(
    part_number: str, 
    quantity_needed: int,
    priority: str = "MEDIUM"
) -> Dict[str, Any]:
    """
    Check if requested quantity is available in inventory with AI-powered analysis.
    
    Args:
        part_number: Part number to check (e.g., 'HYDRAULIC-PUMP-HP450')
        quantity_needed: Required quantity in units
        priority: Request priority (LOW, MEDIUM, HIGH, URGENT)
        
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
        request_id: Associated request ID for tracking
        duration_hours: Reservation duration in hours (default: 24)
        
    Returns:
        Dict with reservation details including reservation ID and expiration
    """
    return await _inventory_agent.reserve_inventory(part_number, quantity, request_id, duration_hours)


@tool
async def get_inventory_status(part_numbers: List[str] = None) -> Dict[str, Any]:
    """
    Get current inventory status for specified parts or all parts.
    
    Args:
        part_numbers: List of specific parts to check (optional, defaults to all)
        
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


# =============================================================================
# STRANDS AGENT FACTORY FUNCTION
# =============================================================================

def create_inventory_agent(use_local_model: bool = False, hooks=None) -> Agent:
    """
    Factory function to create Strands Agent with InventoryAgent tools.
    
    Args:
        use_local_model: If True, uses local Ollama model instead of AWS Bedrock
        hooks: Optional observability hooks for monitoring
    
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

    # Configure agent with tools
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
    
    # Add observability hooks if provided
    if hooks:
        agent_kwargs["hooks"] = hooks
        logger.info("🪝 Adding observability hooks to inventory agent")
    
    # Configure model based on preference
    if use_local_model:
        try:
            from strands.models.ollama import OllamaModel
            agent_kwargs["model"] = OllamaModel(
                host="http://localhost:11434",
                model_id="qwen2.5:7b",
                keep_alive=300
            )
            logger.info("🤖 Using local Ollama model for inventory agent")
        except ImportError:
            logger.warning("⚠️ OllamaModel not available, using default model")

    return Agent(**agent_kwargs)


# =============================================================================
# MAIN EXECUTION - For testing
# =============================================================================

if __name__ == "__main__":
    # Test the inventory agent
    async def main():
        # Create agent
        agent = create_inventory_agent(use_local_model=True)
        
        # Test availability check
        result = await check_availability("HYDRAULIC-PUMP-HP450", 15, "HIGH")
        print(f"Availability check result: {result}")
    
    asyncio.run(main())