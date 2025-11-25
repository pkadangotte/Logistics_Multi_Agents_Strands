# Logistics Multi-Agent System with Strands Framework

A sophisticated multi-agent logistics orchestration system built using the Strands AI framework, featuring specialized agents for inventory management, fleet operations, approval workflows, and intelligent coordination.

## 🚀 **Overview**

This system demonstrates advanced multi-agent coordination in logistics operations, where specialized AI agents work together to handle complex supply chain tasks autonomously. Each agent has domain-specific tools and capabilities while maintaining the ability to communicate with other agents through Agent-to-Agent (A2A) communication.

## 🏗️ **Architecture**

```

├── .git/                    # Git version control
├── .venv/                   # Python virtual environment
├── agents/                  # Main application directory
│   ├── agents.py           # Agent factory and LogisticsAgent class
│   ├── approval_manager.py # Approval workflow management
│   ├── data_setup.py       # Initial data setup and DataFrames
│   ├── fleet_manager.py    # AGV fleet management
│   ├── inventory_manager.py# Inventory operations
│   ├── main.py            # Main execution script
│   ├── requirements.py     # Dependencies and imports
│   ├── test_agents.py      # Comprehensive test suite
│   └── tool_providers.py   # Strands tool wrapper classes
└── README.md               # This file
```

## 🤖 **Agent Architecture**

### **Agent Types**

1. **📦 SmartInventoryAgent** \- Manages inventory operations
    * Tools: 8 inventory-specific + 3 A2A tools = **11 total tools**
    * Capabilities: Part lookup, availability checking, reservations, stock analysis
2. **🚛 IntelligentFleetAgent** \- Manages AGV fleet operations
    * Tools: 7 fleet-specific + 3 A2A tools = **10 total tools**
    * Capabilities: AGV optimization, fleet status, route planning, dispatch
3. **⚖️ ComplianceApprovalAgent** \- Handles approval workflows
    * Tools: 6 approval-specific + 3 A2A tools = **9 total tools**
    * Capabilities: Threshold checking, compliance validation, approval processing
4. **🎯 MasterLogisticsOrchestrator** \- Coordinates multi\-domain operations
    * Tools: 21 combined + 3 A2A tools = **24 total tools**
    * Capabilities: Cross-domain coordination, complex workflow orchestration

### **LogisticsAgent Class**

The `LogisticsAgent` class is a wrapper around the Strands `Agent` that provides:

``` python
class LogisticsAgent:
    def __init__(
        self, 
        name: str,
        agent_type: str, 
        ollama_model,
        system_prompt: str,
        enable_a2a: bool = True,
        data_manager_tools: List = None
    ):
```

**Key Features:**

* **Domain-Specific Tool Assignment**: Each agent only gets tools relevant to their domain
* **A2A Communication**: Agents can discover and communicate with each other
* **Enhanced Logging**: Tool calls are tracked with agent names for transparency
* **JSON Serialization**: Handles pandas data type conversion for tool responses
* **Modular Design**: Easy to extend with new capabilities

### **AgentFactory Class**

The `AgentFactory` centralizes agent creation and configuration:

``` python
class AgentFactory:
    def __init__(
        self,
        inventory_manager=None,
        fleet_manager=None, 
        approval_manager=None
    ):
```

**Factory Methods:**

* `create_ollama_model()` \- Creates OllamaModel instances
* `create_agent()` \- Creates specialized LogisticsAgent instances
* `_get_system_prompt()` \- Provides domain\-specific prompts

**Agent Creation Process:**

1. **Tool Selection**: Factory assigns domain-specific tools based on agent type
2. **Model Creation**: OllamaModel configured with qwen2.5:7b and localhost:11434
3. **System Prompt**: Domain-specific prompts guide agent behavior
4. **A2A Integration**: Agent-to-Agent communication tools added if enabled
5. **Agent Instantiation**: Strands Agent created with proper configuration

## 🛠️ **Data Managers**

### **InventoryDataManager**

