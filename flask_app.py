#!/usr/bin/env python3
"""
Flask Manufacturing Logistics Dashboard
======================================

Clean web application with HTML/CSS/JavaScript for AGV workflow with 10-second delays.
"""

from flask import Flask, render_template, request, jsonify
import time
import json
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project path for imports
sys.path.append('.')

# Import AI agents
try:
    from Agents.LogisticsOrchestratorAgent import LogisticsOrchestratorAgent
    from Agents.FleetAgent import FleetAgent
    from Agents.InventoryAgent import InventoryAgent
    from Agents.ApproverAgent import ApproverAgent
except ImportError as e:
    print(f"Warning: Failed to import AI agents: {e}")

app = Flask(__name__)

# Global variables to track workflow state
workflow_state = {
    'active': False,
    'step': 0,
    'phase': 0,
    'start_time': None,
    'request_data': None,
    'results': {},
    'status': 'idle',
    'agent_activity': '',
    'agv_logs': []
}

def initialize_agents():
    """Initialize AI agents."""
    try:
        orchestrator = LogisticsOrchestratorAgent()
        return orchestrator
    except Exception as e:
        print(f"Failed to initialize agents: {e}")
        return None

# Initialize agents at startup
orchestrator = initialize_agents()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/submit_request', methods=['POST'])
def submit_request():
    """Handle initial request submission and run analysis."""
    global workflow_state
    
    try:
        request_data = request.json
        
        # Reset workflow state
        workflow_state = {
            'active': True,
            'step': 1,
            'phase': 1,
            'start_time': time.time(),
            'request_data': request_data,
            'results': {},
            'status': 'analyzing',
            'agent_activity': '🎯 LogisticsOrchestrator initializing analysis...',
            'agv_logs': []
        }
        
        # Run analysis steps (fast)
        analysis_results = run_analysis_steps(request_data)
        
        # Update workflow state with results
        workflow_state['results'] = analysis_results
        workflow_state['step'] = 0  # Ready for approval
        workflow_state['status'] = 'awaiting_approval'
        
        return jsonify({
            'success': True,
            'status': 'analysis_complete',
            'results': analysis_results
        })
        
    except Exception as e:
        workflow_state['status'] = 'error'
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/approve_request', methods=['POST'])
def approve_request():
    """Handle request approval and start AGV workflow."""
    global workflow_state
    
    try:
        if workflow_state['status'] != 'awaiting_approval':
            return jsonify({'success': False, 'error': 'No request awaiting approval'})
        
        # Start AGV workflow
        workflow_state['status'] = 'agv_workflow_starting'
        workflow_state['step'] = 5  # AGV Dispatch
        workflow_state['phase'] = 1
        workflow_state['start_time'] = time.time()
        
        # Start AGV workflow in background thread
        threading.Thread(target=run_agv_workflow_background, daemon=True).start()
        
        return jsonify({
            'success': True,
            'status': 'agv_workflow_started',
            'message': 'AGV workflow initiated'
        })
        
    except Exception as e:
        workflow_state['status'] = 'error'
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reject_request', methods=['POST'])
def reject_request():
    """Handle request rejection."""
    global workflow_state
    
    workflow_state = {
        'active': False,
        'step': 0,
        'phase': 0,
        'start_time': None,
        'request_data': None,
        'results': {},
        'status': 'rejected',
        'agent_activity': '',
        'agv_logs': []
    }
    
    return jsonify({
        'success': True,
        'status': 'rejected',
        'message': 'Request rejected by supervisor'
    })

@app.route('/api/workflow_status')
def workflow_status():
    """Get current workflow status."""
    return jsonify(workflow_state)

