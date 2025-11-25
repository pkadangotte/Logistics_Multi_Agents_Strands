# Configuration System Examples

This document provides practical examples of YAML configuration files for different use cases and deployment scenarios in the Logistics Multi-Agent System.

## Basic Configuration Examples

### Minimal Configuration
The simplest possible configuration for getting started.

```yaml
# minimal_config.yaml
system:
  name: "Basic Logistics System"
  environment: "development"

agents:
  - name: "SimpleInventory"
    type: "inventory"
    enabled: true
    
  - name: "SimpleFleet"
    type: "fleet"
    enabled: true
    
  - name: "SimpleOrchestrator"
    type: "orchestrator"  
    enabled: true
```

### Small Warehouse Configuration
Configuration for a small warehouse operation.

```yaml
# small_warehouse_config.yaml
system:
  name: "Small Warehouse Logistics"
  version: "1.0.0"
  environment: "production"

ollama:
  host: "http://localhost:11434"
  default_model: "qwen2.5:7b"

data_sources:
  inventory:
    type: "csv"
    source: "data/small_warehouse_inventory.csv"
    refresh_interval: 600  # 10 minutes
    validation:
      quantity_min: 0
      
  fleet:
    type: "csv"
    agv_source: "data/small_warehouse_agvs.csv"
    routes_source: "data/small_warehouse_routes.csv"
    refresh_interval: 300  # 5 minutes

agents:
  - name: "WarehouseInventoryManager"
    type: "inventory"
    enabled: true
    model: "standard"
    custom_prompt: |
      You manage inventory for a small warehouse with 500+ SKUs.
      Focus on preventing stockouts and optimizing storage space.
    specialization:
      low_stock_threshold: 5
      critical_stock_threshold: 2
      focus_categories: ["FastMoving", "Critical"]
      
  - name: "AGVController"
    type: "fleet"
    enabled: true
    model: "standard"
    specialization:
      max_concurrent_agvs: 2
      battery_return_threshold: 25
      route_optimization: "time"
      
  - name: "OperationsCoordinator"
    type: "orchestrator"
    enabled: true
    model: "heavy"
    specialization:
      coordination_style: "proactive"
      reporting_frequency: "daily"
```

## Enterprise Configuration Examples

### Large Distribution Center
Configuration for a large-scale distribution center with multiple zones.

