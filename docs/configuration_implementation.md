# Configuration Implementation Guide

This guide provides technical details for implementing the configuration-driven agent factory system in the Logistics Multi-Agent System.

## Implementation Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   YAML Files    │───▶│ ConfigManager    │───▶│  AgentFactory   │
│                 │    │                  │    │   Enhanced      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ DataSourceManager│    │  GenericAgent   │
                       │                  │    │   Instances     │
                       └──────────────────┘    └─────────────────┘
```

## Core Components Implementation

### 1. Configuration Manager

Create `config/config_manager.py`:

```python
"""
Configuration Manager for YAML-based agent configuration.
"""

import yaml
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError

class ConfigurationManager:
    """Manages YAML configuration loading, validation, and environment overrides."""
    
    def __init__(self, config_path: Optional[str] = None, environment: Optional[str] = None):
        self.config_path = config_path
        self.environment = environment or os.getenv('LOGISTICS_ENV', 'development')
        self.config = {}
        self.schema = self._load_schema()
        
        if config_path:
            self.load_config(config_path, self.environment)
    
    def load_config(self, config_path: str, environment: str = None) -> Dict:
        """Load and validate configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
            
            # Validate against schema
            self.validate_schema(self.config)
            
            # Apply environment overrides
            if environment:
                self.apply_environment_overrides(self.config, environment)
                
            return self.config
            
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML syntax: {e}")
        except ValidationError as e:
            raise ConfigurationError(f"Configuration validation error: {e.message}")
    
    def validate_schema(self, config: Dict) -> bool:
        """Validate configuration against JSON schema."""
        try:
            validate(instance=config, schema=self.schema)
            return True
        except ValidationError:
            raise
    
    def apply_environment_overrides(self, config: Dict, environment: str):
        """Apply environment-specific configuration overrides."""
        if 'environments' not in config:
            return
            
        env_config = config['environments'].get(environment, {})
        
        # Override ollama settings
        if 'ollama' in env_config:
            config['ollama'].update(env_config['ollama'])
            
        # Override data source settings
        if 'data_sources' in env_config:
            self._apply_data_source_overrides(config, env_config)
            
        # Override agent settings
        if 'agents' in env_config:
            self._apply_agent_overrides(config, env_config)
    
    def _apply_data_source_overrides(self, config: Dict, env_config: Dict):
        """Apply data source overrides."""
        ds_overrides = env_config['data_sources']
        
        # Apply multiplier to refresh intervals
        if 'refresh_multiplier' in ds_overrides:
            multiplier = ds_overrides['refresh_multiplier']
            for source_name, source_config in config['data_sources'].items():
                if 'refresh_interval' in source_config:
                    source_config['refresh_interval'] *= multiplier
        
        # Override specific data sources
        for source_name, source_config in ds_overrides.items():
            if source_name in config['data_sources'] and isinstance(source_config, dict):
                config['data_sources'][source_name].update(source_config)
    
    def _apply_agent_overrides(self, config: Dict, env_config: Dict):
        """Apply agent-specific overrides."""
        agent_overrides = env_config['agents']
        
        for override in agent_overrides:
            if 'name' not in override:
                continue
                
            # Find matching agent and apply overrides
            for agent in config['agents']:
                if agent['name'] == override['name']:
                    agent.update({k: v for k, v in override.items() if k != 'name'})
    
    def get_system_config(self) -> Dict:
        """Get system configuration."""
        return self.config.get('system', {})
    
    def get_ollama_config(self) -> Dict:
        """Get Ollama configuration."""
        return self.config.get('ollama', {})
    
    def get_agent_defaults(self) -> Dict:
        """Get default agent settings."""
        return self.config.get('agent_defaults', {})
    
    def get_data_source_config(self, source_name: str) -> Dict:
        """Get configuration for a specific data source."""
        return self.config.get('data_sources', {}).get(source_name, {})
    
    def get_agent_configs(self) -> List[Dict]:
        """Get all agent configurations."""
        return self.config.get('agents', [])
    
    def get_monitoring_config(self) -> Dict:
        """Get monitoring configuration."""
        return self.config.get('monitoring', {})
    
    def _load_schema(self) -> Dict:
        """Load JSON schema for configuration validation."""
        schema_path = Path(__file__).parent / 'logistics_config_schema.json'
        
        if not schema_path.exists():
            # Return basic schema if file doesn't exist
            return self._get_basic_schema()
            
        with open(schema_path, 'r') as file:
            return json.load(file)
    
    def _get_basic_schema(self) -> Dict:
        """Get basic configuration schema for validation."""
        return {
            "type": "object",
            "required": ["system"],
            "properties": {
                "system": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                        "environment": {"enum": ["development", "staging", "production"]}
                    }
                },
                "agents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "enabled"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"enum": ["inventory", "fleet", "approval", "orchestrator"]},
                            "enabled": {"type": "boolean"}
                        }
                    }
                }
            }
        }

class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass
```

### 2. Data Source Manager

Create `config/data_source_manager.py`:

```python
"""
Data Source Manager for flexible data loading.
"""

import pandas as pd
import json
import sqlite3
from typing import Dict, Any, Optional
from pathlib import Path
import threading
import time

class DataSourceManager:
    """Manages flexible data loading from various sources."""
    
    def __init__(self):
        self.data_cache = {}
        self.refresh_threads = {}
        self.stop_refresh = {}
    
    def load_data_source(self, source_config: Dict) -> pd.DataFrame:
        """Load data from configured source."""
        source_type = source_config.get('type', 'csv').lower()
        
        if source_type == 'csv':
            return self._load_csv_data(source_config)
        elif source_type == 'json':
            return self._load_json_data(source_config)
        elif source_type == 'database':
            return self._load_database_data(source_config)
        elif source_type == 'api':
            return self._load_api_data(source_config)
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")
    
    def _load_csv_data(self, config: Dict) -> pd.DataFrame:
        """Load data from CSV file."""
        source_path = config.get('source')
        if not source_path or not Path(source_path).exists():
            raise FileNotFoundError(f"CSV file not found: {source_path}")
        
        # Load CSV with optional column mapping
        df = pd.read_csv(source_path)
        
        # Apply column mapping if specified
        column_mapping = config.get('columns', {})
        if column_mapping:
            df = df.rename(columns={v: k for k, v in column_mapping.items()})
        
        # Validate required columns
        required_columns = config.get('validation', {}).get('required_columns', [])
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        return df
    
    def _load_json_data(self, config: Dict) -> pd.DataFrame:
        """Load data from JSON file."""
        source_path = config.get('source')
        if not source_path or not Path(source_path).exists():
            raise FileNotFoundError(f"JSON file not found: {source_path}")
        
        with open(source_path, 'r') as file:
            data = json.load(file)
        
        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Handle nested JSON structure
            df = pd.json_normalize(data)
        else:
            raise ValueError("JSON data must be a list or dictionary")
        
        return df
    
    def _load_database_data(self, config: Dict) -> pd.DataFrame:
        """Load data from database."""
        connection_string = config.get('connection_string')
        query = config.get('query', "SELECT * FROM inventory")
        
        # Simple SQLite support (extend for PostgreSQL, MySQL, etc.)
        if connection_string.startswith('sqlite'):
            db_path = connection_string.replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        else:
            raise NotImplementedError("Only SQLite databases currently supported")
    
    def _load_api_data(self, config: Dict) -> pd.DataFrame:
        """Load data from API endpoint."""
        import requests
        
        endpoint = config.get('endpoint')
        auth_config = config.get('authentication', {})
        
        headers = {}
        if auth_config.get('type') == 'api_key':
            api_key = os.getenv(auth_config.get('key_env_var'))
            headers['Authorization'] = f"Bearer {api_key}"
        
        response = requests.get(endpoint, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return pd.DataFrame(data)
    
    def setup_auto_refresh(self, source_name: str, source_config: Dict):
        """Setup automatic data refresh for a source."""
        refresh_interval = source_config.get('refresh_interval', 300)  # 5 minutes default
        
        if refresh_interval <= 0:
            return  # No auto-refresh
        
        def refresh_worker():
            while not self.stop_refresh.get(source_name, False):
                try:
                    new_data = self.load_data_source(source_config)
                    self.data_cache[source_name] = new_data
                    print(f"✅ Refreshed data source: {source_name}")
                except Exception as e:
                    print(f"⚠️ Error refreshing {source_name}: {e}")
                
                time.sleep(refresh_interval)
        
        # Stop existing refresh thread if any
        self.stop_auto_refresh(source_name)
        
        # Start new refresh thread
        self.stop_refresh[source_name] = False
        thread = threading.Thread(target=refresh_worker, daemon=True)
        thread.start()
        self.refresh_threads[source_name] = thread
    
    def stop_auto_refresh(self, source_name: str):
        """Stop auto-refresh for a data source."""
        if source_name in self.refresh_threads:
            self.stop_refresh[source_name] = True
            self.refresh_threads[source_name].join(timeout=1)
            del self.refresh_threads[source_name]
            del self.stop_refresh[source_name]
    
    def get_cached_data(self, source_name: str) -> Optional[pd.DataFrame]:
        """Get cached data for a source."""
        return self.data_cache.get(source_name)
    
    def validate_data_source(self, config: Dict) -> bool:
        """Validate data source configuration and accessibility."""
        try:
            self.load_data_source(config)
            return True
        except Exception:
            return False
```

### 3. Enhanced Agent Factory

Enhance `Agents/agent_factory.py`:

```python
"""
Enhanced Agent Factory with Configuration Support
"""

from typing import Optional, Dict, List
from strands.models.ollama import OllamaModel
from generic_agent import GenericAgent
from config.config_manager import ConfigurationManager, ConfigurationError
from config.data_source_manager import DataSourceManager

# ... existing imports ...

class AgentFactory:
    """Enhanced factory for creating specialized logistics agents with configuration support."""
    
    def __init__(self, inventory_manager=None, fleet_manager=None, approval_manager=None, 
                 config_manager: Optional[ConfigurationManager] = None):
        # Existing initialization code...
        self.config_manager = config_manager
        self.data_source_manager = DataSourceManager()
        
        # If configuration is provided, load data managers from config
        if config_manager:
            self._load_data_managers_from_config()
    
    @classmethod
    def from_config(cls, config_path: str, environment: str = None):
        """Create AgentFactory from configuration file."""
        try:
            config_manager = ConfigurationManager(config_path, environment)
            factory = cls(config_manager=config_manager)
            return factory
        except ConfigurationError as e:
            print(f"❌ Configuration error: {e}")
            raise
    
    def create_agents_from_config(self) -> Dict[str, GenericAgent]:
        """Create all agents defined in configuration."""
        if not self.config_manager:
            raise ValueError("No configuration manager available")
        
        agents = {}
        agent_configs = self.config_manager.get_agent_configs()
        
        for agent_config in agent_configs:
            if not agent_config.get('enabled', True):
                continue
                
            try:
                agent = self.create_agent_from_config(agent_config)
                agents[agent_config['name']] = agent
                print(f"✅ Created agent: {agent_config['name']} ({agent_config['type']})")
            except Exception as e:
                print(f"❌ Failed to create agent {agent_config['name']}: {e}")
        
        return agents
    
    def create_agent_from_config(self, agent_config: Dict, overrides: Dict = None) -> GenericAgent:
        """Create a single agent from configuration."""
        if not self.config_manager:
            raise ValueError("No configuration manager available")
        
        # Apply overrides if provided
        if overrides:
            agent_config = {**agent_config, **overrides}
        
        # Get global defaults
        defaults = self.config_manager.get_agent_defaults()
        
        # Create Ollama model
        model = self._create_model_from_config(agent_config)
        
        # Get or create custom prompt
        custom_prompt = agent_config.get('custom_prompt')
        if not custom_prompt:
            custom_prompt = self._get_system_prompt(agent_config['type'])
        
        # Enhance prompt with specialization details
        enhanced_prompt = self._enhance_prompt_with_specialization(
            custom_prompt, agent_config.get('specialization', {}), agent_config['type']
        )
        
        # Get appropriate tools
        data_manager_tools = self._get_tools_for_agent_type(agent_config['type'])
        
        # Create agent
        return GenericAgent(
            name=agent_config['name'],
            agent_type=agent_config['type'],
            ollama_model=model,
            system_prompt=enhanced_prompt,
            enable_a2a=agent_config.get('enable_a2a', defaults.get('enable_a2a', True)),
            data_manager_tools=data_manager_tools
        )
    
    def _create_model_from_config(self, agent_config: Dict) -> OllamaModel:
        """Create Ollama model from configuration."""
        ollama_config = self.config_manager.get_ollama_config()
        
        # Determine model to use
        model_name = agent_config.get('model', 'standard')
        if model_name in ['light', 'standard', 'heavy']:
            # Use named model from config
            models = ollama_config.get('models', {})
            model_id = models.get(model_name, ollama_config.get('default_model', 'qwen2.5:7b'))
        else:
            # Use model name directly
            model_id = model_name
        
        return self.create_ollama_model(
            host=ollama_config.get('host', 'http://localhost:11434'),
            model_id=model_id
        )
    
    def _enhance_prompt_with_specialization(self, base_prompt: str, specialization: Dict, agent_type: str) -> str:
        """Enhance base prompt with specialization details."""
        if not specialization:
            return base_prompt
        
        enhancement = "\n\nSPECIALIZATION DETAILS:\n"
        
        if agent_type == 'inventory':
            if 'low_stock_threshold' in specialization:
                enhancement += f"- Alert on low stock when quantities below {specialization['low_stock_threshold']} units\n"
            if 'critical_stock_threshold' in specialization:
                enhancement += f"- Critical alert when quantities below {specialization['critical_stock_threshold']} units\n"
            if 'focus_categories' in specialization:
                enhancement += f"- Priority categories: {', '.join(specialization['focus_categories'])}\n"
            if 'priority_locations' in specialization:
                enhancement += f"- Priority locations: {', '.join(specialization['priority_locations'])}\n"
                
        elif agent_type == 'fleet':
            if 'max_concurrent_agvs' in specialization:
                enhancement += f"- Maximum concurrent AGVs: {specialization['max_concurrent_agvs']}\n"
            if 'battery_return_threshold' in specialization:
                enhancement += f"- Return AGVs to charge when battery below {specialization['battery_return_threshold']}%\n"
            if 'route_optimization' in specialization:
                enhancement += f"- Route optimization strategy: {specialization['route_optimization']}\n"
                
        elif agent_type == 'approval':
            if 'auto_approve_limit' in specialization:
                enhancement += f"- Auto-approve requests under ${specialization['auto_approve_limit']}\n"
            if 'require_manager_approval' in specialization:
                enhancement += f"- Manager approval required above ${specialization['require_manager_approval']}\n"
            if 'escalation_time_hours' in specialization:
                enhancement += f"- Escalate if not approved within {specialization['escalation_time_hours']} hours\n"
        
        return base_prompt + enhancement
    
    def _load_data_managers_from_config(self):
        """Load and create data managers from configuration."""
        # Load inventory data
        inventory_config = self.config_manager.get_data_source_config('inventory')
        if inventory_config:
            inventory_data = self.data_source_manager.load_data_source(inventory_config)
            # Create inventory manager from data (implementation depends on existing structure)
            # self.inventory_manager = create_inventory_manager_from_df(inventory_data)
            
        # Similar for fleet and approval data sources...
        
    def _get_tools_for_agent_type(self, agent_type: str) -> List:
        """Get appropriate tools for agent type (existing logic)."""
        # This uses the existing logic from the original create_agent method
        if agent_type.lower() == "inventory":
            return self.inventory_tools
        elif agent_type.lower() == "fleet":
            return self.fleet_tools
        elif agent_type.lower() in ["approver", "approval"]:
            return self.approval_tools
        elif agent_type.lower() == "orchestrator":
            return self.inventory_tools + self.fleet_tools + self.approval_tools
        else:
            return self.inventory_tools + self.fleet_tools + self.approval_tools

# Convenience function for configuration-driven initialization
def initialize_agent_factory_from_config(config_path: str, environment: str = None) -> AgentFactory:
    """Initialize agent factory from configuration file."""
    try:
        factory = AgentFactory.from_config(config_path, environment)
        
        # Create all configured agents
        agents = factory.create_agents_from_config()
        
        print(f"✅ Agent Factory initialized from configuration!")
        print(f"📋 Configuration: {config_path}")
        print(f"🌍 Environment: {environment or 'development'}")
        print(f"🤖 Created {len(agents)} agents")
        
        return factory, agents
        
    except Exception as e:
        print(f"❌ Failed to initialize from configuration: {e}")
        raise
```

### 4. Configuration Schema

Create `config/logistics_config_schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Logistics Multi-Agent System Configuration",
  "type": "object",
  "required": ["system"],
  "properties": {
    "system": {
      "type": "object",
      "required": ["name"],
      "properties": {
        "name": {"type": "string"},
        "version": {"type": "string"},
        "environment": {"enum": ["development", "staging", "production"]},
        "description": {"type": "string"}
      }
    },
    "ollama": {
      "type": "object",
      "properties": {
        "host": {"type": "string", "format": "uri"},
        "default_model": {"type": "string"},
        "timeout_seconds": {"type": "integer", "minimum": 1},
        "retry_attempts": {"type": "integer", "minimum": 0},
        "models": {
          "type": "object",
          "properties": {
            "light": {"type": "string"},
            "standard": {"type": "string"},
            "heavy": {"type": "string"}
          }
        }
      }
    },
    "agents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "type", "enabled"],
        "properties": {
          "name": {"type": "string"},
          "type": {"enum": ["inventory", "fleet", "approval", "orchestrator"]},
          "enabled": {"type": "boolean"},
          "model": {"type": "string"},
          "custom_prompt": {"type": "string"},
          "specialization": {"type": "object"}
        }
      }
    }
  }
}
```

## Usage Examples

### Basic Usage
```python
# Load configuration and create agents
factory, agents = initialize_agent_factory_from_config(
    config_path="config/production_config.yaml",
    environment="production"
)

# Use agents
inventory_agent = agents["WarehouseInventoryBot"]
response = inventory_agent.send_message("Check stock levels")
```

### Custom Overrides
```python
# Create factory from config
factory = AgentFactory.from_config("config/base_config.yaml")

# Create agent with custom overrides
custom_agent = factory.create_agent_from_config(
    agent_config={
        "name": "CustomInventoryBot",
        "type": "inventory", 
        "enabled": True,
        "model": "heavy"
    },
    overrides={
        "custom_prompt": "You are a specialized agent for high-value items..."
    }
)
```

## Testing and Validation

### Configuration Validation Tool
Create `tools/validate_config.py`:

```python
#!/usr/bin/env python3
"""
Configuration validation tool.
"""

import sys
import argparse
from config.config_manager import ConfigurationManager, ConfigurationError

def main():
    parser = argparse.ArgumentParser(description="Validate logistics configuration")
    parser.add_argument("config_file", help="Path to configuration file")
    parser.add_argument("--environment", help="Environment to validate")
    
    args = parser.parse_args()
    
    try:
        config_manager = ConfigurationManager()
        config_manager.load_config(args.config_file, args.environment)
        print(f"✅ Configuration is valid: {args.config_file}")
        
        # Additional validation checks
        agents = config_manager.get_agent_configs()
        print(f"📊 Found {len(agents)} agent configurations")
        
        for agent in agents:
            if agent.get('enabled', True):
                print(f"  - {agent['name']} ({agent['type']})")
                
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Unit Tests
```python
# tests/test_configuration.py
import unittest
import tempfile
import yaml
from config.config_manager import ConfigurationManager, ConfigurationError

class TestConfigurationManager(unittest.TestCase):
    
    def setUp(self):
        self.valid_config = {
            "system": {"name": "Test System"},
            "agents": [
                {"name": "TestAgent", "type": "inventory", "enabled": True}
            ]
        }
    
    def test_load_valid_config(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.valid_config, f)
            
        config_manager = ConfigurationManager()
        config = config_manager.load_config(f.name)
        
        self.assertEqual(config['system']['name'], 'Test System')
        self.assertEqual(len(config['agents']), 1)
    
    def test_invalid_config_raises_error(self):
        invalid_config = {"invalid": "config"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            
        config_manager = ConfigurationManager()
        
        with self.assertRaises(ConfigurationError):
            config_manager.load_config(f.name)
```

## Migration Path

### Phase 1: Add Configuration Support
1. Add dependencies: `pip install pyyaml jsonschema`
2. Create configuration manager and data source manager
3. Enhance AgentFactory with configuration support
4. Keep existing programmatic interface working

### Phase 2: Create Configuration Files
1. Generate configuration files from existing setups
2. Test configuration-driven agent creation
3. Validate against existing programmatic creation

### Phase 3: Full Migration
1. Update main application to use configuration
2. Create environment-specific configurations
3. Add monitoring and validation tools
4. Update documentation and training

This implementation provides a robust, flexible configuration system that maintains backward compatibility while enabling powerful new configuration-driven capabilities.