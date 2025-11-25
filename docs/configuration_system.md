# Configuration-Driven Agent Factory System

## Overview

This document describes a planned enhancement to the Logistics Multi-Agent System that will allow users to configure agents, data sources, and system behavior through YAML configuration files instead of writing code. This feature is designed to make the system accessible to non-programmers such as operations teams, warehouse managers, and business users.

## Current State vs. Planned Enhancement

### Current Implementation
- Agents are created programmatically through `AgentFactory` class
- Data sources are hardcoded in Python dictionaries
- System behavior requires code changes to modify
- Technical expertise required for customization
- Configuration scattered across multiple Python files

### Planned Enhancement
- Agents defined declaratively in YAML configuration files
- Data sources configurable through file paths, databases, or APIs
- System behavior controlled through configuration parameters
- Non-technical users can customize agents and workflows
- Centralized configuration management with environment overrides

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   YAML Config   │───▶│ ConfigManager    │───▶│  AgentFactory   │
│                 │    │                  │    │   Enhanced      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ DataSourceManager│
                       │                  │
                       └──────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │ CSV Files   │ │ JSON Files  │ │ Databases   │
        └─────────────┘ └─────────────┘ └─────────────┘
```

## Key Components

### 1. Configuration Manager
**File**: `config/config_manager.py`

```python
class ConfigurationManager:
    """Manages YAML configuration loading, validation, and environment overrides."""
    
    def load_config(self, config_path: str, environment: str = None)
    def validate_schema(self, config: dict) -> bool
    def apply_environment_overrides(self, config: dict, environment: str)
    def get_data_source_config(self, source_name: str)
    def get_agent_configs(self) -> List[dict]
```

### 2. Enhanced Agent Factory
**File**: `Agents/agent_factory.py` (Enhanced)

```python
class AgentFactory:
    """Enhanced factory with configuration file support."""
    
    @classmethod
    def from_config(cls, config_path: str, environment: str = None)
    
    def create_agents_from_config(self) -> Dict[str, GenericAgent]
    def create_agent_from_config(self, agent_name: str, overrides: dict = None)
    def load_data_managers_from_config(self)
```

### 3. Data Source Manager
**File**: `config/data_source_manager.py`

```python
class DataSourceManager:
    """Manages flexible data loading from various sources."""
    
    def load_data_source(self, config: dict) -> pandas.DataFrame
    def setup_auto_refresh(self, source_config: dict)
    def validate_data_source(self, config: dict) -> bool
```

## Configuration Schema

### System Configuration
```yaml
system:
  name: "System Name"
  version: "1.0.0"
  environment: "production"  # development, staging, production
```

### Ollama Model Configuration
```yaml
ollama:
  host: "http://localhost:11434"
  default_model: "qwen2.5:7b"
  timeout_seconds: 30
  models:
    light: "qwen2.5:3b"
    standard: "qwen2.5:7b"
    heavy: "qwen2.5:14b"
```

### Data Sources Configuration
```yaml
data_sources:
  inventory:
    type: "csv"  # csv, json, database, api
    source: "data/inventory.csv"
    refresh_interval: 300
    validation:
      required_columns: ["ItemID", "ItemName", "Quantity"]
      
  fleet:
    type: "database"
    connection_string: "postgresql://user:pass@host/db"
    refresh_interval: 60
```

### Agent Definitions
```yaml
agents:
  - name: "InventoryBot"
    type: "inventory"
    enabled: true
    model: "standard"
    custom_prompt: |
      You are responsible for inventory management...
    specialization:
      low_stock_threshold: 10
      focus_categories: ["Electronics", "Medical"]
```

### Environment Overrides
```yaml
environments:
  development:
    ollama:
      default_model: "qwen2.5:3b"
    data_sources:
      refresh_multiplier: 10
      
  production:
    ollama:
      host: "http://ollama-prod:11434"
    monitoring:
      enabled: true
