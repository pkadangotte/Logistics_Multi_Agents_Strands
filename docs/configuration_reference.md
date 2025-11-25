# Configuration File Reference Guide

This document provides a comprehensive reference for all configuration options available in the YAML configuration system for the Logistics Multi-Agent System.

## Configuration File Structure

```yaml
system:           # System-wide settings
ollama:          # AI model configuration  
agent_defaults:  # Default settings for all agents
data_sources:    # Data source configurations
agents:          # Individual agent definitions
environments:    # Environment-specific overrides
monitoring:      # System monitoring settings
security:        # Security and access control
```

## System Configuration

### `system` Section
Global system identification and settings.

```yaml
system:
  name: string                    # Human-readable system name
  version: string                 # System version (semantic versioning)
  environment: string             # Current environment
  description: string             # Optional system description
```

**Options for `environment`:**
- `development` - Development environment
- `staging` - Staging/testing environment  
- `production` - Production environment

**Example:**
```yaml
system:
  name: "Warehouse Logistics System"
  version: "1.2.3"
  environment: "production"
  description: "Multi-agent logistics coordination system"
```

## Ollama Model Configuration

### `ollama` Section
Configuration for the Ollama AI model service.

```yaml
ollama:
  host: string                    # Ollama server URL
  default_model: string           # Default model for all agents
  timeout_seconds: integer        # Request timeout
  retry_attempts: integer         # Number of retry attempts
  models:                        # Named model configurations
    light: string                # Fast, less capable model
    standard: string             # Balanced performance model  
    heavy: string                # Powerful, slower model
```

**Example:**
```yaml
ollama:
  host: "http://localhost:11434"
  default_model: "qwen2.5:7b"
  timeout_seconds: 30
  retry_attempts: 3
  models:
    light: "qwen2.5:3b"
    standard: "qwen2.5:7b"  
    heavy: "qwen2.5:14b"
```

## Agent Default Settings

### `agent_defaults` Section
Default settings applied to all agents unless overridden.

```yaml
agent_defaults:
  enable_a2a: boolean             # Enable agent-to-agent communication
  conversation_history: boolean   # Keep conversation history
  error_handling: string          # Error handling strategy
  max_tool_calls_per_request: integer  # Limit tool calls per request
  response_format: string         # Response formatting style
```

**Options for `error_handling`:**
- `strict` - Stop on first error
- `graceful` - Continue with warnings
- `ignore` - Suppress all errors

**Options for `response_format`:**
- `natural` - Natural language responses
- `structured` - Structured, formatted responses
- `json` - JSON-formatted responses

**Example:**
```yaml
agent_defaults:
  enable_a2a: true
  conversation_history: true
  error_handling: "graceful"
  max_tool_calls_per_request: 5
  response_format: "structured"
```

## Data Sources Configuration

### `data_sources` Section
Configuration for various data sources used by agents.

#### Inventory Data Source
```yaml
data_sources:
  inventory:
    type: string                  # Data source type
    source: string                # File path or connection string
    refresh_interval: integer     # Refresh interval in seconds
    columns:                      # Column mapping
      item_id: string
      item_name: string
      quantity: string
      location: string
      category: string
    validation:                   # Data validation rules
      required_columns: [string]  # Required column names
      quantity_min: integer       # Minimum quantity value
```

#### Fleet Data Source  
```yaml
data_sources:
  fleet:
    type: string
    agv_source: string            # AGV information file
    routes_source: string         # Routes information file
    refresh_interval: integer
    columns:
      agv_id: string
      status: string
      battery_level: string
      current_location: string
    validation:
      battery_critical_threshold: integer
```

#### Approval Data Source
```yaml
data_sources:
  approval:
    type: string
    source: string
    refresh_interval: integer
    validation:
      max_approval_amount: number
```

**Data Source Types:**
- `csv` - CSV file
- `json` - JSON file  
- `database` - Database connection
- `api` - REST API endpoint

**Example:**
```yaml
data_sources:
  inventory:
    type: "csv"
    source: "data/inventory.csv"
    refresh_interval: 300
    columns:
      item_id: "ItemID"
      item_name: "ItemName"
      quantity: "Quantity"
      location: "Location"
    validation:
      required_columns: ["ItemID", "ItemName", "Quantity"]
      quantity_min: 0
```

## Agent Configuration

### `agents` Section
Individual agent definitions with their specific configurations.

```yaml
agents:
  - name: string                  # Unique agent name
    type: string                  # Agent type
    enabled: boolean              # Enable/disable agent
    model: string                 # Model to use (light/standard/heavy)
    custom_prompt: |              # Multi-line custom prompt
      Custom instructions...
    specialization:               # Agent-specific settings
      # Type-specific options below
```

**Agent Types:**
- `inventory` - Inventory management agent
- `fleet` - Fleet/AGV coordination agent
- `approval` - Approval workflow agent
- `orchestrator` - Multi-domain orchestration agent

#### Inventory Agent Specialization
```yaml
specialization:
  low_stock_threshold: integer        # Alert threshold for low stock
  critical_stock_threshold: integer   # Critical stock alert threshold
  focus_categories: [string]          # Priority item categories
  priority_locations: [string]        # High-priority storage areas
  auto_reorder_enabled: boolean       # Enable automatic reordering
```

#### Fleet Agent Specialization
```yaml
specialization:
  max_concurrent_agvs: integer        # Maximum simultaneous AGVs
  battery_return_threshold: integer   # Battery level for return to charge
  route_optimization: string          # Optimization strategy
  collision_avoidance: boolean        # Enable collision avoidance
  maintenance_alerts: boolean         # Enable maintenance alerts
```

