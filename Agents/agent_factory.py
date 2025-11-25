"""
Agent Factory Module
Contains the AgentFactory for creating specialized agents.
"""

from typing import Optional
from strands.models.ollama import OllamaModel
from generic_agent import GenericAgent
from tool_providers.inventory_tools import InventoryAgentToolProvider
from tool_providers.fleet_tools import FleetAgentToolProvider
from tool_providers.approval_tools import ApprovalAgentToolProvider

class AgentFactory:
    """Factory for creating specialized logistics agents."""
    
    def __init__(self, inventory_manager=None, fleet_manager=None, approval_manager=None):
        self.inventory_manager = inventory_manager
        self.fleet_manager = fleet_manager
        self.approval_manager = approval_manager
        
        # Shared Ollama model instance for performance
        self._shared_model = None
        
        # Create tool providers
        self.inventory_tools = InventoryAgentToolProvider(inventory_manager).tools if inventory_manager else []
        self.fleet_tools = FleetAgentToolProvider(fleet_manager).tools if fleet_manager else []
        self.approval_tools = ApprovalAgentToolProvider(approval_manager).tools if approval_manager else []
    
    @staticmethod
    def create_ollama_model(
        host: str = "http://localhost:11434",
        model_id: str = "qwen2.5:3b"
    ):
        """Create an OllamaModel instance."""
        return OllamaModel(
            model_id=model_id,
            host=host
        )
    
    def get_shared_model(self, host: str = "http://localhost:11434", model_id: str = "qwen2.5:3b"):
        """Get or create shared Ollama model instance for performance."""
        if self._shared_model is None:
            print(f"🚀 Initializing shared Ollama model: {model_id}...")
            self._shared_model = OllamaModel(
                model_id=model_id,
                host=host
            )
            print(f"✅ Shared model ready!")
        return self._shared_model
    
    def create_agent(
        self,
        agent_type: str,
        name: str,
        ollama_model = None,
        custom_prompt: str = None,
        enable_a2a: bool = True,
        host: str = "http://localhost:11434",
        model_id: str = "qwen2.5:3b"
    ):
        """Create a specialized logistics agent."""
        
        # Use provided model or get shared instance for performance
        if ollama_model is None:
            ollama_model = self.get_shared_model(host, model_id)
        
        # Get system prompt based on agent type
        system_prompt = custom_prompt or self._get_system_prompt(agent_type)
        
        # Select appropriate tools based on agent type - DOMAIN-SPECIFIC ONLY
        data_manager_tools = []
        if agent_type.lower() == "inventory":
            data_manager_tools = self.inventory_tools
            system_prompt += "\n\nSPECIALIZATION: INVENTORY MANAGEMENT ONLY\n- Typical workflow: 1-3 tool calls (check availability, get info, reserve/release)\n- Call each tool ONCE per request\n- After getting inventory data, provide Summary immediately\n"
        
        elif agent_type.lower() == "fleet":
            data_manager_tools = self.fleet_tools
            system_prompt += "\n\nSPECIALIZATION: FLEET MANAGEMENT ONLY\n- Typical workflow: 1-3 tool calls (find AGV, check route, dispatch)\n- Call each tool ONCE per request\n- After successful dispatch, provide Summary immediately\n"
        
        elif agent_type.lower() in ["approver", "approval"]:
            data_manager_tools = self.approval_tools
            system_prompt += "\n\nSPECIALIZATION: APPROVAL WORKFLOWS ONLY\n- Typical workflow: 1-2 tool calls (check threshold, create/approve request)\n- Call each tool ONCE per request\n- After approval decision, provide Summary immediately\n"
        
        elif agent_type.lower() == "orchestrator":
            # Orchestrator gets all tools for comprehensive coordination
            data_manager_tools = self.inventory_tools + self.fleet_tools + self.approval_tools
            system_prompt += """\n\nROLE: LOGISTICS ORCHESTRATOR

You coordinate end-to-end logistics workflows efficiently.

TYPICAL WORKFLOW (only 5-7 tools needed):
1. Check inventory availability (check_availability or get_part_info)
2. Check if approval needed (check_approval_threshold)
3. Create approval if needed (create_approval_request)
4. Reserve parts (reserve_parts) - CRITICAL: Do this BEFORE finding AGV
5. Find optimal AGV (find_optimal_agv)
6. Dispatch AGV (dispatch_agv) - ONCE this succeeds, you're DONE
7. Provide summary

CRITICAL WORKFLOW ORDER:
- ALWAYS reserve parts BEFORE finding/dispatching AGV
- Reservation ensures parts are locked for this delivery
- Use the quantity from the original request for reservation
- After successful dispatch_agv, STOP and provide Summary

CRITICAL LOCATION HANDLING:
- Use EXACT location names from check_availability response
- Valid warehouses: "Central Warehouse", "Warehouse A", "Warehouse B"
- Valid destinations: "Production Line A", "Production Line B", "Manufacturing Plant Delta"
- DO NOT modify location strings (no "A1", "warehouse a", lowercase, abbreviations)
- COPY the warehouse_location value exactly as returned by check_availability

CRITICAL CONSTRAINTS:
- Maximum 10 tool calls per request
- Call each tool ONLY ONCE unless it errors
- DO NOT call dispatch_agv multiple times
- DO NOT call release_reservation unless fixing an error
- DO NOT call complete_agv_task - that happens automatically
- After successful dispatch_agv, STOP calling tools and provide Summary
- NEVER repeat the same tool call with identical parameters

WORKFLOW CONTROL:
- If dispatch_agv returns success → STOP and write Summary
- If you've called 8+ tools → STOP and write Summary  
- Don't try to "verify" or "check" after success
- Trust your tool results and move forward
- If find_optimal_agv fails with "route not found" → check that you used EXACT location names
"""
        
        else:
            print(f"⚠️ Warning: Unknown agent type '{agent_type}', using orchestrator configuration")
            data_manager_tools = self.inventory_tools + self.fleet_tools + self.approval_tools
        
        # Create agent with selected tools
        return GenericAgent(
            name=name,
            agent_type=agent_type,
            ollama_model=ollama_model,
            system_prompt=system_prompt,
            enable_a2a=enable_a2a,
            data_manager_tools=data_manager_tools
        )
    
    def _get_system_prompt(self, agent_type: str) -> str:
        """Get the default system prompt for an agent type."""
        
        # Base response format and constraints for all agents
        response_format = """

RESPONSE FORMAT - MANDATORY 3-PHASE STRUCTURE:

YOU MUST ALWAYS include ALL THREE phases in EVERY response:

═══════════════════════════════════════════════════════════
✿ PLANNING PHASE:
═══════════════════════════════════════════════════════════
📋 Task Analysis: [Brief summary of what you need to do]
🎯 Required Actions: [List the tools you'll use - typically 2-7 tools]

═══════════════════════════════════════════════════════════
✿ EXECUTION PHASE:
═══════════════════════════════════════════════════════════
Write out what EACH tool returned as you execute them:

✓ check_availability → Found: 85 units available at Warehouse A, cost $12.50/unit
✓ reserve_parts → Reserved 50 units of PART-ABC123, reservation ID: 5
✓ check_approval_threshold → No approval needed (total $625 is below $1000 threshold)
✓ find_optimal_agv → Selected AGV-002 (capacity: 50 pcs, battery: 92%)
✓ dispatch_agv → Dispatched successfully, ID: 1, time: 4 minutes, distance: 150m

CRITICAL: Include ALL tool results in YOUR response text.
CRITICAL: For dispatch_agv, include estimated_time_minutes and distance_m.

═══════════════════════════════════════════════════════════
✿ SUMMARY:
═══════════════════════════════════════════════════════════
✅ Results: [What was accomplished]
📊 Key Details: [Numbers, IDs, delivery time, distance]
💡 Next Steps: [What happens next]

MANDATORY SUMMARY FORMAT for deliveries:
✅ Results: Successfully dispatched [AGV-ID] to deliver [quantity] units of [part] from [warehouse] to [destination].
📊 Key Details:
- Dispatch ID: [number]
- Delivery Time: [X] minutes
- Distance: [Y] meters
- Estimated Cost: $[Z]
- Reservation ID: [number]
💡 Next Steps: Monitor delivery progress.

CRITICAL RULES:
- YOU MUST include ALL THREE phases (Planning, Execution, Summary)
- Write tool results in Execution Phase as you call them
- Planning Phase comes FIRST, before any tool calls
- Execution Phase shows EACH tool result
- Summary comes LAST with complete details
- For AGV dispatches, ALWAYS mention delivery time and distance
"""
        
        if agent_type.lower() == "inventory":
            return "You are an Inventory Management Agent responsible for tracking stock levels and managing warehouse operations." + response_format
        elif agent_type.lower() == "fleet":
            return "You are a Fleet Management Agent responsible for AGV scheduling and route optimization." + response_format
        elif agent_type.lower() in ["approver", "approval"]:
            return "You are an Approval Agent responsible for validating requests and checking compliance." + response_format
        else:
            return "You are a Logistics Orchestrator Agent responsible for coordinating multi-agent logistics operations." + response_format


def initialize_agent_factory(inventory_manager, fleet_manager, approval_manager):
    """Initialize the agent factory with all data managers."""
    factory = AgentFactory(
        inventory_manager=inventory_manager,
        fleet_manager=fleet_manager, 
        approval_manager=approval_manager
    )
    
    print("✅ Agent Factory initialized with DOMAIN-SPECIFIC data managers!")
    print(f"📦 Inventory Agent gets ONLY inventory tools: {len(factory.inventory_tools)}")
    print(f"🚛 Fleet Agent gets ONLY fleet tools: {len(factory.fleet_tools)}")
    print(f"⚖️ Approval Agent gets ONLY approval tools: {len(factory.approval_tools)}")
    print(f"🎯 Orchestrator Agent gets ALL tools: {len(factory.inventory_tools + factory.fleet_tools + factory.approval_tools)}")
    
    return factory