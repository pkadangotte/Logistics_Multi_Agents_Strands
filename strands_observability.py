#!/usr/bin/env python3
"""
Real Strands/MCP Observability Implementation
==========================================

This implements true MCP observability capture to replace custom UI messages
with real agent communication data from the Strands framework.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import time

# MCP/Strands imports for real observability
try:
    from mcp.types import (
        LoggingMessageNotification, 
        LoggingMessageNotificationParams,
        ProgressNotification,
        ProgressNotificationParams,
        CallToolResult
    )
    from mcp.client.session import ClientSession
    from mcp.server.fastmcp import FastMCP, Context
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ MCP not available - using fallback observability")

logger = logging.getLogger(__name__)

@dataclass
class ObservabilityMessage:
    """Structured observability message from real agent activity."""
    timestamp: str
    agent_name: str
    message_type: str  # 'log', 'progress', 'tool_call', 'agent_communication'
    content: str
    level: str = 'info'
    step: int = 0
    progress: Optional[float] = None
    metadata: Dict[str, Any] = None

    def to_ui_format(self) -> Dict[str, Any]:
        """Convert to UI-compatible format."""
        return {
            'step': self.step,
            'agent': self.agent_name.upper().replace('_', ' '),
            'message': self.content,
            'timestamp': self.timestamp,
            'level': self.level,
            'progress': self.progress,
            'type': self.message_type,
            'metadata': self.metadata or {}
        }

class StrandsObservabilityCapture:
    """Captures real Strands agent communications and activities."""
    
    def __init__(self):
        self.messages: List[ObservabilityMessage] = []
        self.subscribers: List[Callable] = []
        self.active_sessions: Dict[str, Any] = {}
        self.tool_calls: Dict[str, Dict] = {}
        self.agent_communications: List[Dict] = []
        self._lock = threading.Lock()
        
    def subscribe(self, callback: Callable):
        """Subscribe to real-time observability updates."""
        with self._lock:
            self.subscribers.append(callback)
    
    def capture_log_message(self, agent_name: str, level: str, message: str, step: int = 0):
        """Capture real MCP log message."""
        obs_message = ObservabilityMessage(
            timestamp=datetime.now().strftime('%H:%M:%S'),
            agent_name=agent_name,
            message_type='log',
            content=message,
            level=level,
            step=step
        )
        
        with self._lock:
            self.messages.append(obs_message)
            
        # Notify subscribers
        self._notify_subscribers(obs_message)
    
    def capture_progress_update(self, agent_name: str, progress: float, message: str, step: int = 0):
        """Capture real MCP progress notification."""
        obs_message = ObservabilityMessage(
            timestamp=datetime.now().strftime('%H:%M:%S'),
            agent_name=agent_name,
            message_type='progress',
            content=message,
            step=step,
            progress=progress
        )
        
        with self._lock:
            self.messages.append(obs_message)
            
        # Log to file as well
        self._log_to_file(obs_message)
        self._notify_subscribers(obs_message)
    
    def capture_tool_call(self, agent_name: str, tool_name: str, parameters: Dict, result: Any, step: int = 0):
        """Capture real MCP tool call with parameters and result."""
        tool_id = f"{tool_name}_{int(time.time())}"
        
        # Store detailed tool call info
        with self._lock:
            self.tool_calls[tool_id] = {
                'agent': agent_name,
                'tool': tool_name,
                'parameters': parameters,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'step': step
            }
        
        # Create observable message
        obs_message = ObservabilityMessage(
            timestamp=datetime.now().strftime('%H:%M:%S'),
            agent_name=agent_name,
            message_type='tool_call',
            content=f"🛠️ Called {tool_name} with params: {json.dumps(parameters, indent=2)}",
            step=step,
            metadata={'tool_id': tool_id, 'result_preview': str(result)[:100]}
        )
        
        with self._lock:
            self.messages.append(obs_message)
            
        # Log to file as well
        self._log_to_file(obs_message)
        self._notify_subscribers(obs_message)
    
    def capture_agent_communication(self, source_agent: str, target_agent: str, 
                                  query: str, response: Any, step: int = 0):
        """Capture agent-to-agent communication with query and response."""
        comm_id = f"{source_agent}_{target_agent}_{int(time.time())}"
        
        # Store communication details
        with self._lock:
            self.agent_communications[comm_id] = {
                'source': source_agent,
                'target': target_agent,
                'query': query,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'step': step
            }
        
        # Create observable message for the communication
        obs_message = ObservabilityMessage(
            timestamp=datetime.now().strftime('%H:%M:%S'),
            agent_name=f"{source_agent} → {target_agent}",
            message_type='agent_communication',
            content=f"Query: {str(query)[:100]}{'...' if len(str(query)) > 100 else ''}",
            step=step,
            metadata={'response_type': type(response).__name__}
        )
        
        with self._lock:
            self.messages.append(obs_message)
            
        # Log to file as well
        self._log_to_file(obs_message)

    def reset_for_new_request(self, request_id: str = None):
        """Reset observability state and create new log file for new request."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        request_suffix = f"_{request_id}" if request_id else ""
        
        with self._lock:
            # Clear all existing data
            self.messages.clear()
            self.tool_calls.clear()
            self.agent_communications.clear()
            
            # Reset log file
            self.log_file_path = f"agent_messages_{timestamp}{request_suffix}.log"
            
            # Create new log file with header
            try:
                with open(self.log_file_path, 'w') as f:
                    f.write(f"=== Agent Messages Log - {datetime.now().isoformat()} ===\n")
                    f.write(f"Request ID: {request_id}\n")
                    f.write("=" * 60 + "\n\n")
                logger.info(f"📝 New agent messages log: {self.log_file_path}")
            except Exception as e:
                logger.error(f"Failed to create log file: {e}")
                self.log_file_path = None

    def _log_to_file(self, message: ObservabilityMessage):
        """Log message to current log file."""
        if not hasattr(self, 'log_file_path') or not self.log_file_path:
            return
            
        try:
            with open(self.log_file_path, 'a') as f:
                log_line = f"[{message.timestamp}] {message.agent_name}: {message.content}\n"
                f.write(log_line)
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")
    
    def _notify_subscribers(self, message: ObservabilityMessage):
        """Notify all subscribers of new observability data."""
        for callback in self.subscribers:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Error notifying observability subscriber: {e}")
    
    def get_messages_for_ui(self) -> List[Dict[str, Any]]:
        """Get all messages in UI-compatible format."""
        with self._lock:
            return [msg.to_ui_format() for msg in self.messages]
    
    def get_tool_call_details(self, tool_id: str) -> Optional[Dict]:
        """Get detailed information about a specific tool call."""
        with self._lock:
            return self.tool_calls.get(tool_id)
    
    def get_agent_communications(self) -> List[Dict]:
        """Get all agent-to-agent communications."""
        with self._lock:
            return self.agent_communications.copy()
    
    def clear(self):
        """Clear all captured observability data."""
        with self._lock:
            self.messages.clear()
            self.tool_calls.clear()
            self.agent_communications.clear()

