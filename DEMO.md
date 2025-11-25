# 🎬 Logistics Multi-Agent System Demo

Interactive demonstration showcasing the complete agent orchestration system with predefined example queries and custom interaction capabilities.

## 🚀 Quick Start

### Option 1: Using the Launcher Script (Recommended)
```bash
./run_demo.sh
```

### Option 2: Direct Python Execution
```bash
# Using virtual environment
.venv/bin/python demo.py

# Or system Python
python3 demo.py
```

## 🎯 Demo Features

### 📦 **Real System Data**
The demo uses actual system data across all domains with realistic values and configurations:

#### **Inventory Data**
| Part Number | Available | Cost/Unit | Description | Location |
|-------------|-----------|-----------|-------------|----------|
| **HYDRAULIC-PUMP-HP450** | 24 units | $245.00 | Heavy-duty hydraulic pump | Central Warehouse |
| **PART-ABC123** | 85 units | $12.50 | Standard production part | Warehouse A |
| **PART-XYZ789** | 42 units | $18.75 | Specialized component | Warehouse B |
| **PART-DEF456** | 120 units | $8.25 | Common component | Warehouse A |

#### **AGV Fleet Data**
| AGV ID | Type | Capacity | Status | Battery | Cost/Trip |
|--------|------|----------|---------|---------|-----------|
| **AGV-001** | Heavy Duty | 100 pieces | AVAILABLE | 85% | $5.00 |
| **AGV-002** | Standard | 50 pieces | AVAILABLE | 92% | $3.50 |
| **AGV-003** | Heavy Duty | 100 pieces | AVAILABLE | 87% | $5.00 |
| **AGV-004** | Light Duty | 25 pieces | AVAILABLE | 82% | $2.50 |

#### **Approval Workflow Data**
| Level | Threshold | Approval Required | Auto-Process |
|-------|-----------|-------------------|--------------|
| **Low Value** | ≤ $1,000 | Auto-Approved | ✅ |
| **Medium Value** | $1,001 - $5,000 | Manager Required | 👨‍💼 |
| **High Value** | > $5,000 | Director Required | 👔 |

### 📋 **Predefined Example Queries**
The demo includes 16 carefully crafted example queries organized into 5 categories:

#### 🏭 **Inventory Management**
1. **Stock Overview** - Check current stock levels for all warehouse items
2. **Low Stock Alerts** - Find items needing replenishment  
3. **Hydraulic Pump Lookup** - Get detailed info for HYDRAULIC-PUMP-HP450 (24 units, $245 each)
3a. **Multi-Part Check** - Check PART-ABC123 and PART-DEF456 status

#### 🚛 **Fleet Management** 
4. **Fleet Status** - Show AGV status and current assignments
5. **Hydraulic Equipment Route** - Route from Central Warehouse to Manufacturing Plant Delta
6. **Urgent Production Delivery** - Assign AGV for 50 units of PART-ABC123

#### ✅ **Approval Workflows**
7. **Approval Queue** - Show pending approval requests
8. **High-Value Hydraulic Approval** - Process $4,900 HYDRAULIC-PUMP-HP450 shipment
9. **High-Value Audit Trail** - Check approval history for orders >$1,000

#### 🎯 **Complex Orchestration**
10. **Hydraulic Pump Delivery** - 15 units of HYDRAULIC-PUMP-HP450 ($3,675) end-to-end workflow
11. **Emergency Production Parts** - Urgent 50-unit PART-ABC123 delivery from Warehouse A  
12. **Inter-Warehouse Transfer** - 25 units of PART-DEF456 transfer ($206.25)

#### 🔄 **Cross-Agent Communication**
13. **Large PART-XYZ789 Order** - 30 units requested (42 available) with vehicle coordination
14. **High-Value Multi-Agent** - $4,900 HYDRAULIC-PUMP-HP450 approval + fleet workflow
15. **Complete System Analysis** - Full inventory status + fleet + approvals optimization

### 💬 **Custom Query Mode**
- Enter your own natural language queries
- Choose which agent type to handle your request
- Explore system capabilities beyond predefined examples

### 🤖 **Agent Types Available**
- **📦 Inventory Agent** - Specialized in inventory management
- **🚛 Fleet Agent** - Handles AGV and transportation operations  
- **✅ Approval Agent** - Manages approval workflows and compliance
- **🎯 Orchestrator Agent** - Coordinates multi-domain operations

## 🎮 How to Use

### 1. **Start the Demo**
```bash
./run_demo.sh
```

### 2. **System Initialization**
The demo will automatically:
- Initialize all data providers (inventory, fleet, approval)
- Create all four agent types
- Display system status and available options

### 3. **Choose Your Experience**
- **Select 1-15**: Run predefined example queries
- **Select C**: Enter custom queries with agent selection
- **Select Q**: Exit the demo

### 4. **Interact with Responses**
- Review detailed agent responses
- Press Enter to continue to the next interaction
- Use Ctrl+C to interrupt and return to menu

## 📊 Example Interaction Flow

