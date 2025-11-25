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
            
        # Add A2A tools if enabled and available (optimized for performance)
        if self.enable_a2a and A2A_AVAILABLE:
            try:
                # Suppress A2A discovery warnings for local-only operation
                import warnings
                import logging
                
                # Temporarily suppress HTTP connection warnings
                logging.getLogger('httpx').setLevel(logging.ERROR)
                logging.getLogger('httpcore').setLevel(logging.ERROR)
                logging.getLogger('a2a').setLevel(logging.ERROR)
                
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
                    
                    # Configure A2A with minimal overhead for local-only operation
                    a2a_provider = A2AClientToolProvider(
                        known_agent_urls=[],  # Empty list prevents external agent discovery
                        timeout=3,  # Reduced timeout for faster initialization
                    )
                    # Extract individual tools from the provider
                    if hasattr(a2a_provider, 'tools'):
                        tools.extend(a2a_provider.tools)
                    else:
                        # Fallback: add the provider directly
                        tools.append(a2a_provider)
                
                print(f"✅ {self.name}: A2A enabled (fast local-only)")
            except Exception as e:
                # Silently handle A2A errors - not critical for local operation
                pass
            
        # Create Strands agent with correct parameter name
        self.agent = Agent(
            name=self.name,
            model=self.ollama_model,
            system_prompt=self.system_prompt,
            tools=tools,
        )    
        self.is_strands_agent = True
    
    def send_message(self, message: str, streaming: bool = False) -> str:
        """Send a message to the agent and get response."""
        if streaming:
            return self._send_message_streaming(message)
        else:
            return self._send_message_standard(message)
    
    def _send_message_standard(self, message: str) -> str:
        """Send a message to the agent and get response (non-streaming)."""
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
    
    def _send_message_streaming(self, message: str) -> str:
        """Send a message to the agent with streaming response."""
        import threading
        import time
        
        # Save the REAL stdout before any redirection
        real_stdout = sys.stdout
        
        # Display the query being processed
        print(f"\n📝 Query: {message}")
        print()
        
        # Create a stop event for the animation
        stop_animation = threading.Event()
        
        def show_spinner():
            """Show animated spinner using the real stdout."""
            spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            idx = 0
            while not stop_animation.is_set():
                real_stdout.write(f'\r💭 Thinking... {spinner_chars[idx % len(spinner_chars)]}')
                real_stdout.flush()
                idx += 1
                time.sleep(0.1)
            real_stdout.write('\r' + ' ' * 50 + '\r')
            real_stdout.flush()
        
        # Start the spinner in a background thread
        spinner_thread = threading.Thread(target=show_spinner, daemon=True)
        spinner_thread.start()
        
        # Give spinner a moment to start
        time.sleep(0.1)
        
        # Capture stdout to suppress agent output during processing
        captured_output = StringIO()
        
        try:
            # Redirect stdout to capture everything (tool calls, streaming response, etc.)
            sys.stdout = captured_output
            
            # Get response (this will take time and generate output we're capturing)
            response = self.agent(message)
            
            # Restore stdout
            sys.stdout = real_stdout
            
            # Stop animation
            stop_animation.set()
            spinner_thread.join(timeout=0.5)
            
            # Add a newline after clearing the spinner to ensure clean output
            print()
            
            # Return just the response text - no captured output printed
            return str(response)
            
        except Exception as e:
            # Restore stdout and stop animation on error
            sys.stdout = real_stdout
            stop_animation.set()
            spinner_thread.join(timeout=0.5)
            print()  # Newline after spinner on error too
            raise e
    
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
    
