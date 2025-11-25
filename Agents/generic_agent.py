"""
Generic Agent Base Class Module
Contains the GenericAgent wrapper for Strands agents.
"""

import re
import sys
from io import StringIO
from typing import List, Optional
from strands import Agent
from strands.models.ollama import OllamaModel

try:
    from strands_tools.a2a_client import A2AClientToolProvider
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False


class GenericAgent:
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