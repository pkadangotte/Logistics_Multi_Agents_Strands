# AgentFactory Class Documentation

The `AgentFactory` class is a factory pattern implementation that creates specialized logistics agents with domain-specific tools and configurations. It serves as the central hub for creating and configuring different types of agents in the multi-agent logistics system.

## Class Overview

The `AgentFactory` class provides:
- Centralized agent creation with proper tool assignment
- Domain-specific agent configuration (inventory, fleet, approval, orchestrator)
- Standardized Ollama model creation
- Tool provider integration and management
- Flexible agent customization options

## Functions Documentation

### `__init__` Function

```python
def __init__(self, inventory_manager=None, fleet_manager=None, approval_manager=None):
```

**Purpose**: Constructor that initializes the AgentFactory with data managers and sets up tool providers.

**Parameters**:
- `inventory_manager`: Optional inventory data manager instance
- `fleet_manager`: Optional fleet data manager instance  
- `approval_manager`: Optional approval data manager instance

**Functionality**:
- Stores references to all data managers
- Creates tool providers for each domain:
  - `InventoryAgentToolProvider` for inventory operations
  - `FleetAgentToolProvider` for fleet/AGV operations
  - `ApprovalAgentToolProvider` for approval workflows
- Extracts tools from providers if managers are available, otherwise creates empty tool lists
- Ensures graceful handling when managers are not provided

### `create_ollama_model` Static Method

```python
@staticmethod
def create_ollama_model(
    host: str = "http://localhost:11434",
    model_id: str = "qwen2.5:7b"
):
```

**Purpose**: Static factory method for creating standardized Ollama model instances.

**Parameters**:
- `host`: Ollama server host URL (defaults to localhost:11434)
- `model_id`: Model identifier to use (defaults to "qwen2.5:7b")

**Returns**: Configured `OllamaModel` instance

**Functionality**:
- Creates a standardized Ollama model with consistent configuration
- Provides sensible defaults for local development
- Can be customized for different deployment environments
- Static method allows usage without factory instance

### `create_agent` Function

```python
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
```

**Purpose**: Creates specialized logistics agents with domain-specific configurations and tools.

**Parameters**:
- `agent_type`: Type of agent ("inventory", "fleet", "approver"/"approval", "orchestrator")
- `name`: Unique name for the agent instance
- `ollama_model`: Optional pre-configured Ollama model (creates one if not provided)
- `custom_prompt`: Optional custom system prompt (uses default if not provided)
- `enable_a2a`: Whether to enable agent-to-agent communication (default: True)
- `host`: Ollama server host for model creation
- `model_id`: Model identifier for model creation

**Returns**: Configured `GenericAgent` instance

**Functionality**:

1. **Model Creation**: Creates Ollama model if not provided using specified host and model_id
2. **Prompt Selection**: Uses custom prompt or calls `_get_system_prompt()` for default
3. **Domain-Specific Tool Assignment**:
   - **Inventory Agent**: Gets only inventory tools + inventory-specific prompt enhancement
   - **Fleet Agent**: Gets only fleet tools + fleet-specific prompt enhancement
   - **Approval Agent**: Gets only approval tools + approval-specific prompt enhancement
   - **Orchestrator Agent**: Gets ALL tools + orchestrator-specific prompt enhancement
   - **Unknown Types**: Defaults to orchestrator configuration with warning
4. **Agent Creation**: Creates `GenericAgent` with all configured parameters
5. **Prompt Enhancement**: Adds domain-specific instructions to enforce specialization

**Key Design Features**:
- **Domain Isolation**: Each agent type gets only relevant tools
- **Tool Usage Guidelines**: Prompts include instructions for efficient tool usage
- **Fallback Handling**: Unknown agent types default to orchestrator configuration
- **Flexibility**: Supports custom prompts and models while providing sensible defaults

### `_get_system_prompt` Function

