# Logistics Multi-Agent System with Strands Framework

A sophisticated multi-agent logistics orchestration system built using the Strands AI framework, featuring specialized agents for inventory management, fleet operations, approval workflows, and intelligent coordination.

## 🚀 Overview

This system demonstrates advanced multi-agent coordination in logistics operations, where specialized AI agents work together to handle complex supply chain tasks autonomously. Each agent has domain-specific tools and capabilities while maintaining the ability to communicate with other agents through Agent-to-Agent (A2A) communication.

## 🏗️ Architecture

```
├── Agents/                     # Main application directory
│   ├── generic_agent.py       # Enhanced GenericAgent wrapper class
│   ├── agent_factory.py       # AgentFactory for creating specialized agents
│   ├── data_setup.py          # Initial data setup and DataFrames
│   ├── main.py               # Main execution script
│   ├── requirements.py       # Dependencies and imports
│   ├── data/                 # Data management modules
│   │   ├── inventory_data.py
│   │   ├── fleet_data.py
│   │   └── approver_data.py
│   ├── data_providers/       # Data provider classes
│   │   ├── inventory_data_provider.py
│   │   ├── fleet_data_provider.py
│   │   └── approval_data_provider.py
│   └── tool_providers/       # Strands tool wrapper classes
│       ├── inventory_tools.py
│       ├── fleet_tools.py
│       └── approval_tools.py
├── docs/                    # Comprehensive documentation
│   ├── configuration_system.md
│   ├── configuration_reference.md
│   ├── configuration_examples.md
│   └── configuration_implementation.md
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_agents.py      # Comprehensive test suite
│   └── run_tests.py        # Test runner script
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
- qwen2.5:7b model pulled in Ollama

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
cd Agents
pip install -r requirements.py
```

3. **Start Ollama:**
```bash
ollama serve
ollama pull qwen2.5:7b
```

### Running the System

```bash
cd Agents
python main.py
```

## 📊 Usage Examples

### Basic Agent Creation
```python
from agent_factory import AgentFactory, initialize_agent_factory
from data_setup import setup_all_data_managers

# Initialize data managers and factory
inv_mgr, fleet_mgr, approval_mgr = setup_all_data_managers()
factory = initialize_agent_factory(inv_mgr, fleet_mgr, approval_mgr)

# Create specialized agents
inventory_agent = factory.create_agent("inventory", "WarehouseBot")
fleet_agent = factory.create_agent("fleet", "FleetCoordinator")
orchestrator = factory.create_agent("orchestrator", "MasterCoordinator")

# Use agents
response = inventory_agent.send_message("Check stock levels for HYDRAULIC-PUMP-HP450")
```

### Multi-Agent Coordination
```python
# Complex workflow through orchestrator
complex_task = """
Process production order:
- 30 units of HYDRAULIC-PUMP-HP450
- Transport from warehouse to Production Line A  
- Handle $7,350 approval workflow
- Coordinate complete operation
"""

response = orchestrator.send_message(complex_task)
```

The system provides transparent tool execution tracking showing which agent executes which tools in sequence.

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

- **Domain-Specific Intelligence**: Each agent specializes in specific logistics domains
- **Intelligent Orchestration**: Cross-domain workflow coordination
- **Agent-to-Agent Communication**: Built-in A2A discovery and messaging
- **Production-Ready**: Modular design with comprehensive error handling
- **Real-Time Operations**: Live inventory, fleet, and approval management

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
1. **Ollama Connection**: Ensure `ollama serve` is running and `qwen2.5:7b` is pulled
2. **Import Errors**: Activate virtual environment and install dependencies
3. **Tool Failures**: Check JSON serialization and parameter validation

### Success Indicators
- ✅ All 4 agent types created successfully
- ✅ Domain-specific tool assignment working
- ✅ Tool execution tracking with agent names
- ✅ Complex multi-domain workflows completing
- ✅ Real-time logistics operations functioning

---

**The system is production-ready for autonomous logistics operations!** 🚀

For detailed documentation on individual components and future enhancements, see the linked guides above.