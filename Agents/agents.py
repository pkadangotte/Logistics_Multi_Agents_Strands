"""
Logistics Agent Classes Module
Contains the LogisticsAgent wrapper and AgentFactory for creating specialized agents.
"""

from typing import List, Optional
from strands import Agent
from strands.models.ollama import OllamaModel
try:
    from strands_tools.a2a_client import A2AClientToolProvider
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False


import re
import sys
from io import StringIO

from tool_providers import (
    InventoryAgentToolProvider,
    FleetAgentToolProvider, 
    ApprovalAgentToolProvider
)


class LogisticsAgent:
    """Enhanced Generic Agent with Data Manager Integration."""
    
    def __init__(
        self, 
        name: str,
        agent_type: str,
        ollama_model,
        system_prompt: str,
        enable_a2a: bool = True,
        data_manager_tools: list = None
    ):
        self.name = name
        self.agent_type = agent_type
        self.ollama_model = ollama_model
        self.system_prompt = system_prompt
        self.enable_a2a = enable_a2a
        self.data_manager_tools = data_manager_tools or []
        self.conversation_history = []
        
        # Create the agent
        self._create_agent()
    
    def _create_agent(self):
        """Create the Strands agent with proper configuration."""
        # Setup tools
        tools = []
        
        # Add data manager tools
        if self.data_manager_tools:
            tools.extend(self.data_manager_tools)
            
        # Add A2A tools if enabled and available
        if self.enable_a2a and A2A_AVAILABLE:
            try:
                a2a_provider = A2AClientToolProvider()
                # Extract individual tools from the provider
                if hasattr(a2a_provider, 'tools'):
                    tools.extend(a2a_provider.tools)
                else:
                    # Fallback: add the provider directly
                    tools.append(a2a_provider)
            except Exception as e:
                print(f"⚠️ Warning: Could not add A2A tools: {e}")
            
        # Create Strands agent with correct parameter name
        self.agent = Agent(
            name=self.name,
            model=self.ollama_model,
            system_prompt=self.system_prompt,
            tools=tools,
        )    
        self.is_strands_agent = True
    
    def send_message(self, message: str) -> str:
        """Send a message to the agent and get response."""
        # Capture stdout to intercept tool calls
        original_stdout = sys.stdout
        captured_output = StringIO()
        
        try:
            sys.stdout = captured_output
            response = self.agent(message)
            sys.stdout = original_stdout
            
            # Process captured output to add agent name to tool calls
            captured_text = captured_output.getvalue()
            if captured_text:
                # Replace "Tool #X:" with "AgentName -> Tool #X:"
                modified_output = re.sub(
                    r'Tool #(\d+):', 
                    f'{self.name} -> Tool #\\1:', 
                    captured_text
                )
                print(modified_output, end='')
            
            return str(response)
            
        except Exception as e:
            sys.stdout = original_stdout
            raise e
        finally:
            if sys.stdout != original_stdout:
                sys.stdout = original_stdout
    
    def get_info(self):
        """Get information about this agent."""
        # Get model info safely
        model_info = "unknown"
        if hasattr(self.ollama_model, 'model'):
            model_info = self.ollama_model.model
        elif hasattr(self.ollama_model, 'model_name'):
            model_info = self.ollama_model.model_name
        elif hasattr(self.ollama_model, 'name'):
            model_info = self.ollama_model.name
        
        return {
            "name": self.name,
            "type": self.agent_type,
            "model": model_info,
            "a2a_enabled": self.enable_a2a,
            "strands_agent": self.is_strands_agent,
            "data_manager_tools": len(self.data_manager_tools),
            "total_tools": len(self.agent.tool_names) if hasattr(self.agent, 'tool_names') else 0
        }


