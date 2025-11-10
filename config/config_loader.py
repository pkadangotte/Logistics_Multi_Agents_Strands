#!/usr/bin/env python3
"""
Configuration Loader for Multi-Agent Logistics System
===================================================

This module provides centralized configuration loading for all agents and system components.
All test data and system settings are loaded from JSON configuration files.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigLoader:
    """
    Centralized configuration loader that manages all system configuration files.
    Provides easy access to inventory, fleet, AGV, approver, and system settings.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_cache = {}
        self.last_loaded = {}
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration file mappings
        self.config_files = {
            'inventory': 'inventory_config.json',
            'fleet': 'fleet_config.json', 
            'agv': 'agv_config.json',
            'approver': 'approver_config.json',
            'system': 'system_config.json'
        }
        
        logger.info(f"📁 ConfigLoader initialized with directory: {self.config_dir}")

    def _load_json_file(self, filename: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load a JSON configuration file with caching support.
        
        Args:
            filename: Name of the JSON file to load
            use_cache: Whether to use cached version if available
            
        Returns:
            Dict containing the configuration data
        """
        filepath = self.config_dir / filename
        
        try:
            # Check if file exists
            if not filepath.exists():
                logger.error(f"❌ Configuration file not found: {filepath}")
                return {}
            
            # Check cache if enabled
            if use_cache and filename in self.config_cache:
                file_mtime = filepath.stat().st_mtime
                cached_mtime = self.last_loaded.get(filename, 0)
                
                if file_mtime <= cached_mtime:
                    logger.debug(f"📋 Using cached config: {filename}")
                    return self.config_cache[filename]
            
            # Load fresh from file
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Update cache
            self.config_cache[filename] = config_data
            self.last_loaded[filename] = filepath.stat().st_mtime
            
            logger.info(f"📋 Loaded configuration: {filename}")
            return config_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error in {filepath}: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ Error loading {filepath}: {e}")
            return {}

    def get_inventory_config(self) -> Dict[str, Any]:
        """
        Get inventory configuration including parts catalog and demand history.
        
        Returns:
            Dict with inventory configuration data
        """
        return self._load_json_file(self.config_files['inventory'])

    def get_fleet_config(self) -> Dict[str, Any]:
        """
        Get fleet configuration including AGV fleet and routes.
        
        Returns:
            Dict with fleet configuration data
        """
        return self._load_json_file(self.config_files['fleet'])

    def get_agv_config(self) -> Dict[str, Any]:
        """
        Get AGV configuration including models and navigation points.
        
        Returns:
            Dict with AGV configuration data
        """
        return self._load_json_file(self.config_files['agv'])

    def get_approver_config(self) -> Dict[str, Any]:
        """
        Get approver configuration including rules and thresholds.
        
        Returns:
            Dict with approver configuration data
        """
        return self._load_json_file(self.config_files['approver'])

    def get_system_config(self) -> Dict[str, Any]:
        """
        Get system configuration including server settings and AI config.
        
        Returns:
            Dict with system configuration data
        """
        return self._load_json_file(self.config_files['system'])

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all configuration data at once.
        
        Returns:
            Dict containing all configuration sections
        """
        return {
            'inventory': self.get_inventory_config(),
            'fleet': self.get_fleet_config(),
            'agv': self.get_agv_config(),
            'approver': self.get_approver_config(),
            'system': self.get_system_config()
        }

    def reload_config(self, config_name: str = None) -> bool:
        """
        Force reload configuration from files, bypassing cache.
        
        Args:
            config_name: Specific config to reload (optional, defaults to all)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if config_name:
                if config_name in self.config_files:
                    filename = self.config_files[config_name]
                    if filename in self.config_cache:
                        del self.config_cache[filename]
                    if filename in self.last_loaded:
                        del self.last_loaded[filename]
                    self._load_json_file(filename, use_cache=False)
                    logger.info(f"🔄 Reloaded config: {config_name}")
                else:
                    logger.error(f"❌ Unknown config name: {config_name}")
                    return False
            else:
                # Reload all configs
                self.config_cache.clear()
                self.last_loaded.clear()
                for config_name, filename in self.config_files.items():
                    self._load_json_file(filename, use_cache=False)
                logger.info("🔄 Reloaded all configurations")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reloading config: {e}")
            return False

    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """
        Save configuration data to file.
        
        Args:
            config_name: Name of the config section to save
            config_data: Configuration data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if config_name not in self.config_files:
                logger.error(f"❌ Unknown config name: {config_name}")
                return False
            
            filename = self.config_files[config_name]
            filepath = self.config_dir / filename
            
            # Create backup if file exists
            if filepath.exists():
                backup_path = filepath.with_suffix(f'.backup_{int(datetime.now().timestamp())}.json')
                filepath.rename(backup_path)
                logger.info(f"💾 Created backup: {backup_path.name}")
            
            # Save new configuration
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            # Update cache
            self.config_cache[filename] = config_data
            self.last_loaded[filename] = filepath.stat().st_mtime
            
            logger.info(f"💾 Saved configuration: {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving config {config_name}: {e}")
            return False

    def validate_configs(self) -> Dict[str, bool]:
        """
        Validate all configuration files for required fields and data integrity.
        
        Returns:
            Dict with validation results for each config
        """
        validation_results = {}
        
        try:
            # Validate inventory config
            inventory_config = self.get_inventory_config()
            validation_results['inventory'] = self._validate_inventory_config(inventory_config)
            
            # Validate fleet config
            fleet_config = self.get_fleet_config()
            validation_results['fleet'] = self._validate_fleet_config(fleet_config)
            
            # Validate AGV config
            agv_config = self.get_agv_config()
            validation_results['agv'] = self._validate_agv_config(agv_config)
            
            # Validate approver config
            approver_config = self.get_approver_config()
            validation_results['approver'] = self._validate_approver_config(approver_config)
            
            # Validate system config
            system_config = self.get_system_config()
            validation_results['system'] = self._validate_system_config(system_config)
            
        except Exception as e:
            logger.error(f"❌ Config validation error: {e}")
            
        return validation_results

    def _validate_inventory_config(self, config: Dict[str, Any]) -> bool:
        """Validate inventory configuration structure"""
        required_fields = ['parts_catalog', 'demand_history', 'warehouse_locations']
        return all(field in config for field in required_fields)

    def _validate_fleet_config(self, config: Dict[str, Any]) -> bool:
        """Validate fleet configuration structure"""
        required_fields = ['agv_fleet', 'routes', 'delivery_destinations']
        return all(field in config for field in required_fields)

    def _validate_agv_config(self, config: Dict[str, Any]) -> bool:
        """Validate AGV configuration structure"""
        required_fields = ['agv_models', 'base_locations', 'navigation_points']
        return all(field in config for field in required_fields)

    def _validate_approver_config(self, config: Dict[str, Any]) -> bool:
        """Validate approver configuration structure"""
        required_fields = ['approver_agents', 'approval_rules', 'risk_factors']
        return all(field in config for field in required_fields)

    def _validate_system_config(self, config: Dict[str, Any]) -> bool:
        """Validate system configuration structure"""
        required_fields = ['system_settings', 'ui_config', 'demo_mode']
        return all(field in config for field in required_fields)

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all loaded configurations.
        
        Returns:
            Dict with configuration summary statistics
        """
        try:
            configs = self.get_all_configs()
            
            summary = {
                'config_directory': str(self.config_dir),
                'loaded_configs': list(self.config_cache.keys()),
                'validation_results': self.validate_configs(),
                'statistics': {
                    'inventory': {
                        'total_parts': len(configs.get('inventory', {}).get('parts_catalog', {})),
                        'warehouse_locations': len(configs.get('inventory', {}).get('warehouse_locations', []))
                    },
                    'fleet': {
                        'total_agvs': len(configs.get('fleet', {}).get('agv_fleet', {})),
                        'total_routes': len(configs.get('fleet', {}).get('routes', {})),
                        'delivery_destinations': len(configs.get('fleet', {}).get('delivery_destinations', []))
                    },
                    'agv': {
                        'agv_models': len(configs.get('agv', {}).get('agv_models', {})),
                        'navigation_points': len(configs.get('agv', {}).get('navigation_points', {}))
                    },
                    'approver': {
                        'approver_agents': len(configs.get('approver', {}).get('approver_agents', [])),
                        'cost_thresholds': len(configs.get('approver', {}).get('approval_rules', {}).get('cost_thresholds', {}))
                    }
                },
                'last_updated': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating config summary: {e}")
            return {'error': str(e)}

# Global configuration loader instance
config_loader = ConfigLoader()

# Convenience functions for easy access
def get_inventory_config() -> Dict[str, Any]:
    """Get inventory configuration"""
    return config_loader.get_inventory_config()

def get_fleet_config() -> Dict[str, Any]:
    """Get fleet configuration"""
    return config_loader.get_fleet_config()

def get_agv_config() -> Dict[str, Any]:
    """Get AGV configuration"""
    return config_loader.get_agv_config()

def get_approver_config() -> Dict[str, Any]:
    """Get approver configuration"""
    return config_loader.get_approver_config()

def get_system_config() -> Dict[str, Any]:
    """Get system configuration"""
    return config_loader.get_system_config()

def reload_all_configs() -> bool:
    """Reload all configuration files"""
    return config_loader.reload_config()

def get_config_summary() -> Dict[str, Any]:
    """Get configuration summary"""
    return config_loader.get_config_summary()

if __name__ == "__main__":
    # Test configuration loading
    print("🔧 Testing Configuration Loader")
    print("=" * 50)
    
    try:
        # Test loading all configs
        all_configs = config_loader.get_all_configs()
        print(f"✅ Loaded {len(all_configs)} configuration sections")
        
        # Test validation
        validation = config_loader.validate_configs()
        print(f"📋 Validation results: {validation}")
        
        # Test summary
        summary = config_loader.get_config_summary()
        print(f"📊 Configuration summary:")
        print(f"   - Total parts: {summary['statistics']['inventory']['total_parts']}")
        print(f"   - Total AGVs: {summary['statistics']['fleet']['total_agvs']}")
        print(f"   - Routes: {summary['statistics']['fleet']['total_routes']}")
        print(f"   - Approver agents: {summary['statistics']['approver']['approver_agents']}")
        
        print("\n🎉 Configuration system ready!")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")