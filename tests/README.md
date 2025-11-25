# Tests Directory

This directory contains the comprehensive test suite for the Logistics Multi-Agent System.

## Test Files

### `test_agents.py`
The main test module containing:
- **Enhanced test suite** with 7 different test scenarios
- **Agent creation validation** 
- **Individual agent function tests**
- **Multi-agent orchestration tests**
- **Agent discovery and communication tests**
- **Emergency/urgent request simulations**
- **Interactive test selection**

### `run_tests.py`
Convenient test runner script that:
- Automatically sets up the system
- Initializes all data managers and agents
- Runs the interactive test suite
- Provides clear error messages and guidance

### `__init__.py`
Package initialization file that exports the main testing functions.

## Running Tests

### Method 1: Test Runner (Recommended)
```bash
# From the root directory
python tests/run_tests.py
```

### Method 2: Direct Execution
```bash
# From the tests directory
cd tests
python test_agents.py
```

### Method 3: Programmatic Usage
```python
import sys
sys.path.append('Agents')

from agent_factory import initialize_agent_factory
from data_setup import setup_all_data_managers
from tests.test_agents import main_enhanced_testing

# Setup system
inv_mgr, fleet_mgr, approval_mgr = setup_all_data_managers()
factory = initialize_agent_factory(inv_mgr, fleet_mgr, approval_mgr)

# Run tests
main_enhanced_testing(factory)
```

## Test Scenarios

The test suite includes 7 comprehensive test scenarios:

1. **Basic Agent Creation Tests** - Validates agent creation and configuration
2. **Individual Agent Function Tests** - Tests each agent type's specific functions
3. **Agent Discovery & Communication Tests** - Tests A2A communication capabilities
4. **Complex Orchestration with Discovery** - Multi-phase complex logistics operations
5. **Urgent Request Simulation** - Emergency scenario handling
6. **Full Integration Test Suite** - Comprehensive system testing
7. **Run All Tests** - Executes all available tests

## Prerequisites

Before running tests, ensure:

1. **Ollama is running**:
   ```bash
   ollama serve
   ```

2. **Required model is available**:
   ```bash
   ollama pull qwen2.5:7b
   ```

3. **Dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Virtual environment is activated** (if using one):
   ```bash
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

## Test Features

### Interactive Testing
- Menu-driven test selection
- Option to run individual or all tests
- Clear progress indicators and results

### Agent Discovery Testing
- Tests A2A (Agent-to-Agent) communication
- Validates agent capability discovery
- Tests inter-agent coordination

### Comprehensive Coverage
- Agent creation and configuration validation
- Tool execution and response validation
- Multi-domain workflow orchestration
- Error handling and edge cases

### Production-Like Scenarios
- Real logistics workflows
- Emergency situation handling
- Complex multi-step operations
- Cost and approval considerations

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the correct directory
   - Check that all dependencies are installed
   - Verify virtual environment is activated

2. **Ollama Connection Errors**
   - Confirm Ollama server is running: `ollama serve`
   - Verify model is available: `ollama list`
   - Check if model needs to be pulled: `ollama pull qwen2.5:7b`

3. **Tool Execution Failures**
   - Check system initialization messages
   - Verify data managers are properly created
   - Review agent creation success/failure indicators

### Success Indicators

When tests run successfully, you should see:
- ✅ All 4 agent types created successfully
- ✅ Domain-specific tool assignment working
- ✅ Tool execution tracking with agent names
- ✅ Complex multi-domain workflows completing
- ✅ Real-time logistics operations functioning

## Extending Tests

To add new tests:

1. Add new test functions to `test_agents.py`
2. Update the test menu in `display_test_menu()`
3. Add the new test option to `run_test_suite()`
4. Follow the existing pattern for error handling and output formatting

The test framework is designed to be easily extensible for new agent types, tools, and scenarios.