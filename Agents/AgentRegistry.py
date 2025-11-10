#!/usr/bin/env python3
"""
Agent Registry for Logistics Multi-Agent System
===============================================

Registry pattern for managing all agents in the Strands-based logistics system.
This provides centralized agent management and follows Strands best practices
for multi-agent coordination.
"""

from typing import Dict, Any, Optional
from strands import Agent
import logging

logger = logging.getLogger(__name__)

class AgentRegistry:
    """Registry for managing all agents in the logistics system"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents in the system"""
        try:
            # Import agent factory functions
            from .InventoryAgent import create_inventory_agent
            from .FleetAgent import create_fleet_agent
            from .ApproverAgent import create_approver_agent
            from .LogisticsOrchestratorAgent import create_logistics_orchestrator_agent
            
            # Create and register all agents
            self.agents['inventory'] = create_inventory_agent()
            self.agents['fleet'] = create_fleet_agent()
            self.agents['approver'] = create_approver_agent()
            # Note: Orchestrator creates its own instance to avoid circular dependency
            
            logger.info(f"🏭 Agent Registry initialized with {len(self.agents)} agents")
            
        except ImportError as e:
            logger.error(f"❌ Failed to initialize agents: {str(e)}")
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get agent by name"""
        agent = self.agents.get(agent_name)
        if agent is None:
            logger.warning(f"⚠️  Agent '{agent_name}' not found in registry")
        return agent
    
    def list_agents(self) -> Dict[str, Agent]:
        """List all registered agents"""
        return self.agents.copy()
    
    def add_agent(self, name: str, agent: Agent):
        """Add agent to registry"""
        self.agents[name] = agent
        logger.info(f"✅ Added agent '{name}' to registry")
    
    def remove_agent(self, name: str) -> bool:
        """Remove agent from registry"""
        if name in self.agents:
            del self.agents[name]
            logger.info(f"🗑️  Removed agent '{name}' from registry")
            return True
        else:
            logger.warning(f"⚠️  Cannot remove '{name}' - not found in registry")
            return False
    
    def get_agent_count(self) -> int:
        """Get total number of registered agents"""
        return len(self.agents)
    
    def get_agent_names(self) -> list:
        """Get list of all agent names"""
        return list(self.agents.keys())

# Global registry instance
registry = AgentRegistry()

def get_registry() -> AgentRegistry:
    """Get the global agent registry"""
    return registry