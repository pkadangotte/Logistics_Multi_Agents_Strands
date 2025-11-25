# Requirements and Setup
# Run this to install required packages:
# pip install pandas ollama strands-agents strands-tools

import ollama
from typing import List, Dict, Any, Optional
import json
from strands.models.ollama import OllamaModel
from strands.agent import Agent as StrandsAgent
from strands_tools.a2a_client import A2AClientToolProvider
import pandas as pd