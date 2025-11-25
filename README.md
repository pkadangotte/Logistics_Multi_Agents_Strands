# Logistics Multi-Agent System with Strands Framework

A sophisticated multi-agent logistics orchestration system built using the Strands AI framework, featuring specialized agents for inventory management, fleet operations, approval workflows, and intelligent coordination with a beautiful Rich-powered interactive demo interface.

## 🚀 Overview

This system demonstrates advanced multi-agent coordination in logistics operations, where specialized AI agents work together to handle complex supply chain tasks autonomously. Each agent has domain-specific tools and capabilities, providing real-time orchestration with an elegant terminal UI showcasing planning, execution, and results.

## ✨ Key Highlights

- 🎨 **Beautiful Terminal UI** - Rich-powered interface with animated spinners, color-coded tables, and formatted panels
- 🤖 **4 Specialized Agents** - Inventory (8 tools), Fleet (7 tools), Approval (6 tools), Orchestrator (21 tools)
- 📊 **Transparent Execution** - 3-phase responses showing Planning → Execution → Summary with tool results
- ⏱️ **Real-Time Metrics** - Delivery time estimation, distance calculation, cost tracking, reservation management
- 🔄 **Complete Workflows** - End-to-end orchestration from inventory check to AGV dispatch with approval handling
- 🚀 **Performance Optimized** - Directive-focused prompts, constrained tool calls (4-7 per workflow), fast qwen2.5:3b model

## 🏗️ Architecture

```
├── Agents/                     # Core application modules
│   ├── generic_agent.py       # Enhanced GenericAgent with Rich spinner animation
│   ├── agent_factory.py       # AgentFactory with optimized prompts
│   ├── data_setup.py          # Initial data setup and DataFrames
│   ├── data/                 # Data management modules
│   │   ├── inventory_data.py
│   │   ├── fleet_data.py
│   │   └── approver_data.py
│   ├── data_providers/       # Data provider classes with metrics
│   │   ├── inventory_data_provider.py  # Self-documenting responses
│   │   ├── fleet_data_provider.py      # Time/distance calculation
│   │   └── approval_data_provider.py
│   └── tool_providers/       # Strands tool wrappers (optimized docstrings)
│       ├── inventory_tools.py   # 8 tools
│       ├── fleet_tools.py       # 7 tools
│       └── approval_tools.py    # 6 tools
├── docs/                    # Comprehensive documentation
│   ├── configuration_system.md
│   ├── configuration_reference.md
│   ├── configuration_examples.md
│   └── configuration_implementation.md
├── tests/                   # Test suite
│   ├── test_agent_creation.py
│   ├── test_inventory_agent.py
│   ├── test_fleet_agent.py
│   ├── test_approval_agent.py
│   └── test_orchestration.py
├── demo.py                  # Interactive Rich-powered demo interface
├── main.py                  # Main application entry point
├── requirements.txt         # Python dependencies (includes Rich)
└── README.md               # This file
```

## 🤖 Agent Architecture

### Agent Types

1. **📦 Inventory Agent** - Manages inventory operations (8 tools)
   - Stock checking, reservations, low-stock alerts, inventory transfers

2. **🚛 Fleet Agent** - Manages AGV fleet operations (7 tools)  
   - AGV optimization, dispatching, route planning, battery monitoring

3. **⚖️ Approval Agent** - Handles approval workflows (6 tools)
   - Threshold checking, compliance validation, approval processing

4. **🎯 Orchestrator Agent** - Coordinates multi-domain operations (21 tools)
   - Cross-domain coordination, complex workflow orchestration

### Core Classes

#### GenericAgent Class
Enhanced wrapper for Strands agents with additional functionality:
- Domain-specific tool assignment and A2A communication
- Enhanced logging with agent identification
- Robust error handling and system state restoration

> 📖 **Detailed Documentation**: [Generic Agent Guide](Agents/generic_agent.md)

#### AgentFactory Class  
Centralized factory for creating specialized logistics agents:
- Domain-specific tool selection and model configuration
- Standardized agent creation with proper specialization
- Support for custom prompts and configurations

> 📖 **Detailed Documentation**: [Agent Factory Guide](Agents/agent_factory.md)

## 🛠️ System Components

### Data Providers
- **InventoryDataProvider**: Manages inventory data and operations
- **FleetDataProvider**: Handles AGV fleet and route management  
- **ApprovalDataProvider**: Manages approval workflows and thresholds

### Tool Providers
Each data provider is wrapped by a tool provider that exposes functionality as Strands tools:
- **InventoryAgentToolProvider**: 8 inventory management tools
- **FleetAgentToolProvider**: 7 fleet coordination tools  
- **ApprovalAgentToolProvider**: 6 approval workflow tools

