import time
import json
import uuid
import threading
import os
from queue import Queue
from flask import Flask, Response, request, jsonify, render_template_string
from datetime import datetime

# Import our existing agent
from Agents.LogisticsOrchestratorAgent import create_logistics_orchestrator_agent

# Flask app
app = Flask(__name__)

# Task management
tasks = {}

def real_orchestrator_agent(request_data: dict, queue: Queue, task_id: str):
    """
    Real orchestrator agent execution with hooks for message capture.
    Shows ONLY orchestrator-level messages, not sub-agent details.
    """
    try:

        
        # Import the hooks
        from orchestrator_hooks import create_orchestrator_hooks
        
        # Create Langfuse-enabled hooks for this task
        hooks = create_orchestrator_hooks(queue, task_id)
        
        # Create detailed query for the orchestrator
        query = f"""
        Analyze this logistics request step by step:
        
        Part: {request_data['part_number']} 
        Quantity: {request_data['quantity_requested']}
        Destination: {request_data['destination']}
        Priority: {request_data['priority']}
        Reason: {request_data['urgency_reason']}
        
        Please use your tools in sequence and provide detailed analysis:
        1. Check inventory availability and costs
        2. Coordinate fleet operations for delivery
        3. Process approval based on total cost
        
        Provide clear status updates and final recommendations.
        """
        
        # Create the orchestrator with hooks (must be a list/iterable)
        orchestrator = create_logistics_orchestrator_agent(use_local_model=True, hooks=[hooks])
        
        hooks.log_message(
            "thought",
            "🚀 Starting orchestrator analysis..."
        )
        
        # Run the orchestrator - this will trigger all the hooks automatically
        result = orchestrator(query)
        
        # Final completion message
        result_str = str(result)
        hooks.log_message(
            "final_answer",
            f"✅ Orchestrator completed:\n\n{result_str}"
        )
        
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        
        # Create minimal hooks for error reporting if hooks not yet created
        try:
            hooks.log_message("error", f"❌ Orchestrator error: {str(e)}")
        except:
            queue.put(json.dumps({
                "type": "error", 
                "content": f"❌ Orchestrator error: {str(e)}"
            }))
    finally:
        queue.put("[DONE]")
        print("🏁 Real orchestrator workflow completed")

@app.route('/')
def index():
    """Main page with logistics form"""
    from flask import make_response
    response = make_response(render_template_string(LOGISTICS_TEMPLATE))
    # Add cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/start-logistics', methods=['POST'])
