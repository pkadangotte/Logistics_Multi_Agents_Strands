#!/usr/bin/env python3
"""
AI-Powered Logistics Orchestrator Agent using Strands Framework
============================================================

This intelligent agent orchestrates the complete manufacturing replenishment workflow 
by coordinating with multiple AI-powered specialized agents:
- AI Inventory Agent: Smart stock management with demand forecasting
- AI Fleet Agent: Intelligent AGV operations with route optimization  
- AI Approver Agent: Risk-based approval decisions with predictive analytics

The AI orchestrator manages the complete lifecycle from Lambda trigger through 
InMemory status tracking, intelligent agent coordination, and delivery completion.

Features:
- Lambda function integration for external triggers
- Real-time InMemory status management 
- AI-powered workflow orchestration and optimization
- Complete AGV-to-destination delivery coordination
- Intelligent error handling and recovery
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Removed DynamoDB dependencies

# LLM Integration for AI capabilities (using Ollama)
try:
    import requests
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Requests not installed. Run: pip install requests")

# Strands Framework imports with fallback
try:
    from strands_agents import Agent, tool
    from strands_agents.communication import send_message
    from strands_agents.models import Message, MessageType
    STRANDS_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    STRANDS_AVAILABLE = False
    class Agent:
        def __init__(self, name: str):
            self.name = name
    
    def tool(func):
        return func
    
    # Fallback Message and MessageType classes
    class MessageType:
        REQUEST = "REQUEST"
        RESPONSE = "RESPONSE"
        ERROR = "ERROR"
    
    class Message:
        def __init__(self, type: str, content: str, sender: str, recipient: str):
            self.type = type
            self.content = content
            self.sender = sender
            self.recipient = recipient
    
    async def send_message(message):
        """Fallback send_message function"""
        return {"status": "fallback", "message": "Strands framework not available"}
# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Warn about missing strands agents
if not STRANDS_AVAILABLE:
    logger.warning("Strands agents not available - using fallback mode")

class LogisticsOrchestratorAgent(Agent):
    """
    AI-Powered Logistics Orchestrator Agent that coordinates replenishment operations
    across multiple AI specialized agents, manages Lambda integration, and handles 
    complete DynamoDB workflow tracking with intelligent orchestration.
    """
    
    def __init__(self, name: str = "AI_LogisticsOrchestrator", llm_model: str = "llama3:latest"):
        super().__init__(name=name)
        self.llm_model = llm_model
        self.llm_enabled = LLM_AVAILABLE
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_base_url = "http://localhost:11434"  # For compatibility
        
        # Test Ollama connection for AI orchestration
        if self.llm_enabled:
            try:
                test_response = requests.post(
                    self.ollama_url,
                    json={"model": self.llm_model, "prompt": "Hello", "stream": False},
                    timeout=15
                )
                if test_response.status_code == 200:
                    logger.info(f"🎯 Ollama connected for AI orchestration with model: {self.llm_model}")
                else:
                    self.llm_enabled = False
                    logger.warning(f"🎯 Ollama connection failed - using rule-based orchestration")
            except Exception as e:
                self.llm_enabled = False
                logger.warning(f"🎯 Ollama not available ({str(e)}) - using rule-based orchestration")
        else:
            logger.warning("🎯 Requests library not available - using rule-based orchestration")
        
        # Configuration - using in-memory storage instead of DynamoDB
        self.max_retries = 3
        self.timeout_seconds = 30
        
        # In-memory storage for requests (replacing DynamoDB)
        self.requests_storage = {}  # Dictionary to store request data
        
        # Import AI agents for direct integration 
        try:
            from .FleetAgent import create_fleet_agent
            from .InventoryAgent import create_inventory_agent  
            from .ApproverAgent import create_approver_agent
            
            # Initialize AI agents
            self.inventory_agent = create_inventory_agent()
            self.fleet_agent = create_fleet_agent()
            self.approver_agent = create_approver_agent()
            
            logger.info(f"🤖 AI agents initialized: Inventory, Fleet, Approver")
            
        except ImportError as e:
            logger.warning(f"⚠️  AI agents not available: {e}")
            self.inventory_agent = None
            self.fleet_agent = None
            self.approver_agent = None
        
        # Status workflow definitions
        self.status_flow = {
            "RECEIVED": "Initial request received from Lambda",
            "CHECKING_INVENTORY": "Analyzing inventory availability with AI",
            "INVENTORY_CONFIRMED": "Inventory available and reserved",
            "SCHEDULING_AGV": "Coordinating AGV assignment with AI",
            "AGV_ASSIGNED": "AGV assigned and route planned", 
            "AWAITING_APPROVAL": "Pending approval review",
            "APPROVED": "Request approved, initiating execution",
            "AGV_DISPATCHED": "AGV en route to warehouse",
            "PICKING_INVENTORY": "AGV collecting inventory from warehouse",
            "IN_TRANSIT": "AGV delivering to destination",
            "DELIVERED": "Successfully delivered to destination",
            "COMPLETED": "Replenishment workflow completed",
            "REJECTED": "Request rejected during approval",
            "FAILED": "Workflow failed - requires intervention"
        }
        
        # Status workflow for compatibility  
        self.status_workflow = list(self.status_flow.keys())
        
        logger.info(f"🎯 AI LogisticsOrchestrator initialized")
        logger.info(f"� Storage: In-memory (DynamoDB removed)")
        logger.info(f"� AI Agents: {len([a for a in [self.inventory_agent, self.fleet_agent, self.approver_agent] if a])} active")
        logger.info(f"🔄 Status Flow: {len(self.status_flow)} states tracked")

    async def initialize_agents(self):
        """Initialize AI agents - compatibility method for testing."""
        # Agents are already initialized in constructor, this is for compatibility
        logger.info(f"🤖 AI agent initialization confirmed - all agents ready")
        return True

    def setup_storage(self):
        """Initialize in-memory storage (replacing DynamoDB)"""
        logger.info("� In-memory storage initialized (DynamoDB removed)")
        return True

    async def llm_orchestration_decision(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Use Ollama LLM for intelligent orchestration decisions.
        
        Args:
            prompt: Decision prompt for the LLM
            context: Additional orchestration context data
            
        Returns:
            LLM response for orchestration decision-making
        """
        if not self.llm_enabled:
            return "LLM not available - using rule-based orchestration"
        
        try:
            # Prepare context for LLM
            context_str = ""
            if context:
                context_str = f"\nOrchestration Context: {json.dumps(context, indent=2)}"
            
            full_prompt = f"""You are an AI Manufacturing Logistics Orchestrator.
Make intelligent workflow decisions based on the following:

{prompt}{context_str}

Provide clear, actionable orchestration decisions with reasoning. Be decisive and specific."""
            
            # Make request to Ollama
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.llm_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 200
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from Ollama").strip()
            else:
                logger.error(f"❌ Ollama API error: {response.status_code}")
                return f"Ollama API error - using rule-based orchestration"
            
        except Exception as e:
            logger.error(f"❌ Orchestration LLM decision failed: {str(e)}")
            return f"LLM error: {str(e)} - using rule-based orchestration"

    @tool
    async def lambda_triggered_replenishment(
        self,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point for Lambda-triggered replenishment requests.
        Orchestrates the complete workflow with AI decision-making and DynamoDB tracking.
        
        Args:
            request_data: Dictionary containing:
                - part_number: Part number required (e.g., "PART-ABC123")
                - quantity_requested: Quantity needed (e.g., 50)
                - destination: Destination location (e.g., "Machine 1 Production Floor") 
                - priority: Request priority (LOW/MEDIUM/HIGH/URGENT)
                - Additional fields like order_id, current_bin_level, etc.
            
        Returns:
            Dict with orchestration results and tracking information
        """
        # Extract data from request dictionary
        part_number = request_data.get('part_number', request_data.get('PartNumber', 'UNKNOWN'))
        quantity_required = request_data.get('quantity_requested', request_data.get('RemainingQuantityRequired', 0))
        destination = request_data.get('destination', 'Unknown Destination')
        priority = request_data.get('priority', 'MEDIUM')
        request_source = "Lambda"
        
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}-{part_number}"
        
        logger.info(f"🎯 Lambda-triggered replenishment: {request_id}")
        logger.info(f"📦 Part: {part_number}, Qty: {quantity_required}, Dest: {destination}")
        
        try:
            # Initialize request in DynamoDB with proper request_data structure
            await self.write_replenishment_request(
                request_data=request_data,
                status="RECEIVED",
                priority=priority
            )
            
            # AI Orchestration Decision
            ai_orchestration_prompt = f"""
Plan the optimal workflow for this replenishment request:
Part: {part_number}
Quantity: {quantity_required}
Destination: {destination}
Priority: {priority}

Recommend:
1. Workflow sequence optimization
2. Risk factors to monitor
3. Contingency planning
4. Expected completion time
5. Resource allocation priority

Provide structured orchestration plan.
"""
            
            logger.info(f"🤖 Generating AI orchestration plan...")
            ai_plan = await self.llm_orchestration_decision(ai_orchestration_prompt)
            
            # Execute AI workflow
            logger.info(f"🚀 Executing AI workflow for {request_id}")
            workflow_result = await self.execute_ai_workflow(
                request_data=request_data,
                request_id=request_id,
                ai_plan={"strategy": ai_plan}
            )
            
            return {
                "success": True,
                "request_id": request_id,
                "ai_orchestration_plan": ai_plan,
                "workflow_result": workflow_result,
                "started_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Lambda orchestration failed: {str(e)}")
            # Update status to failed
            await self.update_request_status(request_id, "FAILED", f"Orchestration error: {str(e)}")
            return {
                "success": False,
                "request_id": request_id,
                "error": str(e)
            }

    @tool
    async def orchestrate_replenishment_request(
        self, 
        request_data: Dict[str, Any],
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Orchestrate a complete replenishment request workflow by coordinating
        with Inventory, Fleet, and Approver agents.
        
        Args:
            request_data: Replenishment request details including order_id, part_number, quantity, etc.
            priority: Request priority (LOW, MEDIUM, HIGH, URGENT)
        
        Returns:
            Dict containing orchestration results and status
        """
        request_id = request_data.get('RequestId', f"REQ-{int(datetime.now().timestamp())}")
        
        logger.info(f"🎯 Starting replenishment orchestration for {request_id}")
        
        try:
            # Step 1: Write initial request to DynamoDB
            initial_status = await self.write_replenishment_request(
                request_data=request_data,
                status="ORCHESTRATING", 
                priority=priority
            )
            
            if not initial_status.get('success'):
                return {
                    "success": False,
                    "request_id": request_id,
                    "error": "Failed to write initial request to DynamoDB",
                    "details": initial_status
                }
            
            # Step 2: Check inventory availability
            inventory_result = await self.check_inventory_availability(request_data)
            
            # Step 3: If inventory available, coordinate with fleet
            fleet_result = None
            if inventory_result.get('available', False):
                fleet_result = await self.coordinate_fleet_delivery(request_data, inventory_result)
            
            # Step 4: Get approval for the complete plan
            approval_request = {
                "request_id": request_id,
                "request_data": request_data,
                "inventory_result": inventory_result,
                "fleet_result": fleet_result,
                "priority": priority
            }
            
            approval_result = await self.request_approval(approval_request)
            
            # Step 5: Update final status based on orchestration results
            final_status = self.determine_final_status(
                inventory_result, fleet_result, approval_result
            )
            
            # Step 6: Write final status to DynamoDB
            await self.update_request_status(
                request_id=request_id,
                status=final_status,
                orchestration_details={
                    "inventory": inventory_result,
                    "fleet": fleet_result, 
                    "approval": approval_result,
                    "completed_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"✅ Orchestration completed for {request_id} with status: {final_status}")
            
            return {
                "success": True,
                "request_id": request_id,
                "final_status": final_status,
                "orchestration_results": {
                    "inventory": inventory_result,
                    "fleet": fleet_result,
                    "approval": approval_result
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Orchestration failed for {request_id}: {str(e)}")
            
            # Update status to FAILED
            await self.update_request_status(
                request_id=request_id,
                status="FAILED",
                error_details={"error": str(e), "failed_at": datetime.now().isoformat()}
            )
            
            return {
                "success": False,
                "request_id": request_id,
                "error": str(e)
            }

    async def execute_ai_workflow(
        self, 
        request_data: Dict[str, Any], 
        request_id: str,
        ai_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the complete AI-coordinated workflow by managing all three agents
        through the full replenishment process with DynamoDB status tracking.
        
        This method coordinates:
        1. Inventory Agent - Check availability and warehouse details
        2. Fleet Agent - Schedule AGV and route optimization  
        3. Approver Agent - Risk assessment and approval
        4. Complete delivery workflow with status updates
        
        Args:
            request_data: Original request data from Lambda
            request_id: Unique identifier for tracking
            ai_plan: AI orchestration plan from LLM
            
        Returns:
            Dict containing complete workflow results
        """
        logger.info(f"🤖 Starting AI workflow execution for {request_id}")
        
        try:
            # Step 1: Update status to CHECKING_INVENTORY
            await self.update_request_status(request_id, "CHECKING_INVENTORY", 
                {"stage": "inventory_check", "started_at": datetime.now().isoformat()})
            
            # Step 1: Query Inventory Agent for availability
            inventory_request = {
                "part_number": request_data.get('part_number'),
                "quantity_needed": request_data.get('quantity_requested'),
                "destination": request_data.get('destination'),
                "priority": request_data.get('priority', 'MEDIUM'),
                "request_id": request_id
            }
            
            logger.info(f"📦 Checking inventory with AI agent for {inventory_request['part_number']}")
            inventory_result = await self.inventory_agent.check_availability(
                part_number=inventory_request['part_number'],
                quantity_needed=inventory_request['quantity_needed']
            )
            
            if not inventory_result.get('available', False):
                await self.update_request_status(request_id, "INVENTORY_UNAVAILABLE", 
                    {"inventory_result": inventory_result})
                return {
                    "success": False,
                    "stage": "inventory_check",
                    "reason": "Inventory not available",
                    "inventory_result": inventory_result
                }
            
            # Step 2: Update status to INVENTORY_CONFIRMED
            await self.update_request_status(request_id, "INVENTORY_CONFIRMED", 
                {"inventory_result": inventory_result, "stage": "agv_scheduling"})
            
            # Step 2: Coordinate with Fleet Agent for AGV scheduling
            fleet_request = {
                "part_number": request_data.get('part_number'),
                "quantity_pieces": request_data.get('quantity_requested'),
                "pickup_location": inventory_result.get('warehouse_location', 'Warehouse A'),
                "destination": request_data.get('destination'),
                "priority": request_data.get('priority', 'MEDIUM'),
                "estimated_weight": inventory_result.get('estimated_weight', 50),
                "request_id": request_id,
                "delivery_deadline": (datetime.now() + timedelta(hours=2)).isoformat()
            }
            
            logger.info(f"🚛 Scheduling AGV with AI fleet agent for delivery to {fleet_request['destination']}")
            await self.update_request_status(request_id, "SCHEDULING_AGV")
            
            fleet_result = await self.fleet_agent.schedule_delivery(
                pickup_location=fleet_request['pickup_location'],
                destination=fleet_request['destination'],
                quantity_pieces=fleet_request['quantity_pieces'],
                priority=fleet_request['priority'],
                delivery_deadline=fleet_request['delivery_deadline']
            )
            
            if not fleet_result.get('scheduled', False):
                await self.update_request_status(request_id, "AGV_UNAVAILABLE", 
                    {"fleet_result": fleet_result})
                return {
                    "success": False,
                    "stage": "agv_scheduling",
                    "reason": "No AGV available",
                    "fleet_result": fleet_result
                }
            
            # Step 3: Update status to AGV_ASSIGNED
            await self.update_request_status(request_id, "AGV_ASSIGNED", 
                {"fleet_result": fleet_result, "stage": "approval_process"})
            
            # Step 3: Get approval from Approver Agent
            approval_request = {
                "request_id": request_id,
                "part_number": request_data.get('part_number'),
                "quantity": request_data.get('quantity_requested'),
                "destination": request_data.get('destination'),
                "estimated_cost": (inventory_result.get('cost_per_unit', 0) * 
                                 request_data.get('quantity_requested', 0) + 
                                 fleet_result.get('delivery_cost', 0)),
                "priority": request_data.get('priority', 'MEDIUM'),
                "inventory_details": inventory_result,
                "fleet_details": fleet_result,
                "delivery_time": fleet_result.get('estimated_delivery_time')
            }
            
            logger.info(f"✋ Requesting approval for ${approval_request['estimated_cost']:.2f} delivery")
            await self.update_request_status(request_id, "AWAITING_APPROVAL")
            
            approval_result = await self.approver_agent.review_replenishment_plan(
                request_id=approval_request['request_id'],
                original_request=request_data,
                inventory_plan=inventory_result,
                fleet_plan=fleet_result,
                estimated_cost=approval_request['estimated_cost'],
                business_justification=f"Manufacturing replenishment for {request_data.get('destination')}",
                priority=approval_request['priority']
            )
            
            if not approval_result.get('approved', False):
                await self.update_request_status(request_id, "REJECTED", 
                    {"approval_result": approval_result})
                return {
                    "success": False,
                    "stage": "approval",
                    "reason": approval_result.get('reason', 'Request rejected'),
                    "approval_result": approval_result
                }
            
            # Step 4: Update status to APPROVED and execute delivery workflow
            await self.update_request_status(request_id, "APPROVED", 
                {"approval_result": approval_result, "stage": "delivery_execution"})
            
            # Step 4: Execute the complete delivery workflow
            logger.info(f"🚀 Executing delivery workflow - AGV {fleet_result.get('vehicle_id')} to {request_data.get('destination')}")
            
            # AGV dispatch
            await self.update_request_status(request_id, "AGV_DISPATCHED", 
                {"agv_id": fleet_result.get('vehicle_id'), "dispatch_time": datetime.now().isoformat()})
            await asyncio.sleep(1)  # Simulate AGV dispatch processing
            
            # AGV picking inventory  
            await self.update_request_status(request_id, "PICKING_INVENTORY", 
                {"warehouse": inventory_result.get('warehouse_location'), "picking_started": datetime.now().isoformat()})
            await asyncio.sleep(2)  # Simulate inventory picking
            
            # AGV in transit
            await self.update_request_status(request_id, "IN_TRANSIT", 
                {"route": f"{inventory_result.get('warehouse_location')} → {request_data.get('destination')}", 
                 "transit_started": datetime.now().isoformat(),
                 "estimated_arrival": fleet_result.get('estimated_delivery_time')})
            await asyncio.sleep(3)  # Simulate transit time
            
            # Delivery completed
            await self.update_request_status(request_id, "DELIVERED", 
                {"delivered_at": datetime.now().isoformat(), 
                 "delivered_by": fleet_result.get('vehicle_id'),
                 "delivery_confirmation": True})
            await asyncio.sleep(0.5)  # Simulate delivery confirmation
            
            # Final completion
            await self.update_request_status(request_id, "COMPLETED", 
                {"completed_at": datetime.now().isoformat(),
                 "total_cost": approval_request['estimated_cost'],
                 "delivery_success": True})
            
            logger.info(f"✅ AI workflow completed successfully for {request_id}")
            
            return {
                "success": True,
                "request_id": request_id,
                "workflow_stages": {
                    "inventory": inventory_result,
                    "fleet": fleet_result, 
                    "approval": approval_result,
                    "delivery_status": "COMPLETED"
                },
                "total_cost": approval_request['estimated_cost'],
                "completion_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI workflow execution failed for {request_id}: {str(e)}")
            await self.update_request_status(request_id, "WORKFLOW_FAILED", 
                {"error": str(e), "failed_at": datetime.now().isoformat()})
            
            return {
                "success": False,
                "request_id": request_id,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }

    @tool
    async def write_replenishment_request(
        self,
        request_data: Dict[str, Any],
        status: str = "ACTIVE",
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Write a replenishment request to in-memory storage.
        
        Args:
            request_data: Request details
            status: Initial status 
            priority: Request priority
            
        Returns:
            Dict with success status and details
        """
        try:
            request_id = request_data.get('RequestId', f"REQ-{int(datetime.now().timestamp())}")
            
            # Prepare item for in-memory storage
            item = {
                'RequestId': request_id,
                'Timestamp': datetime.now().isoformat(),
                'RequestStatus': status,
                'Priority': priority,
                'CreatedBy': 'LogisticsOrchestratorAgent',
                'OrchestratorVersion': '1.0.0',
                
                # Request details
                'OrderId': str(request_data.get('order_id', request_data.get('OrderId', 'Unknown'))),
                'PartNumber': str(request_data.get('part_number', request_data.get('PartNumber', 'Unknown'))),
                'QuantityRequested': int(request_data.get('quantity_requested', request_data.get('RemainingQuantityRequired', 0))),
                'CurrentBinLevel': int(request_data.get('current_bin_level', request_data.get('CurrentBinLevel', 0))),
                'MaxBinCapacity': int(request_data.get('max_bin_capacity', request_data.get('MaxBinCapacity', 100))),
                
                # Orchestrator metadata
                'OrchestrationStarted': datetime.now().isoformat(),
                'AgentWorkflow': 'Orchestrator -> Inventory -> Fleet -> Approver',
                'ExpectedCompletion': (datetime.now() + timedelta(hours=2)).isoformat()
            }
            
            # Add optional fields if present
            optional_fields = ['BinLevelPercent', 'RemainingQuantityRequired', 'RequestedBy', 'Location']
            for field in optional_fields:
                if field in request_data:
                    item[field] = request_data[field]
            
            # Store in memory (replacing DynamoDB)
            self.requests_storage[request_id] = item
            
            logger.info(f"📝 Written to memory storage: {request_id} (Status: {status})")
            
            return {
                "success": True,
                "request_id": request_id,
                "status": status,
                "item": item
            }
            
        except Exception as e:
            logger.error(f"❌ Write request failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @tool
    async def update_request_status(
        self,
        request_id: str,
        status: str,
        orchestration_details: Optional[Dict] = None,
        error_details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Update the status of an existing replenishment request in memory storage.
        
        Args:
            request_id: Request ID to update
            status: New status
            orchestration_details: Results from agent coordination
            error_details: Error information if status is FAILED
            
        Returns:
            Dict with update results
        """
        try:
            # Check if request exists in memory storage
            if request_id not in self.requests_storage:
                logger.warning(f"⚠️  Request {request_id} not found in storage")
                # Create new entry if not exists
                self.requests_storage[request_id] = {
                    'RequestId': request_id,
                    'Timestamp': datetime.now().isoformat(),
                    'CreatedBy': 'LogisticsOrchestratorAgent'
                }
            
            # Update the status and timestamp
            self.requests_storage[request_id]['RequestStatus'] = status
            self.requests_storage[request_id]['LastUpdated'] = datetime.now().isoformat()
            
            # Add status-specific fields
            if status == "ACCEPTED":
                self.requests_storage[request_id]['AcceptedTimestamp'] = datetime.now().isoformat()
                
            elif status == "COMPLETED":
                self.requests_storage[request_id]['CompletedTimestamp'] = datetime.now().isoformat()
                
            elif status == "FAILED":
                self.requests_storage[request_id]['FailedTimestamp'] = datetime.now().isoformat()
                
                if error_details:
                    self.requests_storage[request_id]['ErrorDetails'] = error_details
            
            # Add orchestration details if provided
            if orchestration_details:
                self.requests_storage[request_id]['OrchestrationDetails'] = orchestration_details
            
            logger.info(f"✅ Updated status: {request_id} → {status}")
            
            return {
                "success": True,
                "request_id": request_id,
                "new_status": status,
                "updated_item": self.requests_storage[request_id]
            }
            
        except Exception as e:
            logger.error(f"❌ Status update failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @tool
    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """
        Retrieve the current status and details of a replenishment request.
        
        Args:
            request_id: Request ID to query
            
        Returns:
            Dict with request details or error
        """
        try:
            response = self.table.get_item(Key={'RequestId': request_id})
            
            if 'Item' in response:
                return {
                    "success": True,
                    "request_id": request_id,
                    "item": response['Item']
                }
            else:
                return {
                    "success": False,
                    "error": f"Request {request_id} not found"
                }
                
        except Exception as e:
            logger.error(f"❌ Get status failed for {request_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def check_inventory_availability(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Communicate with Inventory Agent using Strands framework messaging.
        
        Args:
            request_data: Request details for inventory check
            
        Returns:
            Dict with inventory availability results
        """
        try:
            logger.info(f"📦 Checking inventory availability via InventoryAgent")
            
            # Prepare message for Inventory Agent
            inventory_request = {
                "action": "check_availability",
                "part_number": request_data.get('part_number', request_data.get('PartNumber')),
                "quantity_needed": request_data.get('quantity_requested', request_data.get('RemainingQuantityRequired', 0)),
                "priority": request_data.get('priority', 'MEDIUM'),
                "request_id": request_data.get('RequestId', 'Unknown')
            }
            
            if STRANDS_AVAILABLE:
                # Use Strands framework messaging
                message = Message(
                    type=MessageType.REQUEST,
                    content=json.dumps(inventory_request),
                    sender=self.name,
                    recipient="InventoryAgent"
                )
                
                response = await send_message(message)
                
                if response and response.get("status") == "success":
                    return json.loads(response.get("content", "{}"))
                else:
                    logger.warning("Strands messaging failed, falling back to direct agent call")
            
            # Fallback to direct agent call if Strands not available or failed
            if self.inventory_agent:
                part_number = inventory_request["part_number"]
                quantity_needed = inventory_request["quantity_needed"]
                priority = inventory_request["priority"]
                
                inventory_result = await self.inventory_agent.check_availability(
                    part_number=part_number,
                    quantity_needed=quantity_needed,
                    priority=priority
                )
                
                logger.info(f"📦 Inventory check completed: {inventory_result.get('available', False)}")
                return inventory_result
            else:
                raise Exception("No InventoryAgent available and Strands messaging failed")
            
        except Exception as e:
            logger.error(f"❌ Inventory check failed: {str(e)}")
            return {
                "available": False,
                "error": str(e),
                "fallback_plan": "Manual inventory verification required"
            }

    async def coordinate_fleet_delivery(
        self, 
        request_data: Dict[str, Any], 
        inventory_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate with Fleet Agent using Strands framework messaging.
        
        Args:
            request_data: Original request details
            inventory_result: Results from inventory check
            
        Returns:
            Dict with fleet coordination results
        """
        try:
            logger.info(f"🚛 Coordinating fleet delivery via FleetAgent")
            
            # Prepare fleet coordination request
            fleet_request = {
                "action": "schedule_delivery",
                "part_number": request_data.get('part_number', request_data.get('PartNumber')),
                "quantity": inventory_result.get('available_quantity', 0),
                "source_location": inventory_result.get('warehouse_location', 'Main Warehouse'),
                "destination": request_data.get('destination', 'Production Floor'),
                "priority": request_data.get('priority', 'MEDIUM'),
                "request_id": request_data.get('RequestId', 'Unknown')
            }
            
            if STRANDS_AVAILABLE:
                # Use Strands framework messaging
                message = Message(
                    type=MessageType.REQUEST,
                    content=json.dumps(fleet_request),
                    sender=self.name,
                    recipient="FleetAgent"
                )
                
                response = await send_message(message)
                
                if response and response.get("status") == "success":
                    return json.loads(response.get("content", "{}"))
                else:
                    logger.warning("Strands messaging failed, falling back to direct agent call")
            
            # Fallback to direct agent call if Strands not available or failed
            if self.fleet_agent:
                pickup_location = fleet_request["source_location"]
                destination = fleet_request["destination"]
                quantity_pieces = fleet_request["quantity"]
                priority = fleet_request["priority"]
                
                # Call fleet agent directly
                fleet_result = await self.fleet_agent.schedule_delivery(
                    part_number=request_data.get('part_number', request_data.get('PartNumber')),
                    quantity=quantity_pieces,
                    source_location=pickup_location,
                    destination=destination,
                    priority=priority,
                    request_id=request_data.get('RequestId', 'Unknown')
                )
                
                logger.info(f"🚛 Fleet coordination completed: ETA {fleet_result.get('estimated_delivery_time', 'Unknown')}")
                return fleet_result
            else:
                raise Exception("No FleetAgent available and Strands messaging failed")
            
        except Exception as e:
            logger.error(f"❌ Fleet coordination failed: {str(e)}")
            return {
                "scheduled": False,
                "error": str(e),
                "fallback_plan": "Manual delivery coordination required"
            }

    async def request_approval(self, approval_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request approval from Approver Agent using Strands framework messaging.
        
        Args:
            approval_request: Complete request with inventory and fleet results
            
        Returns:
            Dict with approval results
        """
        try:
            logger.info(f"✅ Requesting approval via ApproverAgent")
            
            # Prepare approval request
            approver_request = {
                "action": "review_replenishment_plan",
                "request_id": approval_request.get('request_id'),
                "original_request": approval_request.get('request_data'),
                "inventory_plan": approval_request.get('inventory_result'),
                "fleet_plan": approval_request.get('fleet_result'),
                "priority": approval_request.get('priority', 'MEDIUM'),
                "estimated_cost": self.calculate_estimated_cost(approval_request),
                "business_justification": self.generate_business_justification(approval_request)
            }
            
            if STRANDS_AVAILABLE:
                # Use Strands framework messaging
                message = Message(
                    type=MessageType.REQUEST,
                    content=json.dumps(approver_request),
                    sender=self.name,
                    recipient="ApproverAgent"
                )
                
                response = await send_message(message)
                
                if response and response.get("status") == "success":
                    return json.loads(response.get("content", "{}"))
                else:
                    logger.warning("Strands messaging failed, falling back to direct agent call")
            
            # Fallback to direct agent call if Strands not available or failed
            if self.approver_agent:
                request_id = approver_request["request_id"]
                original_request = approver_request["original_request"]
                inventory_plan = approver_request["inventory_plan"]
                fleet_plan = approver_request["fleet_plan"]
                estimated_cost = approver_request["estimated_cost"]
                business_justification = approver_request["business_justification"]
                priority = approver_request["priority"]
                
                approval_result = await self.approver_agent.review_replenishment_plan(
                    request_id=request_id,
                    original_request=original_request,
                    inventory_plan=inventory_plan,
                    fleet_plan=fleet_plan,
                    estimated_cost=estimated_cost,
                    business_justification=business_justification,
                    priority=priority
                )
                
                logger.info(f"✅ Approval result: {approval_result.get('approved', False)}")
                return approval_result
            else:
                raise Exception("No ApproverAgent available and Strands messaging failed")
            
        except Exception as e:
            logger.error(f"❌ Approval request failed: {str(e)}")
            return {
                "approved": False,
                "error": str(e),
                "fallback_plan": "Manual approval required"
            }

    def determine_final_status(
        self, 
        inventory_result: Dict[str, Any], 
        fleet_result: Optional[Dict[str, Any]], 
        approval_result: Dict[str, Any]
    ) -> str:
        """
        Determine the final status based on orchestration results.
        
        Returns:
            Final status string
        """
        if not inventory_result.get('available', False):
            return "PENDING_INVENTORY"
        
        if fleet_result and not fleet_result.get('scheduled', False):
            return "PENDING_DELIVERY"
            
        if not approval_result.get('approved', False):
            return "PENDING_APPROVAL"
            
        # If all steps succeeded
        if (inventory_result.get('available', False) and 
            (not fleet_result or fleet_result.get('scheduled', False)) and
            approval_result.get('approved', False)):
            return "APPROVED"
        
        return "PENDING_REVIEW"

    def calculate_estimated_cost(self, approval_request: Dict[str, Any]) -> float:
        """Calculate estimated cost for the replenishment operation."""
        # Simple cost calculation (can be made more sophisticated)
        base_cost = 100.0  # Base handling cost
        
        inventory_result = approval_request.get('inventory_result', {})
        fleet_result = approval_request.get('fleet_result', {})
        
        # Add inventory cost
        quantity = inventory_result.get('available_quantity', 0)
        cost_per_unit = inventory_result.get('cost_per_unit', 10.0)
        inventory_cost = quantity * cost_per_unit
        
        # Add delivery cost
        delivery_cost = fleet_result.get('delivery_cost', 50.0) if fleet_result else 0
        
        total_cost = base_cost + inventory_cost + delivery_cost
        return round(total_cost, 2)

    def generate_business_justification(self, approval_request: Dict[str, Any]) -> str:
        """Generate business justification for the replenishment request."""
        request_data = approval_request.get('request_data', {})
        priority = approval_request.get('priority', 'MEDIUM')
        
        part_number = request_data.get('part_number', request_data.get('PartNumber', 'Unknown'))
        current_level = request_data.get('current_bin_level', request_data.get('CurrentBinLevel', 0))
        
        justification = f"Replenishment required for {part_number} due to low inventory ({current_level} units). "
        
        if priority == "URGENT":
            justification += "URGENT: Production line stoppage imminent without immediate replenishment."
        elif priority == "HIGH":
            justification += "HIGH PRIORITY: Critical for production schedule maintenance."
        else:
            justification += "Standard replenishment to maintain operational efficiency."
            
        return justification

    # Simulation methods (replace these with actual agent communication when agents are deployed)
    
    async def simulate_inventory_response(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Inventory Agent response."""
        await asyncio.sleep(0.5)  # Simulate processing time
        
        quantity_needed = request.get('quantity_needed', 0)
        available_quantity = min(quantity_needed + 20, 100)  # Simulate availability
        
        return {
            "available": available_quantity >= quantity_needed,
            "available_quantity": available_quantity,
            "warehouse_location": "Warehouse A",
            "cost_per_unit": 12.50,
            "lead_time_minutes": 30,
            "agent_response_time": datetime.now().isoformat()
        }

    async def simulate_fleet_response(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Fleet Agent response."""
        await asyncio.sleep(0.3)  # Simulate processing time
        
        return {
            "scheduled": True,
            "vehicle_id": "TRUCK-001",
            "estimated_delivery_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "delivery_cost": 75.0,
            "driver_assigned": "Driver-123",
            "agent_response_time": datetime.now().isoformat()
        }

    async def simulate_approver_response(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Approver Agent response."""
        await asyncio.sleep(0.2)  # Simulate processing time
        
        estimated_cost = request.get('estimated_cost', 0)
        priority = request.get('priority', 'MEDIUM')
        
        # Auto-approve based on cost and priority
        auto_approve = (estimated_cost < 500) or (priority in ['HIGH', 'URGENT'])
        
        return {
            "approved": auto_approve,
            "approver_id": "AUTO-APPROVER-001",
            "approval_reason": f"Auto-approved: Cost ${estimated_cost}, Priority {priority}",
            "conditions": ["Delivery within business hours", "Quality verification on receipt"],
            "agent_response_time": datetime.now().isoformat()
        }

    @tool
    async def list_active_requests(self, limit: int = 10) -> Dict[str, Any]:
        """
        List active replenishment requests from memory storage.
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            Dict with list of active requests
        """
        try:
            # Filter requests by status from memory storage
            active_requests = [
                request for request in self.requests_storage.values()
                if request.get('RequestStatus') == 'ACTIVE'
            ]
            
            # Apply limit
            if limit > 0:
                active_requests = active_requests[:limit]
            
            return {
                "success": True,
                "count": len(active_requests),
                "requests": active_requests
            }
            
        except Exception as e:
            logger.error(f"❌ List requests failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def run_orchestrator_loop(self):
        """
        Main orchestrator loop that monitors for new requests and processes them.
        """
        logger.info(f"🔄 Starting LogisticsOrchestrator main loop")
        
        while True:
            try:
                # Check for new ACTIVE requests that need orchestration
                active_requests = await self.list_active_requests()
                
                if active_requests.get('success') and active_requests.get('count', 0) > 0:
                    for request in active_requests['requests']:
                        # Skip if already being orchestrated
                        if request.get('RequestStatus') != 'ACTIVE':
                            continue
                            
                        logger.info(f"🎯 Processing request: {request.get('RequestId')}")
                        
                        # Orchestrate the request
                        result = await self.orchestrate_replenishment_request(
                            request_data=request,
                            priority=request.get('Priority', 'MEDIUM')
                        )
                        
                        if result.get('success'):
                            logger.info(f"✅ Successfully orchestrated: {request.get('RequestId')}")
                        else:
                            logger.error(f"❌ Orchestration failed: {request.get('RequestId')}")
                
                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                logger.info(f"🛑 Orchestrator loop stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in orchestrator loop: {str(e)}")
                await asyncio.sleep(30)  # Wait longer on error

# Agent Factory Function
def create_logistics_orchestrator_agent() -> LogisticsOrchestratorAgent:
    """
    Factory function to create and configure a LogisticsOrchestratorAgent.
    
    Returns:
        Configured LogisticsOrchestratorAgent instance
    """
    agent = LogisticsOrchestratorAgent(name="LogisticsOrchestrator")
    
    # Add any additional configuration here
    logger.info(f"🏭 LogisticsOrchestratorAgent created and ready for deployment")
    
    return agent

# Main execution
if __name__ == "__main__":
    # Create and run the orchestrator agent
    orchestrator = create_logistics_orchestrator_agent()
    
    # Run the orchestrator loop
    asyncio.run(orchestrator.run_orchestrator_loop())