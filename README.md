# 🤖 AI Manufacturing Logistics Multi-Agent System

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-green.svg)](https://flask.palletsprojects.com/)
[![AI](https://img.shields.io/badge/AI-Ollama%20Powered-purple.svg)](https://ollama.ai)
[![Multi-Agent](https://img.shields.io/badge/Architecture-Multi%20Agent-orange.svg)]()

> **An intelligent AI-powered logistics coordination system featuring multi-agent architecture for manufacturing part requests, AGV workflow management, and real-time decision making.**

## 🚀 What This System Does

- **🤖 AI Multi-Agent Coordination**: Four specialized AI agents working together for logistics decisions
- **📱 Real-Time Web Dashboard**: Interactive Flask-based interface with live workflow tracking
- **🚛 AGV Workflow Simulation**: 10-second realistic dispatch, pickup, and delivery sequences
- **⚖️ AI-Powered Approvals**: Intelligent cost analysis and supervisor approval workflow
- **📦 Smart Inventory Management**: Real-time stock monitoring and availability checking
- **🎯 Complete Logistics Pipeline**: End-to-end part request handling with agent communication

## 🎯 Quick Start

### **🚀 Easy Server Management (Recommended)**
```bash
# 1. Start the AI logistics server
python start.py
# → Web dashboard: http://127.0.0.1:5555
# → All AI agents initialize automatically
# → Server runs in background

# 2. Access the logistics dashboard
# Open http://127.0.0.1:5555 in your browser

# 3. Create manufacturing part requests
# Use the web interface to submit requests
# Watch AI agents coordinate in real-time

# 4. Stop the server when done
python stop.py
# → Graceful shutdown with cleanup
```

### **🐍 Direct Method (Development)**
```bash
# 1. Install dependencies (one-time setup)
pip install -r requirements.txt

# 2. Start Flask server directly
python flask_app.py
# → Access: http://127.0.0.1:5555

# 3. Use Ctrl+C to stop
```

**Intelligent AI-powered logistics coordination made simple!** ✨

## 🏗️ Multi-Agent System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        🌐 Flask Web Dashboard                       │
│                        http://127.0.0.1:5555                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🎯 LogisticsOrchestratorAgent                    │
│               (Coordinates all agents and workflows)                │
└─────────────────────────────────────────────────────────────────────┘
                │                │                │
                ▼                ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  📦 InventoryAgent │ │  🚛 FleetAgent    │ │  ⚖️ ApproverAgent │
│                  │ │                  │ │                  │
│ • Stock checking │ │ • AGV management │ │ • Cost analysis  │
│ • Availability   │ │ • Route planning │ │ • Risk assessment│
│ • Warehouses     │ │ • Battery status │ │ • Approval logic │
└──────────────────┘ └──────────────────┘ └──────────────────┘
                │                │                │
                └────────────────┼────────────────┘
                                ▼
                    🤖 Ollama AI Integration
                   (llama3:latest model)
```

## 🛠️ Prerequisites & Setup

### 📋 **Requirements**

| Component | Version | Purpose | Installation |
|-----------|---------|---------|--------------|
| **Python** | 3.13+ | Core runtime | [python.org](https://python.org) |
| **Flask** | 2.0+ | Web framework | `pip install flask` |
| **Ollama** | Latest | AI model runtime | [ollama.ai](https://ollama.ai) (Optional) |
| **psutil** | 5.8+ | Process management | `pip install psutil` |

### 🔑 **AI Setup (Optional)**

**Option 1: Ollama Integration (Recommended)**
```bash
# Install Ollama for enhanced AI capabilities
# Visit: https://ollama.ai
ollama pull llama3:latest
# Agents will automatically connect to Ollama if available
```

**Option 2: Fallback Mode**
```bash
# System works without Ollama using rule-based logic
# No additional setup required
# Agents use deterministic decision-making
```

**AI Agent Capabilities:**
- **With Ollama**: Advanced natural language processing and decision-making
- **Fallback Mode**: Rule-based logic with predefined decision trees
- **Automatic Detection**: System chooses best available mode

### ⚡ **Installation**

```bash
# 1. Clone or download the project
cd Logistics_Multi_Agents

# 2. Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Make scripts executable (Unix/Linux/macOS)
chmod +x start.py stop.py

# 5. Now you can use either:
python start.py              # Start server
python stop.py               # Stop server
```

## 📂 Project Structure

```
Logistics_Multi_Agents/
├── 🔧 requirements.txt           # Python dependencies
├── 📚 README.md                  # This documentation
├── 🌐 flask_app.py              # Main Flask web application
├── 🚀 start.py                  # Server startup script
├── 🛑 stop.py                   # Server shutdown script
│
├── 📂 Agents/                   # 🤖 AI Agent System
│   ├── LogisticsOrchestratorAgent.py  # Master coordinator agent
│   ├── InventoryAgent.py             # Inventory management agent
│   ├── FleetAgent.py                 # AGV fleet management agent
│   └── ApproverAgent.py              # Cost analysis & approval agent
│
└── 📂 templates/                # 🎨 Web Interface
    └── index.html               # Interactive logistics dashboard
```

## 🎯 Core AI Agents

### 🎯 **LogisticsOrchestratorAgent**
- **Role**: Master coordinator and workflow manager
- **Capabilities**: Request analysis, agent coordination, status tracking
- **AI Features**: Natural language processing, decision orchestration
- **Responsibilities**: End-to-end workflow management

### 📦 **InventoryAgent** 
- **Role**: Stock level monitoring and availability checking
- **Capabilities**: Real-time inventory tracking, warehouse management
- **AI Features**: Demand prediction, stock optimization recommendations
- **Responsibilities**: Part availability, location mapping, cost estimation

### 🚛 **FleetAgent**
- **Role**: AGV fleet management and route optimization
- **Capabilities**: Vehicle assignment, battery monitoring, route planning
- **AI Features**: Optimal vehicle selection, traffic prediction
- **Responsibilities**: AGV dispatch, travel time estimation, resource allocation

### ⚖️ **ApproverAgent**
- **Role**: Cost analysis and approval decision support
- **Capabilities**: Financial analysis, risk assessment, policy compliance
- **AI Features**: Cost prediction, approval recommendations
- **Responsibilities**: Budget analysis, approval workflows, decision logging

## 🌐 Web Dashboard Features

### 📱 **Interactive Interface**
**Access:** http://127.0.0.1:5555

**Main Sections:**
- **📋 Request Form**: Submit new manufacturing part requests
- **🔄 Workflow Tracker**: Real-time step-by-step progress visualization
- **💬 Agent Messages**: Live communication feed from all AI agents
- **📊 Results Display**: Analysis results, costs, and approval status

### 🎮 **User Workflow**

1. **📝 Submit Request**: Fill out part details (number, quantity, destination, priority)
2. **🔍 Analysis Phase**: Watch AI agents analyze inventory, fleet, and costs
3. **⚖️ Approval Decision**: Review analysis results and approve/reject
4. **🚀 AGV Workflow**: Monitor 10-second realistic AGV dispatch and delivery
5. **✅ Completion**: View final results and metrics

### 📊 **Real-Time Features**

- **🔄 Live Updates**: 500ms polling for instant status changes
- **🎯 Step Progress**: Visual progress indicator with 7 workflow stages
- **💬 Agent Communication**: Real-time messages from all AI agents
- **📈 Metrics Display**: Cost breakdowns, time tracking, resource usage

## 🚛 AGV Workflow Simulation

### 📋 **Workflow Stages**

| Stage | Duration | Description | AI Agent |
|-------|----------|-------------|-----------|
| **🔍 Analysis** | 2s | Request analysis and validation | Orchestrator |
| **📦 Inventory** | 1.5s | Stock checking and availability | Inventory |
| **🚛 Fleet** | 1.5s | AGV assignment and route planning | Fleet |
| **💰 Cost** | 1s | Financial analysis and approval prep | Approver |
| **🤖 AGV Dispatch** | 10s | Vehicle preparation and navigation | Fleet |
| **📋 Pickup** | 10s | Material loading and securing | Inventory |
| **🎯 Delivery** | 3s | Final delivery to destination | Fleet |

### ⏱️ **Realistic Timing**

- **Pre-Approval**: ~6 seconds (fast analysis for decision-making)
- **AGV Operations**: ~23 seconds (realistic industrial timing)
- **Total Workflow**: ~30 seconds (end-to-end with approval)

## 📊 Server Management

### 🚀 **Start Server**

```bash
# Using management script (recommended)
python start.py

# Expected output:
# ✅ Server started successfully!
# 🌐 Access: http://127.0.0.1:5555
# 💡 Server runs in background
```

**Features:**
- ✅ **Smart Detection**: Prevents multiple server instances
- ✅ **Background Operation**: Server continues after script exits
- ✅ **PID Management**: Tracks process ID for clean shutdown
- ✅ **Log Management**: Creates `server.log` for troubleshooting
- ✅ **Error Handling**: Clear error messages and recovery guidance

### 🛑 **Stop Server**

```bash
# Using management script (recommended)
python stop.py

# Expected output:
# 🛑 Stopping Flask server...
# ✅ All processes stopped successfully!
# 🧹 Resources cleaned up
```

**Features:**
- ✅ **Graceful Shutdown**: SIGTERM first, SIGKILL if needed
- ✅ **Process Discovery**: Finds all Flask processes automatically
- ✅ **Resource Cleanup**: Removes PID files and temporary resources
- ✅ **Verification**: Confirms complete shutdown

### 📊 **Server Status Checking**

```bash
# Check if server is running
lsof -i :5555

# View server logs
tail -f server.log

# Check processes manually
ps aux | grep flask_app

# Test server response
curl http://127.0.0.1:5555
```

## 🎮 Usage Examples

### 📝 **Basic Request Workflow**

1. **Start System**:
   ```bash
   python start.py
   # Open http://127.0.0.1:5555
   ```

2. **Submit Request**:
   - Part Number: `BEARING-2024-X1`
   - Quantity: `15`
   - Destination: `Production Line A`
   - Priority: `High`

3. **Watch Analysis**: Agents analyze in real-time (~6 seconds)

4. **Make Decision**: Approve or reject based on analysis

5. **Monitor AGV**: Watch realistic 23-second AGV workflow

6. **View Results**: Check final metrics and completion status

### 🧪 **Advanced Testing Scenarios**

**High-Volume Request:**
- Quantity: `50+` units
- Expected: Higher costs, longer AGV operations

**Critical Priority:**
- Priority: `Critical`
- Expected: Expedited processing, priority AGV assignment

**Multiple Destinations:**
- Test different production lines
- Expected: Different travel times and costs

**Resource Constraints:**
- Submit multiple requests quickly
- Expected: AGV conflicts, queuing behavior

## 🔧 Troubleshooting

### 🚨 **Common Issues**

**Server Won't Start:**
```bash
# Check if port 5555 is in use
lsof -i :5555

# Kill conflicting processes
pkill -f flask_app.py

# Try starting again
python start.py
```

**Server Won't Stop:**
```bash
# Force stop
sudo python stop.py

# Manual cleanup
pkill -9 -f flask_app.py
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

### 🔄 **Multi-Request Handling**
- Submit multiple requests simultaneously
- Watch agent coordination and resource management
- Observe intelligent queuing and prioritization

### 📊 **Performance Monitoring**
- Real-time agent response times
- AGV utilization tracking  
- Cost optimization analysis

### 🤖 **AI Enhancement**
- Install Ollama for advanced AI capabilities
- Natural language request processing
- Intelligent decision recommendations

### 🔧 **Customization**
- Modify agent behaviors in `Agents/` directory
- Customize web interface in `templates/index.html`
- Adjust workflow timing in `flask_app.py`

## 🎯 Perfect For

- **🏭 Manufacturing Automation**: Real-world logistics coordination simulation
- **🤖 AI/ML Learning**: Multi-agent system architecture and coordination
- **🌐 Web Development**: Flask-based real-time dashboard development
- **📊 Process Optimization**: Workflow analysis and bottleneck identification
- **🚛 AGV Systems**: Autonomous vehicle coordination and management

## 📞 Support & Development

### 🔍 **Debugging**
- Server logs: `tail -f server.log`
- Browser console: F12 Developer Tools
- Agent communication: Watch real-time messages in web UI

### 🛠️ **Development Mode**
```bash
# Run with debug output
python flask_app.py

# Watch for file changes
# (Note: Debug mode disabled in production for stability)
```

### 📈 **Performance Tuning**
- Adjust polling intervals in `templates/index.html`
- Modify AGV timing in `flask_app.py`
- Optimize agent response times in `Agents/` files

---

## 🎉 That's It!

You now have a **complete AI-powered multi-agent logistics system** that:

- ✅ **Coordinates 4 specialized AI agents** for intelligent decision-making
- ✅ **Provides real-time web dashboard** with live workflow tracking
- ✅ **Simulates realistic AGV operations** with 10-second timing
- ✅ **Handles complete request lifecycle** from submission to delivery
- ✅ **Offers intelligent cost analysis** and approval workflows
- ✅ **Includes smart server management** with start/stop scripts

### 🚀 **Perfect for:**
- Manufacturing logistics automation
- Multi-agent system learning
- AI coordination demonstrations
- Real-time workflow visualization
- Industrial process simulation

**Happy AI logistics coordination! 🤖🏭✨**

---

*For support, enhancements, or questions about this multi-agent logistics system, refer to the comprehensive troubleshooting and development sections above.*