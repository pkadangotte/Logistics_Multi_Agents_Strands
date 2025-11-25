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
4. **Multi-Part Check** - Check PART-ABC123 and PART-DEF456 status

#### 🚛 **Fleet Management** 
5. **Fleet Status** - Show AGV status and current assignments
6. **Hydraulic Equipment Route** - Route from Central Warehouse to Manufacturing Plant Delta
7. **Urgent Production Delivery** - Assign AGV for 50 units of PART-ABC123

#### ✅ **Approval Workflows**
8. **Approval Queue** - Show pending approval requests
9. **High-Value Hydraulic Approval** - Process $4,900 HYDRAULIC-PUMP-HP450 shipment
10. **High-Value Audit Trail** - Check approval history for orders >$1,000

#### 🎯 **Complex Orchestration**
11. **Hydraulic Pump Delivery** - 15 units of HYDRAULIC-PUMP-HP450 ($3,675) end-to-end workflow
12. **Emergency Production Parts** - Urgent 50-unit PART-ABC123 delivery from Warehouse A  
13. **Inter-Warehouse Transfer** - 30 units of PART-XYZ789 to Production Line B

#### 🔄 **Cross-Agent Communication**
14. **Large Order Coordination** - 25 units of PART-DEF456 to Manufacturing Plant Delta
15. **High-Value Multi-Agent** - 20 units HYDRAULIC-PUMP-HP450 ($4,900) approval + fleet workflow
16. **Complete System Analysis** - Full inventory status + fleet + approvals optimization

### 🎨 **Rich Terminal UI Features**
- 💭 **Animated Spinner** - Beautiful "Thinking..." animation with braille characters during processing
- 📊 **Formatted Tables** - Color-coded agent status, inventory, fleet, and approval data
- 🎯 **Structured Responses** - 3-phase format (Planning → Execution → Summary) in elegant panels
- 📝 **Query Display** - See exactly what's being processed before agent responds

### 🔧 **Interactive Controls**
- **1-16**: Run predefined example queries
- **100**: Custom query mode - enter your own queries with agent selection
- **200**: Toggle streaming mode on/off
- **300**: Switch between models (qwen2.5:3b ↔ qwen2.5:7b)
- **400**: Quit demo

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
- **Select 1-16**: Run predefined example queries
- **Select 100**: Enter custom queries with agent selection
- **Select 200**: Toggle streaming mode (animated spinner)
- **Select 300**: Switch AI model (fast 3b ↔ powerful 7b)
- **Select 400**: Exit the demo

### 4. **Interact with Responses**
- Watch animated "💭 Thinking..." spinner during processing
- Review detailed 3-phase agent responses:
  - ✿ Planning Phase: Task analysis and required actions
  - ✿ Execution Phase: Each tool result with real data
  - ✿ Summary: Complete details with metrics (time, distance, cost, IDs)
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
  1. 📦 Stock overview
  2. 📦 Low stock alerts
  3. 📦 Hydraulic pump lookup
  4. 📦 Multi-part check

🚛 Fleet Management  
  5. 🚛 Fleet status
  6. 🚛 Route optimization
  7. 🚛 Urgent delivery

✅ Approval Workflows
  8. ✅ Approval queue
  9. ✅ High-value approval
  10. ✅ Audit trail

🎯 Complex Orchestration
  11. 🎯 Hydraulic pump delivery
  12. 🎯 Emergency parts
  13. 🎯 Warehouse transfer

🔄 Cross-Agent Communication
  14. 🔄 Large order coordination
  15. 🔄 High-value multi-agent
  16. 🔄 System optimization

  100. 💬 Custom query
  200. ⚡ Toggle streaming (ON)
  300. 🎮 Switch model (qwen2.5:3b)
  400. 🚪 Quit

🎯 Select option: 12

📝 Query: URGENT: Need to deliver 50 units of PART-ABC123...

💭 Thinking... ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏

╭─ 🎯 Agent Response ─────────────────────────────────╮
│                                                     │
│ ═══════════════════════════════════════════════════ │
│ ✿ PLANNING PHASE:                                  │
│ ═══════════════════════════════════════════════════ │
│ 📋 Task: Urgent 50-unit delivery of PART-ABC123    │
│ 🎯 Actions: 5 tools (availability, reserve,        │
│            approval check, find AGV, dispatch)      │
│                                                     │
│ ═══════════════════════════════════════════════════ │
│ ✿ EXECUTION PHASE:                                 │
│ ═══════════════════════════════════════════════════ │
│ ✓ check_availability → 85 units at Warehouse A     │
│ ✓ reserve_parts → Reserved 50 units, ID: 7         │
│ ✓ check_approval_threshold → Auto-approved ($625)  │
│ ✓ find_optimal_agv → AGV-002 selected              │
│ ✓ dispatch_agv → Success, time: 4 min, 150m        │
│                                                     │
│ ═══════════════════════════════════════════════════ │
│ ✿ SUMMARY:                                         │
│ ═══════════════════════════════════════════════════ │
│ ✅ Results: Dispatched AGV-002 successfully        │
│ 📊 Details:                                         │
│    - Dispatch ID: 1                                 │
│    - Delivery Time: 4 minutes                       │
│    - Distance: 150 meters                           │
│    - Cost: $3.50                                    │
│    - Reservation ID: 7                              │
│ 💡 Next: Monitor delivery progress                 │
╰─────────────────────────────────────────────────────╯

Press Enter to continue...
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
3. **Pull required models**:
   ```bash
   ollama pull qwen2.5:3b  # Fast model (default)
   ollama pull qwen2.5:7b  # Powerful model (optional)
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
- Use queries 11-13 (Orchestration) for complex multi-agent workflows
- Try queries 14-16 (Cross-Agent) for advanced coordination
- Use Custom mode (100) to test your own logistics scenarios
- Toggle streaming (200) to see responses with/without animated spinner
- Switch models (300) to compare qwen2.5:3b (fast) vs 7b (powerful)

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
❌ Model not found: qwen2.5:3b
```
**Solution**: Pull the model: `ollama pull qwen2.5:3b`

#### Spinner Not Animating
```bash
💭 Thinking... ⠋ [static, not rotating]
```
**Solution**: Ensure Rich is installed: `pip install rich>=13.0.0`

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