**Route Optimization Options:**
- `time` - Optimize for fastest routes
- `distance` - Optimize for shortest distance
- `energy` - Optimize for energy efficiency

#### Approval Agent Specialization
```yaml
specialization:
  auto_approve_limit: number          # Auto-approve threshold
  require_manager_approval: number    # Manager approval threshold
  require_justification: number       # Justification required threshold
  escalation_time_hours: integer     # Hours before escalation
  compliance_categories: [string]     # Compliance focus areas
```

#### Orchestrator Agent Specialization
```yaml
specialization:
  coordination_style: string          # Coordination approach
  conflict_resolution: string         # Conflict resolution strategy
  reporting_frequency: string         # Reporting schedule
  escalation_enabled: boolean         # Enable issue escalation
  cross_domain_optimization: boolean  # Cross-domain optimization
```

**Coordination Style Options:**
- `reactive` - Respond to events as they occur
- `proactive` - Anticipate and prevent issues
- `predictive` - Use predictive analytics

**Conflict Resolution Options:**
- `time_optimized` - Prioritize speed
- `cost_optimized` - Prioritize cost efficiency

**Reporting Frequency Options:**
- `hourly` - Every hour
- `daily` - Once per day
- `weekly` - Once per week

**Example Agent Configuration:**
```yaml
agents:
  - name: "WarehouseInventoryBot"
    type: "inventory"
    enabled: true
    model: "standard"
    custom_prompt: |
      You are the Warehouse Inventory Management Agent.
      Focus on accuracy and timely alerts for stock issues.
    specialization:
      low_stock_threshold: 10
      critical_stock_threshold: 3
      focus_categories: ["Electronics", "Medical"]
      priority_locations: ["A1", "A2", "B1"]
      auto_reorder_enabled: false
```

## Environment Configuration

### `environments` Section
Environment-specific overrides for different deployment scenarios.

```yaml
environments:
  environment_name:               # development, staging, production
    ollama:                       # Ollama overrides
      host: string
      default_model: string
    data_sources:                 # Data source overrides
      refresh_multiplier: number  # Multiply refresh intervals
      use_sample_data: boolean    # Use test data
    agents:                       # Agent-specific overrides
      - name: string
        # Agent override properties
    logging:                      # Logging configuration
      level: string               # Log level
      console_output: boolean     # Console logging
      file_output: boolean        # File logging
```

**Log Levels:**
- `DEBUG` - Detailed debugging information
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error messages only

**Example:**
```yaml
environments:
  development:
    ollama:
      default_model: "qwen2.5:3b"
    data_sources:
      refresh_multiplier: 10
    logging:
      level: "DEBUG"
      console_output: true
      
  production:
    ollama:
      host: "http://ollama-prod:11434"
    logging:
      level: "INFO"
      file_output: true
```

## Monitoring Configuration

### `monitoring` Section
System monitoring and alerting configuration.

```yaml
monitoring:
  enabled: boolean                # Enable monitoring
  performance:                    # Performance monitoring
    max_response_time_seconds: integer
    max_memory_usage_mb: integer
  health_checks:                  # Health check configuration
    interval_seconds: integer     # Check interval
    ollama_connectivity: boolean  # Check Ollama connection
    data_source_accessibility: boolean  # Check data sources
  alerts:                         # Alert configuration
    critical_stock_alerts: boolean
    agv_malfunction_alerts: boolean
    approval_backlog_alerts: boolean
```

**Example:**
```yaml
monitoring:
  enabled: true
  performance:
    max_response_time_seconds: 30
    max_memory_usage_mb: 1024
  health_checks:
    interval_seconds: 60
    ollama_connectivity: true
    data_source_accessibility: true
  alerts:
    critical_stock_alerts: true
    agv_malfunction_alerts: true
    approval_backlog_alerts: true
```

## Security Configuration

### `security` Section
Security and access control settings.

```yaml
security:
  api_key_required: boolean       # Require API keys
  rate_limiting:                  # Rate limiting configuration
    enabled: boolean
    requests_per_minute: integer
  encrypt_sensitive_data: boolean # Data encryption
  role_based_access: boolean      # Role-based access control
```

**Example:**
```yaml
security:
  api_key_required: false
  rate_limiting:
    enabled: true
    requests_per_minute: 60
  encrypt_sensitive_data: false
  role_based_access: false
```

## Configuration Validation

### Schema Validation
All configuration files are validated against a JSON schema to ensure:
- Required fields are present
- Data types are correct
- Values are within acceptable ranges
- References between sections are valid

### Validation Examples

**Valid Configuration:**
```yaml
system:
  name: "Valid System"
  environment: "production"
  
agents:
  - name: "ValidAgent"
    type: "inventory"
    enabled: true
```

**Invalid Configuration:**
```yaml
system:
  name: "Invalid System"
  environment: "invalid_env"  # Invalid environment
  
agents:
  - name: ""                  # Empty name not allowed
    type: "invalid_type"      # Invalid agent type
    enabled: "yes"            # Should be boolean
```

## Best Practices

### Naming Conventions
- Use descriptive, human-readable names for agents
- Use snake_case for configuration keys
- Use PascalCase for agent names
- Include environment in system name for clarity

### Configuration Organization
- Group related settings together
- Use comments to explain business rules
- Keep environment-specific overrides minimal
- Document custom prompts with business context

### Security Considerations
- Never include passwords or API keys in configuration files
- Use environment variables for sensitive data
- Restrict file permissions on configuration files
- Validate all external data sources

### Performance Optimization
- Set appropriate refresh intervals for data sources
- Use lighter models for development environments
- Limit tool calls per request to prevent loops
- Monitor resource usage and adjust thresholds