```yaml
# enterprise_distribution_config.yaml
system:
  name: "Enterprise Distribution Center"
  version: "2.1.0"
  environment: "production"
  description: "Multi-zone distribution center with 50,000+ SKUs"

ollama:
  host: "http://ollama-cluster:11434"
  default_model: "qwen2.5:14b"
  timeout_seconds: 60
  retry_attempts: 5

agent_defaults:
  enable_a2a: true
  conversation_history: true
  error_handling: "graceful"
  max_tool_calls_per_request: 8

data_sources:
  inventory:
    type: "database"
    connection_string: "postgresql://user:pass@inventory-db:5432/warehouse"
    refresh_interval: 120  # 2 minutes for high-frequency updates
    validation:
      required_columns: ["sku", "description", "quantity", "zone", "bin"]
      quantity_min: 0
      
  fleet:
    type: "api"
    agv_endpoint: "https://api.agv-system.com/v1/fleet"
    routes_endpoint: "https://api.agv-system.com/v1/routes"
    refresh_interval: 30  # 30 seconds for real-time tracking
    authentication:
      type: "api_key"
      key_env_var: "AGV_API_KEY"
      
  approval:
    type: "database"
    connection_string: "postgresql://user:pass@approval-db:5432/compliance"
    refresh_interval: 300

agents:
  # Zone-specific inventory agents
  - name: "ZoneA_InventoryAgent"
    type: "inventory"
    enabled: true
    model: "heavy"
    custom_prompt: |
      You manage inventory for Zone A (Electronics & High-Value Items).
      Maintain strict accuracy and security protocols.
      Monitor for theft indicators and compliance violations.
    specialization:
      low_stock_threshold: 25
      critical_stock_threshold: 10
      focus_categories: ["Electronics", "HighValue", "Security"]
      priority_locations: ["A1", "A2", "A3", "SECURE-A"]
      
  - name: "ZoneB_InventoryAgent"
    type: "inventory"
    enabled: true
    model: "standard"
    custom_prompt: |
      You manage inventory for Zone B (Bulk Items & General Merchandise).
      Focus on efficient space utilization and bulk movement optimization.
    specialization:
      low_stock_threshold: 100
      critical_stock_threshold: 25
      focus_categories: ["Bulk", "General", "Seasonal"]
      priority_locations: ["B1", "B2", "B3", "B4"]
      
  # Fleet management for different AGV types
  - name: "HeavyLiftr_FleetManager"
    type: "fleet"
    enabled: true
    model: "heavy"
    custom_prompt: |
      You coordinate heavy-lift AGVs for palletized goods.
      Prioritize safety and load balancing across the facility.
    specialization:
      max_concurrent_agvs: 8
      battery_return_threshold: 15  # Lower threshold for heavy-duty AGVs
      route_optimization: "energy"  # Energy efficiency for heavy loads
      collision_avoidance: true
      maintenance_alerts: true
      
  - name: "PickBot_FleetManager"  
    type: "fleet"
    enabled: true
    model: "standard"
    custom_prompt: |
      You coordinate lightweight picking robots for order fulfillment.
      Optimize for speed and order completion times.
    specialization:
      max_concurrent_agvs: 15
      battery_return_threshold: 20
      route_optimization: "time"
      
  # Compliance and approval agents
  - name: "SafetyComplianceAgent"
    type: "approval"
    enabled: true
    model: "heavy"
    custom_prompt: |
      You ensure all operations comply with safety regulations and OSHA standards.
      Prioritize worker safety over operational efficiency when conflicts arise.
    specialization:
      auto_approve_limit: 100
      require_manager_approval: 5000
      require_justification: 1000
      escalation_time_hours: 4  # Faster escalation for safety issues
      compliance_categories: ["Safety", "OSHA", "Environmental"]
      
  - name: "FinancialApprovalAgent"
    type: "approval" 
    enabled: true
    model: "standard"
    custom_prompt: |
      You manage financial approvals and budget compliance for logistics operations.
      Ensure all expenditures are properly authorized and within budget limits.
    specialization:
      auto_approve_limit: 1000
      require_manager_approval: 10000
      require_justification: 2500
      escalation_time_hours: 12
      compliance_categories: ["Financial", "Budget", "Procurement"]
      
  # Master orchestrator
  - name: "DistributionCenterOrchestrator"
    type: "orchestrator"
    enabled: true
    model: "heavy"
    custom_prompt: |
      You are the Master Orchestrator for a large distribution center.
      Coordinate complex multi-zone operations, resolve conflicts between zones,
      and optimize overall facility performance. Handle escalated issues from
      specialized agents and provide executive reporting.
    specialization:
      coordination_style: "predictive"
      conflict_resolution: "cost_optimized"
      reporting_frequency: "hourly"
      escalation_enabled: true
      cross_domain_optimization: true

monitoring:
  enabled: true
  performance:
    max_response_time_seconds: 45
    max_memory_usage_mb: 2048
  health_checks:
    interval_seconds: 30
    ollama_connectivity: true
    data_source_accessibility: true
  alerts:
    critical_stock_alerts: true
    agv_malfunction_alerts: true
    approval_backlog_alerts: true

environments:
  production:
    monitoring:
      alerts:
        email_notifications: true
        slack_webhook: "https://hooks.slack.com/services/..."
```

## Specialized Use Case Examples

### E-commerce Fulfillment Center
Configuration optimized for high-velocity e-commerce operations.

