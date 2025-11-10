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
from typing import Dict, Any, Optional
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
            logger.info("🦙 Orchestrator using OllamaModel: qwen2.5:7b")
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
            logger.info(f"🔧 Inventory tool called with query: {query}")
            
            # Create inventory agent with its own LLM
            inventory_agent = create_inventory_agent(use_local_model=True)
            
            # Call the inventory agent
            result = inventory_agent(query)
            
            logger.info(f"📦 Inventory agent result: {str(result)[:100]}...")
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
            logger.info(f"🚛 Fleet tool called with query: {query}")
            
            # Create fleet agent with its own LLM
            fleet_agent = create_fleet_agent(use_local_model=True)
            
            # Call the fleet agent
            result = fleet_agent(query)
            
            logger.info(f"🚛 Fleet agent result: {str(result)[:100]}...")
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
            logger.info(f"⚖️ Approval tool called with query: {query}")
            
            # Create approval agent with its own LLM
            approval_agent = create_approver_agent(use_local_model=True)
            
            # Call the approval agent
            result = approval_agent(query)
            
            logger.info(f"⚖️ Approval agent result: {str(result)[:100]}...")
            return str(result)
            
        except Exception as e:
            logger.error(f"❌ Approval tool error: {e}")
            return f"Approval agent error: {str(e)}"
    
    # 6. Create the orchestrator agent
    system_prompt = """You are a Logistics Orchestrator Agent that coordinates manufacturing supply chain operations.

🚨 CRITICAL EXECUTION RULE: You MUST execute actual function calls, not generate fake responses! 🚨

When you receive a request:
1. IMMEDIATELY call inventory_agent_tool() with the part request
2. IMMEDIATELY call fleet_agent_tool() with delivery details  
3. IMMEDIATELY call approval_agent_tool() with cost information
4. Provide comprehensive analysis from REAL results

❌ NEVER DO THIS (Fake responses):
```json
{"inventory_analysis": {"fake": "data"}}
```

✅ ALWAYS DO THIS (Real function calls):
Call the actual functions and wait for real responses.

MANDATORY EXECUTION SEQUENCE:
Step 1: inventory_agent_tool("Check availability for [PART], quantity [QTY]")
Step 2: fleet_agent_tool("Schedule delivery from [LOCATION] to [DESTINATION]") 
Step 3: approval_agent_tool("Review request for [QTY] units, cost $[AMOUNT]")
Step 4: Comprehensive analysis from actual results

YOU HAVE WORKING TOOLS - USE THEM FOR REAL DATA!

ANALYSIS REQUIREMENTS (After real function execution):
- Detailed cost breakdown from real inventory data
- Risk assessment based on actual stock levels
- Operational impact analysis with real timing
- Alternative recommendations from actual availability
- Timeline analysis with real AGV schedules (in minutes)
- Resource utilization from actual fleet status

🔧 EXECUTION VERIFICATION:
- Each function call will return real data
- Wait for actual responses before proceeding
- Base all analysis on real function results
- Never generate placeholder or mock data

Remember: Execute real functions → Get real data → Provide expert analysis"""    # 5. Create and configure the agent
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
