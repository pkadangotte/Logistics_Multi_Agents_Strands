#!/usr/bin/env python3
"""
AI-Powered Fleet Agent - Part of Manufacturing Replenishment System
=================================================================

This intelligent agent manages AGV fleet and delivery operations including:
- AI-driven AGV scheduling and assignment
- Route optimization with LLM reasoning
- Delivery time estimation using historical data
- Cost calculation and optimization
- Battery and charging management
- Intelligent decision-making for fleet operations
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# LLM Integration for AI capabilities (using Ollama)
try:
    import requests
    import json
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Requests not installed. Run: pip install requests")

# Placeholder for Strands imports
try:
    from strands_agents import Agent, tool
except ImportError:
    class Agent:
        def __init__(self, name: str):
            self.name = name
    
    def tool(func):
        return func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FleetAgent(Agent):
    """
    AI-Powered Fleet Agent that manages AGV operations with intelligent decision-making.
    Uses LLM for route optimization, priority management, and operational decisions.
    """
    
    def __init__(self, name: str = "FleetAgent", llm_model: str = "llama3.2"):
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
                    logger.info(f"🤖 Ollama connected successfully with model: {self.llm_model}")
                else:
                    self.llm_enabled = False
                    logger.warning(f"🤖 Ollama connection failed - using rule-based decisions")
            except Exception as e:
                self.llm_enabled = False
                logger.warning(f"🤖 Ollama not available ({str(e)}) - using rule-based decisions")
        else:
            logger.warning("🤖 Requests library not available - using rule-based decisions")
        
        # Mock AGV fleet data with piece-based capacity
        self.vehicles = {
            "AGV-001": {
                "type": "heavy_duty_agv",
                "capacity_pieces": 100,  # Can carry 100 pieces/parts
                "current_location": "Warehouse A",
                "status": "AVAILABLE",
                "battery_level": 85,
                "cost_per_trip": 5.00,
                "max_speed_mps": 1.5,
                "charging_status": "not_charging",
                "last_updated": datetime.now().isoformat()
            },
            "AGV-002": {
                "type": "standard_agv",
                "capacity_pieces": 50,  # Can carry 50 pieces/parts
                "current_location": "Warehouse B",
                "status": "AVAILABLE", 
                "battery_level": 92,
                "cost_per_trip": 3.50,
                "max_speed_mps": 1.2,
                "charging_status": "not_charging",
                "last_updated": datetime.now().isoformat()
            },
            "AGV-003": {
                "type": "heavy_duty_agv",
                "capacity_pieces": 100,  # Can carry 100 pieces/parts
                "current_location": "Production Floor",
                "status": "AVAILABLE",  # Demo mode: Always available
                "battery_level": 87,  # Demo mode: Good battery level
                "cost_per_trip": 5.00,
                "max_speed_mps": 1.5,
                "charging_status": "not_charging",
                "last_updated": datetime.now().isoformat()
            },
            "AGV-004": {
                "type": "light_duty_agv",
                "capacity_pieces": 25,  # Can carry 25 pieces/parts
                "current_location": "Loading Dock", 
                "status": "AVAILABLE",  # Demo mode: Always available
                "battery_level": 82,  # Demo mode: Good battery level
                "cost_per_trip": 2.50,
                "max_speed_mps": 1.0,
                "charging_status": "not_charging",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        # AGV route database (factory floor distances in meters)
        self.routes = {
            ("Warehouse A", "Production Floor"): {"distance_m": 150, "time_minutes": 4},
            ("Warehouse B", "Production Floor"): {"distance_m": 220, "time_minutes": 6},
            ("Warehouse A", "Loading Dock"): {"distance_m": 80, "time_minutes": 2},
            ("Warehouse B", "Loading Dock"): {"distance_m": 180, "time_minutes": 5},
            ("Production Floor", "Warehouse A"): {"distance_m": 150, "time_minutes": 4},
            ("Production Floor", "Warehouse B"): {"distance_m": 220, "time_minutes": 6},
            ("Loading Dock", "Warehouse A"): {"distance_m": 80, "time_minutes": 2},
            ("Loading Dock", "Production Floor"): {"distance_m": 200, "time_minutes": 5},
            # Routes for our test scenario
            ("Central Warehouse", "Manufacturing Cell 3 - CNC Machine #7"): {"distance_m": 180, "time_minutes": 5},
            ("Warehouse A", "Manufacturing Cell 3 - CNC Machine #7"): {"distance_m": 160, "time_minutes": 4.5},
            ("Warehouse B", "Manufacturing Cell 3 - CNC Machine #7"): {"distance_m": 240, "time_minutes": 6.5}
        }
        
        logger.info(f"🤖 AGV FleetAgent initialized with {len(self.vehicles)} AGVs")

    async def llm_decision(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Use Ollama LLM for intelligent decision-making in fleet operations.
        
        Args:
            prompt: Decision prompt for the LLM
            context: Additional context data
            
        Returns:
            LLM response for decision-making
        """
        if not self.llm_enabled:
            return "LLM not available - using fallback logic"
        
        try:
            # Prepare context for LLM
            context_str = ""
            if context:
                context_str = f"\nContext: {json.dumps(context, indent=2)}"
            
            full_prompt = f"""You are an AI Fleet Manager for AGV operations in a manufacturing facility.
Make intelligent decisions based on the following:

{prompt}{context_str}

Provide a clear, actionable decision with reasoning. Be concise and specific."""
            
            # Make request to Ollama
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.llm_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
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
                return f"Ollama API error - using fallback logic"
            
        except Exception as e:
            logger.error(f"❌ LLM decision failed: {str(e)}")
            return f"LLM error: {str(e)} - using fallback logic"

    def ensure_demo_agv_availability(self) -> None:
        """Ensure AGVs are available for demo purposes"""
        available_count = len([
            agv for agv in self.vehicles.values() 
            if agv["status"] == "AVAILABLE" and agv["battery_level"] > 30
        ])
        
        if available_count < 2:  # Ensure at least 2 AGVs available
            # Reset existing AGVs to available status
            reset_count = 0
            for agv_id, agv_data in self.vehicles.items():
                if reset_count >= 2:
                    break
                self.vehicles[agv_id]["status"] = "AVAILABLE"
                self.vehicles[agv_id]["battery_level"] = max(85, agv_data["battery_level"])
                reset_count += 1
            
            logger.info(f"🎯 Demo Mode: Ensured {reset_count} AGVs are available for demonstrations")

    async def analyze_fleet_optimization(self) -> Dict[str, Any]:
        """
        Use LLM to analyze fleet performance and suggest optimizations.
        
        Returns:
            Dict with optimization recommendations
        """
        try:
            # Gather fleet data for analysis
            fleet_context = {
                "total_agvs": len(self.vehicles),
                "available_agvs": len([v for v in self.vehicles.values() if v["status"] == "AVAILABLE"]),
                "charging_agvs": len([v for v in self.vehicles.values() if v["status"] == "CHARGING"]),
                "battery_levels": {agv_id: data["battery_level"] for agv_id, data in self.vehicles.items()},
                "capacity_utilization": {agv_id: data["capacity_pieces"] for agv_id, data in self.vehicles.items()}
            }
            
            optimization_prompt = """
Analyze the current AGV fleet status and provide optimization recommendations.
Consider:
1. Battery management strategies
2. Capacity utilization efficiency
3. Charging schedule optimization
4. Fleet deployment patterns
5. Potential bottlenecks

Provide specific, actionable recommendations.
"""
            
            llm_analysis = await self.llm_decision(optimization_prompt, fleet_context)
            
            return {
                "success": True,
                "analysis": llm_analysis,
                "fleet_metrics": fleet_context,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Fleet optimization analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @tool
    async def schedule_delivery(
        self,
        part_number: str,
        quantity: int,
        source_location: str,
        destination: str,
        priority: str = "MEDIUM",
        request_id: str = None
    ) -> Dict[str, Any]:
        """
        Schedule an AGV delivery for replenishment request.
        
        Args:
            part_number: Part to be delivered
            quantity: Quantity to deliver
            source_location: Pickup location
            destination: Delivery destination
            priority: Delivery priority
            request_id: Associated request ID
            
        Returns:
            Dict with AGV delivery scheduling results
        """
        logger.info(f"🤖 Scheduling AGV delivery for {part_number} ({quantity} units)")
        
        # Ensure AGV availability for demos
        self.ensure_demo_agv_availability()
        
        try:
            await asyncio.sleep(0.3)  # Simulate processing time
            
            # Use LLM for intelligent AGV selection if available
            selection_context = {
                "part_number": part_number,
                "quantity": quantity,
                "source": source_location,
                "destination": destination,
                "priority": priority,
                "available_agvs": {
                    agv_id: {
                        "capacity_pieces": data["capacity_pieces"],
                        "battery_level": data["battery_level"],
                        "location": data["current_location"],
                        "status": data["status"]
                    } for agv_id, data in self.vehicles.items() 
                    if data["status"] == "AVAILABLE" and data["battery_level"] > 30
                }
            }
            
            # Get LLM recommendation for AGV selection
            llm_prompt = f"""
Given a delivery request for {quantity} pieces of {part_number} from {source_location} to {destination} with {priority} priority,
which AGV should be selected? Consider:
1. Capacity (pieces): AGV must handle {quantity} pieces
2. Battery level (minimum 30% for safety)
3. Current location (closer is better)
4. AGV type suitability for the task

Recommend the best AGV ID and explain reasoning briefly.
"""
            
            llm_recommendation = await self.llm_decision(llm_prompt, selection_context)
            
            # Find available AGV (with LLM guidance)
            available_agv = await self.find_optimal_agv_with_ai(
                source_location, destination, quantity, priority, llm_recommendation
            )
            
            if not available_agv:
                return {
                    "scheduled": False,
                    "error": "No available AGVs with sufficient capacity",
                    "estimated_wait_time": "15 minutes",
                    "alternative_options": self.get_alternative_delivery_options(),
                    "llm_advice": llm_recommendation
                }
            
            # Calculate route and timing
            route_key = (source_location, destination)
            route_info = self.routes.get(route_key, {"distance_m": 250, "time_minutes": 8})
            
            # Calculate AGV delivery details
            agv_data = self.vehicles[available_agv]
            travel_time = route_info["time_minutes"]
            loading_time = max(2, quantity // 10)  # 1 min per 10 pieces, min 2 min (piece-based loading)
            total_time = travel_time + loading_time
            
            delivery_cost = agv_data["cost_per_trip"]  # AGVs charge per trip, not distance
            estimated_delivery = datetime.now() + timedelta(minutes=total_time)
            
            # Update AGV status
            self.vehicles[available_agv]["status"] = "ASSIGNED"
            self.vehicles[available_agv]["current_assignment"] = request_id
            
            delivery_plan = {
                "scheduled": True,
                "delivery_id": f"AGV-DEL-{request_id or 'DIRECT'}-{int(datetime.now().timestamp())}",
                "agv_id": available_agv,
                "agv_type": agv_data["type"],
                "battery_level": agv_data["battery_level"],
                "max_speed_mps": agv_data["max_speed_mps"],
                "source_location": source_location,
                "destination": destination,
                "estimated_pickup_time": (datetime.now() + timedelta(minutes=1)).isoformat(),
                "estimated_delivery_time": estimated_delivery.isoformat(),
                "total_duration_minutes": total_time,
                "distance_m": route_info["distance_m"],
                "delivery_cost": round(delivery_cost, 2),
                "part_number": part_number,
                "quantity": quantity,
                "priority": priority,
                "scheduled_at": datetime.now().isoformat()
            }
            
            logger.info(f"🤖 AGV delivery scheduled: {delivery_plan['delivery_id']} (ETA: {total_time} min)")
            return delivery_plan
            
        except Exception as e:
            logger.error(f"❌ Delivery scheduling failed: {str(e)}")
            return {
                "scheduled": False,
                "error": str(e)
            }

    @tool
    async def get_delivery_status(self, delivery_id: str) -> Dict[str, Any]:
        """
        Get status of an existing delivery.
        
        Args:
            delivery_id: Delivery ID to check
            
        Returns:
            Dict with delivery status
        """
        logger.info(f"📍 Checking delivery status: {delivery_id}")
        
        try:
            await asyncio.sleep(0.1)
            
            # Simulate delivery tracking (in real implementation, would check actual delivery system)
            status_options = ["SCHEDULED", "IN_TRANSIT", "DELIVERED", "DELAYED"]
            
            # Simple simulation based on delivery_id timestamp
            delivery_time = int(delivery_id.split('-')[-1]) if '-' in delivery_id else int(datetime.now().timestamp())
            current_time = int(datetime.now().timestamp())
            elapsed_minutes = (current_time - delivery_time) / 60
            
            if elapsed_minutes < 5:
                status = "SCHEDULED"
                location = "Preparing for pickup"
            elif elapsed_minutes < 30:
                status = "IN_TRANSIT"
                location = "En route to destination"
            elif elapsed_minutes < 60:
                status = "DELIVERED"
                location = "Delivered successfully"
            else:
                status = "DELIVERED"
                location = "Delivery completed"
            
            return {
                "success": True,
                "delivery_id": delivery_id,
                "status": status,
                "current_location": location,
                "estimated_completion": (datetime.now() + timedelta(minutes=max(0, 30 - elapsed_minutes))).isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Status check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @tool
    async def get_fleet_availability(self) -> Dict[str, Any]:
        """
        Get current AGV fleet availability and status.
        
        Returns:
            Dict with AGV fleet status information
        """
        logger.info(f"🤖 Checking AGV fleet availability")
        
        try:
            await asyncio.sleep(0.1)
            
            fleet_status = {
                "timestamp": datetime.now().isoformat(),
                "total_agvs": len(self.vehicles),
                "available_agvs": 0,
                "in_transit_agvs": 0,
                "charging_agvs": 0,
                "maintenance_agvs": 0,
                "agvs": {}
            }
            
            for agv_id, agv_data in self.vehicles.items():
                status = agv_data["status"]
                
                if status == "AVAILABLE":
                    fleet_status["available_agvs"] += 1
                elif status in ["IN_TRANSIT", "ASSIGNED"]:
                    fleet_status["in_transit_agvs"] += 1
                elif status == "CHARGING":
                    fleet_status["charging_agvs"] += 1
                elif status == "MAINTENANCE":
                    fleet_status["maintenance_agvs"] += 1
                
                fleet_status["agvs"][agv_id] = {
                    "type": agv_data["type"],
                    "status": status,
                    "location": agv_data["current_location"],
                    "battery_level": agv_data["battery_level"],
                    "capacity_pieces": agv_data["capacity_pieces"],
                    "charging_status": agv_data["charging_status"]
                }
            
            return {
                "success": True,
                "fleet_status": fleet_status
            }
            
        except Exception as e:
            logger.error(f"❌ Fleet status check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @tool
    async def calculate_delivery_cost(
        self,
        source_location: str,
        destination: str,
        quantity: int,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Calculate delivery cost for a route and quantity.
        
        Args:
            source_location: Pickup location
            destination: Delivery destination
            quantity: Quantity to deliver
            priority: Delivery priority
            
        Returns:
            Dict with cost breakdown
        """
        logger.info(f"💰 Calculating delivery cost: {source_location} → {destination}")
        
        try:
            await asyncio.sleep(0.1)
            
            # Get route information
            route_key = (source_location, destination)
            route_info = self.routes.get(route_key, {"distance_m": 250, "time_minutes": 8})
            
            # AGV-based costs (fixed per trip, not distance-based)
            base_agv_cost = 15.0  # Base cost per AGV trip
            handling_cost = max(5, quantity * 0.1)  # Lower handling for automated system
            battery_cost = 2.0  # Energy cost per trip
            
            # Priority multiplier
            priority_multiplier = {
                "LOW": 0.8,
                "MEDIUM": 1.0,
                "HIGH": 1.2,
                "URGENT": 1.5
            }.get(priority, 1.0)
            
            # Calculate total
            subtotal = base_agv_cost + handling_cost + battery_cost
            priority_adjustment = subtotal * (priority_multiplier - 1.0)
            total_cost = subtotal + priority_adjustment
            
            cost_breakdown = {
                "success": True,
                "route": f"{source_location} → {destination}",
                "distance_m": route_info["distance_m"],
                "estimated_time_minutes": route_info["time_minutes"],
                "quantity": quantity,
                "priority": priority,
                "cost_breakdown": {
                    "agv_trip_cost": round(base_agv_cost, 2),
                    "handling_cost": round(handling_cost, 2),
                    "energy_cost": round(battery_cost, 2),
                    "priority_adjustment": round(priority_adjustment, 2),
                    "total_cost": round(total_cost, 2)
                },
                "calculated_at": datetime.now().isoformat()
            }
            
            return cost_breakdown
            
        except Exception as e:
            logger.error(f"❌ Cost calculation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @tool
    async def get_ai_fleet_recommendations(self) -> Dict[str, Any]:
        """
        Get AI-powered recommendations for fleet optimization and operations.
        
        Returns:
            Dict with LLM-generated fleet optimization recommendations
        """
        logger.info(f"🧠 Getting AI fleet recommendations")
        
        try:
            optimization_analysis = await self.analyze_fleet_optimization()
            
            return {
                "success": True,
                "ai_recommendations": optimization_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI recommendations failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def find_optimal_agv_with_ai(
        self, 
        source: str, 
        destination: str, 
        quantity: int, 
        priority: str,
        llm_recommendation: str
    ) -> Optional[str]:
        """Find the best available AGV using AI recommendation and fallback logic"""
        
        available_agvs = [
            agv_id for agv_id, data in self.vehicles.items() 
            if data["status"] == "AVAILABLE" and data["battery_level"] > 30
        ]
        
        # DEMO MODE: Ensure unlimited AGVs for smooth demonstrations
        if not available_agvs:
            # Create a virtual AGV for demo purposes
            virtual_agv_id = f"AGV-DEMO-{len(self.vehicles) + 1:03d}"
            self.vehicles[virtual_agv_id] = {
                "type": "demo_agv",
                "capacity_pieces": 150,  # High capacity for any demo request
                "current_location": source,  # Convenient location
                "status": "AVAILABLE",
                "battery_level": 95,  # Full battery
                "cost_per_trip": 4.00,
                "max_speed_mps": 1.3,
                "charging_status": "not_charging",
                "last_updated": datetime.now().isoformat()
            }
            available_agvs = [virtual_agv_id]
            logger.info(f"🎯 Demo Mode: Created virtual AGV {virtual_agv_id} for unlimited availability")
        
        # Also ensure existing AGVs are available for demo if needed
        if len(available_agvs) < 2:  # Keep at least 2 AGVs available for demos
            for agv_id, agv_data in self.vehicles.items():
                if agv_data["status"] != "AVAILABLE" and len(available_agvs) < 3:
                    # Reset AGV to available status for demo
                    self.vehicles[agv_id]["status"] = "AVAILABLE"
                    self.vehicles[agv_id]["battery_level"] = max(85, agv_data["battery_level"])
                    available_agvs.append(agv_id)
                    logger.info(f"🎯 Demo Mode: Reset {agv_id} to AVAILABLE status")
        
        # Try to extract AGV recommendation from LLM response
        recommended_agv = None
        for agv_id in available_agvs:
            if agv_id in llm_recommendation:
                # Verify the recommended AGV can handle the quantity
                if self.vehicles[agv_id]["capacity_pieces"] >= quantity:
                    recommended_agv = agv_id
                    logger.info(f"🤖 Using LLM recommendation: {agv_id}")
                    break
        
        if recommended_agv:
            return recommended_agv
        
        # Fallback to rule-based selection
        return self.find_optimal_agv(source, destination, quantity, priority)

    def find_optimal_agv(
        self, 
        source: str, 
        destination: str, 
        quantity: int, 
        priority: str
    ) -> Optional[str]:
        """Find the best available AGV for the delivery (fallback method)"""
        
        available_agvs = [
            agv_id for agv_id, data in self.vehicles.items() 
            if data["status"] == "AVAILABLE" and data["battery_level"] > 30
        ]
        
        # DEMO MODE: Ensure unlimited AGVs (fallback version)
        if not available_agvs:
            # Create a virtual AGV for demo purposes
            virtual_agv_id = f"AGV-FALLBACK-{len(self.vehicles) + 1:03d}"
            self.vehicles[virtual_agv_id] = {
                "type": "demo_fallback_agv",
                "capacity_pieces": 200,  # Very high capacity
                "current_location": source,
                "status": "AVAILABLE", 
                "battery_level": 90,
                "cost_per_trip": 3.75,
                "max_speed_mps": 1.4,
                "charging_status": "not_charging",
                "last_updated": datetime.now().isoformat()
            }
            available_agvs = [virtual_agv_id]
            logger.info(f"🎯 Demo Mode (Fallback): Created virtual AGV {virtual_agv_id}")
        
        # Reset busy AGVs if needed for demo continuity
        if len(available_agvs) < 2:
            for agv_id, agv_data in list(self.vehicles.items())[:2]:  # Reset first 2 AGVs
                if agv_data["status"] != "AVAILABLE":
                    self.vehicles[agv_id]["status"] = "AVAILABLE"
                    self.vehicles[agv_id]["battery_level"] = 88
                    if agv_id not in available_agvs:
                        available_agvs.append(agv_id)
        
        # AGV selection logic - prefer AGVs with sufficient piece capacity and closer location
        suitable_agvs = []
        
        for agv_id in available_agvs:
            agv = self.vehicles[agv_id]
            
            # Check capacity based on pieces (not kg)
            if agv["capacity_pieces"] >= quantity:
                # Calculate priority score based on location, battery, and capacity
                location_score = 10 if agv["current_location"] == source else 0
                battery_score = agv["battery_level"] / 10  # Higher battery is better
                capacity_score = agv["capacity_pieces"] / 50  # Higher capacity is better
                
                total_score = location_score + battery_score + capacity_score
                suitable_agvs.append((agv_id, total_score))
        
        if suitable_agvs:
            # Return AGV with highest score
            suitable_agvs.sort(key=lambda x: x[1], reverse=True)
            return suitable_agvs[0][0]
        
        # If no perfectly suitable AGV, return first available
        return available_agvs[0] if available_agvs else None

    def get_alternative_delivery_options(self) -> List[Dict[str, Any]]:
        """Get alternative delivery options when no AGVs are available"""
        return [
            {
                "option": "manual_cart_delivery",
                "cost_multiplier": 0.5,
                "time_increase": "200%",
                "description": "Manual push cart delivery by operator"
            },
            {
                "option": "wait_for_agv_charging",
                "delay_minutes": 15,
                "cost_same": True, 
                "description": "Wait for AGV to complete charging cycle"
            },
            {
                "option": "priority_agv_recall",
                "cost_multiplier": 1.5,
                "time_reduction": "30%",
                "description": "Recall AGV from lower priority task"
            },
            {
                "option": "manual_pickup",
                "cost_reduction": "100%",
                "description": "Manual pickup from warehouse by production staff"
            }
        ]

    async def run_agv_monitoring(self):
        """Main AGV fleet monitoring loop"""
        logger.info(f"🤖 Starting AGV FleetAgent monitoring loop")
        
        while True:
            try:
                # Monitor AGV status
                for agv_id, agv_data in self.vehicles.items():
                    status = agv_data["status"]
                    
                    if status == "IN_TRANSIT":
                        # Check if AGV should be returning to available
                        if "estimated_return" in agv_data:
                            return_time = datetime.fromisoformat(agv_data["estimated_return"])
                            if datetime.now() >= return_time:
                                agv_data["status"] = "AVAILABLE"
                                logger.info(f"🤖 AGV {agv_id} returned to service")
                    
                    elif status == "CHARGING":
                        # Check if AGV charging is complete
                        if agv_data["battery_level"] >= 95:
                            agv_data["status"] = "AVAILABLE"
                            agv_data["charging_status"] = "not_charging"
                            logger.info(f"🔋 AGV {agv_id} charging complete, back in service")
                
                # Wait before next check
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                logger.info(f"🛑 AGV monitoring stopped")
                break
            except Exception as e:
                logger.error(f"❌ AGV monitoring error: {str(e)}")
                await asyncio.sleep(60)

def create_fleet_agent() -> FleetAgent:
    """Factory function to create AI-powered FleetAgent with Ollama"""
    return FleetAgent(name="AI_FleetAgent", llm_model="llama3:latest")

if __name__ == "__main__":
    # Test the AI-powered AGV fleet agent
    async def test_ai_agv_fleet_agent():
        agent = create_fleet_agent()
        
        print("🤖 Testing AI-Powered AGV Fleet Agent")
        print("=" * 50)
        
        # Test AGV delivery scheduling with AI
        print("\n📦 Testing AGV delivery scheduling...")
        delivery = await agent.schedule_delivery(
            "PART-ABC123", 25, "Warehouse A", "Production Floor", "HIGH", "TEST-REQ-001"
        )
        print(f"AGV delivery result: {delivery}")
        
        # Test AGV cost calculation
        print("\n💰 Testing cost calculation...")
        cost = await agent.calculate_delivery_cost(
            "Warehouse A", "Production Floor", 25, "HIGH"
        )
        print(f"Cost breakdown: {cost}")
        
        # Test AGV fleet availability with piece capacity
        print("\n📊 Testing fleet availability...")
        availability = await agent.get_fleet_availability()
        print(f"Fleet status: {availability}")
        
        # Test AI recommendations
        print("\n🧠 Testing AI fleet recommendations...")
        ai_recommendations = await agent.get_ai_fleet_recommendations()
        print(f"AI recommendations: {ai_recommendations}")
    
    asyncio.run(test_ai_agv_fleet_agent())
