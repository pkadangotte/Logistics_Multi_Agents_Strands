"""
Approval Agent Tool Provider
Contains tool provider class for approval workflow operations.
"""

import json
from strands import tool


class ApprovalAgentToolProvider:
    """Tool provider for approval workflow operations."""
    
    def __init__(self, approval_manager):
        self.approval_manager = approval_manager
    
    @tool(name="check_approval_threshold")
    def check_approval_threshold(self, cost: float) -> str:
        """
        Check if cost requires approval. Returns requires_approval (true/false).
        If false, skip create_approval_request and proceed to find_optimal_agv.
        If true, call create_approval_request next.
        """
        try:
            cost = float(cost)
            result = self.approval_manager.get_approval_threshold(cost)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid cost parameter: {cost}. Must be a number.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Approval threshold check failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="create_approval_request")
    def create_approval_request(self, cost: float, description: str, request_type: str, requester: str = "ApprovalAgent") -> str:
        """
        Create approval request. ONLY call if check_approval_threshold said requires_approval=true.
        Call ONCE. If status='auto_approved', proceed. If 'pending', stop and report.
        """
        try:
            cost = float(cost)
            request_details = {
                "cost": cost,
                "description": description,
                "request_type": request_type
            }
            result = self.approval_manager.create_approval_request(request_details, requester)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid cost parameter: {cost}. Must be a number.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Create approval request failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="process_approval")
    def process_approval(self, request_id: str, decision: str, approver: str, comments: str = "") -> str:
        """
        Manual approval processing. NOT needed in normal workflows.
        """
        result = self.approval_manager.process_approval(request_id, decision, approver, comments)
        return json.dumps(result, indent=2)
    
    @tool(name="get_pending_approvals")
    def get_pending_approvals(self, approver_type: str = None) -> str:
        """
        List pending approvals. For reporting only, not needed in workflows.
        """
        result = self.approval_manager.get_pending_approvals(approver_type)
        return json.dumps(result, indent=2)
    
    @tool(name="check_compliance")
    def check_compliance(self, cost: float, description: str, request_type: str) -> str:
        """
        Compliance check. Redundant - check_approval_threshold handles this.
        """
        try:
            cost = float(cost)
            request_details = {
                "cost": cost,
                "description": description,
                "request_type": request_type
            }
            result = self.approval_manager.check_compliance(request_details)
            return json.dumps(result, indent=2)
        except (ValueError, TypeError) as e:
            error_result = {"error": f"Invalid cost parameter: {cost}. Must be a number.", "details": str(e)}
            return json.dumps(error_result, indent=2)
        except Exception as e:
            error_result = {"error": f"Compliance check failed: {str(e)}"}
            return json.dumps(error_result, indent=2)
    
    @tool(name="get_approval_statistics")
    def get_approval_statistics(self) -> str:
        """
        Approval statistics. NEVER needed in delivery workflows.
        """
        result = self.approval_manager.get_approval_statistics()
        return json.dumps(result, indent=2)

    @property
    def tools(self):
        return [
            self.check_approval_threshold,
            self.create_approval_request,
            self.process_approval,
            self.get_pending_approvals,
            self.check_compliance,
            self.get_approval_statistics
        ]