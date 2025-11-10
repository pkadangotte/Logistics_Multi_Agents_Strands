"""
Application Configuration - Central Config System
"""
import sys
import os
from enum import Enum
from pathlib import Path

# Add config path for imports
sys.path.append(str(Path(__file__).parent))
from config.config_loader import get_system_config

class LLMBackend(Enum):
    OLLAMA = "ollama"
    BEDROCK = "bedrock"

class Config:
    """Application configuration class using central config system"""
    
    def __init__(self):
        # Load from central configuration
        system_config = get_system_config()
        
        # Server configuration
        server_config = system_config.get('system_settings', {}).get('server_config', {})
        self.flask_host = server_config.get('host', '127.0.0.1')
        self.flask_port = server_config.get('port', 5555)
        self.flask_debug = server_config.get('debug_mode', False)
        
        # AI/LLM Backend configuration
        ai_config = system_config.get('system_settings', {}).get('ai_config', {})
        llm_backend_str = ai_config.get('llm_backend', 'ollama').lower()
        self.llm_backend = LLMBackend.OLLAMA if llm_backend_str == 'ollama' else LLMBackend.BEDROCK
        
        # Strands observability features
        strands_config = system_config.get('system_settings', {}).get('strands_config', {})
        self.enable_strands_observability = strands_config.get('enable_observability', True)
        self.enable_strands_metrics = strands_config.get('enable_metrics', True)
        self.enable_agent_streaming = strands_config.get('enable_agent_streaming', True)