```yaml
# ecommerce_fulfillment_config.yaml
system:
  name: "E-commerce Fulfillment Center"
  environment: "production"

ollama:
  default_model: "qwen2.5:14b"  # High-performance model for speed

agents:
  - name: "FastMoving_InventoryAgent"
    type: "inventory"
    enabled: true
    model: "heavy"
    custom_prompt: |
      You manage fast-moving inventory for e-commerce fulfillment.
      Prioritize order fulfillment speed and same-day shipping capabilities.
      Monitor trending products and seasonal demand patterns.
    specialization:
      low_stock_threshold: 50   # Higher thresholds for fast movers
      critical_stock_threshold: 20
      focus_categories: ["Trending", "SameDay", "Prime"]
      priority_locations: ["PICK-ZONE-1", "PICK-ZONE-2"]
      
  - name: "OrderFulfillment_FleetManager"
    type: "fleet" 
    enabled: true
    model: "heavy"
    custom_prompt: |
      You coordinate AGVs for rapid order fulfillment operations.
      Optimize for order completion speed and customer satisfaction.
      Handle peak hour scaling and rush order prioritization.
    specialization:
      max_concurrent_agvs: 20
      battery_return_threshold: 25
      route_optimization: "time"  # Speed over energy efficiency
      rush_order_priority: true
      
  - name: "ShippingApprovalAgent"
    type: "approval"
    enabled: true
    custom_prompt: |
      You handle shipping method approvals and expedited shipping requests.
      Balance cost efficiency with customer satisfaction and delivery promises.
    specialization:
      auto_approve_limit: 25      # Low auto-approve for shipping costs
      expedited_shipping_threshold: 100
      same_day_approval_required: true
```

### Manufacturing Supply Chain
Configuration for manufacturing supply chain integration.

```yaml
# manufacturing_supply_chain_config.yaml
system:
  name: "Manufacturing Supply Chain Logistics"
  environment: "production"

data_sources:
  inventory:
    type: "erp_integration"
    erp_system: "SAP"
    connection_string: "sap://prod-server:3300"
    refresh_interval: 60  # Frequent updates for production
    
  fleet:
    type: "mes_integration" 
    mes_system: "Wonderware"
    refresh_interval: 15   # Very frequent for production line coordination

agents:
  - name: "RawMaterials_InventoryAgent"
    type: "inventory"
    enabled: true
    custom_prompt: |
      You manage raw materials inventory for continuous manufacturing.
      Prevent production line stoppages due to material shortages.
      Coordinate with suppliers for just-in-time deliveries.
    specialization:
      low_stock_threshold: 2   # Measured in days of production
      critical_stock_threshold: 0.5
      focus_categories: ["RawMaterials", "JIT", "Critical"]
      production_line_priority: true
      
  - name: "ProductionLine_FleetManager"
    type: "fleet"
    enabled: true 
    custom_prompt: |
      You coordinate material transport AGVs for production lines.
      Maintain continuous flow to prevent line stoppages.
      Prioritize critical path materials and bottleneck prevention.
    specialization:
      max_concurrent_agvs: 12
      production_line_priority: true
      route_optimization: "reliability"  # Consistency over speed
      predictive_scheduling: true
```

## Environment-Specific Examples

### Development Environment Configuration
```yaml
# development_config.yaml
system:
  name: "Development Environment"
  environment: "development"

ollama:
  host: "http://localhost:11434"
  default_model: "qwen2.5:3b"  # Lightweight for development

agent_defaults:
  max_tool_calls_per_request: 2  # Limited for testing

data_sources:
  inventory:
    type: "csv"
    source: "test_data/sample_inventory.csv"
    refresh_interval: 3600  # Slow refresh for development
    
agents:
  - name: "DevInventoryAgent"
    type: "inventory"
    enabled: true
    model: "light"
    specialization:
      low_stock_threshold: 2  # Low thresholds for small test data
      critical_stock_threshold: 1

environments:
  development:
    logging:
      level: "DEBUG"
      console_output: true
    data_sources:
      use_sample_data: true
```

