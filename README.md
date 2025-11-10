# 🤖 Multi-Agent Logistics System

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Interface-green.svg)](https://flask.palletsprojects.com/)
[![AI-Powered](https://img.shields.io/badge/AI-Ollama%20Enhanced-orange.svg)](https://ollama.ai)
[![Real-Time](https://img.shields.io/badge/Real--Time-SSE%20Streaming-success.svg)]()

> **A sophisticated multi-agent system that orchestrates manufacturing logistics workflows. Watch intelligent agents coordinate inventory checks, AGV fleet management, and approval processes in real-time through an interactive web dashboard.**

## 🎯 What This System Demonstrates

**Complete Autonomous Logistics Workflow**: Submit a parts request through the web interface and watch five specialized AI agents work together:

1. **🎯 Logistics Orchestrator** - Coordinates the entire workflow and manages agent communication
2. **📦 Inventory Agent** - Checks stock availability across multiple warehouses  
3. **🚛 Fleet Agent** - Assigns optimal AGVs based on capacity, battery, and location
4. **🤖 AGV Agent** - Individual vehicle control with real-time movement and mission execution
5. **⚖️ Approver Agent** - Reviews requests with intelligent cost and risk analysis

**Live Real-Time Tracking**: Watch the complete AGV lifecycle unfold - from accepting missions to pickup, loading, delivery, unloading, and completion - all with live status updates and progress visualization.

## 🚀 Quick Start

### Start the System
```bash
# Install dependencies
pip install -r requirements.txt

# Launch the multi-agent system
python3 strands_flask_app.py
```

### Access the Web Interface
Open **http://localhost:5555** in your browser to see the interactive dashboard.

### Try a Sample Request
1. **Part Number**: `HYDRAULIC-PUMP-HP450`
2. **Quantity**: `15`
3. **Destination**: `Production Line A`
4. **Priority**: `Medium`

Click "🚀 Start Workflow" and watch the agents coordinate the entire logistics process in real-time!

## 🎬 Live Agent Coordination

Watch the **Live Agent Feed** as four specialized agents work together:

### Real-Time Workflow Visualization
```
🎯 Step 1: Analysis     → Logistics Orchestrator coordinates the request
📦 Step 2: Inventory    → Agent checks stock across warehouses  
🚛 Step 3: Fleet        → AGV assignment and route planning
💰 Step 4: Cost         → Automated cost calculation
⚖️ Step 5: AGV Dispatch → AGV accepts mission and starts journey
� Step 6: Pickup       → AGV moves to pickup location
✅ Step 7: Delivery     → Complete AGV lifecycle tracking
```

### Live Agent Messages
The system provides real-time updates showing each agent's actions:
- **🎯 Accepting delivery mission MISSION-HYDRAULIC-PUMP-HP450-REQ-1762680696**
- **🚶 Moving to pickup location Central Warehouse**
- **✅ Reached pickup location Central Warehouse (Battery: 85.0%)**
- **📦 Loading 15 pieces of HYDRAULIC-PUMP-HP450**
- **🚚 Moving to delivery location Production Line A with 15 pieces**
- **📤 Unloading 15 pieces at Production Line A**
- **✅ Mission completed successfully**

## 🧠 Key Features

### � **Interactive Web Dashboard**
- **Real-Time Progress Tracking**: Visual workflow steps from analysis to delivery
- **Live Agent Feed**: Watch 22+ live messages stream from the AGV and coordination agents
- **Smart Forms**: Dropdown menus for parts, destinations, and priorities with validation
- **Status Cards**: Live updates showing inventory levels, fleet status, and costs

### 🤖 **Complete AGV Lifecycle Tracking**
- **Mission Acceptance**: Watch AGVs accept delivery missions with unique IDs
- **Movement Tracking**: Real-time location updates from warehouse to production line
- **Loading Operations**: Detailed cargo handling with piece counts and battery monitoring
- **Delivery Confirmation**: Complete mission lifecycle from start to successful completion

### 🎯 **Intelligent Workflow Orchestration**  
- **Multi-Agent Coordination**: Four specialized agents work together seamlessly
- **Real-Time Communication**: Server-Sent Events (SSE) for instant updates
- **State Management**: Tracks workflow progress through multiple phases
- **Error Handling**: Graceful management of edge cases and system states

### 📦 **Smart Inventory Management**
- **Multi-Warehouse Support**: Central Warehouse, Production Line locations
- **Stock Validation**: Real-time availability checking before workflow execution
- **Cost Calculation**: Automatic pricing with quantity and priority adjustments
- **Availability Status**: Clear indicators for stock levels and locations

## 🏗️ System Architecture

```
🌐 Web Interface (Flask + SSE)              👤 User Experience
├── Interactive Dashboard                     ├── Submit Requests
├── Live Agent Feed (22+ messages)          ├── Monitor Progress  
├── Real-time Progress Tracking             ├── Visual Status Cards
└── Responsive Design                       └── Live Updates
                    │
    ┌───────────────┼─────────────────────────┐
    │               │                         │
    ▼               ▼                         ▼
🎯 LOGISTICS     📦 INVENTORY      🚛 FLEET        🤖 AGV         ⚖️ APPROVER
ORCHESTRATOR       AGENT           AGENT          AGENT          AGENT
│                  │               │              │              │
├─ Workflow Mgmt   ├─ Stock Check  ├─ AGV Assign  ├─ Movement     ├─ Cost Review
├─ Agent Coord     ├─ Availability ├─ Route Plan  ├─ Navigation   ├─ Risk Analysis
├─ Status Track    ├─ Multi-Whse   ├─ Battery     ├─ Loading      ├─ Approval Flow
├─ State Mgmt      ├─ Cost Calc    ├─ Capacity    ├─ Delivery     ├─ Multi-Tier
└─ Error Handle    └─ Validation   └─ Fleet Mgmt  ├─ Unloading    └─ Intelligence
                                                  └─ Mission Exec

💾 In-Memory Data Store                     🤖 AI Enhancement
├── Parts Catalog (4 parts)                ├── Ollama Integration
├── Warehouse Locations                    ├── llama3:latest
├── AGV Fleet Status (4 vehicles)          ├── Natural Language
├── Request State Management               ├── Decision Support
└── Live Messaging System                  └── Fallback Logic
```

## 📦 Available Test Data

### 🔧 **Sample Parts for Testing**

| Part Number | Stock | Location | Cost/Unit | Description |
|-------------|-------|----------|-----------|-------------|
| `HYDRAULIC-PUMP-HP450` | 24 units | Central Warehouse | $245.00 | High-value hydraulic component |
| `PART-ABC123` | 85 units | Warehouse A | $12.50 | Standard production part |
| `PART-DEF456` | 120 units | Warehouse A | $8.25 | Common component |
| `PART-XYZ789` | 42 units | Warehouse B | $18.75 | Specialized part |

### 🚛 **AGV Fleet Status**

| AGV ID | Capacity | Battery | Base Location | Status |
|--------|----------|---------|---------------|--------|
| AGV-001 | 100 pieces | 85% | AGV_BASE | Ready for Delivery |
| AGV-002 | 50 pieces | 92% | AGV_BASE | Ready for Delivery |
| AGV-003 | 100 pieces | 87% | AGV_BASE | Ready for Delivery |
| AGV-004 | 25 pieces | 82% | AGV_BASE | Ready for Delivery |

### 🏭 **Delivery Destinations**

- **Production Line A** - Main assembly line
- **Production Line B** - Secondary production 
- **Central Warehouse** - Primary storage facility
- **Quality Control** - Inspection station

## 📋 System Requirements

### 💻 **Prerequisites**
- **Python 3.12+** - Core runtime environment
- **Modern Web Browser** - For accessing the interactive dashboard

### 📚 **Dependencies**
```bash
flask>=2.0.0           # Web framework and SSE support
requests               # HTTP client for agent communication  
psutil                 # System process management
```

### 🤖 **Optional AI Enhancement**
```bash
# Install Ollama for enhanced AI decision-making
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3:latest
```
*Note: System automatically falls back to rule-based logic if Ollama is unavailable*

### ⚡ **Installation**
```bash
# Clone repository
git clone [repository-url]
cd Logistics_Multi_Agents_Strands

# Install dependencies
pip install -r requirements.txt

# Start the system
python3 strands_flask_app.py
```

## 🧪 Testing Scenarios

### 🎯 **Recommended Test Cases**

#### **Standard Workflow Test**
```
Part: HYDRAULIC-PUMP-HP450
Quantity: 15
Destination: Production Line A
Expected: ✅ Complete workflow with AGV tracking
```

#### **High Quantity Test**  
```
Part: PART-DEF456
Quantity: 50
Destination: Production Line B
Expected: ✅ Large order processing
```

#### **Multiple Parts Test**
```
Try different parts to see varying inventory levels:
- PART-ABC123 (85 available)
- PART-XYZ789 (42 available) 
- HYDRAULIC-PUMP-HP450 (24 available)
```

### 📊 **What to Observe**

**🎯 Real-Time Progress**:
- Watch the workflow progress bar advance through 7 stages
- Monitor live agent messages in the feed panel
- See status cards update with current information

**🤖 AGV Lifecycle**:
- Mission acceptance with unique IDs
- Movement tracking with battery levels
- Loading/unloading operations with piece counts
- Mission completion confirmations

**🔄 Live Updates**:
- Server-Sent Events streaming
- No page refresh needed
- Persistent connection status

## � Technical Details

### � **Web Interface Technology**
- **Flask Framework**: Lightweight Python web server
- **Server-Sent Events (SSE)**: Real-time message streaming
- **Responsive Design**: Works on desktop and mobile browsers
- **Live Agent Feed**: 22+ messages streamed during workflow execution

### 🤖 **Agent Architecture**
- **Modular Design**: Five specialized agents with distinct responsibilities
- **Async Communication**: Non-blocking agent coordination
- **State Management**: Persistent workflow tracking across requests
- **Error Resilience**: Graceful handling of agent failures

### 💾 **Data Management**
- **In-Memory Storage**: No database setup required
- **Session Persistence**: State maintained during browser sessions
- **Real-Time Updates**: Instant synchronization across all components
- **Configuration-Driven**: Easy modification of parts, AGVs, and settings

## 🛠️ Configuration-Based Customization

### � **Adding New Parts**
Edit `Agents/InventoryAgent.py` to add new parts to the inventory:
```python
"YOUR-NEW-PART": {
    "available_quantity": 150,
    "warehouse_location": "Central Warehouse", 
    "unit_cost": 45.00,
    "reorder_point": 25
}
```

### 🚛 **Adding AGVs**
Modify `Agents/FleetAgent.py` to expand the fleet:
```python
"AGV-005": {
    "type": "heavy_duty_agv",
    "capacity_pieces": 75,
    "status": "AVAILABLE", 
    "battery_level": 90
}
```

### 🏭 **Adding Destinations**
Update delivery locations in `Agents/FleetAgent.py`:
```python
"New Production Line": {
    "location_id": "PROD_LINE_C",
    "distance_km": 2.1,
    "travel_time_minutes": 8
}
```

## 🤖 The Five Agents

### 🎯 **Logistics Orchestrator Agent**
**Master workflow coordinator** - Manages the entire request lifecycle and coordinates communication between all other agents.

### 📦 **Inventory Agent** 
**Smart stock management** - Checks availability across warehouses, calculates costs, and validates inventory levels for incoming requests.

### 🚛 **Fleet Agent**
**AGV fleet coordination** - Assigns optimal vehicles based on capacity and battery levels, manages overall fleet operations and routing.

### 🤖 **AGV Agent**
**Individual vehicle control** - Handles real-time movement, navigation, loading/unloading operations, and mission execution for each autonomous vehicle.

### ⚖️ **Approver Agent**
**Intelligent approval** - Reviews requests for cost analysis, risk assessment, and multi-tier approval workflows.

## � Troubleshooting

### � **Common Issues**

**"Port already in use"**
```bash
# Check what's using port 5555
lsof -i :5555

# Kill any existing Flask processes  
pkill -f strands_flask_app.py

# Try starting again
python start.py
```

**"Agents not responding"**
```bash
# Check the server logs
tail -20 server.log

# Verify Strands SDK is installed
pip show strands

# Test agents directly
python test_complete_integration.py
```

**"Import errors"** 
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify Python version (3.9+)
python --version
```

### � **Getting Help**

**View Logs:**
```bash
# Server logs (if running in background)
tail -f server.log

# Direct run for detailed output
python strands_flask_app.py
```

**Test Individual Components:**
```bash
# Test just the orchestrator
python test_orchestrator_agent.py

# Test all agent integration
python test_complete_integration.py

# Check available parts
cat INVENTORY_PARTS_REFERENCE.md
```

## � What Makes This Special

### 🤖 **Strands Agent SDK Implementation**
- **Proper @tool registration** - All 20 agent methods properly decorated  
- **Direct agent communication** - Optimized for performance, no message passing overhead
- **Zero external dependencies** - No databases, no cloud services, no configuration
- **Production-ready patterns** - Global instances, error handling, comprehensive logging

### 🏭 **Real Manufacturing Workflow** 
- **Authentic business logic** - Based on actual manufacturing replenishment processes
- **Realistic data** - Parts, costs, AGVs, and approvers reflect real-world scenarios  
- **Complete orchestration** - Full workflow from request submission to delivery confirmation
- **Intelligent coordination** - AI-powered decisions with rule-based fallbacks

### 🚀 **Ready to Deploy**
- **One command start** - `python start.py` and everything works
- **Comprehensive testing** - Full integration test suite validates all functionality
- **Clear documentation** - Complete setup, usage, and troubleshooting guides
- **Educational value** - Perfect for learning Strands Agent SDK patterns

### 🔬 **Technical Excellence**
- **Clean architecture** - Separation of concerns between agents
- **Performance optimized** - In-memory operations, direct method calls
- **Extensible design** - Easy to add new agents, tools, or workflows  
- **Error resilience** - Graceful degradation and comprehensive error handling

## 🔧 Troubleshooting

### 🚨 **Common Issues**

**Server Won't Start:**
```bash
# Check if port 5555 is in use
lsof -i :5555

# Kill conflicting processes
pkill -f strands_flask_app.py

# Try starting again
python start.py
```

**Server Won't Stop:**
```bash
# Force stop
sudo python stop.py

# Manual cleanup
pkill -9 -f strands_flask_app.py
rm -f .server.pid
```

**Web UI Not Loading:**
```bash
# Verify server is running
lsof -i :5555

# Check server logs
tail -20 server.log

# Test local connection
curl -I http://127.0.0.1:5555
```

**AI Agents Not Responding:**
```bash
# Check Ollama connection (if using)
ollama list

# Server falls back to rule-based mode automatically
# Check logs for "fallback mode" messages
```

### 📋 **Dependency Issues**

**Missing Dependencies:**
```bash
# Reinstall requirements
pip install -r requirements.txt

# Update specific packages
pip install --upgrade flask psutil requests
```

**Python Version:**
```bash
# Check Python version
python --version
# Requires Python 3.13+

# Use specific Python version
python3.13 start.py
```

**Virtual Environment:**
```bash
# Create fresh environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🎉 Advanced Features

### 🔄 **Strands Agent Integration**
- All 4 agents built on Strands Agent SDK framework
- 20 total @tool decorated methods across all agents
- Direct agent-to-agent communication via global instances
- Zero external database dependencies (pure in-memory)

### 📊 **Testing & Validation**
- Comprehensive integration test suite (`test_complete_integration.py`)
- Individual agent testing with tool validation
- Pre-loaded inventory data for immediate testing
- Real-time agent method execution verification

### 🤖 **AI Enhancement**
- Ollama integration for advanced AI capabilities
- Automatic fallback to rule-based logic if Ollama unavailable
- Enhanced decision-making with natural language processing
- Intelligent cost analysis and risk assessment

### 🔧 **Zero-Dependency Architecture**
- No AWS credentials required (DynamoDB removed)
- No external database setup needed
- Pure in-memory storage with session persistence
- Simplified deployment with maximum portability

## 🎯 Perfect For

- **🏭 Manufacturing Automation**: Real-world logistics coordination simulation
- **🤖 Strands Agent SDK Learning**: Multi-agent system architecture with @tool registration
- **🌐 Web Development**: Flask-based real-time dashboard development
- **📊 Process Optimization**: Workflow analysis and bottleneck identification  
- **🚛 AGV Systems**: Autonomous vehicle coordination and management
- **🔧 Zero-Dependency Deployment**: No databases, no cloud services required
- **🧪 Agent Testing**: Complete test suite for validation and development

## 📞 Support & Development

### 🔍 **Debugging**
- Server logs: `tail -f server.log`
- Browser console: F12 Developer Tools
- Agent communication: Watch real-time messages in web UI

### 🛠️ **Development Mode**
```bash
# Run with debug output
python strands_flask_app.py

# Watch for file changes
# (Note: Debug mode disabled in production for stability)
```

### 📈 **Performance Tuning**
- Adjust polling intervals in `templates/index.html`
- Modify AGV timing in `strands_flask_app.py`
- Optimize agent response times in `Agents/` files

---

## 🎉 You're All Set!

This is a **complete, production-ready manufacturing replenishment system** built with Strands Agent SDK:

✅ **Zero setup complexity** - Install deps, run `python start.py`, done  
✅ **Real manufacturing workflow** - Authentic part requests → inventory → AGVs → approvals  
✅ **Strands Agent SDK best practices** - 4 agents, 20 @tool methods, proper patterns  
✅ **No external dependencies** - No databases, no cloud services, pure in-memory  
✅ **Comprehensive testing** - Everything validated and ready to use  
✅ **Educational value** - Perfect example of multi-agent coordination  

### � **Start Using It:**

```bash
python start.py                    # Start the system
# → Open http://127.0.0.1:5555    # Use the web interface  
# → Submit requests with valid parts (PART-ABC123, etc.)
# → Watch 4 agents coordinate in real-time
python stop.py                     # Stop when done
```

### 💡 **Learn From It:**
- Study the Strands Agent patterns in `Agents/`
- Examine the @tool decorations and agent communication  
- Run the tests to see everything working
- Extend it with your own agents and workflows

This system demonstrates **professional-grade multi-agent architecture** with the **Strands Agent SDK** - use it as a foundation for your own manufacturing automation projects!

---

## 🎯 Perfect For

- 🏭 **Manufacturing Automation**: Understanding logistics coordination and workflow orchestration
- 🤖 **Multi-Agent Systems**: Learning agent communication, coordination, and specialization patterns  
- 📊 **Process Optimization**: Analyzing bottlenecks, resource utilization, and workflow efficiency
- 🎓 **Educational Projects**: Comprehensive example of production-ready agent system
- 🔬 **Research & Development**: Foundation for advanced manufacturing intelligence systems
- 🚀 **Rapid Prototyping**: Quick setup for testing logistics and coordination algorithms

---

## 🔧 Troubleshooting

### 🚨 **Common Issues**

**Port already in use:**
```bash
pkill -f strands_flask_app.py  # Kill existing processes
python3 strands_flask_app.py   # Restart server
```

**Web interface not loading:**
```bash
curl -I http://localhost:5555  # Test connectivity
# Check terminal for error messages
```

**Dependencies missing:**
```bash
pip install -r requirements.txt  # Reinstall packages
python3 --version              # Verify Python 3.12+
```

---

## 🚀 Get Started

**Ready to see intelligent agents in action?**

```bash
# 1. Clone and setup
git clone [repository-url]
cd Logistics_Multi_Agents_Strands
pip install -r requirements.txt

# 2. Launch the system
python3 strands_flask_app.py

# 3. Open your browser
# → Navigate to http://localhost:5555
# → Submit a request for HYDRAULIC-PUMP-HP450
# → Watch 22+ live messages stream from the agents
# → See complete AGV lifecycle from pickup to delivery
```

### 🎯 **What You'll Experience**

- **Real-time agent coordination** with live message streaming
- **Complete AGV lifecycle tracking** from mission acceptance to completion
- **Interactive web dashboard** with progress visualization
- **Intelligent workflow orchestration** across four specialized agents

### � **Perfect For**

- **Learning multi-agent systems** and coordination patterns
- **Understanding manufacturing logistics** automation
- **Exploring real-time web interfaces** with Server-Sent Events
- **Building on top of** the agent architecture for your own projects

**Start exploring intelligent logistics automation now! 🤖**

---

*A sophisticated multi-agent system demonstrating real-world logistics coordination*