## 🚦 Getting Started

### Prerequisites
- Python 3.8+
- Ollama server running on localhost:11434  
- qwen2.5:3b model (default, fast) or qwen2.5:7b model (more powerful)

### Installation

1. **Clone and setup:**
```bash
git clone <repository-url>
cd Logistics_Multi_Agents_Strands
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start Ollama and pull model:**
```bash
ollama serve
ollama pull qwen2.5:3b  # Fast model (default)
# OR
ollama pull qwen2.5:7b  # More powerful model
```

### Running the Interactive Demo

The recommended way to experience the system:

```bash
./run_demo.sh
# OR
python demo.py
```

**Demo Features:**
- 📋 **16 Example Queries** across all agent types (inventory, fleet, approval, orchestration)
- 🎨 **Beautiful Tables** showing inventory, AGV fleet, and approval workflows
- 💭 **Animated Spinner** with "Thinking..." indicator during agent processing
- 📝 **Query Display** showing what's being processed
- 🎯 **Structured Responses** with Planning, Execution, and Summary phases
- 🔧 **Interactive Controls**:
  - `1-16`: Run predefined example queries
  - `100`: Enter custom query
  - `200`: Toggle streaming mode
  - `300`: Switch between models (qwen2.5:3b ↔ qwen2.5:7b)
  - `400`: Quit demo

**Example Demo Flow:**
1. Select option `12` - Emergency production parts delivery
2. Watch animated spinner: `💭 Thinking... ⠋`
3. See detailed response with:
   - ✿ Planning Phase: Task analysis and required actions
   - ✿ Execution Phase: Each tool result (availability, reservation, approval, AGV selection, dispatch)
   - ✿ Summary: Results with delivery time (4 minutes), distance (150m), cost, and IDs

### Running Tests

```bash
pytest tests/
# OR
python -m pytest tests/ -v
```

## 📊 Usage Examples

### Interactive Demo (Recommended)
```bash
python demo.py
```
Select from 16 pre-configured queries or create your own. See beautiful formatted output with planning, execution, and summary phases.

### Programmatic Usage

#### Basic Agent Creation
```python
from agent_factory import initialize_agent_factory
from data_setup import initialize_dataframes
from data_providers.inventory_data_provider import InventoryDataProvider
from data_providers.fleet_data_provider import FleetDataProvider
from data_providers.approval_data_provider import ApprovalDataProvider

# Initialize data
inventory_df, agv_df, routes_df, approval_df = initialize_dataframes()

# Create data providers
inventory_mgr = InventoryDataProvider(inventory_df)
fleet_mgr = FleetDataProvider(agv_df, routes_df)
approval_mgr = ApprovalDataProvider(approval_df)

# Initialize factory
factory = initialize_agent_factory(inventory_mgr, fleet_mgr, approval_mgr)

# Create specialized agents
inventory_agent = factory.create_agent("inventory", "WarehouseBot")
fleet_agent = factory.create_agent("fleet", "FleetCoordinator")
orchestrator = factory.create_agent("orchestrator", "MasterCoordinator")

# Use agents
response = inventory_agent.send_message(
    "Check stock levels for HYDRAULIC-PUMP-HP450",
    streaming=True
)
print(response)
```

### Multi-Agent Orchestration
```python
# Complex end-to-end workflow
complex_task = """
URGENT: Need to deliver 50 units of PART-ABC123 to Production Line A.
Get approvals and dispatch the fastest available AGV.
"""

response = orchestrator.send_message(complex_task, streaming=True)

# Response includes:
# ✿ Planning Phase: Lists tools needed (4-7 tools)
# ✿ Execution Phase: Shows each tool result
#   ✓ check_availability → Found: 85 units at Warehouse A
#   ✓ reserve_parts → Reserved 50 units, ID: 5
#   ✓ check_approval_threshold → No approval needed ($625 < $1000)
#   ✓ find_optimal_agv → Selected AGV-002 (50 pcs capacity, 92% battery)
#   ✓ dispatch_agv → Success, ID: 1, time: 4 min, distance: 150m
# ✿ Summary: Complete details with metrics
```

### Model Switching
```python
# Create agent with specific model
fast_agent = factory.create_agent(
    "orchestrator", 
    "FastBot",
    model_id="qwen2.5:3b"
)

powerful_agent = factory.create_agent(
    "orchestrator",
    "PowerBot", 
    model_id="qwen2.5:7b"
)
```

## 🧪 Testing

Run comprehensive tests:
```bash
# Option 1: Using the test runner
python tests/run_tests.py

# Option 2: Direct execution  
cd tests && python test_agents.py