* Manages pandas DataFrame with inventory data
* Handles reservations and availability checks
* Provides real-time stock analysis
* JSON-serializable output for tool integration

### **FleetDataManager**

* Manages AGV fleet operations and routes
* Optimizes AGV selection based on efficiency algorithms
* Tracks dispatch status and fleet metrics
* Handles route planning and cost calculations

### **ApprovalDataManager**

* Manages approval thresholds and workflows
* Validates compliance requirements
* Tracks approval history and requests
* Automates approval routing based on cost thresholds

## 🔧 **Tool Providers**

Each data manager is wrapped by a corresponding tool provider that exposes functionality as Strands tools:

### **InventoryAgentToolProvider**

``` python
@tool(name="get_part_info")
@tool(name="check_availability") 
@tool(name="reserve_inventory")
@tool(name="release_reservation")
@tool(name="search_parts")
@tool(name="get_low_stock_items")
@tool(name="get_inventory_summary")
@tool(name="get_reservation_history")
```

### **FleetAgentToolProvider**

``` python
@tool(name="get_available_agvs")
@tool(name="find_optimal_agv")
@tool(name="dispatch_agv")
@tool(name="get_fleet_status")
@tool(name="get_route_info")
@tool(name="update_agv_status")
@tool(name="complete_task")
```

### **ApprovalAgentToolProvider**

``` python
@tool(name="check_approval_threshold")
@tool(name="create_approval_request")
@tool(name="process_approval")
@tool(name="check_compliance")
@tool(name="get_approval_history")
@tool(name="get_pending_approvals")
```

## 🚦 **Getting Started**

### **Prerequisites**

* Python 3.8+
* Ollama server running on localhost:11434
* qwen2.5:7b model pulled in Ollama

### **Installation**

1. **Clone the repository:**

``` bash
git clone <repository-url>
cd Logistics_Multi_Agents_Strands
```

2. **Set up virtual environment:**

``` bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**

``` bash
pip install pandas ollama strands-agents strands-tools
```

4. **Start Ollama server:**

``` bash
ollama serve
ollama pull qwen2.5:7b
```

### **Running the System**

1. **Execute the main application:**

``` bash
cd agents
python main.py
```

2. **Run individual components:**

``` bash
# Test only data setup
python data_setup.py

# Test specific managers
python -c "from inventory_manager import *; # your code here"
```

## 📊 **Usage Examples**

### **Creating Individual Agents**

``` python
from agents import AgentFactory
from data_setup import initialize_dataframes
from inventory_manager import InventoryDataManager

# Setup data
inventory_df, agv_df, routes_df, approval_df = initialize_dataframes()
inventory_manager = InventoryDataManager(inventory_df)

# Create factory
factory = AgentFactory(inventory_manager=inventory_manager)

# Create inventory agent
inventory_agent = factory.create_agent(
    agent_type="inventory",
    name="WarehouseAgent",
    enable_a2a=True
)

# Use the agent
response = inventory_agent.send_message(
    "Check availability for 10 units of PART-ABC123"
)
```

### **Multi-Agent Coordination**

``` python
# Create orchestrator with all capabilities
orchestrator = factory.create_agent(
    agent_type="orchestrator", 
    name="MasterCoordinator"
)

# Complex multi-domain request
complex_task = """
I need to process a production order:
- 30 units of HYDRAULIC-PUMP-HP450
- Transport from Central Warehouse to Production Line A
- Handle approvals for $7,350 total cost
- Coordinate the entire workflow
"""