```

## Implementation Plan

### Phase 1: Core Infrastructure
- [ ] Create `ConfigurationManager` class
- [ ] Implement YAML parsing with schema validation
- [ ] Add environment override support
- [ ] Create configuration file templates

### Phase 2: Data Source Abstraction
- [ ] Implement `DataSourceManager` class
- [ ] Support CSV file loading
- [ ] Support JSON file loading
- [ ] Add data validation and refresh capabilities

### Phase 3: Agent Factory Enhancement
- [ ] Add configuration-driven constructor to `AgentFactory`
- [ ] Implement `from_config()` class method
- [ ] Add agent creation from configuration
- [ ] Support configuration overrides

### Phase 4: Advanced Features
- [ ] Database data source support
- [ ] API data source support
- [ ] Configuration hot-reloading
- [ ] Monitoring and alerting integration

### Phase 5: Tooling and Documentation
- [ ] Configuration validation CLI tool
- [ ] Configuration templates for different scenarios
- [ ] User documentation and examples
- [ ] Migration guide from programmatic to configuration-driven

## Benefits

### For Non-Technical Users
- **No Code Required**: Modify system behavior through text files
- **Visual Configuration**: Clear, readable YAML syntax
- **Business-Focused**: Configure thresholds, limits, and rules directly
- **Environment Management**: Easy dev/staging/production configurations
- **Self-Documenting**: Comments and examples in configuration files

### For Technical Users
- **Reduced Maintenance**: Less code to maintain for configuration changes
- **Version Control**: Configuration changes tracked in git
- **Deployment Flexibility**: Same codebase, different configurations
- **Testing**: Easy to create test configurations
- **Extensibility**: Framework for adding new configuration options

### For Operations
- **Quick Adjustments**: Change agent behavior without deployments
- **A/B Testing**: Easy to test different configurations
- **Disaster Recovery**: Configuration backup and restore
- **Audit Trail**: Track configuration changes over time
- **Compliance**: Documented system configurations

## Migration Strategy

### Backward Compatibility
- Existing programmatic agent creation continues to work
- Configuration system is opt-in, not required
- Gradual migration path available

### Migration Steps
1. **Install Dependencies**: Add PyYAML to requirements
2. **Create Initial Config**: Generate configuration from existing setup
3. **Test Configuration**: Validate configuration creates identical agents
4. **Gradual Migration**: Move to configuration-driven creation
5. **Cleanup**: Remove hardcoded configurations

## Example Usage Scenarios

### Warehouse Manager Scenario
```yaml
# Adjust inventory thresholds for holiday season
agents:
  - name: "InventoryBot"
    specialization:
      low_stock_threshold: 25      # Increased from 10
      critical_stock_threshold: 10  # Increased from 3
```

### Fleet Optimization Scenario
```yaml
# Optimize for energy efficiency during peak hours
agents:
  - name: "FleetCoordinator"
    specialization:
      route_optimization: "energy"    # Changed from "time"
      battery_return_threshold: 30    # Increased from 20
```

### Multi-Environment Deployment
```yaml
environments:
  staging:
    data_sources:
      inventory:
        source: "staging_data/inventory.csv"
  production:
    data_sources:
      inventory:
        source: "production_data/inventory.csv"
```

## Risk Assessment and Mitigation

### Risks
- **Configuration Errors**: Invalid configurations could break the system
- **Security**: Configuration files might contain sensitive information
- **Performance**: Configuration parsing overhead
- **Complexity**: Additional abstraction layer

### Mitigation Strategies
- **Schema Validation**: Comprehensive configuration validation
- **Error Handling**: Graceful fallbacks and clear error messages
- **Security**: Environment variable support for sensitive data
- **Testing**: Automated configuration validation tests
- **Documentation**: Comprehensive examples and troubleshooting guides

## Dependencies

### New Dependencies
- **PyYAML**: YAML parsing and generation
- **jsonschema**: Configuration schema validation
- **python-dotenv**: Environment variable management (optional)

### Optional Dependencies
- **psycopg2**: PostgreSQL database connectivity
- **pymongo**: MongoDB connectivity  
- **requests**: API data source support

## Future Enhancements

### Configuration GUI
- Web-based configuration editor for non-technical users
- Visual agent workflow designer
- Real-time configuration validation

### Advanced Features
- Configuration versioning and rollback
- A/B testing framework for configurations
- Dynamic configuration hot-reloading
- Configuration templates marketplace

### Integration Features
- Kubernetes ConfigMap integration
- Docker environment variable injection
- CI/CD pipeline configuration validation
- Monitoring and alerting on configuration changes

## Conclusion

The configuration-driven agent factory system represents a significant enhancement that will make the Logistics Multi-Agent System accessible to a broader range of users while maintaining the flexibility and power that technical users require. The phased implementation approach ensures minimal disruption to existing functionality while providing a clear path forward for enhanced configurability and usability.