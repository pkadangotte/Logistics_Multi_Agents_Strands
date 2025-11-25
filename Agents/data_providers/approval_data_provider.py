"""
Approval Data Provider Module
Provides the ApprovalDataProvider class for approval workflow operations.
"""

from datetime import datetime
import uuid
from typing import Dict, List, Union


class ApprovalDataProvider:
    """
    Data access class for approval workflow operations.
    Provides methods to manage approvals, compliance checks, and authorization workflows.
    """
    
    def __init__(self, approval_df):
        """Initialize with approval thresholds DataFrame"""
        self.approval_df = approval_df.copy()
        self.approval_requests = []
        self.approval_history = []
    
    def _convert_to_json_serializable(self, obj):
        """Convert pandas types to JSON-serializable types."""
        if hasattr(obj, 'item'):  # numpy/pandas scalar
            return obj.item()
        elif isinstance(obj, dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(v) for v in obj]
        else:
            return obj
        
    def get_approval_threshold(self, cost: float) -> dict:
        """
        Determine the approval threshold category for a given cost.
        
        Args:
            cost: The cost amount to evaluate
            
        Returns:
            Dictionary with threshold information and requirements
        """
        try:
            for threshold_name, threshold_data in self.approval_df.iterrows():
                if cost <= threshold_data['max_cost']:
                    result = {
                        "threshold_category": threshold_name,
                        "max_cost": threshold_data['max_cost'],
                        "auto_approve": threshold_data.get('auto_approve', False),
                        "requires_manager": threshold_data.get('requires_manager', False),
                        "requires_director": threshold_data.get('requires_director', False),
                        "cost_amount": cost,
                        "approval_required": not threshold_data.get('auto_approve', False)
                    }
                    return self._convert_to_json_serializable(result)
            
            # If no threshold found, return highest level requirement
            return {
                "threshold_category": "high_value",
                "cost_amount": cost,
                "approval_required": True,
                "requires_director": True,
                "error": f"Cost ${cost} exceeds all defined thresholds"
            }
            
        except Exception as e:
            return {"error": f"Error determining approval threshold: {str(e)}"}
    
    def create_approval_request(self, request_details: dict, requester: str = "system") -> dict:
        """
        Create a new approval request.
        
        Args:
            request_details: Dictionary with request information (cost, description, etc.)
            requester: Who is making the request
            
        Returns:
            Dictionary with approval request result
        """
        try:
            # Validate required fields
            required_fields = ['cost', 'description', 'request_type']
            for field in required_fields:
                if field not in request_details:
                    return {"error": f"Missing required field: {field}"}
            
            cost = request_details['cost']
            threshold_info = self.get_approval_threshold(cost)
            
            if "error" in threshold_info:
                return threshold_info
            
            # Create approval request
            approval_request = {
                "request_id": str(uuid.uuid4())[:8],
                "timestamp": datetime.now().isoformat(),
                "requester": requester,
                "cost": cost,
                "description": request_details['description'],
                "request_type": request_details['request_type'],
                "threshold_category": threshold_info['threshold_category'],
                "approval_required": threshold_info['approval_required'],
                "auto_approve": threshold_info.get('auto_approve', False),
                "requires_manager": threshold_info.get('requires_manager', False),
                "requires_director": threshold_info.get('requires_director', False),
                "status": "PENDING",
                "approver": None,
                "approval_timestamp": None,
                "comments": []
            }
            
            # Auto-approve if threshold allows
            if threshold_info.get('auto_approve', False):
                approval_request['status'] = 'APPROVED'
                approval_request['approver'] = 'SYSTEM_AUTO'
                approval_request['approval_timestamp'] = datetime.now().isoformat()
                approval_request['comments'].append({
                    "timestamp": datetime.now().isoformat(),
                    "author": "SYSTEM",
                    "comment": f"Auto-approved: Cost ${cost} is within {threshold_info['threshold_category']} threshold"
                })
            
            self.approval_requests.append(approval_request)
            
            return {
                "success": True,
                "request_id": approval_request['request_id'],
                "status": approval_request['status'],
                "approval_required": approval_request['approval_required'],
                "threshold_category": approval_request['threshold_category'],
                "auto_approved": approval_request.get('auto_approve', False)
            }
            
        except Exception as e:
            return {"error": f"Failed to create approval request: {str(e)}"}
    
    def process_approval(self, request_id: str, decision: str, approver: str, comments: str = "") -> dict:
        """
        Process an approval decision for a pending request.
        
        Args:
            request_id: The request ID to process
            decision: 'APPROVED' or 'REJECTED'
            approver: Who is making the approval decision
            comments: Optional approval comments
            
        Returns:
            Dictionary with approval processing result
        """
        try:
            # Find the request
            request = None
            for req in self.approval_requests:
                if req['request_id'] == request_id:
                    request = req
                    break
            
            if not request:
                return {"error": f"Approval request '{request_id}' not found"}
            
            if request['status'] != 'PENDING':
                return {"error": f"Request '{request_id}' is not pending (current status: {request['status']})"}
            
            if decision not in ['APPROVED', 'REJECTED']:
                return {"error": "Decision must be 'APPROVED' or 'REJECTED'"}
            
            # Validate approver authority
            if request['requires_director'] and 'director' not in approver.lower():
                return {"error": "Director approval required for this request"}
            
            if request['requires_manager'] and 'manager' not in approver.lower() and 'director' not in approver.lower():
                return {"error": "Manager or Director approval required for this request"}
            
            # Update request
            request['status'] = decision
            request['approver'] = approver
            request['approval_timestamp'] = datetime.now().isoformat()
            
            # Add comment
            comment_entry = {
                "timestamp": datetime.now().isoformat(),
                "author": approver,
                "comment": comments or f"Request {decision.lower()}"
            }
            request['comments'].append(comment_entry)
            
            # Move to history
            self.approval_history.append(request.copy())
            
            return {
                "success": True,
                "request_id": request_id,
                "decision": decision,
                "approver": approver,
                "timestamp": request['approval_timestamp'],
                "cost": request['cost'],
                "description": request['description']
            }
            
        except Exception as e:
            return {"error": f"Failed to process approval: {str(e)}"}
    
    def get_approval_request(self, request_id: str) -> dict:
        """Get details of a specific approval request"""
        try:
            for request in self.approval_requests + self.approval_history:
                if request['request_id'] == request_id:
                    return request
            
            return {"error": f"Approval request '{request_id}' not found"}
            
        except Exception as e:
            return {"error": f"Error retrieving approval request: {str(e)}"}
    
    def get_pending_approvals(self, approver_type: str = None) -> Union[List[Dict], Dict]:
        """
        Get list of pending approval requests, optionally filtered by approver type.
        
        Args:
            approver_type: Filter by 'manager', 'director', or None for all
            
        Returns:
            List of pending approval requests
        """
        try:
            pending = [req for req in self.approval_requests if req['status'] == 'PENDING']
            
            if approver_type:
                if approver_type.lower() == 'manager':
                    pending = [req for req in pending if req['requires_manager'] and not req['requires_director']]
                elif approver_type.lower() == 'director':
                    pending = [req for req in pending if req['requires_director']]
            
            return pending
            
        except Exception as e:
            return {"error": f"Error getting pending approvals: {str(e)}"}
    
    def check_compliance(self, request_details: dict) -> dict:
        """
        Perform compliance checks on a request.
        
        Args:
            request_details: Dictionary with request information
            
        Returns:
            Dictionary with compliance check results
        """
        try:
            compliance_results = {
                "compliant": True,
                "violations": [],
                "warnings": [],
                "checks_performed": []
            }
            
            # Cost compliance check
            if 'cost' in request_details:
                cost = request_details['cost']
                threshold_info = self.get_approval_threshold(cost)
                
                compliance_results["checks_performed"].append("cost_threshold_check")
                
                if cost > 10000:  # Example compliance rule
                    compliance_results["warnings"].append(f"High cost item (${cost}) requires additional documentation")
                
                if cost < 0:
                    compliance_results["violations"].append("Negative cost values are not allowed")
                    compliance_results["compliant"] = False
            
            # Request type compliance
            if 'request_type' in request_details:
                request_type = request_details['request_type']
                compliance_results["checks_performed"].append("request_type_validation")
                
                valid_types = ['inventory_request', 'fleet_dispatch', 'maintenance', 'procurement']
                if request_type not in valid_types:
                    compliance_results["violations"].append(f"Invalid request type: {request_type}")
                    compliance_results["compliant"] = False
            
            # Description compliance
            if 'description' in request_details:
                description = request_details['description']
                compliance_results["checks_performed"].append("description_validation")
                
                if len(description.strip()) < 10:
                    compliance_results["violations"].append("Description must be at least 10 characters long")
                    compliance_results["compliant"] = False
            
            return compliance_results
            
        except Exception as e:
            return {"error": f"Compliance check failed: {str(e)}"}
    
    def get_approval_statistics(self) -> dict:
        """Get approval workflow statistics"""
        try:
            all_requests = self.approval_requests + self.approval_history
            
            if not all_requests:
                return {
                    "total_requests": 0,
                    "pending_requests": 0,
                    "approved_requests": 0,
                    "rejected_requests": 0,
                    "auto_approved_requests": 0,
                    "average_approval_time": 0
                }
            
            status_counts = {}
            for req in all_requests:
                status = req['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            auto_approved = len([req for req in all_requests if req.get('approver') == 'SYSTEM_AUTO'])
            
            return {
                "total_requests": len(all_requests),
                "pending_requests": status_counts.get('PENDING', 0),
                "approved_requests": status_counts.get('APPROVED', 0),
                "rejected_requests": status_counts.get('REJECTED', 0),
                "auto_approved_requests": auto_approved,
                "approval_rate": (status_counts.get('APPROVED', 0) / len(all_requests)) * 100 if all_requests else 0,
                "threshold_distribution": {
                    threshold: len([req for req in all_requests if req['threshold_category'] == threshold])
                    for threshold in self.approval_df.index
                }
            }
            
        except Exception as e:
            return {"error": f"Error getting approval statistics: {str(e)}"}
    
    def search_approvals(self, search_criteria: dict) -> Union[List[Dict], Dict]:
        """
        Search approval requests based on various criteria.
        
        Args:
            search_criteria: Dictionary with search parameters (status, requester, cost_range, etc.)
            
        Returns:
            List of matching approval requests
        """
        try:
            all_requests = self.approval_requests + self.approval_history
            results = all_requests.copy()
            
            # Filter by status
            if 'status' in search_criteria:
                results = [req for req in results if req['status'] == search_criteria['status']]
            
            # Filter by requester
            if 'requester' in search_criteria:
                results = [req for req in results if search_criteria['requester'].lower() in req['requester'].lower()]
            
            # Filter by cost range
            if 'min_cost' in search_criteria:
                results = [req for req in results if req['cost'] >= search_criteria['min_cost']]
            
            if 'max_cost' in search_criteria:
                results = [req for req in results if req['cost'] <= search_criteria['max_cost']]
            
            # Filter by threshold category
            if 'threshold_category' in search_criteria:
                results = [req for req in results if req['threshold_category'] == search_criteria['threshold_category']]
            
            return results
            
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}


def initialize_approval_manager(approval_df):
    """Initialize the approval manager with the provided DataFrame."""
    manager = ApprovalDataProvider(approval_df)
    
    print("✅ Approval Data Manager initialized!")
    print(f"⚖️ Managing {len(approval_df)} approval thresholds")
    print(f"📋 Approval categories: {list(approval_df.index)}")
    
    return manager