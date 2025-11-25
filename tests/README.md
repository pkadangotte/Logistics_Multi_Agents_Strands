# Tests Directory

This directory contains the test suite for the Logistics Multi-Agent System, organized into individual test modules for better CI/CD integration and maintainability.

## Test Structure

### Test Modules

- **`test_agent_creation.py`** - Tests for agent creation and basic functionality
- **`test_inventory_agent.py`** - Tests specific to inventory agent operations  
- **`test_fleet_agent.py`** - Tests specific to fleet management agent operations
- **`test_approval_agent.py`** - Tests specific to approval workflow agent operations
- **`test_orchestration.py`** - Tests for orchestration and integration between agents

### Configuration Files

- **`conftest.py`** - Shared pytest fixtures and utilities
- **`../pyproject.toml`** - pytest configuration and coverage settings
- **`../run_tests.py`** - Local test runner script (moved to project root)

### Supporting Files

- **`__init__.py`** - Package initialization file

## Running Tests

### Individual Test Modules

Run specific test modules using pytest directly:

```bash
# Test agent creation
python -m pytest tests/test_agent_creation.py -v

# Test inventory agent
python -m pytest tests/test_inventory_agent.py -v

# Test fleet agent
python -m pytest tests/test_fleet_agent.py -v

# Test approval agent
python -m pytest tests/test_approval_agent.py -v

# Test orchestration
python -m pytest tests/test_orchestration.py -v
```

### All Tests

Run all tests:

```bash
python -m pytest tests/ -v
```

### With Coverage

Run tests with coverage reporting:

```bash
python -m pytest tests/ --cov=Agents --cov-report=term-missing --cov-report=html
```

### Using Test Runner

Use the provided test runner script:

```bash
# Run specific module
python run_tests.py agent_creation
python run_tests.py inventory_agent
python run_tests.py fleet_agent
python run_tests.py approval_agent
python run_tests.py orchestration

# Run all tests
python run_tests.py all

# Run with coverage
python run_tests.py coverage
```

## CI/CD Integration

The test suite is designed for CI/CD pipelines:

- **GitHub Actions**: See `.github/workflows/ci.yml` for automated testing
- **Individual Execution**: Each test module can be run independently
- **Coverage Reporting**: Integrated with codecov for coverage tracking
- **Multiple Python Versions**: Tested against Python 3.8, 3.9, 3.10, 3.11

## Test Fixtures

The `conftest.py` file provides shared fixtures:

- **`data_managers`** - Session-scoped data providers
- **`agent_factory`** - Session-scoped agent factory  
- **`test_agents`** - Function-scoped test agents for all types
- **Individual agent fixtures** - Function-scoped single agents
- **Helper functions** - Validation utilities

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