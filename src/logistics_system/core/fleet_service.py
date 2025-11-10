#!/usr/bin/env python3
"""
Fleet Service - Core Business Logic
==================================

Extracted business logic from FleetAgent for better separation of concerns.
This service handles all fleet operations independent of the Strands framework.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

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
from config.config_loader import get_fleet_config, get_system_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AGVStatus:
    """AGV status data structure"""
    agv_id: str
    current_location: str
    battery_level: int
    status: str  # "available", "busy", "charging", "maintenance"
    current_task: Optional[str] = None
    estimated_completion: Optional[str] = None


class FleetService:
    """
    Core fleet business logic service.
    
    This class contains all the business logic for fleet operations,
    separated from Strands framework concerns. Can be used independently
    or wrapped by FleetAgent.
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
        
        # Test LLM connection
        if self.llm_enabled and llm_backend == 'ollama':
            try:
                test_response = requests.post(
                    self.ollama_url,
                    json={"model": self.llm_model, "prompt": "Hello", "stream": False},
                    timeout=15
                )
                if test_response.status_code == 200:
                    logger.info(f"🚛 Ollama connected successfully for fleet AI with model: {self.llm_model}")
                else:
                    self.llm_enabled = False
                    logger.warning(f"🚛 Ollama connection failed - using rule-based fleet management")
            except Exception as e:
                self.llm_enabled = False
                logger.warning(f"🚛 Ollama not available ({str(e)}) - using rule-based fleet management")
        else:
            logger.warning("🚛 Requests library not available - using rule-based fleet management")
        
        # Load fleet configuration
        self._load_fleet_configuration()

    def _load_fleet_configuration(self):
        """Load fleet data from configuration files"""
        try:
            fleet_config = get_fleet_config()
            system_config = get_system_config()
            
            # Load AGV fleet data from agv_fleet (dictionary with agv_id as keys)
            self.agv_fleet = {}
            agv_fleet_data = fleet_config.get('agv_fleet', {})
            
            for agv_id, agv_data in agv_fleet_data.items():
                self.agv_fleet[agv_id] = {
                    "agv_id": agv_id,
                    "type": agv_data.get('type', 'Standard AGV'),
                    "capacity_kg": agv_data.get('capacity_pieces', 100),  # Note: config uses 'capacity_pieces'
                    "battery_level": agv_data.get('battery_level', 100),
                    "current_location": agv_data.get('current_location', 'Dock-01'),
                    "status": agv_data.get('status', 'AVAILABLE').lower(),
                    "max_speed_mps": agv_data.get('max_speed_mps', 2.0),
                    "charging_time_minutes": agv_data.get('charging_time_minutes', 60),
                    "maintenance_due": agv_data.get('maintenance_due', False),
                    "cost_per_trip": agv_data.get('cost_per_trip', 5.0),
                    "current_task": None,
                    "estimated_completion": None,
                    "last_updated": datetime.now().isoformat()
                }
            
            # Load delivery routes and warehouse locations
            self.warehouse_locations = fleet_config.get('warehouse_locations', [])
            self.delivery_routes = fleet_config.get('delivery_routes', {})
            
            # Load system parameters
            self.system_params = {
                "base_cost_per_km": system_config.get('base_cost_per_km', 0.50),
                "rush_delivery_multiplier": system_config.get('rush_delivery_multiplier', 1.5),
                "battery_threshold_low": system_config.get('battery_threshold_low', 20),
                "max_delivery_distance_km": system_config.get('max_delivery_distance_km', 50)
            }
            
            logger.info(f"🚛 Loaded fleet config: {len(self.agv_fleet)} AGVs, {len(self.warehouse_locations)} locations")
            
        except Exception as e:
            logger.error(f"❌ Failed to load fleet configuration: {e}")
            # Fallback to minimal default data
            self.agv_fleet = {
                "AGV-001": {
                    "agv_id": "AGV-001",
                    "type": "Heavy Duty AGV",
                    "capacity_kg": 500,
                    "battery_level": 85,
                    "current_location": "Warehouse-Central",
                    "status": "available",
                    "max_speed_mps": 2.5,
                    "charging_time_minutes": 45,
                    "maintenance_due": False,
                    "current_task": None,
                    "estimated_completion": None,
                    "last_updated": datetime.now().isoformat()
                }
            }
            self.warehouse_locations = ["Warehouse-Central", "Production-Line-A", "Shipping-Dock"]
            self.delivery_routes = {}
            self.system_params = {
                "base_cost_per_km": 0.50,
                "rush_delivery_multiplier": 1.5,
                "battery_threshold_low": 20,
                "max_delivery_distance_km": 50
            }
        
        logger.info(f"🚛 FleetService initialized with {len(self.agv_fleet)} AGVs")

    async def llm_fleet_decision(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Use Ollama LLM for intelligent fleet management decisions.
        
        Args:
            prompt: Decision prompt for the LLM
            context: Additional fleet context data
            
        Returns:
            LLM response for fleet decision-making
        """
        if not self.llm_enabled:
            return "LLM not available - using rule-based fleet logic"
        
        try:
            # Prepare context for LLM
            context_str = ""
            if context:
                context_str = f"\nFleet Context: {json.dumps(context, indent=2)}"
            
            full_prompt = f"""You are an AI Fleet Manager for a manufacturing facility.
Make intelligent fleet management decisions based on the following:

{prompt}{context_str}

Provide clear recommendations with reasoning, cost analysis, and timing considerations. Be specific and actionable."""
            
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
                return f"Ollama API error - using rule-based fleet logic"
            
        except Exception as e:
            logger.error(f"❌ Fleet LLM decision failed: {str(e)}")
            return f"LLM error: {str(e)} - using rule-based fleet logic"

    async def schedule_delivery(
        self,
        pickup_location: str,
        delivery_location: str,
        priority: str = "MEDIUM",
        weight_kg: float = 0,
        special_requirements: str = None
    ) -> Dict[str, Any]:
        """
        Schedule a delivery using optimal AGV assignment with AI reasoning.
        
        Args:
            pickup_location: Source location
            delivery_location: Destination location
            priority: Delivery priority (LOW, MEDIUM, HIGH, URGENT)
            weight_kg: Package weight in kg
            special_requirements: Any special handling requirements
            
        Returns:
            Dict with delivery assignment details and AI insights
        """
        logger.info(f"🚛 Scheduling delivery: {pickup_location} → {delivery_location} (Priority: {priority})")
        
        try:
            await asyncio.sleep(0.2)  # Simulate processing time
            
            # Find optimal AGV using AI
            agv_selection = await self.find_optimal_agv_with_ai(
                pickup_location, delivery_location, priority, weight_kg
            )
            
            if not agv_selection.get("success"):
                return {
                    "success": False,
                    "error": agv_selection.get("error", "No suitable AGV found"),
                    "alternatives": self._get_alternative_delivery_options(pickup_location, delivery_location)
                }
            
            selected_agv = agv_selection["selected_agv"]
            agv_id = selected_agv["agv_id"]
            
            # Calculate delivery details
            delivery_time = await self._estimate_delivery_time(
                agv_id, pickup_location, delivery_location, priority
            )
            
            delivery_cost = await self.calculate_delivery_cost(
                pickup_location, delivery_location, weight_kg, priority
            )
            
            # Create delivery ID and assign task
            delivery_id = f"DEL-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{agv_id}"
            
            # Update AGV status
            self.agv_fleet[agv_id].update({
                "status": "assigned",
                "current_task": delivery_id,
                "estimated_completion": (datetime.now() + timedelta(minutes=delivery_time["total_minutes"])).isoformat(),
                "last_updated": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "delivery_id": delivery_id,
                "assigned_agv": selected_agv,
                "pickup_location": pickup_location,
                "delivery_location": delivery_location,
                "priority": priority,
                "weight_kg": weight_kg,
                "special_requirements": special_requirements,
                "estimated_delivery_time": delivery_time,
                "delivery_cost": delivery_cost,
                "ai_reasoning": agv_selection.get("ai_reasoning", "Rule-based selection"),
                "scheduled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Delivery scheduling failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def find_optimal_agv_with_ai(
        self,
        pickup_location: str,
        delivery_location: str,
        priority: str,
        weight_kg: float
    ) -> Dict[str, Any]:
        """Find the optimal AGV for a delivery using AI analysis"""
        try:
            # Get available AGVs
            available_agvs = [
                agv for agv in self.agv_fleet.values()
                if agv["status"] == "available" and agv["capacity_kg"] >= weight_kg
            ]
            
            if not available_agvs:
                return {
                    "success": False,
                    "error": "No available AGVs with sufficient capacity"
                }
            
            # Prepare context for AI decision
            agv_context = {
                "available_agvs": [
                    {
                        "agv_id": agv["agv_id"],
                        "type": agv["type"],
                        "capacity_kg": agv["capacity_kg"],
                        "battery_level": agv["battery_level"],
                        "current_location": agv["current_location"],
                        "max_speed_mps": agv["max_speed_mps"]
                    }
                    for agv in available_agvs
                ],
                "delivery_details": {
                    "pickup": pickup_location,
                    "delivery": delivery_location,
                    "priority": priority,
                    "weight_kg": weight_kg
                }
            }
            
            ai_prompt = f"""
Select the optimal AGV for this delivery:
- Pickup: {pickup_location}
- Delivery: {delivery_location}
- Priority: {priority}
- Weight: {weight_kg}kg

Consider:
1. Battery level and charging needs
2. Current location vs pickup distance
3. AGV capacity and type suitability
4. Priority level requirements
5. Overall efficiency and cost

Recommend the best AGV ID with reasoning.
"""
            
            ai_recommendation = await self.llm_fleet_decision(ai_prompt, agv_context)
            
            # Rule-based fallback selection (closest AGV with best battery)
            best_agv = max(available_agvs, key=lambda x: (x["battery_level"], -abs(hash(x["current_location"]) % 100)))
            
            return {
                "success": True,
                "selected_agv": best_agv,
                "ai_reasoning": ai_recommendation,
                "available_options": len(available_agvs)
            }
            
        except Exception as e:
            logger.error(f"❌ AGV selection failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _estimate_delivery_time(
        self,
        agv_id: str,
        pickup_location: str,
        delivery_location: str,
        priority: str
    ) -> Dict[str, Any]:
        """Estimate delivery time with AI-enhanced calculations"""
        try:
            agv = self.agv_fleet.get(agv_id)
            if not agv:
                return {"total_minutes": 60, "breakdown": {}, "confidence": "low"}
            
            # Base calculations (simplified - would use actual route data)
            pickup_distance = 2.0  # km (simplified)
            delivery_distance = 5.0  # km (simplified)
            loading_time = 5  # minutes
            
            # Calculate travel time based on AGV speed
            agv_speed = agv["max_speed_mps"] * 0.8  # 80% efficiency
            travel_time_minutes = ((pickup_distance + delivery_distance) / (agv_speed * 0.06))  # Convert to minutes
            
            # Priority adjustments
            priority_multiplier = {
                "URGENT": 0.7,  # Faster processing
                "HIGH": 0.8,
                "MEDIUM": 1.0,
                "LOW": 1.2
            }.get(priority, 1.0)
            
            total_time = (travel_time_minutes + loading_time) * priority_multiplier
            
            return {
                "total_minutes": int(total_time),
                "breakdown": {
                    "pickup_travel": int(pickup_distance / (agv_speed * 0.06)),
                    "loading_time": loading_time,
                    "delivery_travel": int(delivery_distance / (agv_speed * 0.06)),
                    "priority_adjustment": f"{priority_multiplier}x"
                },
                "confidence": "medium",
                "estimated_completion": (datetime.now() + timedelta(minutes=total_time)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Delivery time estimation failed: {str(e)}")
            return {"total_minutes": 60, "error": str(e)}

    async def calculate_delivery_cost(
        self,
        pickup_location: str,
        delivery_location: str,
        weight_kg: float,
        priority: str
    ) -> Dict[str, Any]:
        """Calculate delivery cost with AI-optimized pricing"""
        try:
            await asyncio.sleep(0.1)
            
            # Base cost calculations
            distance_km = 7.0  # Simplified distance calculation
            base_cost = distance_km * self.system_params["base_cost_per_km"]
            
            # Weight-based cost (linear scaling)
            weight_cost = weight_kg * 0.02  # $0.02 per kg
            
            # Priority multiplier
            priority_multiplier = {
                "URGENT": self.system_params["rush_delivery_multiplier"],
                "HIGH": 1.3,
                "MEDIUM": 1.0,
                "LOW": 0.8
            }.get(priority, 1.0)
            
            total_cost = (base_cost + weight_cost) * priority_multiplier
            
            return {
                "total_cost": round(total_cost, 2),
                "breakdown": {
                    "base_distance_cost": round(base_cost, 2),
                    "weight_cost": round(weight_cost, 2),
                    "priority_multiplier": priority_multiplier,
                    "distance_km": distance_km
                },
                "currency": "USD"
            }
            
        except Exception as e:
            logger.error(f"❌ Cost calculation failed: {str(e)}")
            return {
                "total_cost": 10.0,
                "error": str(e)
            }

    async def get_fleet_availability(self) -> Dict[str, Any]:
        """Get current fleet availability status"""
        try:
            await asyncio.sleep(0.1)
            
            total_agvs = len(self.agv_fleet)
            available_agvs = [agv for agv in self.agv_fleet.values() if agv["status"] == "available"]
            busy_agvs = [agv for agv in self.agv_fleet.values() if agv["status"] in ["assigned", "busy"]]
            charging_agvs = [agv for agv in self.agv_fleet.values() if agv["status"] == "charging"]
            maintenance_agvs = [agv for agv in self.agv_fleet.values() if agv["maintenance_due"]]
            
            # Calculate capacity metrics
            total_capacity = sum(agv["capacity_kg"] for agv in self.agv_fleet.values())
            available_capacity = sum(agv["capacity_kg"] for agv in available_agvs)
            
            return {
                "success": True,
                "fleet_summary": {
                    "total_agvs": total_agvs,
                    "available": len(available_agvs),
                    "busy": len(busy_agvs),
                    "charging": len(charging_agvs),
                    "maintenance": len(maintenance_agvs)
                },
                "capacity_summary": {
                    "total_capacity_kg": total_capacity,
                    "available_capacity_kg": available_capacity,
                    "utilization_percent": round((1 - len(available_agvs) / total_agvs) * 100, 1) if total_agvs > 0 else 0
                },
                "agv_details": {
                    "available": [
                        {
                            "agv_id": agv["agv_id"],
                            "type": agv["type"],
                            "capacity_kg": agv["capacity_kg"],
                            "battery_level": agv["battery_level"],
                            "location": agv["current_location"]
                        }
                        for agv in available_agvs
                    ],
                    "busy": [
                        {
                            "agv_id": agv["agv_id"],
                            "current_task": agv["current_task"],
                            "estimated_completion": agv["estimated_completion"],
                            "location": agv["current_location"]
                        }
                        for agv in busy_agvs
                    ]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Fleet availability check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_delivery_status(self, delivery_id: str) -> Dict[str, Any]:
        """Get status of a specific delivery"""
        try:
            await asyncio.sleep(0.1)
            
            # Find AGV assigned to this delivery
            assigned_agv = None
            for agv in self.agv_fleet.values():
                if agv.get("current_task") == delivery_id:
                    assigned_agv = agv
                    break
            
            if not assigned_agv:
                return {
                    "success": False,
                    "delivery_id": delivery_id,
                    "error": "Delivery not found or not assigned to any AGV"
                }
            
            # Simulate delivery progress
            progress_percent = min(90, hash(delivery_id) % 100)  # Simulate progress
            
            status_mapping = {
                (0, 25): "pickup_in_progress",
                (25, 50): "pickup_complete",
                (50, 75): "in_transit",
                (75, 100): "delivery_in_progress"
            }
            
            current_status = "scheduled"
            for (min_progress, max_progress), status in status_mapping.items():
                if min_progress <= progress_percent < max_progress:
                    current_status = status
                    break
            
            return {
                "success": True,
                "delivery_id": delivery_id,
                "status": current_status,
                "progress_percent": progress_percent,
                "assigned_agv": {
                    "agv_id": assigned_agv["agv_id"],
                    "type": assigned_agv["type"],
                    "current_location": assigned_agv["current_location"],
                    "battery_level": assigned_agv["battery_level"]
                },
                "estimated_completion": assigned_agv.get("estimated_completion"),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Delivery status check failed: {str(e)}")
            return {
                "success": False,
                "delivery_id": delivery_id,
                "error": str(e)
            }

    def _get_alternative_delivery_options(self, pickup: str, delivery: str) -> List[Dict[str, Any]]:
        """Get alternative delivery options when optimal scheduling fails"""
        alternatives = []
        
        # Alternative 1: Delayed delivery
        alternatives.append({
            "option": "delayed_delivery",
            "description": "Schedule for next available AGV slot",
            "estimated_delay_minutes": 30,
            "cost_impact": "none"
        })
        
        # Alternative 2: Manual transport
        alternatives.append({
            "option": "manual_transport",
            "description": "Use manual transport for urgent delivery",
            "estimated_time_minutes": 45,
            "cost_impact": "+50%"
        })
        
        return alternatives


# Global service instance
_fleet_service = None

def get_fleet_service() -> FleetService:
    """Get or create global fleet service instance"""
    global _fleet_service
    if _fleet_service is None:
        _fleet_service = FleetService()
    return _fleet_service