# Option 3: From Python
python -c "
import sys; sys.path.append('Agents')
from agent_factory import initialize_agent_factory
from data_setup import setup_all_data_managers  
from tests.test_agents import main_enhanced_testing

inv_mgr, fleet_mgr, approval_mgr = setup_all_data_managers()
factory = initialize_agent_factory(inv_mgr, fleet_mgr, approval_mgr)
main_enhanced_testing(factory)
"
```

## 🎯 Key Features

### User Experience
- 🎨 **Rich Terminal UI** - Professional tables, animated spinners, color-coded output
- 📊 **Transparent Execution** - See planning, tool execution, and results in real-time
- 💭 **Visual Feedback** - Animated "Thinking..." spinner during processing
- 🎯 **Structured Responses** - Mandatory 3-phase format (Planning → Execution → Summary)

### Agent Intelligence
- 🤖 **Domain Specialization** - Each agent focuses on specific logistics domains
- 🔄 **Smart Orchestration** - Cross-domain workflow coordination with 4-7 tool calls
- 📍 **Location Validation** - Exact location name handling with self-documenting hints
- ⏱️ **Real-Time Metrics** - Delivery time estimation, distance calculation, cost tracking

### Operational Excellence
- 🚀 **Performance Optimized** - 80-90% shorter tool docstrings, directive-focused prompts
- 🔒 **Workflow Constraints** - Maximum 10 tools per request, no duplicate calls
- 📦 **Complete Workflows** - Availability → Reservation → Approval → AGV → Dispatch
- 📈 **Self-Documenting** - Tool responses include usage hints for next steps

### Data & Metrics
- ⏱️ **Time Estimation** - Accurate delivery time from route data (e.g., 4 minutes)
- 📏 **Distance Tracking** - Precise distance in meters (e.g., 150m)
- 💰 **Cost Calculation** - Estimated costs per trip (e.g., $3.50)
- 🔢 **ID Tracking** - Dispatch IDs, reservation IDs, approval request IDs

## 🔧 Configuration

### Current Implementation
- Programmatic agent creation through `AgentFactory`
- Default Ollama configuration (qwen2.5:7b, localhost:11434)
- Domain-specific system prompts for each agent type

### Future Enhancement: Configuration-Driven System
A comprehensive YAML-based configuration system is planned to make the system accessible to non-programmers.

> 📖 **Detailed Documentation**: 
> - [Configuration System Overview](docs/configuration_system.md)
> - [Configuration Reference Guide](docs/configuration_reference.md) 
> - [Configuration Examples](docs/configuration_examples.md)
> - [Implementation Guide](docs/configuration_implementation.md)

## 🚧 Extension Points

- **New Agent Types**: Add data managers, tool providers, and factory configuration
- **New Tools**: Extend existing providers with `@tool` decorators
- **Custom Workflows**: Orchestrator handles complex multi-domain operations

## 📈 Performance & Security

- **Optimized**: Efficient qwen2.5:7b model with pandas DataFrames
- **Secure**: Domain-specific tool isolation and approval workflows  
- **Auditable**: Complete logging of tool executions and decisions

## 🆘 Troubleshooting

### Common Issues

**1. No animation showing**
- The spinner should animate smoothly: `💭 Thinking... ⠋⠙⠹⠸`
- If stuck, ensure Rich is installed: `pip install rich>=13.0.0`

**2. Ollama Connection Issues**
```bash
# Ensure Ollama is running
ollama serve

# Verify model is available
ollama list

# Pull if needed
ollama pull qwen2.5:3b
```

**3. Missing Delivery Metrics**
- Ensure you're running latest code with route time/distance calculation
- Check that `dispatch_agv` response includes `estimated_time_minutes` and `distance_m`

**4. Agent Not Following 3-Phase Format**
- System prompts enforce Planning → Execution → Summary structure
- If missing phases, try switching to qwen2.5:7b model (option 300 in demo)

**5. Too Many Tool Calls**
- Expected: 4-7 tools per workflow
- If seeing 10+, check system prompts have latest constraints
- Verify tools have directive-focused docstrings

### Success Indicators
- ✅ Animated spinner shows during processing
- ✅ All 3 phases (Planning, Execution, Summary) appear in response
- ✅ Delivery summaries include time (minutes) and distance (meters)
- ✅ Tool calls stay within 4-7 range for typical workflows
- ✅ Rich tables display properly with colors and formatting
- ✅ No duplicate tool calls with same parameters
- ✅ Parts are reserved before AGV dispatch

---

**The system is production-ready for autonomous logistics operations!** 🚀

For detailed documentation on individual components and future enhancements, see the linked guides above.