# Global observability capture instance
observability_capture = StrandsObservabilityCapture()

class ObservabilityAwareAgent:
    """Wrapper for Strands agents that captures observability data."""
    
    def __init__(self, agent, agent_name: str):
        self.agent = agent
        self.agent_name = agent_name
        self.step_counter = 0
    
    def __call__(self, query: str, **kwargs) -> Any:
        """Intercept agent calls to capture observability data."""
        self.step_counter += 1
        
        # Capture the request
        observability_capture.capture_log_message(
            self.agent_name,
            'info',
            f"📥 Received request: {query[:100]}...",
            self.step_counter
        )
        
        try:
            # Call the actual agent
            result = self.agent(query, **kwargs)
            
            # Capture the response
            observability_capture.capture_log_message(
                self.agent_name,
                'info',
                f"📤 Response generated: {str(result)[:100]}...",
                self.step_counter
            )
            
            return result
            
        except Exception as e:
            # Capture errors
            observability_capture.capture_log_message(
                self.agent_name,
                'error',
                f"❌ Error: {str(e)}",
                self.step_counter
            )
            raise

def create_observability_aware_orchestrator():
    """Create an orchestrator wrapped with observability capture."""
    from Agents.LogisticsOrchestratorAgent import create_logistics_orchestrator_agent
    
    try:
        from config.config_loader import get_system_config
        config = get_system_config()
        
        # Create the base orchestrator
        use_local = config.get('system_settings', {}).get('ai_config', {}).get('fallback_to_rules', True)
        base_orchestrator = create_logistics_orchestrator_agent(use_local_model=use_local)
        
        # Wrap with observability
        return ObservabilityAwareAgent(base_orchestrator, "logistics_orchestrator")
        
    except Exception as e:
        logger.error(f"Error creating observability-aware orchestrator: {e}")
        return None