def start_logistics():
    """Start logistics analysis in background thread"""
    request_data = request.json
    
    # Validate required fields
    required_fields = ['part_number', 'quantity_requested', 'destination', 'priority']
    if not all(field in request_data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    task_id = str(uuid.uuid4())
    tasks[task_id] = Queue()
    
    # Start real orchestrator agent in background
    thread = threading.Thread(
        target=real_orchestrator_agent,
        args=(request_data, tasks[task_id], task_id)
    )
    thread.start()
    
    return jsonify({"task_id": task_id})

@app.route('/api/stream/<task_id>')
def stream_logistics(task_id):
    """Stream logistics agent messages"""
    if task_id not in tasks:
        print(f"🔍 STREAM: Task {task_id} not found")
        return "Task not found", 404
    
    print(f"🔍 STREAM: Starting stream for task {task_id}")
    
    def event_stream():
        queue = tasks[task_id]
        message_count = 0
        while True:
            message = queue.get()  # Block until message available
            message_count += 1
            print(f"🔍 STREAM: Got message #{message_count}: {message[:100]}...")
            
            if message == "[DONE]":
                print(f"🔍 STREAM: Stream completed for task {task_id}")
                break
            yield f"data: {message}\n\n"
        
        # Cleanup
        del tasks[task_id]
    
    return Response(event_stream(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
    })

@app.route('/api/approve', methods=['POST'])
def handle_approval():
    """Handle manual approval decisions"""
    data = request.json
    decision = data.get('decision')  # 'approve' or 'reject'
    reason = data.get('reason', '')
    task_id = data.get('task_id')
    
    if decision not in ['approve', 'reject']:
        return jsonify({'error': 'Invalid decision'}), 400
    
    # In a real system, you'd update the workflow state here
    # For now, just return success
    return jsonify({
        'success': True,
        'decision': decision,
        'message': f'Request {decision}d: {reason}' if reason else f'Request {decision}d'
    })

# HTML Template with proper Strands-style UI
LOGISTICS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏭 Logistics Multi-Agent System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        
        .content { padding: 30px; }
        .form-section {
            background: #f8fafc;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 2px solid #e2e8f0;
        }
        .form-row {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .form-group {
            flex: 1;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #374151;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #4f46e5;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            width: 100%;
        }
        .submit-btn:hover { transform: translateY(-2px); }
        .submit-btn:disabled { 
            background: #9ca3af; 
            cursor: not-allowed;
            transform: none;
        }
        
        .results-section {
            margin-top: 30px;
        }
        
        .approval-panel {
            background: #fef3c7;
            border: 2px solid #f59e0b;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .approval-panel h3 { color: #92400e; margin-bottom: 15px; }
        .approval-buttons {
            display: flex;
            gap: 15px;
            margin-top: 15px;
        }
        .approval-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            flex: 1;
        }
        .approve { background: #10b981; color: white; }
        .reject { background: #ef4444; color: white; }
        
        .agent-log {
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 25px;
            min-height: 400px;
            max-height: 800px;
            overflow-y: auto;
        }
        .agent-log h3 {
            margin-bottom: 20px;
            color: #374151;
            font-size: 1.3em;
        }
        
        .log-item {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            padding: 20px;
            margin-bottom: 16px;
            border-radius: 10px;
            border-left: 4px solid;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
            overflow: hidden;
            width: 100%;
            box-sizing: border-box;
        }
        
        .log-item:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }
        
        .thought { 
            background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); 
            border-left-color: #8b5cf6;
        }
        .action { 
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); 
            border-left-color: #3b82f6;
        }
        .observation { 
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); 
            border-left-color: #10b981;
        }
        .final_answer { 
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); 
            border-left-color: #f59e0b;
        }
        .error { 
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); 
            border-left-color: #ef4444;
        }
        .approval_needed {
            background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
            border-left-color: #ea580c;
        }
        .raw_result, .raw_tool_call {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left-color: #6c757d;
            font-family: 'Courier New', monospace;
        }
        
        .log-icon {
            font-size: 1.3em;
            margin-top: 3px;
            min-width: 24px;
            text-align: center;
        }
        .log-content {
            flex: 1;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-width: 100%;
            min-width: 0;
            font-size: 14px;
            font-weight: normal;
            color: #374151;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            overflow-wrap: break-word;
        }
        
        .log-content h1, .log-content h2, .log-content h3, .log-content h4 {
            font-weight: 600;
            margin: 12px 0 8px 0;
            color: #1f2937;
        }
        
        .log-content strong {
            font-weight: 600;
            color: #1f2937;
        }
        
        .log-content code {
            background: #f3f4f6;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 13px;
            border: 1px solid #e5e7eb;
        }
        
        .log-content pre {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            overflow-x: auto;
            margin: 8px 0;
            max-width: 100%;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .log-time {
            font-size: 0.8em;
            color: #9ca3af;
            margin-left: auto;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            white-space: nowrap;
            min-width: 70px;
            text-align: right;
        }
        
        /* New message type styles */
        .log-item.plan {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            border-left: 4px solid #3b82f6;
        }
        
        .log-item.progress {
            background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
            border-left: 4px solid #f59e0b;
            animation: pulse 2s infinite;
        }
        
        .log-item.result {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-left: 4px solid #10b981;
        }
        
        .log-item.summary {
            background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
            border-left: 4px solid #6366f1;
            border: 2px solid #6366f1;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }
        
        /* Loading animation */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        @keyframes typing {
            0% { opacity: 0; }
            50% { opacity: 1; }
            100% { opacity: 0; }
        }
        
        .loading-dots {
            display: inline-block;
            animation: typing 1.5s infinite;
        }
        
        .loading-dots:after {
            content: '...';
            animation: typing 1.5s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 AI Manufacturing Logistics</h1>
            <p>Intelligent part requests with real-time agent coordination</p>
        </div>
        
        <div class="content">
            <div class="form-section">
                <h3>📋 New Logistics Request</h3>
                <form id="logisticsForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Part Number</label>
                            <select id="partNumber" required>
                                <option value="HYDRAULIC-PUMP-HP450">HYDRAULIC-PUMP-HP450 - Heavy Duty</option>
                                <option value="BEARING-SKF-6205">BEARING-SKF-6205 - High Precision</option>
                                <option value="MOTOR-ABB-M3BP">MOTOR-ABB-M3BP - Industrial</option>
                                <option value="VALVE-PARKER-D1VW">VALVE-PARKER-D1VW - Control</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Quantity</label>
                            <input type="number" id="quantity" min="1" max="50" value="15" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Destination</label>
                            <select id="destination" required>
                                <option value="Production Line A">Production Line A</option>
                                <option value="Production Line B">Production Line B</option>
                                <option value="Assembly Station 1">Assembly Station 1</option>
                                <option value="Quality Control Lab">Quality Control Lab</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Priority</label>
                            <select id="priority" required>
                                <option value="LOW">Low Priority</option>
                                <option value="MEDIUM" selected>Medium Priority</option>
                                <option value="HIGH">High Priority</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Reason for Request</label>
                        <textarea id="reason" placeholder="e.g., Regular maintenance, Emergency repair, Scheduled replacement..." required>Regular production maintenance replacement</textarea>
                    </div>
                    <button type="submit" class="submit-btn" id="submitBtn">
                        🚀 Submit Request
                    </button>
                </form>
            </div>
            
            <div class="results-section" id="resultsSection" style="display: none;">
                <!-- Approval Panel (shown when needed) -->
                <div id="approvalPanel" class="approval-panel" style="display: none;">
                    <h3>⚖️ Manual Approval Required</h3>
                    <div id="approvalDetails"></div>
                    <div>
                        <label>Approval Reason (optional):</label>
                        <input type="text" id="approvalReason" placeholder="Enter reason for approval/rejection...">
                    </div>
                    <div class="approval-buttons">
                        <button class="approval-btn approve" onclick="handleApproval('approve')">
                            ✅ Approve Request
                        </button>
                        <button class="approval-btn reject" onclick="handleApproval('reject')">
                            ❌ Reject Request
                        </button>
                    </div>
                </div>
                
                <!-- Agent Activity Log -->
                <div class="agent-log">
                    <h3>🤖 Live Agent Activity</h3>
                    <div id="agentLog"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Version: FIXED-2025-11-10-10:55 - Regex error fixed
        console.log('🔥 JavaScript loading... Version FIXED-2025-11-10-10:55');
        let currentTaskId = null;
        
        // Test basic functionality
        window.addEventListener('load', function() {
            console.log('🌐 Window loaded');
        });
        
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🎯 DOM loaded, setting up form listener...');
            
            // Check for all required elements
            const form = document.getElementById('logisticsForm');
            const partNumber = document.getElementById('partNumber');
            const quantity = document.getElementById('quantity');
            const destination = document.getElementById('destination');
            const priority = document.getElementById('priority');
            const reason = document.getElementById('reason');
            const submitBtn = document.getElementById('submitBtn');
            
            console.log('🔍 Form elements check:');
            console.log('Form:', form);
            console.log('Part Number:', partNumber);
            console.log('Quantity:', quantity);
            console.log('Destination:', destination);
            console.log('Priority:', priority);
            console.log('Reason:', reason);
            console.log('Submit Button:', submitBtn);
            
            if (!form) {
                console.error('❌ Form element not found!');
                return;
            }
            
            console.log('✅ Form element found:', form);
            
            
            // Add a simple click handler for debugging
            if (submitBtn) {
                submitBtn.addEventListener('click', function(e) {
                    console.log('🎯 Submit button clicked!');
                });
            }
            
            form.addEventListener('submit', async (e) => {
                console.log('🚀 Form submit event triggered');
                e.preventDefault();            console.log('📋 Collecting form data...');
            const formData = {
                part_number: document.getElementById('partNumber').value,
                quantity_requested: parseInt(document.getElementById('quantity').value),
                destination: document.getElementById('destination').value,
                priority: document.getElementById('priority').value,
                urgency_reason: document.getElementById('reason').value
            };
            
            console.log('📦 Form data collected:', formData);
            
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Processing...';
            
            // Show results section
            document.getElementById('resultsSection').style.display = 'block';
            document.getElementById('agentLog').innerHTML = '';
            
            try {
                console.log('🌐 Making POST request to /api/start-logistics...');
                
                // Start the logistics task
                const response = await fetch('/api/start-logistics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                console.log('📡 Response received:', response.status, response.statusText);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('📊 Response data:', data);
                currentTaskId = data.task_id;
                
                // Connect to the event stream
                const eventSource = new EventSource(`/api/stream/${currentTaskId}`);
                
                eventSource.onmessage = (event) => {
                    console.log('📨 Received message:', event.data);
                    try {
                        const message = JSON.parse(event.data);
                        console.log('📋 Parsed message:', message);
                        displayMessage(message);
                        
                        // Check for approval needed
                        if (message.type === 'approval_needed') {
                            showApprovalPanel(message.content);
                        }
                    } catch (error) {
                        console.error('❌ Error parsing message:', error, event.data);
                    }
                };
                
                eventSource.onerror = (error) => {
                    console.log('❌ Stream error:', error);
                    console.log('Stream closed');
                    eventSource.close();
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 Submit Request';
                };
                
                eventSource.onopen = () => {
                    console.log('✅ Stream connection opened');
                };
                
            } catch (error) {
                console.error('Error:', error);
                submitBtn.disabled = false;
                submitBtn.textContent = '🚀 Submit Request';
            }
        });
        
        function displayMessage(message) {
            console.log('🎨 Displaying message:', message.type, message.content.substring(0, 50));
            
            const agentLog = document.getElementById('agentLog');
            if (!agentLog) {
                console.error('❌ Agent log element not found!');
                return;
            }
            
            const logItem = document.createElement('div');
            logItem.className = `log-item ${message.type}`;
            
            const icon = getMessageIcon(message.type);
            const timestamp = new Date().toLocaleTimeString();
            
            // Format the message content for better display
            let formattedContent = formatMessageContent(message.content, message.type);
            
            // Add loading animation for progress messages
            if (message.type === 'progress' && message.is_loading) {
                formattedContent += '<span class="loading-dots"></span>';
            }
            
            // Special formatting for different message types
            if (message.type === 'phase_header') {
                logItem.style.fontSize = '1.2em';
                logItem.style.fontWeight = '600';
                logItem.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                logItem.style.color = 'white';
                logItem.style.marginTop = '20px';
                logItem.style.marginBottom = '10px';
            } else if (message.type === 'phase_complete') {
                logItem.style.fontSize = '1.1em';
                logItem.style.fontWeight = '500';
                logItem.style.background = 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)';
                logItem.style.color = 'white';
                logItem.style.marginBottom = '15px';
            } else if (message.type === 'final_summary') {
                logItem.style.fontSize = '1.1em';
                logItem.style.fontWeight = '500';
                logItem.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)';
                logItem.style.color = 'white';
                logItem.style.marginTop = '15px';
            }
            
            logItem.innerHTML = `
                <div class="log-icon">${icon}</div>
                <div class="log-content">${formattedContent}</div>
                <div class="log-time">${timestamp}</div>
            `;
            
            console.log('📝 Adding log item to DOM');
            agentLog.appendChild(logItem);
            agentLog.scrollTop = agentLog.scrollHeight;
        }
        
        function formatMessageContent(content, messageType) {
            // Simple, safe formatting for user-friendly content
            let formatted = content;
            
            try {
                // Format bold text
                formatted = formatted.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
                
                // Format costs
                formatted = formatted.replace(/\\$([0-9]+\\.[0-9]{2})/g, '<strong style="color: #059669;">$$$1</strong>');
                
                // Format time
                formatted = formatted.replace(/([0-9]+)\\s*(minutes?|min)/gi, '<strong style="color: #0ea5e9;">$1 $2</strong>');
                
                // Format part numbers
                formatted = formatted.replace(/HYDRAULIC-PUMP-HP450/g, '<code style="background: #f3f4f6; padding: 2px 4px;">HYDRAULIC-PUMP-HP450</code>');
                formatted = formatted.replace(/AGV-001/g, '<code style="background: #f3f4f6; padding: 2px 4px;">AGV-001</code>');
                
                // Simple line break handling
                formatted = formatted.replace(/\\n/g, '<br>');
                
            } catch (error) {
                console.error('Formatting error:', error);
            }
            
            return formatted;
        }
        
        function getMessageIcon(type) {
            const icons = {
                'thought': '🤔',
                'reasoning': '🧠',
                'decision': '💡',
                'analysis': '🔍',
                'action': '🛠️',
                'observation': '👀',
                'final_answer': '✅',
                'plan': '📋',
                'progress': '⏳',
                'result': '📊',
                'summary': '🎉',
                'phase_header': '📋',
                'phase_complete': '✅',
                'final_summary': '🎉',
                'error': '❌',
                'approval_needed': '⚖️',
                'raw_result': '🔍',
                'raw_tool_call': '🔧'
            };
            return icons[type] || '📝';
        }
        
        function showApprovalPanel(details) {
            const panel = document.getElementById('approvalPanel');
            const detailsDiv = document.getElementById('approvalDetails');
            
            detailsDiv.innerHTML = `<strong>${details}</strong>`;
            panel.style.display = 'block';
        }
        
        async function handleApproval(decision) {
            const reason = document.getElementById('approvalReason').value;
            
            try {
                const response = await fetch('/api/approve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        decision: decision,
                        reason: reason,
                        task_id: currentTaskId
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Hide approval panel
                    document.getElementById('approvalPanel').style.display = 'none';
                    
                    // Add approval message to log
                    displayMessage({
                        type: decision === 'approve' ? 'final_answer' : 'error',
                        content: `${decision === 'approve' ? '✅ Request APPROVED' : '❌ Request REJECTED'}: ${result.message}`
                    });
                    
                    // Re-enable submit button
                    const submitBtn = document.getElementById('submitBtn');
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 Submit Request';
                }
            } catch (error) {
                console.error('Approval error:', error);
            }
        }
        
        }); // End DOMContentLoaded
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("🚀 Starting Strands-style Logistics Multi-Agent System...")
    app.run(host='127.0.0.1', port=5555, debug=True, threaded=True)