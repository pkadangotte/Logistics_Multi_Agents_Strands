#!/usr/bin/env python3
"""
Flask Server Stop Script
========================

This script stops the Flask logistics dashboard server and provides
information about the shutdown process.
"""

import os
import sys
import signal
import time
import psutil
from pathlib import Path

# Import config loader to get server settings
sys.path.append(str(Path(__file__).parent))
from config.config_loader import get_system_config

def find_flask_processes():
    """Find all running Flask processes for this application."""
    processes = []
    
    # First, check if there's a PID file
    pid_file = Path('.server.pid')
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            proc = psutil.Process(pid)
            if proc.is_running():
                cmdline = ' '.join(proc.cmdline())
                # Check for flask processes running on our port (5555) or our app files
                if (('flask run' in cmdline and '--port=5555' in cmdline) or 
                    'strands_flask_app.py' in cmdline or
                    ('flask run' in cmdline and 'Logistics_Multi_Agents_Strands' in cmdline)):
                    processes.append(proc)
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
            # PID file exists but process is not running, remove stale PID file
            pid_file.unlink()
    
    # Also search for processes by command line
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                # Look for flask processes that match our application
                if (('flask run' in cmdline and '--port=5555' in cmdline) or 
                    'strands_flask_app.py' in cmdline or
                    ('flask run' in cmdline and 'Logistics_Multi_Agents_Strands' in cmdline)):
                    if proc not in processes:  # Avoid duplicates
                        processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def stop_server():
    """Stop the Flask server."""
    print("🛑 Stopping Flask Logistics Dashboard Server...")
    print("=" * 60)
    
    # Load server configuration to get the correct port
    try:
        system_config = get_system_config()
        server_config = system_config.get('system_settings', {}).get('server_config', {})
        host = server_config.get('host', '127.0.0.1')
        port = server_config.get('port', 5555)
        print(f"🔧 Looking for server on: {host}:{port}")
    except Exception as e:
        print(f"⚠️  Could not load server config: {e}")
        print("   Using default values: 127.0.0.1:5555")
        host = '127.0.0.1'
        port = 5555
    
    # Find running processes
    processes = find_flask_processes()
    
    if not processes:
        print("ℹ️  No Flask server processes found.")
        print("   The server may not be running, or it may have been stopped already.")
        return True
    
    print(f"📋 Found {len(processes)} Flask server process(es):")
    for proc in processes:
        try:
            print(f"   • PID: {proc.pid} | Status: {proc.status()}")
        except psutil.NoSuchProcess:
            continue
    
    # Attempt graceful shutdown first
    print("\n🔄 Attempting graceful shutdown...")
    stopped_processes = []
    
    for proc in processes:
        try:
            print(f"   Sending SIGTERM to PID {proc.pid}...")
            proc.terminate()  # Send SIGTERM for graceful shutdown
            stopped_processes.append(proc)
        except psutil.NoSuchProcess:
            print(f"   Process {proc.pid} already terminated.")
        except psutil.AccessDenied:
            print(f"   Access denied for PID {proc.pid}. Try running with sudo.")
        except Exception as e:
            print(f"   Error terminating PID {proc.pid}: {e}")
    
    # Wait for graceful shutdown
    if stopped_processes:
        print("⏳ Waiting for graceful shutdown (5 seconds)...")
        time.sleep(5)
    
    # Check which processes are still running
    still_running = []
    for proc in stopped_processes:
        try:
            if proc.is_running():
                still_running.append(proc)
        except psutil.NoSuchProcess:
            continue
    
    # Force kill if necessary
    if still_running:
        print(f"\n💀 Force killing {len(still_running)} stubborn process(es)...")
        for proc in still_running:
            try:
                print(f"   Sending SIGKILL to PID {proc.pid}...")
                proc.kill()  # Force kill
                time.sleep(1)
            except psutil.NoSuchProcess:
                print(f"   Process {proc.pid} already terminated.")
            except Exception as e:
                print(f"   Error force killing PID {proc.pid}: {e}")
    
    # Final verification
    time.sleep(1)
    remaining_processes = find_flask_processes()
    
    if not remaining_processes:
        print("✅ All Flask server processes stopped successfully!")
        print("\n📊 Server shutdown summary:")
        print("   • All processes terminated")
        print(f"   • http://{host}:{port} is no longer accessible")
        print("   • AI agents have been shut down")
        print("   • Resources have been freed")
        print("\n💡 To start the server again, run: python start.py")
        return True
    else:
        print(f"⚠️  {len(remaining_processes)} process(es) still running:")
        for proc in remaining_processes:
            try:
                print(f"   • PID: {proc.pid} | Status: {proc.status()}")
            except psutil.NoSuchProcess:
                continue
        print("\n🔧 Manual cleanup options:")
        print("   • Try: sudo python stop.py")
        print("   • Or manually: kill -9 <PID>")
        return False

def cleanup_resources():
    """Clean up any remaining resources."""
    print("\n🧹 Cleaning up resources...")
    
    # Remove any temporary files if they exist
    temp_files = [
        ".server.pid",
        ".server_lock"
    ]
    
    for temp_file in temp_files:
        file_path = Path(temp_file)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"   Removed: {temp_file}")
            except Exception as e:
                print(f"   Could not remove {temp_file}: {e}")

def main():
    """Main entry point."""
    print("Flask Logistics Dashboard - Server Shutdown")
    print("===========================================")
    
    success = stop_server()
    
    if success:
        cleanup_resources()
        print("\n🎉 Shutdown complete! The server has been stopped safely.")
        sys.exit(0)
    else:
        print("\n💥 Shutdown incomplete! Some processes may still be running.")
        print("   Check the messages above for manual cleanup instructions.")
        sys.exit(1)

if __name__ == "__main__":
    main()