def instrument_inventory_agent():
    """Add observability capture to inventory agent operations."""
    try:
        from Agents.InventoryAgent import _inventory_agent
        
        # Monkey-patch key methods to add observability
        original_check_availability = _inventory_agent.check_availability
        original_get_inventory_info = _inventory_agent.get_inventory_info
        
        def observed_check_availability(*args, **kwargs):
            observability_capture.capture_log_message(
                'inventory_agent',
                'info', 
                f"🔍 Checking availability for: {args}",
                1
            )
            result = original_check_availability(*args, **kwargs)
            observability_capture.capture_log_message(
                'inventory_agent',
                'info',
                f"✅ Availability result: {result}",
                1
            )
            return result
        
        def observed_get_inventory_info(*args, **kwargs):
            observability_capture.capture_log_message(
                'inventory_agent',
                'info',
                f"📊 Getting inventory info for: {args}",
                2
            )
            result = original_get_inventory_info(*args, **kwargs)
            observability_capture.capture_log_message(
                'inventory_agent', 
                'info',
                f"📋 Inventory info: {result}",
                2
            )
            return result
        
        # Replace methods
        _inventory_agent.check_availability = observed_check_availability
        _inventory_agent.get_inventory_info = observed_get_inventory_info
        
        logger.info("✅ Inventory agent instrumented with observability")
        
    except Exception as e:
        logger.error(f"Error instrumenting inventory agent: {e}")

def instrument_fleet_agent():
    """Add observability capture to fleet agent operations.""" 
    try:
        from Agents.FleetAgent import _fleet_agent
        
        # Check available methods and patch existing ones
        if hasattr(_fleet_agent, 'schedule_delivery'):
            original_schedule_delivery = _fleet_agent.schedule_delivery
            
            def observed_schedule_delivery(*args, **kwargs):
                observability_capture.capture_log_message(
                    'fleet_agent',
                    'info',
                    f"🚛 Scheduling delivery for: {args}",
                    3
                )
                result = original_schedule_delivery(*args, **kwargs)
                observability_capture.capture_log_message(
                    'fleet_agent',
                    'info', 
                    f"✅ Delivery scheduled: {result}",
                    3
                )
                return result
            
            _fleet_agent.schedule_delivery = observed_schedule_delivery
        
        if hasattr(_fleet_agent, 'get_fleet_availability'):
            original_get_fleet_availability = _fleet_agent.get_fleet_availability
            
            def observed_get_fleet_availability(*args, **kwargs):
                observability_capture.capture_log_message(
                    'fleet_agent',
                    'info',
                    f"📊 Getting fleet availability",
                    4
                )
                result = original_get_fleet_availability(*args, **kwargs)
                observability_capture.capture_log_message(
                    'fleet_agent',
                    'info',
                    f"🚛 Fleet availability: {result}",
                    4
                )
                return result
            
            _fleet_agent.get_fleet_availability = observed_get_fleet_availability
        
        logger.info("✅ Fleet agent instrumented with observability")
        
    except Exception as e:
        logger.error(f"Error instrumenting fleet agent: {e}")

def initialize_real_observability():
    """Initialize the complete real observability system."""
    logger.info("🔍 Initializing Real Strands Observability System")
    
    # Clear any existing data
    observability_capture.clear()
    
    # Instrument all agents
    instrument_inventory_agent()
    instrument_fleet_agent()
    
    # Create observability-aware orchestrator
    orchestrator = create_observability_aware_orchestrator()
    
    logger.info("✅ Real Strands observability system initialized")
    return orchestrator

if __name__ == "__main__":
    # Test the observability system
    observability_capture = StrandsObservabilityCapture()
    
    # Simulate some agent activity
    observability_capture.capture_log_message("inventory_agent", "info", "Starting inventory check", 1)
    observability_capture.capture_progress_update("inventory_agent", 0.5, "Checking database", 1)
    observability_capture.capture_tool_call("inventory_agent", "check_stock", {"part": "ABC123"}, {"available": 50}, 1)
    observability_capture.capture_agent_communication("orchestrator", "inventory_agent", "Check stock for ABC123", {"available": 50}, 1)
    
    # Print results
    print("📊 Real Observability Messages:")
    for msg in observability_capture.get_messages_for_ui():
        print(f"  {msg['timestamp']} [{msg['agent']}] {msg['message']}")


# ============================================================================
# STRANDS HOOKS INTEGRATION
# ============================================================================