```
🏭 LOGISTICS MULTI-AGENT SYSTEM DEMO
=====================================
Experience the power of AI-driven logistics orchestration!

📊 AGENT STATUS
🤖 INVENTORY     | DemoInventoryAgent       | 11 tools
🤖 FLEET         | DemoFleetAgent          | 10 tools  
🤖 APPROVAL      | DemoApprovalAgent       | 9 tools
🤖 ORCHESTRATOR  | DemoOrchestratorAgent   | 24 tools

📦 CURRENT INVENTORY SNAPSHOT
📋 HYDRAULIC-PUMP-HP450 |  24 units |  $245.00 | Heavy-duty hydraulic pump
📋 PART-ABC123          |  85 units |   $12.50 | Standard production part
📋 PART-XYZ789          |  42 units |   $18.75 | Specialized component
📋 PART-DEF456          | 120 units |    $8.25 | Common component

🚛 CURRENT AGV FLEET SNAPSHOT  
🤖 AGV-001 | Heavy Duty  | 100 pcs | AVAILABLE | 85% | $5.00
🤖 AGV-002 | Standard    |  50 pcs | AVAILABLE | 92% | $3.50
🤖 AGV-003 | Heavy Duty  | 100 pcs | AVAILABLE | 87% | $5.00
🤖 AGV-004 | Light Duty  |  25 pcs | AVAILABLE | 82% | $2.50

✅ CURRENT APPROVAL WORKFLOW SNAPSHOT
✅ Low Value    | ≤ $1,000        | Auto-Approved
👨‍💼 Medium Value | $1,001 - $5,000 | Manager Required  
👔 High Value   | > $5,000        | Director Required

📋 EXAMPLE QUERIES
🏭 Inventory Management
  1. 📦 Basic inventory overview
  2. 📦 Low stock alert system
  3. 📦 Specific item lookup

🚛 Fleet Management  
  4. 🚛 Fleet status overview
  5. 🚛 Route optimization
  6. 🚛 Vehicle assignment

🎯 Select option: 10

🤖 Executing with ORCHESTRATOR agent...
📝 Query: I need to deliver 100 units of SKU001 to customer location XYZ...

🎯 AGENT RESPONSE
============================================================
[Agent provides comprehensive delivery coordination response]
============================================================
```

## 🔧 Prerequisites

### Required Dependencies
```bash
pip install -r requirements.txt
```

### Ollama Setup
1. **Install Ollama** (if not already installed)
2. **Start Ollama server**:
   ```bash
   ollama serve
   ```
3. **Pull required model**:
   ```bash
   ollama pull qwen2.5:7b
   ```

### Directory Structure
Ensure you're running from the project root directory with this structure:
```
Logistics_Multi_Agents_Strands/
├── demo.py                 # Main demo script
├── run_demo.sh            # Launcher script  
├── Agents/                # Agent system code
│   ├── agent_factory.py
│   ├── data_setup.py
│   └── ...
└── requirements.txt
```

## 🎯 Demo Scenarios

### **Beginner Scenarios**
- Start with queries 1-3 (Inventory) to understand basic agent interactions
- Try queries 4-6 (Fleet) to see specialized agent capabilities
- Explore queries 7-9 (Approval) for workflow management

### **Advanced Scenarios**  
- Use queries 10-12 (Orchestration) for complex multi-agent workflows
- Try queries 13-15 (Cross-Agent) for advanced coordination
- Use Custom mode (C) to test your own logistics scenarios

### **System Testing**
- Test error handling with invalid requests
- Explore agent specialization boundaries  
- Verify multi-agent communication and coordination

## 🔍 Troubleshooting

### Common Issues

#### Demo Won't Start
```bash
❌ Error: Please run this script from the project root directory
```
**Solution**: Navigate to the project root where `Agents/` directory exists

#### Import Errors
```bash
❌ ModuleNotFoundError: No module named 'strands'
```
**Solution**: Install dependencies: `pip install -r requirements.txt`

#### Agent Creation Failures
```bash  
❌ Error initializing system: Connection refused
```
**Solution**: Start Ollama server: `ollama serve`

#### Model Not Available
```bash
❌ Model not found: qwen2.5:7b
```
**Solution**: Pull the model: `ollama pull qwen2.5:7b`

### Debug Mode
For detailed debugging, run with verbose output:
```bash
PYTHONPATH=./Agents python3 demo.py
```

## 🎓 Learning Objectives

After using this demo, you'll understand:

1. **Agent Specialization** - How different agents handle domain-specific tasks
2. **Multi-Agent Orchestration** - How complex workflows span multiple agents  
3. **Natural Language Processing** - How agents interpret and respond to queries
4. **System Integration** - How data flows between agents and providers
5. **Error Handling** - How the system gracefully handles edge cases
6. **Scalability Patterns** - How the architecture supports complex logistics operations

## 📚 Related Documentation

- **[Agent Factory Documentation](Agents/agent_factory.md)** - Understanding agent creation
- **[Generic Agent Documentation](Agents/generic_agent.md)** - Core agent functionality  
- **[Configuration System](docs/)** - Future YAML-based configuration
- **[Testing Guide](tests/README.md)** - Running tests and validation

## 🚀 Next Steps

After exploring the demo:

1. **Customize Agents** - Modify prompts and tool assignments
2. **Add New Domains** - Create agents for other business areas
3. **Implement YAML Config** - Use the planned configuration system
4. **Scale Production** - Deploy with proper infrastructure
5. **Integrate APIs** - Connect to real logistics systems

---

**🎉 Enjoy exploring the Logistics Multi-Agent System!**