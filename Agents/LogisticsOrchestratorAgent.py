#!/usr/bin/env python3
"""
Logistics Orchestrator Agent - Multi-Agent Architecture
================================================================

This orchestrator coordinates with the Inventory Agent using the Strands Framework.
- Orchestrator Agent: Uses LLM to coordinate workflow  
- Inventory Agent: Smart inventory management with its own LLM

Each agent uses its own LLM instance for specialized decision making.
The orchestrator uses LLM to coordinate the overall workflow.
"""

import logging
from strands import Agent, tool
from strands.models.ollama import OllamaModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_logistics_orchestrator_agent(use_local_model: bool = True, hooks=None) -> Agent:
    """
    Create the Logistics Orchestrator Agent with inventory management capability.
    
    Architecture:
    - Orchestrator Agent (uses LLM) coordinates workflow
    - Inventory Agent (uses own LLM) handles inventory expertise
    - Inventory agent is wrapped as a tool and provided to orchestrator
    
    Args:
        use_local_model: If True, uses Ollama local model
        hooks: Optional observability hooks
        
    Returns:
        Configured Strands Agent with inventory tool coordination
    """
    
    # 1. Configure the LLM model for orchestrator
    if use_local_model:
        try:
            ollama_model = OllamaModel(
                host="http://localhost:11434",
                model_id="qwen2.5:7b",
                keep_alive=300  # Keep model alive for 5 minutes
            )

        except Exception as e:
            logger.error(f"❌ Failed to initialize OllamaModel: {e}")
            raise
    else:
        # Fallback or other model configurations
        raise NotImplementedError("Non-local models not implemented yet")
    
    # 2. Import factory functions for agents
    from Agents.InventoryAgent import create_inventory_agent
    from Agents.FleetAgent import create_fleet_agent
    from Agents.ApproverAgent import create_approver_agent
    
    # 3. Create the inventory agent tool
    @tool
    def inventory_agent_tool(query: str) -> str:
        """
        Use the Inventory Agent to check stock levels, availability, and warehouse information.
        
        Args:
            query: Natural language query about inventory (e.g. "Check availability for part ABC123, quantity 5")
            
        Returns:
            Inventory analysis and availability information
        """
        try:

            
            # Create inventory agent with its own LLM and pass hooks for observability
            inventory_agent = create_inventory_agent(use_local_model=True, hooks=hooks)
            
            # Call the inventory agent
            result = inventory_agent(query)
            

            return str(result)
            
        except Exception as e:
            logger.error(f"❌ Inventory tool error: {e}")
            return f"Inventory agent error: {str(e)}"
    
    # 4. Create the fleet agent tool
    @tool
    def fleet_agent_tool(query: str) -> str:
        """
        Use the Fleet Agent to coordinate AGV fleet operations and delivery scheduling.
        
        Args:
            query: Natural language query about fleet operations (e.g. "Schedule delivery from Warehouse A to Production Line 1")
            
        Returns:
            Fleet coordination results including AGV assignment and delivery schedule
        """
        try:

            
            # Create fleet agent with its own LLM and pass hooks for observability
            fleet_agent = create_fleet_agent(use_local_model=True, hooks=hooks)
            
            # Call the fleet agent
            result = fleet_agent(query)
            

            return str(result)
            
        except Exception as e:
            logger.error(f"❌ Fleet tool error: {e}")
            return f"Fleet agent error: {str(e)}"
    
    # 5. Create the approval agent tool
    @tool
    def approval_agent_tool(query: str) -> str:
        """
        Use the Approval Agent to process approval requests and make authorization decisions.
        
        Args:
            query: Natural language query about approval (e.g. "Review and approve request for 5 units of PART-123, estimated cost $250")
            
        Returns:
            Approval decision with reasoning and authorization details
        """
        try:

            
            # Create approval agent with its own LLM and pass hooks for observability
            approval_agent = create_approver_agent(use_local_model=True, hooks=hooks)
            
            # Call the approval agent
            result = approval_agent(query)
            

            return str(result)
            
        except Exception as e:
            logger.error(f"❌ Approval tool error: {e}")
            return f"Approval agent error: {str(e)}"
    
    # 6. Create the orchestrator agent
    system_prompt = """You are a Logistics Orchestrator Agent that coordinates manufacturing supply chain operations.

🚨 CRITICAL EXECUTION RULE: You MUST execute actual function calls, not generate fake responses! 🚨

When you receive a request, follow this COMPLETE LOGISTICS WORKFLOW:
1. Check inventory availability and get pricing information
2. Verify AGV availability for the required pickup and delivery
3. Get authorization approval based on total costs
4. Reserve the parts and assign AGV only after approval
5. Dispatch the AGV for pickup and delivery
6. Provide comprehensive tracking and status information

❌ NEVER DO THIS (Fake responses):
```json
{"inventory_analysis": {"fake": "data"}}
```

✅ ALWAYS DO THIS (Real function calls):
Call the actual functions and wait for real responses.

MANDATORY EXECUTION SEQUENCE:
Step 1: inventory_agent_tool("Check availability for [PART], quantity [QTY]")
Step 2: fleet_agent_tool("Check AGV availability for pickup from [WAREHOUSE] to [DESTINATION]")
Step 3: approval_agent_tool("Review and approve request for [QTY] units, total cost $[AMOUNT]")
Step 4: inventory_agent_tool("Reserve [QTY] units of [PART] for confirmed request")
Step 5: fleet_agent_tool("Dispatch AGV to pickup [PART] from [WAREHOUSE] and deliver to [DESTINATION]")
Step 6: Comprehensive status report with tracking information

YOU HAVE WORKING TOOLS - USE THEM FOR REAL DATA!

ANALYSIS REQUIREMENTS (After real function execution):
- Detailed cost breakdown from real inventory and delivery data
- Risk assessment based on actual stock levels and AGV availability
- Operational timeline with pickup and delivery estimates (in minutes)
- Resource allocation confirmation (parts reserved, AGV assigned)
- Alternative recommendations if resources unavailable
- Tracking information for dispatched AGV and reserved parts
- Final status summary with next steps and completion timeline

🔧 EXECUTION VERIFICATION:
- Each function call will return real data
- Wait for actual responses before proceeding to next step
- Base all analysis on real function results
- Never generate placeholder or mock data
- Only proceed to reservation/dispatch AFTER approval is granted

⚠️ CRITICAL BUSINESS LOGIC:
- DO NOT reserve parts or dispatch AGVs without approval
- If any step fails, stop the workflow and provide alternatives
- Always confirm resource availability before making commitments
- Provide clear tracking information for dispatched operations

Remember: Check → Verify → Approve → Reserve → Dispatch → Track"""    # 5. Create and configure the agent
    try:
        orchestrator = Agent(
            name="LogisticsOrchestrator",
            model=ollama_model,
            system_prompt=system_prompt,
            tools=[inventory_agent_tool, fleet_agent_tool, approval_agent_tool],
            hooks=hooks
        )
        
        logger.info("✅ Logistics Orchestrator Agent created successfully")
        logger.info(f"🛠️  Available tools: {orchestrator.tool_names}")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"❌ Failed to create orchestrator agent: {e}")
        raise