```python
def _get_system_prompt(self, agent_type: str) -> str:
```

**Purpose**: Private method that provides default system prompts for different agent types.

**Parameters**:
- `agent_type`: The type of agent requiring a system prompt

**Returns**: Default system prompt string for the specified agent type

**Functionality**:
- **Inventory Agent**: Returns prompt focused on stock levels and warehouse operations
- **Fleet Agent**: Returns prompt focused on AGV scheduling and route optimization
- **Approval Agent**: Returns prompt focused on request validation and compliance checking
- **Default/Orchestrator**: Returns prompt for multi-agent logistics coordination

**Design Note**: These are base prompts that get enhanced with domain-specific instructions in `create_agent()`.

### `initialize_agent_factory` Function

```python
def initialize_agent_factory(inventory_manager, fleet_manager, approval_manager):
```

**Purpose**: Convenience function for initializing the agent factory with all data managers and providing setup confirmation.

**Parameters**:
- `inventory_manager`: Inventory data manager instance
- `fleet_manager`: Fleet data manager instance
- `approval_manager`: Approval data manager instance

**Returns**: Configured `AgentFactory` instance

**Functionality**:
1. **Factory Creation**: Creates `AgentFactory` with all provided managers
2. **Setup Confirmation**: Prints detailed information about tool assignment:
   - Number of tools available for each agent type
   - Confirmation of domain-specific tool isolation
   - Total tools available to orchestrator
3. **Validation**: Provides immediate feedback about successful initialization

## Agent Type Specifications

### Inventory Agent
- **Tools**: Only inventory management tools
- **Specialization**: Stock levels, warehouse operations, inventory tracking
- **Restrictions**: Cannot access fleet or approval tools

### Fleet Agent  
- **Tools**: Only fleet management tools
- **Specialization**: AGV scheduling, route optimization, transportation
- **Restrictions**: Cannot access inventory or approval tools

### Approval Agent
- **Tools**: Only approval workflow tools
- **Specialization**: Request validation, compliance checking, authorization
- **Restrictions**: Cannot access inventory or fleet tools

### Orchestrator Agent
- **Tools**: ALL available tools (inventory + fleet + approval)
- **Specialization**: Cross-domain coordination, workflow orchestration
- **Capabilities**: Can coordinate complex multi-domain operations

## Usage Example

```python
from agent_factory import AgentFactory, initialize_agent_factory

# Initialize with data managers
factory = initialize_agent_factory(
    inventory_manager=inv_manager,
    fleet_manager=fleet_manager,
    approval_manager=approval_manager
)

# Create domain-specific agents
inventory_agent = factory.create_agent(
    agent_type="inventory",
    name="WarehouseBot",
    model_id="qwen2.5:7b"
)

fleet_agent = factory.create_agent(
    agent_type="fleet", 
    name="TransportCoordinator",
    custom_prompt="You are an advanced AGV fleet manager..."
)

# Create orchestrator with all capabilities
orchestrator = factory.create_agent(
    agent_type="orchestrator",
    name="LogisticsOrchestrator"
)

# Use agents
response = inventory_agent.send_message("Check stock levels for item ABC123")
```

## Key Design Benefits

1. **Domain Isolation**: Prevents agents from accessing irrelevant tools
2. **Centralized Configuration**: Single point for agent creation and setup
3. **Flexible Customization**: Supports custom prompts, models, and configurations
4. **Scalable Architecture**: Easy to add new agent types and tools
5. **Development-Friendly**: Provides clear feedback and sensible defaults
6. **Production-Ready**: Handles missing dependencies and error conditions gracefully

## Integration with Logistics System

The `AgentFactory` serves as the backbone of the multi-agent logistics system by:
- Ensuring proper tool distribution across agent types
- Maintaining domain boundaries and responsibilities
- Providing consistent agent configuration and initialization
- Supporting both specialized agents and orchestrator patterns
- Enabling flexible deployment scenarios with optional components