"""
Simple Application Configuration
"""
import os
from enum import Enum

class LLMBackend(Enum):
    OLLAMA = "ollama"
    BEDROCK = "bedrock"

class Config:
    """Simple application configuration class"""
    
    def __init__(self):
        # LLM Backend configuration
        llm_backend_str = os.getenv('LLM_BACKEND', 'ollama').lower()
        self.llm_backend = LLMBackend.OLLAMA if llm_backend_str == 'ollama' else LLMBackend.BEDROCK
        
        # Flask server configuration
        self.flask_host = os.getenv('FLASK_HOST', '127.0.0.1')
        self.flask_port = int(os.getenv('FLASK_PORT', 5555))
        self.flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        # Strands observability features
        self.enable_strands_observability = os.getenv('ENABLE_STRANDS_OBSERVABILITY', 'True').lower() == 'true'
        self.enable_strands_metrics = os.getenv('ENABLE_STRANDS_METRICS', 'True').lower() == 'true'
        self.enable_agent_streaming = os.getenv('ENABLE_AGENT_STREAMING', 'True').lower() == 'true'