class AgentFactory:
    """Factory for creating specialized logistics agents."""
    
    def __init__(self, inventory_manager=None, fleet_manager=None, approval_manager=None):
        self.inventory_manager = inventory_manager
        self.fleet_manager = fleet_manager
        self.approval_manager = approval_manager
        
        # Create tool providers
        self.inventory_tools = InventoryAgentToolProvider(inventory_manager).tools if inventory_manager else []
        self.fleet_tools = FleetAgentToolProvider(fleet_manager).tools if fleet_manager else []
        self.approval_tools = ApprovalAgentToolProvider(approval_manager).tools if approval_manager else []
    
    @staticmethod
    def create_ollama_model(
        host: str = "http://localhost:11434",
        model_id: str = "qwen2.5:7b"
    ):
        """Create an OllamaModel instance."""
        return OllamaModel(
            model_id=model_id,
            host=host
        )
    
    def create_agent(
        self,
        agent_type: str,
        name: str,
        ollama_model = None,
        custom_prompt: str = None,
        enable_a2a: bool = True,
        host: str = "http://localhost:11434",
        model_id: str = "qwen2.5:7b"
    ):
        """Create a specialized logistics agent."""
        
        # Create model if not provided
        if ollama_model is None:
            ollama_model = self.create_ollama_model(host, model_id)
        
        # Get system prompt based on agent type
        system_prompt = custom_prompt or self._get_system_prompt(agent_type)
        
        # Select appropriate tools based on agent type - DOMAIN-SPECIFIC ONLY
        data_manager_tools = []
        if agent_type.lower() == "inventory":
            data_manager_tools = self.inventory_tools
            system_prompt += "\n\nYou are specialized in INVENTORY MANAGEMENT ONLY. You have access to inventory tools. You ONLY handle inventory-related tasks. Call each tool only ONCE per request unless you get an error. Provide clear, concise responses based on the tool results."
        
        elif agent_type.lower() == "fleet":
            data_manager_tools = self.fleet_tools
            system_prompt += "\n\nYou are specialized in FLEET MANAGEMENT ONLY. You have access to fleet tools. You ONLY handle AGV and transportation-related tasks. Call each tool only ONCE per request unless you get an error. Provide clear, concise responses based on the tool results."
        
        elif agent_type.lower() in ["approver", "approval"]:
            data_manager_tools = self.approval_tools
            system_prompt += "\n\nYou are specialized in APPROVAL WORKFLOWS ONLY. You have access to approval tools. You ONLY handle approval, compliance, and authorization tasks. Call each tool only ONCE per request unless you get an error. Provide clear, concise responses based on the tool results."
        
        elif agent_type.lower() == "orchestrator":
            # Orchestrator gets all tools for comprehensive coordination
            data_manager_tools = self.inventory_tools + self.fleet_tools + self.approval_tools
            system_prompt += "\n\nAs the Logistics Orchestrator, you have access to ALL management tools. You are the ONLY agent that can orchestrate workflows spanning multiple domains. Call each tool only ONCE per request unless you get an error. Provide clear, structured responses based on the tool results."
        
        else:
            print(f"⚠️ Warning: Unknown agent type '{agent_type}', using orchestrator configuration")
            data_manager_tools = self.inventory_tools + self.fleet_tools + self.approval_tools
        
        # Create agent with selected tools
        return LogisticsAgent(
            name=name,
            agent_type=agent_type,
            ollama_model=ollama_model,
            system_prompt=system_prompt,
            enable_a2a=enable_a2a,
            data_manager_tools=data_manager_tools
        )
    
    def _get_system_prompt(self, agent_type: str) -> str:
        """Get the default system prompt for an agent type."""
        if agent_type.lower() == "inventory":
            return "You are an Inventory Management Agent responsible for tracking stock levels and managing warehouse operations."
        elif agent_type.lower() == "fleet":
            return "You are a Fleet Management Agent responsible for AGV scheduling and route optimization."
        elif agent_type.lower() in ["approver", "approval"]:
            return "You are an Approval Agent responsible for validating requests and checking compliance."
        else:
            return "You are a Logistics Orchestrator Agent responsible for coordinating multi-agent logistics operations."


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