response = orchestrator.send_message(complex_task)
```

## 🔍 **Tool Execution Tracking**

The system provides transparent tool execution tracking:

```
MasterLogisticsOrchestrator -> Tool #1: check_availability
MasterLogisticsOrchestrator -> Tool #2: find_optimal_agv
MasterLogisticsOrchestrator -> Tool #3: check_approval_threshold
MasterLogisticsOrchestrator -> Tool #4: reserve_inventory
MasterLogisticsOrchestrator -> Tool #5: dispatch_agv
```

Each tool call shows:

* **Agent Name**: Which agent is executing
* **Tool Number**: Sequential execution order
* **Tool Name**: Specific function being called

## 🧪 **Testing**

The system includes comprehensive tests in `test_agents.py`:

``` bash
cd agents
python test_agents.py
```

**Test Coverage:**

* ✅ Agent creation and configuration
* ✅ Individual agent functionality
* ✅ Multi-domain orchestration
* ✅ Tool execution and response validation
* ✅ A2A communication capabilities
* ✅ Error handling and edge cases

## 🎯 **Key Features**

### **Domain-Specific Intelligence**

* Each agent specializes in specific logistics domains
* Tools are carefully curated per agent type
* System prompts guide domain-specific behavior

### **Intelligent Orchestration**

* Orchestrator agent coordinates complex workflows
* Sequential tool execution with dependency awareness
* Real-time adaptation based on actual system state

### **Agent-to-Agent Communication**

* Built-in A2A discovery and messaging capabilities
* Agents can collaborate on complex tasks
* Transparent inter-agent communication tracking

### **Production-Ready Architecture**

* Modular design for easy extension
* Comprehensive error handling
* JSON serialization for API integration
* Transparent logging and monitoring

### **Real-Time Operations**

* Live inventory management
* Dynamic AGV fleet optimization
* Automated approval workflows
* Cost-aware decision making

## 🔧 **Configuration**

### **Model Configuration**

``` python
# Default Ollama configuration
OllamaModel(
    model_id="qwen2.5:7b",
    host="http://localhost:11434"
)
```

### **Agent Specialization**

Each agent type receives domain-specific system prompts:

* **Inventory**: "You are specialized in INVENTORY MANAGEMENT ONLY..."
* **Fleet**: "You are specialized in FLEET MANAGEMENT ONLY..."
* **Approval**: "You are specialized in APPROVAL WORKFLOWS ONLY..."
* **Orchestrator**: "As the Logistics Orchestrator, you have access to ALL management tools..."

## 🚧 **Extension Points**

### **Adding New Agent Types**

1. Create new data manager class
2. Implement corresponding tool provider
3. Add agent type to AgentFactory
4. Define domain-specific system prompt

### **Adding New Tools**

1. Add method to appropriate data manager
2. Wrap with `@tool` decorator in tool provider
3. Update tool assignment in AgentFactory
4. Add tests for new functionality

### **Custom Workflows**

The orchestrator agent can handle custom workflows by combining existing tools in intelligent sequences based on natural language requests.

## 📈 **Performance Considerations**

* **Tool Caching**: Strands framework provides built-in tool result caching
* **Model Optimization**: Uses efficient qwen2.5:7b model for fast responses
* **Data Management**: Pandas DataFrames for efficient data operations
* **Memory Management**: Proper cleanup and resource management

## 🔒 **Security & Compliance**

* **Approval Workflows**: Built-in approval thresholds and compliance checking
* **Tool Isolation**: Domain-specific tool access prevents unauthorized operations
* **Audit Trail**: Complete logging of all tool executions and decisions
* **Input Validation**: Robust parameter validation and error handling

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Ensure all existing tests pass
5. Submit a pull request with detailed description

## 📝 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Troubleshooting**

### **Common Issues**

1. **Ollama Connection Errors**

``` bash
# Ensure Ollama is running
ollama serve

# Check model availability
ollama list
```

2. **Import Errors**

``` bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Install missing dependencies
pip install strands-agents strands-tools
```

3. **Tool Execution Failures**
    * Check JSON serialization issues with pandas data types
    * Verify tool parameter types and validation
    * Review agent system prompts and tool assignments

## 🎉 **Success Metrics**

When properly configured, you should see:

* ✅ All 4 agent types created successfully
* ✅ Tool counts showing domain + A2A tools
* ✅ Successful tool executions with agent name tracking
* ✅ Complex multi-domain workflows completing successfully
* ✅ Real-time inventory, fleet, and approval operations

The system is production-ready for autonomous logistics operations! 🚀