class ObservabilityHookProvider:
    """Hook provider to capture Strands agent interactions automatically."""
    
    def __init__(self, observability_capture):
        self.observability_capture = observability_capture
        logger.info("🪝 ObservabilityHookProvider initialized")
    
    def register_hooks(self, registry):
        """Register hooks with the Strands hook registry."""
        try:
            from strands.hooks import BeforeToolCallEvent, AfterToolCallEvent, AfterModelCallEvent
            
            # Register before tool call hook
            registry.add_callback(BeforeToolCallEvent, self.before_tool_call)
            logger.info("🪝 DEBUG: Registered BeforeToolCallEvent handler")
            
            # Register after tool call hook  
            registry.add_callback(AfterToolCallEvent, self.after_tool_call)
            logger.info("🪝 DEBUG: Registered AfterToolCallEvent handler")
            
            # Register after model call hook
            registry.add_callback(AfterModelCallEvent, self.after_model_call)
            logger.info("🪝 DEBUG: Registered AfterModelCallEvent handler")
            
        except Exception as e:
            logger.error(f"🪝 DEBUG: Error registering hooks: {e}")
            import traceback
            traceback.print_exc()
            import traceback
            traceback.print_exc()
    
    def before_tool_call(self, event):
        """Hook: Before tool call - capture the intent."""
        try:
            logger.info(f"🪝 DEBUG: BEFORE_TOOL_CALL triggered!")
            agent_name = getattr(event.agent, 'name', 'Unknown Agent')
            tool_name = event.tool_name
            args = event.arguments
            
            logger.info(f"🪝 DEBUG: Agent: {agent_name}, Tool: {tool_name}")
            
            message = f"🔧 About to call {tool_name}"
            if args:
                # Only show first few args to avoid clutter
                arg_preview = {k: v for k, v in list(args.items())[:2]} if isinstance(args, dict) else str(args)[:50]
                message += f" with {arg_preview}"
            
            self.observability_capture.capture_log_message(
                agent_name=agent_name,
                message=message,
                level='INFO'
            )
            
            logger.info(f"🪝 DEBUG: BEFORE_TOOL_CALL message captured: {message}")
            
        except Exception as e:
            logger.error(f"🪝 DEBUG: Error in before_tool_call hook: {e}")
            import traceback
            traceback.print_exc()
    
    def after_tool_call(self, event):
        """Hook: After tool call - capture the result."""
        try:
            logger.info(f"🪝 DEBUG: AFTER_TOOL_CALL triggered!")
            agent_name = getattr(event.agent, 'name', 'Unknown Agent')
            tool_name = event.tool_name
            result = event.result
            
            logger.info(f"🪝 DEBUG: Agent: {agent_name}, Tool: {tool_name}, Result type: {type(result)}")
            
            # Capture full tool call details
            self.observability_capture.capture_tool_call(
                agent_name=agent_name,
                tool_name=tool_name,
                parameters=event.arguments,
                result=result
            )
            
            logger.info(f"🪝 DEBUG: AFTER_TOOL_CALL captured tool call for {tool_name}")
            
        except Exception as e:
            logger.error(f"🪝 DEBUG: Error in after_tool_call hook: {e}")
            import traceback
            traceback.print_exc()
    
    def after_model_call(self, event):
        """Hook: After model call - capture model responses."""
        try:
            logger.info(f"🪝 DEBUG: AFTER_MODEL_CALL triggered!")
            agent_name = getattr(event.agent, 'name', 'Unknown Agent')
            
            # Extract response content if available
            response_preview = "Model response"
            if hasattr(event, 'result') and event.result:
                response_text = str(event.result)
                response_preview = response_text[:150] + "..." if len(response_text) > 150 else response_text
            
            logger.info(f"🪝 DEBUG: Model call from {agent_name}: {response_preview[:50]}...")
            
            self.observability_capture.capture_log_message(
                agent_name=agent_name,
                message=f"🤖 {response_preview}",
                level='INFO'
            )
            
            logger.info(f"🪝 DEBUG: AFTER_MODEL_CALL captured model response")
            
        except Exception as e:
            logger.error(f"🪝 DEBUG: Error in after_model_call hook: {e}")
            import traceback
            traceback.print_exc()


def create_observability_hooks():
    """Create observability hooks provider for Strands Agent."""
    hook_provider = ObservabilityHookProvider(observability_capture)
    # Return as list since Strands Agent expects iterable
    return [hook_provider]