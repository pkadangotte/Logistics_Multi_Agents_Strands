#!/bin/bash
"""
Logistics Multi-Agent System Demo Launcher

Simple launcher script for the interactive demo.
"""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
    echo "🐍 Using virtual environment Python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python" 
    echo "🐍 Using virtual environment Python"
else
    PYTHON_CMD="python3"
    echo "🐍 Using system Python"
fi

echo "🎬 Launching Logistics Multi-Agent System Demo..."
echo "📂 Working directory: $SCRIPT_DIR"

# Run the demo
$PYTHON_CMD demo.py "$@"