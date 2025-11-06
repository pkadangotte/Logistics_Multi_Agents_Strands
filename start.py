#!/usr/bin/env python3
"""
Flask Server Startup Script
===========================

This script starts the Flask logistics dashboard server in the background
and provides useful information about how to access and manage it.
"""

import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path

def find_flask_processes():
    """Find all running Flask processes for this application."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'flask_app.py' in ' '.join(proc.info['cmdline']):
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def is_server_running():
    """Check if the Flask server is already running."""
    return len(find_flask_processes()) > 0

def start_server():
    """Start the Flask server."""
    print("🚀 Starting Flask Logistics Dashboard Server...")
    print("=" * 60)
    
    # Check if server is already running
    if is_server_running():
        print("⚠️  Server is already running!")
        running_processes = find_flask_processes()
        for proc in running_processes:
            print(f"   PID: {proc.pid}")
        print("\n💡 Use stop.py to stop the server first, or check http://127.0.0.1:5555")
        return False
    
    # Get the current directory and python path
    current_dir = Path(__file__).parent
    venv_python = current_dir / ".venv" / "bin" / "python"
    flask_app = current_dir / "flask_app.py"
    
    # Check if virtual environment exists
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        print(f"   Expected: {venv_python}")
        print("   Please run: python -m venv .venv")
        return False
    
    # Check if flask_app.py exists
    if not flask_app.exists():
        print("❌ Flask app not found!")
        print(f"   Expected: {flask_app}")
        return False
    
    try:
        # Start the server in the background
        print("📦 Initializing AI agents and starting server...")
        
        # Change to the project directory
        os.chdir(current_dir)
        
        # Start the process in the background with proper detachment
        log_file = open('server.log', 'w')
        process = subprocess.Popen(
            [str(venv_python), str(flask_app)],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL
        )
        
        # Wait a bit to see if it starts successfully
        print("⏳ Waiting for server initialization...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully!")
            print(f"   PID: {process.pid}")
            print("\n🌐 Access your application at:")
            print("   • Local:   http://127.0.0.1:5555")
            print("   • Network: http://192.168.1.179:5555")
            print("\n🔧 Management:")
            print("   • Stop server: python stop.py")
            print("   • View logs:   tail -f server.log")
            print("   • Check status: ps aux | grep flask_app")
            print(f"   • Server PID file: {process.pid}")
            
            # Write PID to file for easier management
            with open('.server.pid', 'w') as pid_file:
                pid_file.write(str(process.pid))
            print("\n📊 Features available:")
            print("   • Multi-agent logistics coordination")
            print("   • Real-time AGV workflow tracking")
            print("   • Inventory management")
            print("   • AI-powered approval system")
            print("\n💡 The server is now running in the background.")
            print("   Close this terminal window safely - the server will continue running.")
            
            return True
        else:
            print("❌ Server failed to start!")
            # Try to get some output
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stdout:
                    print("Output:", stdout)
            except subprocess.TimeoutExpired:
                pass
            return False
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main entry point."""
    print("Flask Logistics Dashboard - Server Startup")
    print("==========================================")
    
    success = start_server()
    
    if success:
        print("\n🎉 Startup complete! Your logistics dashboard is ready.")
        sys.exit(0)
    else:
        print("\n💥 Startup failed! Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()