### Staging Environment Configuration  
```yaml
# staging_config.yaml
system:
  name: "Staging Environment"
  environment: "staging"

ollama:
  host: "http://ollama-staging:11434"
  default_model: "qwen2.5:7b"

data_sources:
  inventory:
    type: "database"
    connection_string: "postgresql://user:pass@staging-db:5432/warehouse"
    refresh_interval: 300

agents:
  - name: "StagingInventoryAgent"
    type: "inventory"
    enabled: true
    model: "standard"
    # Use production-like configuration with staging data

environments:
  staging:
    logging:
      level: "INFO"
      file_output: true
    monitoring:
      performance_monitoring: true
```

## Configuration Templates

### Starter Template
```yaml
# starter_template.yaml
# Copy this file and customize for your environment

system:
  name: "YOUR_SYSTEM_NAME_HERE"
  version: "1.0.0" 
  environment: "development"  # Change to production when ready

ollama:
  host: "http://localhost:11434"  # Update for your Ollama server
  default_model: "qwen2.5:7b"

data_sources:
  inventory:
    type: "csv"  # Change to database/api as needed
    source: "data/your_inventory.csv"  # Update path
    refresh_interval: 300
    
  fleet:
    type: "csv"
    agv_source: "data/your_agvs.csv"  # Update path
    routes_source: "data/your_routes.csv"  # Update path  
    refresh_interval: 60

agents:
  - name: "YOUR_INVENTORY_AGENT"  # Customize name
    type: "inventory"
    enabled: true
    model: "standard"
    custom_prompt: |
      # Add your specific instructions here
      You are responsible for inventory management in YOUR_FACILITY.
    specialization:
      low_stock_threshold: 10  # Adjust for your needs
      critical_stock_threshold: 3  # Adjust for your needs
      
  - name: "YOUR_FLEET_AGENT"  # Customize name
    type: "fleet"
    enabled: true
    model: "standard"
    specialization:
      max_concurrent_agvs: 3  # Adjust for your fleet size
      battery_return_threshold: 20
      
  - name: "YOUR_ORCHESTRATOR"  # Customize name
    type: "orchestrator"
    enabled: true
    model: "heavy"
```

### Production Template
```yaml
# production_template.yaml
# Production-ready template with monitoring and security

system:
  name: "PRODUCTION_SYSTEM_NAME"
  version: "1.0.0"
  environment: "production"

ollama:
  host: "http://ollama-prod:11434"  # Production server
  default_model: "qwen2.5:14b"      # Production-grade model
  timeout_seconds: 60
  retry_attempts: 5

agent_defaults:
  enable_a2a: true
  conversation_history: true
  error_handling: "graceful"

data_sources:
  # Configure your production data sources
  inventory:
    type: "database"  # Recommended for production
    connection_string: "REPLACE_WITH_YOUR_CONNECTION_STRING"
    refresh_interval: 120
    
monitoring:
  enabled: true
  performance:
    max_response_time_seconds: 30
    max_memory_usage_mb: 2048
  health_checks:
    interval_seconds: 60
    ollama_connectivity: true
    data_source_accessibility: true
  alerts:
    critical_stock_alerts: true
    agv_malfunction_alerts: true
    approval_backlog_alerts: true

security:
  api_key_required: true  # Enable for production
  rate_limiting:
    enabled: true
    requests_per_minute: 120
    
# Add your production agents here
agents: []
```

## Migration Examples

### From Programmatic to Configuration-Driven
Shows how to convert existing programmatic agent creation to configuration.

**Before (Programmatic):**
```python
# Old way - in Python code
factory = AgentFactory(inventory_manager, fleet_manager, approval_manager)

inventory_agent = factory.create_agent(
    agent_type="inventory",
    name="WarehouseBot", 
    model_id="qwen2.5:7b",
    custom_prompt="You manage warehouse inventory..."
)
```

**After (Configuration-Driven):**
```yaml
# New way - in YAML config
agents:
  - name: "WarehouseBot"
    type: "inventory"
    enabled: true
    model: "standard"  # Maps to qwen2.5:7b
    custom_prompt: |
      You manage warehouse inventory...
```

This comprehensive set of examples demonstrates the flexibility and power of the configuration-driven approach, showing how different organizations and use cases can be supported through YAML configuration files without any code changes.