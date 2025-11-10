#!/usr/bin/env python3
"""
AI-Powered Fleet Agent - Strands Framework Wrapper
================================================

REFACTORED VERSION - Clean separation of concerns.

This is a thin wrapper around FleetService that handles:
- Strands framework integration
- Tool registration with @tool decorators  
- Service initialization and delegation
- Backward compatibility interfaces

The actual business logic is in FleetService.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Strands Agent imports
from strands import Agent, tool

# Import the service layer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.logistics_system.core.fleet_service import FleetService, get_fleet_service
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    print(f"Warning: FleetService not available - {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FleetAgent:
    """
    Strands Framework Wrapper for FleetService.
    
    This class is a thin wrapper that delegates all business logic to FleetService
    while handling Strands framework concerns like tool registration and agent creation.
    
    Architecture:
    - FleetAgent: Strands integration (this class - minimal code)
    - FleetService: Business logic (separate service - core functionality)
    """
    
    def __init__(self, llm_model: str = None):
        self.llm_model = llm_model or os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
        
        if SERVICE_AVAILABLE:
            # Use the service layer for all business logic
            self.service = get_fleet_service()
            logger.info("✅ FleetAgent using FleetService architecture")
            
            # Expose service properties for backward compatibility
            self.agv_fleet = getattr(self.service, 'agv_fleet', {})
            self.warehouse_locations = getattr(self.service, 'warehouse_locations', [])
            self.llm_enabled = getattr(self.service, 'llm_enabled', False)
        else:
            # Graceful degradation if service unavailable
            logger.error("❌ FleetService not available - agent will not function properly")
            self.service = None
            self.agv_fleet = {}
            self.warehouse_locations = []
            self.llm_enabled = False
        
        logger.info(f"🚛 FleetAgent initialized - Service: {SERVICE_AVAILABLE}, AGVs: {len(self.agv_fleet)}")

    # =============================================================================
    # DELEGATION METHODS - All business logic delegated to FleetService
    # =============================================================================

    async def schedule_delivery(
        self,
        pickup_location: str,
        delivery_location: str,
        priority: str = "MEDIUM",
        weight_kg: float = 0,
        special_requirements: str = None
    ) -> Dict[str, Any]:
        """
        Schedule delivery - delegates to FleetService.
        """
        if not self.service:
            return {
                "success": False,
                "error": "FleetService not available"
            }
        
        return await self.service.schedule_delivery(
            pickup_location, delivery_location, priority, weight_kg, special_requirements
        )

    async def get_delivery_status(self, delivery_id: str) -> Dict[str, Any]:
        """
        Get delivery status - delegates to FleetService.
        """
        if not self.service:
            return {
                "success": False,
                "delivery_id": delivery_id,
                "error": "FleetService not available"
            }
        
        return await self.service.get_delivery_status(delivery_id)

    async def get_fleet_availability(self) -> Dict[str, Any]:
        """
        Get fleet availability - delegates to FleetService.
        """
        if not self.service:
            return {
                "success": False,
                "error": "FleetService not available",
                "fleet_summary": {"total_agvs": 0, "available": 0}
            }
        
        return await self.service.get_fleet_availability()

    async def calculate_delivery_cost(
        self,
        pickup_location: str,
        delivery_location: str,
        weight_kg: float,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Calculate delivery cost - delegates to FleetService.
        """
        if not self.service:
            return {
                "total_cost": 0.0,
                "error": "FleetService not available"
            }
        
        return await self.service.calculate_delivery_cost(
            pickup_location, delivery_location, weight_kg, priority
        )

    async def find_optimal_agv_with_ai(
        self,
        pickup_location: str,
        delivery_location: str,
        priority: str,
        weight_kg: float
    ) -> Dict[str, Any]:
        """
        Find optimal AGV - uses FleetService AI capabilities.
        """
        if not self.service:
            return {
                "success": False,
                "error": "FleetService not available"
            }
        
        return await self.service.find_optimal_agv_with_ai(
            pickup_location, delivery_location, priority, weight_kg
        )

    async def get_ai_fleet_recommendations(self) -> Dict[str, Any]:
        """
        Get AI fleet recommendations - uses FleetService capabilities.
        """
        if not self.service:
            return {
                "success": False,
                "error": "FleetService not available"
            }
        
        try:
            # Get current fleet status for AI analysis
            fleet_status = await self.service.get_fleet_availability()
            
            if not fleet_status.get("success"):
                return fleet_status
            
            recommendations_context = {
                "fleet_summary": fleet_status["fleet_summary"],
                "capacity_summary": fleet_status["capacity_summary"],
                "agv_details": fleet_status["agv_details"]
            }
            
            recommendations_prompt = f"""
Analyze current fleet status and provide optimization recommendations:

Fleet Status:
- Total AGVs: {fleet_status['fleet_summary']['total_agvs']}
- Available: {fleet_status['fleet_summary']['available']}
- Busy: {fleet_status['fleet_summary']['busy']}  
- Charging: {fleet_status['fleet_summary']['charging']}
- Utilization: {fleet_status['capacity_summary']['utilization_percent']}%

Provide recommendations for:
1. Fleet optimization opportunities
2. Battery and charging management
3. Maintenance scheduling priorities
4. Route efficiency improvements
5. Cost reduction strategies

Be specific and actionable.
"""
            
            ai_recommendations = await self.service.llm_fleet_decision(
                recommendations_prompt,
                recommendations_context
            )
            
            return {
                "success": True,
                "ai_recommendations": ai_recommendations,
                "fleet_context": recommendations_context,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI fleet recommendations failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def analyze_fleet_optimization(self) -> Dict[str, Any]:
        """
        Analyze fleet optimization opportunities - uses FleetService data.
        """
        if not self.service:
            return {
                "success": False,
                "error": "FleetService not available"
            }
        
        try:
            # Get fleet availability for analysis
            fleet_data = await self.service.get_fleet_availability()
            
            if not fleet_data.get("success"):
                return fleet_data
            
            analysis_context = {
                "utilization": fleet_data["capacity_summary"]["utilization_percent"],
                "available_agvs": len(fleet_data["agv_details"]["available"]),
                "busy_agvs": len(fleet_data["agv_details"]["busy"]),
                "total_capacity": fleet_data["capacity_summary"]["total_capacity_kg"]
            }
            
            optimization_prompt = f"""
Analyze fleet optimization opportunities:

Current Metrics:
- Utilization: {analysis_context['utilization']}%
- Available AGVs: {analysis_context['available_agvs']}
- Busy AGVs: {analysis_context['busy_agvs']}
- Total Capacity: {analysis_context['total_capacity']}kg

Identify:
1. Efficiency bottlenecks
2. Capacity optimization opportunities
3. Battery management improvements
4. Route optimization potential
5. Cost saving recommendations

Provide actionable insights with priority levels.
"""
            
            ai_analysis = await self.service.llm_fleet_decision(
                optimization_prompt,
                analysis_context
            )
            
            return {
                "success": True,
                "optimization_analysis": ai_analysis,
                "current_metrics": analysis_context,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Fleet optimization analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def run_agv_monitoring(self):
        """
        Background AGV monitoring - delegates to FleetService.
        This method provides compatibility with existing monitoring systems.
        """
        if not self.service:
            logger.warning("⚠️ AGV monitoring skipped - FleetService not available")
            return
        
        try:
            logger.info("🔍 Starting AGV monitoring loop...")
            
            while True:
                # Get current fleet status
                status = await self.service.get_fleet_availability()
                
                if status.get("success"):
                    # Check for low battery AGVs
                    low_battery_agvs = [
                        agv for agv in self.service.agv_fleet.values()
                        if agv["battery_level"] < self.service.system_params["battery_threshold_low"]
                    ]
                    
                    if low_battery_agvs:
                        logger.warning(f"⚠️ {len(low_battery_agvs)} AGVs have low battery")
                    
                    # Check for maintenance due
                    maintenance_due = [
                        agv for agv in self.service.agv_fleet.values()
                        if agv.get("maintenance_due", False)
                    ]
                    
                    if maintenance_due:
                        logger.warning(f"🔧 {len(maintenance_due)} AGVs need maintenance")
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except asyncio.CancelledError:
            logger.info("🔍 AGV monitoring stopped")
        except Exception as e:
            logger.error(f"❌ AGV monitoring error: {e}")


# =============================================================================
# GLOBAL AGENT INSTANCE - Used by Strands tools
# =============================================================================

# Global FleetAgent instance for tools to use
_fleet_agent = FleetAgent(llm_model="qwen2.5:7b")


# =============================================================================
# STRANDS TOOL FUNCTIONS - @tool decorated functions for Strands framework
# =============================================================================

@tool
async def schedule_delivery(
    pickup_location: str,
    delivery_location: str,
    priority: str = "MEDIUM",
    weight_kg: float = 0,
    special_requirements: str = None
) -> Dict[str, Any]:
    """
    Schedule AGV delivery with AI-powered optimization and route planning.
    
    Args:
        pickup_location: Source location for pickup
        delivery_location: Destination location for delivery
        priority: Delivery priority (LOW, MEDIUM, HIGH, URGENT)
        weight_kg: Package weight in kilograms
        special_requirements: Any special handling requirements
        
    Returns:
        Dict with delivery assignment, timing, costs, and AI reasoning
    """
    return await _fleet_agent.schedule_delivery(
        pickup_location, delivery_location, priority, weight_kg, special_requirements
    )


@tool
async def get_delivery_status(delivery_id: str) -> Dict[str, Any]:
    """
    Get current status and progress of a scheduled delivery.
    
    Args:
        delivery_id: Unique delivery identifier returned from schedule_delivery
        
    Returns:
        Dict with delivery progress, AGV status, and timing information
    """
    return await _fleet_agent.get_delivery_status(delivery_id)


@tool
async def get_fleet_availability() -> Dict[str, Any]:
    """
    Get comprehensive fleet availability and capacity status.
    
    Returns:
        Dict with AGV availability, capacity metrics, and utilization data
    """
    return await _fleet_agent.get_fleet_availability()


@tool
async def calculate_delivery_cost(
    pickup_location: str,
    delivery_location: str,
    weight_kg: float,
    priority: str = "MEDIUM"
) -> Dict[str, Any]:
    """
    Calculate estimated cost for delivery with priority and weight factors.
    
    Args:
        pickup_location: Source location
        delivery_location: Destination location  
        weight_kg: Package weight in kilograms
        priority: Delivery priority affecting cost multiplier
        
    Returns:
        Dict with cost breakdown and pricing factors
    """
    return await _fleet_agent.calculate_delivery_cost(
        pickup_location, delivery_location, weight_kg, priority
    )


@tool
async def get_ai_fleet_recommendations() -> Dict[str, Any]:
    """
    Get AI-powered recommendations for fleet optimization and management.
    
    Returns:
        Dict with LLM-generated fleet optimization strategies and insights
    """
    return await _fleet_agent.get_ai_fleet_recommendations()


# =============================================================================
# STRANDS AGENT FACTORY FUNCTION
# =============================================================================

def create_fleet_agent(use_local_model: bool = False, hooks=None) -> Agent:
    """
    Factory function to create Strands Agent with FleetAgent tools.
    
    Args:
        use_local_model: If True, uses local Ollama model instead of AWS Bedrock
        hooks: Optional observability hooks for monitoring
    
    Returns:
        Strands Agent configured with fleet management tools
    """
    system_prompt = """You are an AI-powered Fleet Manager for a manufacturing facility's AGV (Automated Guided Vehicle) operations.

Your responsibilities include:
- Scheduling and optimizing AGV deliveries across the facility
- Managing fleet availability and capacity allocation
- Calculating delivery costs and time estimates
- Monitoring AGV battery levels and maintenance needs
- Providing AI-driven route optimization and efficiency recommendations

You have access to advanced fleet management tools that use AI/LLM capabilities for:
- Intelligent AGV assignment based on location, capacity, and battery status
- AI-powered route optimization and delivery scheduling
- Smart cost calculation with priority-based pricing
- Predictive maintenance and battery management
- Fleet utilization analysis and optimization recommendations

Fleet capabilities:
- Manage diverse AGV types: Heavy Duty AGVs (500kg), Standard AGVs (100kg), Specialized units
- Handle multi-location operations: Central Warehouse, Production Lines, Shipping Docks
- Process deliveries with flexible priority levels and special requirements
- Provide real-time delivery tracking and status updates
- Generate AI-driven fleet optimization and efficiency insights

Current fleet includes:
- AGV-001: Heavy Duty AGV (500kg capacity, 85% battery, available)
- Multiple warehouse locations and optimized delivery routes
- Advanced battery management and charging coordination
- Predictive maintenance scheduling based on usage patterns

Be efficient, cost-conscious, and always optimize for both delivery speed and operational efficiency.
Prioritize urgent deliveries while maintaining overall fleet productivity."""

    # Configure agent with tools
    agent_kwargs = {
        "system_prompt": system_prompt,
        "tools": [
            schedule_delivery,
            get_delivery_status,
            get_fleet_availability,
            calculate_delivery_cost,
            get_ai_fleet_recommendations
        ]
    }
    
    # Add observability hooks if provided
    if hooks:
        agent_kwargs["hooks"] = hooks
        logger.info("🪝 Adding observability hooks to fleet agent")
    
    # Configure model based on preference
    if use_local_model:
        try:
            from strands.models.ollama import OllamaModel
            agent_kwargs["model"] = OllamaModel(
                host="http://localhost:11434",
                model_id="qwen2.5:7b",
                keep_alive=300
            )
            logger.info("🤖 Using local Ollama model for fleet agent")
        except ImportError:
            logger.warning("⚠️ OllamaModel not available, using default model")

    return Agent(**agent_kwargs)


# =============================================================================
# MAIN EXECUTION - For testing
# =============================================================================

if __name__ == "__main__":
    # Test the fleet agent
    async def main():
        # Create agent
        agent = create_fleet_agent(use_local_model=True)
        
        # Test delivery scheduling
        result = await schedule_delivery(
            "Central-Warehouse", 
            "Production-Line-A", 
            "HIGH", 
            150.0, 
            "Handle with care"
        )
        print(f"Delivery scheduling result: {result}")
    
    asyncio.run(main())