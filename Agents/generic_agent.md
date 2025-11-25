# GenericAgent Class Documentation

The `GenericAgent` class serves as an enhanced wrapper for Strands agents, providing additional functionality for data management integration and agent-to-agent communication in the logistics multi-agent system.

## Class Overview

The `GenericAgent` class is designed to:
- Wrap Strands agents with enhanced functionality
- Integrate data management tools seamlessly
- Support agent-to-agent (A2A) communication
- Provide clear agent identification in multi-agent interactions
- Handle errors gracefully with proper system state restoration

## Functions Documentation

### `__init__` Function

```python
def __init__(
    self, 
    name: str,
    agent_type: str,
    ollama_model,
    system_prompt: str,
    enable_a2a: bool = True,
    data_manager_tools: list = None
):
```

**Purpose**: Constructor that initializes a new GenericAgent instance.

**Parameters**:
- `name`: The agent's name for identification
- `agent_type`: Category/type of the agent (e.g., "inventory", "fleet", "approval")
- `ollama_model`: The Ollama language model to use for the agent
- `system_prompt`: The system prompt that defines the agent's behavior and role
- `enable_a2a`: Boolean flag to enable agent-to-agent communication tools
- `data_manager_tools`: Optional list of data management tools to provide to the agent

**Functionality**:
- Stores all initialization parameters as instance variables
- Initializes an empty conversation history
- Calls `_create_agent()` to set up the underlying Strands agent

### `_create_agent` Function

```python
def _create_agent(self):
    """Create the Strands agent with proper configuration."""
```

**Purpose**: Private method that creates and configures the underlying Strands agent.

**Functionality**:
1. **Tool Setup**: Creates an empty tools list and adds data manager tools if provided
2. **A2A Integration**: If A2A (Agent-to-Agent) communication is enabled and available:
   - Creates an `A2AClientToolProvider` instance
   - Extracts individual tools from the provider or adds the provider directly
   - Handles exceptions gracefully with warning messages
3. **Agent Creation**: Creates a Strands `Agent` instance with:
   - The agent's name
   - The specified Ollama model
   - The system prompt
   - All configured tools
4. **Flag Setting**: Sets `is_strands_agent = True` to indicate this is a Strands-based agent

### `send_message` Function

```python
def send_message(self, message: str) -> str:
    """Send a message to the agent and get response."""
```

**Purpose**: Sends a message to the agent and processes the response with enhanced output formatting.

**Parameters**:
- `message`: The input message/query to send to the agent

**Returns**: The agent's response as a string

**Functionality**:
1. **Output Capture**: Temporarily redirects `sys.stdout` to capture tool call outputs
2. **Message Processing**: Calls the underlying Strands agent with the message
3. **Output Enhancement**: Processes captured output to add the agent's name to tool calls:
   - Uses regex to find patterns like "Tool #X:"
   - Replaces them with "AgentName -> Tool #X:" for better identification
4. **Error Handling**: Ensures stdout is restored even if exceptions occur
5. **Response Return**: Returns the agent's response as a string

**Key Feature**: This function enhances the user experience by clearly identifying which agent is making tool calls during multi-agent interactions.

### `get_info` Function

```python
def get_info(self):
    """Get information about this agent."""
```

**Purpose**: Provides comprehensive information about the agent's configuration and capabilities.

**Returns**: A dictionary containing agent metadata

**Functionality**:
1. **Model Info Extraction**: Safely extracts model information by checking multiple possible attribute names:
   - `model`
   - `model_name` 
   - `name`
   - Defaults to "unknown" if none are found
2. **Information Compilation**: Returns a dictionary with:
   - `name`: Agent's name
   - `type`: Agent type/category
   - `model`: Model information
   - `a2a_enabled`: Whether A2A communication is enabled
   - `strands_agent`: Confirms this is a Strands-based agent
   - `data_manager_tools`: Count of data management tools
   - `total_tools`: Total number of tools available to the agent

**Use Cases**: 
- Debugging agent configurations
- Displaying agent capabilities in user interfaces
- Logging and monitoring agent setups

## Key Design Features

1. **Modular Tool Integration**: Supports both data manager tools and A2A communication tools
2. **Graceful Degradation**: Handles missing A2A tools without breaking functionality
3. **Enhanced Logging**: Adds agent identification to tool call outputs
4. **Robust Error Handling**: Ensures system state is properly restored after operations
5. **Flexible Model Support**: Works with different Ollama model attribute naming conventions

## Usage Example

```python
from generic_agent import GenericAgent
from strands.models.ollama import OllamaModel

# Create an Ollama model
model = OllamaModel(model="llama2")

# Create a generic agent
agent = GenericAgent(
    name="InventoryAgent",
    agent_type="inventory",
    ollama_model=model,
    system_prompt="You are an inventory management agent...",
    enable_a2a=True,
    data_manager_tools=inventory_tools
)

# Send a message
response = agent.send_message("Check inventory levels for product ABC123")

# Get agent information
info = agent.get_info()
print(f"Agent: {info['name']}, Tools: {info['total_tools']}")
```

## Integration with Logistics System

This class provides a solid foundation for building multi-agent logistics systems with:
- Clear agent identification in tool calls
- Comprehensive tool integration capabilities
- Robust error handling and state management
- Flexible configuration options for different agent types

The `GenericAgent` class is particularly well-suited for logistics applications where multiple specialized agents (inventory, fleet, approval) need to work together while maintaining clear communication boundaries and tool access controls.