def run_analysis_steps(request_data):
    """Run the initial analysis steps with real AI agent responses via orchestrator."""
    global workflow_state
    
    # Initialize agent_logs in workflow_state if not exists
    if 'agent_logs' not in workflow_state:
        workflow_state['agent_logs'] = []
    
    # Step 1: Orchestrator Analysis - ACTIVE
    workflow_state['step'] = 1
    workflow_state['agent_activity'] = "🎯 LogisticsOrchestrator analyzing request..."
    
    # Add message to workflow_state immediately for real-time display
    new_message = {
        'step': 1,
        'agent': 'LogisticsOrchestrator',
        'message': f"📋 Analyzing request for {request_data['part_number']} ({request_data['quantity_requested']} units)",
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    workflow_state['agent_logs'].append(new_message)
    
    # Delay to show step progression clearly
    time.sleep(1.0)
    
    # Prepare request data for orchestrator (before try blocks to ensure scope)
    orchestrator_request = {
        'RequestId': f"REQ-{request_data['part_number']}-{int(time.time())}",
        'part_number': request_data['part_number'],
        'quantity_requested': request_data['quantity_requested'], 
        'destination': request_data['destination'],
        'priority': request_data['priority'],
        'urgency_reason': request_data.get('urgency_reason', f"HIGH priority replenishment for {request_data['part_number']}"),
        'timestamp': request_data.get('timestamp', datetime.now().isoformat())
    }

    # Call the real orchestrator agent
    try:
        
        logger.info(f"🔍 DEBUG: Received request data: {request_data}")
        logger.info(f"🔍 DEBUG: Orchestrator request: {orchestrator_request}")
        logger.info(f"🔍 DEBUG: Orchestrator available: {orchestrator is not None}")
        
        # Get real agent responses through orchestrator
        if orchestrator:
            # Use orchestrator to coordinate with all agents
            
            # Step 2: InventoryAgent - ACTIVE
            workflow_state['step'] = 2
            workflow_state['agent_activity'] = "📦 InventoryAgent checking stock levels..."
            new_message = {
                'step': 2,
                'agent': 'InventoryAgent',
                'message': f"🔍 Checking inventory for part {request_data['part_number']} in Central Warehouse",
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            workflow_state['agent_logs'].append(new_message)
            
            # Delay to show step progression clearly
            time.sleep(1.2)
            
            # Call real inventory agent through orchestrator
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                logger.info(f"🔍 DEBUG: Calling orchestrator.check_inventory_availability with: {orchestrator_request}")
                inventory_result_raw = loop.run_until_complete(
                    orchestrator.check_inventory_availability(orchestrator_request)
                )
                logger.info(f"🔍 DEBUG: Raw inventory result: {inventory_result_raw}")
                
                # Extract inventory data from agent response
                if inventory_result_raw.get('available', False):
                    inventory_result = {
                        'available_quantity': inventory_result_raw.get('available_quantity', 0),
                        'warehouse_location': inventory_result_raw.get('warehouse_location', 'Central Warehouse'),
                        'estimated_cost': inventory_result_raw.get('total_cost', request_data['quantity_requested'] * 25.0),
                        'stock_status': 'Available' if inventory_result_raw.get('available', False) else 'Unavailable'
                    }
                    
                    new_message = {
                        'step': 2,
                        'agent': 'InventoryAgent',
                        'message': f"✅ REAL AGENT DATA: Found {inventory_result['available_quantity']} units of {request_data['part_number']} in {inventory_result['warehouse_location']} - Cost: ${inventory_result['estimated_cost']:.2f}",
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }
                    workflow_state['agent_logs'].append(new_message)
                else:
                    # Handle case where part is not available
                    inventory_result = {
                        'available_quantity': 0,
                        'warehouse_location': 'Central Warehouse',
                        'estimated_cost': request_data['quantity_requested'] * 25.0,
                        'stock_status': 'Not Available'
                    }
                    
                    new_message = {
                        'step': 2,
                        'agent': 'InventoryAgent',
                        'message': f"❌ AGENT RESPONSE: Part {request_data['part_number']} not available. Inventory check returned: {inventory_result_raw.get('error', 'Unknown error')}",
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }
                    workflow_state['agent_logs'].append(new_message)
            finally:
                loop.close()
        else:
            # Fallback to mock data if orchestrator not available
            inventory_result = {
                'available_quantity': max(0, request_data['quantity_requested'] - 2),
                'warehouse_location': 'Central Warehouse',
                'estimated_cost': request_data['quantity_requested'] * 25.0,
                'stock_status': 'Available' if request_data['quantity_requested'] <= 20 else 'Partial'
            }
    except Exception as e:
        # Fallback to mock data on error
        logger.error(f"❌ INTEGRATION ERROR - Orchestrator call failed: {e}")
        logger.error(f"❌ FALLBACK: Using mock data instead of real agent data")
        inventory_result = {
            'available_quantity': max(0, request_data['quantity_requested'] - 2),
            'warehouse_location': 'Central Warehouse',
            'estimated_cost': request_data['quantity_requested'] * 25.0,
            'stock_status': 'Available' if request_data['quantity_requested'] <= 20 else 'Partial'
        }
        
        # Add error to agent logs
        new_message = {
            'step': 2,
            'agent': 'InventoryAgent',
            'message': f"❌ INTEGRATION ERROR: Failed to connect to real agent. Using fallback data. Error: {str(e)[:100]}",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        workflow_state['agent_logs'].append(new_message)
    
    
    # Step 3: FleetAgent - ACTIVE  
    workflow_state['step'] = 3
    workflow_state['agent_activity'] = "🚛 FleetAgent optimizing AGV assignment..."
    new_message = {
        'step': 3,
        'agent': 'FleetAgent',
        'message': f"🤖 Analyzing AGV fleet for delivery to {request_data['destination']}",
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    workflow_state['agent_logs'].append(new_message)
    
    try:
        if orchestrator and inventory_result['stock_status'] != 'Not Available':
            # Call real fleet agent through orchestrator
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                fleet_result_raw = loop.run_until_complete(
                    orchestrator.coordinate_fleet_delivery(orchestrator_request, inventory_result)
                )
                
                fleet_result = {
                    'vehicle_id': fleet_result_raw.get('vehicle_id', 'AGV-001'),
                    'battery_level': fleet_result_raw.get('battery_level', 87),
                    'estimated_travel_time': fleet_result_raw.get('estimated_travel_time', 15),
                    'availability_status': fleet_result_raw.get('status', 'Ready')
                }
            finally:
                loop.close()
        else:
            # Fallback to mock data
            fleet_result = {
                'vehicle_id': 'AGV-001',
                'battery_level': 87,
                'estimated_travel_time': 15,
                'availability_status': 'Ready'
            }
    except Exception as e:
        logger.error(f"❌ Error calling fleet agent: {e}")
        fleet_result = {
            'vehicle_id': 'AGV-001',
            'battery_level': 87,
            'estimated_travel_time': 15,
            'availability_status': 'Ready'
        }
    
    new_message = {
        'step': 3,
        'agent': 'FleetAgent',
        'message': f"🎯 Assigned {fleet_result['vehicle_id']} (Battery: {fleet_result['battery_level']}%) - ETA: {fleet_result['estimated_travel_time']} min",
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    workflow_state['agent_logs'].append(new_message)
    
    # Delay to show step progression clearly
    time.sleep(1.2)
    
    # Step 4: ApproverAgent - ACTIVE
    workflow_state['step'] = 4
    workflow_state['agent_activity'] = "⚖️ ApproverAgent calculating costs..."
    new_message = {
        'step': 4,
        'agent': 'ApproverAgent',
        'message': f"💰 Calculating total costs for {request_data['priority']} priority request",
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    workflow_state['agent_logs'].append(new_message)
    
    try:
        if orchestrator:
            # Call real approver agent through orchestrator
            approval_request = {
                "request_id": orchestrator_request['RequestId'],
                "request_data": orchestrator_request,
                "inventory_result": inventory_result,
                "fleet_result": fleet_result,
                "priority": request_data['priority']
            }
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                approval_result_raw = loop.run_until_complete(
                    orchestrator.request_approval(approval_request)
                )
                
                # Extract cost data from approval result
                estimated_cost = approval_result_raw.get('total_cost', inventory_result['estimated_cost'] + 70.0)
                
            finally:
                loop.close()
        else:
            # Fallback to mock calculation
            handling_cost = 45.0
            agv_cost = 25.0
            estimated_cost = inventory_result['estimated_cost'] + handling_cost + agv_cost
    except Exception as e:
        logger.error(f"❌ Error calling approver agent: {e}")
        handling_cost = 45.0
        agv_cost = 25.0
        estimated_cost = inventory_result['estimated_cost'] + handling_cost + agv_cost
    
    new_message = {
        'step': 4,
        'agent': 'ApproverAgent',
        'message': f"💵 Total cost calculated: ${estimated_cost:.2f} (includes materials, handling, and AGV costs)",
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    workflow_state['agent_logs'].append(new_message)
    
    # Delay to show step progression clearly
    time.sleep(1.2)
    
    # Analysis Complete - Set to ready for approval
    workflow_state['step'] = 0  # Ready for approval
    workflow_state['agent_activity'] = "✅ All agents completed analysis - Ready for approval"
    
    # Add completion log
    new_message = {
        'step': 5,
        'agent': 'System',
        'message': f"✅ Analysis complete. Total cost: ${estimated_cost:.2f}. Ready for supervisor approval.",
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    workflow_state['agent_logs'].append(new_message)
    
    return {
        'inventory': inventory_result,
        'fleet': fleet_result,
        'total_cost': estimated_cost,
        'analysis_time': time.time() - workflow_state['start_time'],
        'agent_logs': workflow_state['agent_logs']  # Return the logs from workflow_state
    }

def run_agv_workflow_background():
    """Run the AGV workflow with 10-second delays and agent updates."""
    global workflow_state
    
    try:
        # Initialize AGV logs if not exists
        if 'agv_logs' not in workflow_state:
            workflow_state['agv_logs'] = []
        
        # Step 5: AGV Dispatch (10 seconds total)
        workflow_state['status'] = 'agv_dispatch_phase1'
        workflow_state['step'] = 5
        workflow_state['phase'] = 1
        workflow_state['start_time'] = time.time()
        workflow_state['agent_activity'] = "🚛 FleetAgent dispatching AGV-001..."
        
        workflow_state['agv_logs'].append({
            'step': 5,
            'agent': 'FleetAgent',
            'message': "🔄 AGV-001 initializing dispatch sequence...",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # Phase 1: Dispatch preparation (3 seconds)
        time.sleep(3)
        workflow_state['agv_logs'].append({
            'step': 5,
            'agent': 'FleetAgent',
            'message': "🗺️ AGV-001 calculating optimal route to Central Warehouse...",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # Phase 2: Navigation to pickup (7 seconds)
        workflow_state['status'] = 'agv_dispatch_phase2'
        workflow_state['phase'] = 2
        workflow_state['agent_activity'] = "🎯 AGV-001 navigating to pickup location..."
        workflow_state['agv_logs'].append({
            'step': 5,
            'agent': 'FleetAgent',
            'message': "🚀 AGV-001 en route to Central Warehouse (Battery: 87%)",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        time.sleep(7)
        
        # Step 6: Material Pickup (10 seconds total)
        workflow_state['status'] = 'material_pickup_phase1'
        workflow_state['step'] = 6
        workflow_state['phase'] = 1
        workflow_state['agent_activity'] = "📦 InventoryAgent coordinating material loading..."
        
        workflow_state['agv_logs'].append({
            'step': 6,
            'agent': 'InventoryAgent',
            'message': "📍 AGV-001 arrived at Central Warehouse - Position: Bay 3A",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # Phase 1: Loading materials (6 seconds)
        workflow_state['agv_logs'].append({
            'step': 6,
            'agent': 'InventoryAgent',
            'message': f"🏗️ Loading {workflow_state['request_data']['part_number']} units onto AGV-001...",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        time.sleep(6)
        
        # Phase 2: Securing materials (4 seconds)
        workflow_state['status'] = 'material_pickup_phase2'
        workflow_state['phase'] = 2
        workflow_state['agent_activity'] = "🔐 Securing materials for transport..."
        workflow_state['agv_logs'].append({
            'step': 6,
            'agent': 'InventoryAgent',
            'message': "🔒 Securing cargo and performing safety checks...",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        time.sleep(4)
        
        # Step 7: Delivery (3 seconds)
        workflow_state['status'] = 'delivery'
        workflow_state['step'] = 7
        workflow_state['phase'] = 1
        workflow_state['agent_activity'] = f"🚚 Delivering to {workflow_state['request_data']['destination']}..."
        
        workflow_state['agv_logs'].append({
            'step': 7,
            'agent': 'FleetAgent',
            'message': f"🎯 AGV-001 departing to {workflow_state['request_data']['destination']}",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        time.sleep(3)
        
        # Workflow complete
        workflow_state['status'] = 'completed'
        workflow_state['active'] = False
        workflow_state['agent_activity'] = "✅ All operations completed successfully"
        workflow_state['agv_logs'].append({
            'step': 7,
            'agent': 'LogisticsOrchestrator',
            'message': f"✅ Delivery completed! Materials delivered to {workflow_state['request_data']['destination']}",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
    except Exception as e:
        workflow_state['status'] = 'error'
        workflow_state['agent_activity'] = f"❌ Error: {str(e)}"
        print(f"AGV Workflow error: {e}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5555)