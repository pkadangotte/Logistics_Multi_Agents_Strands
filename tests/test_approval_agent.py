"""
Test approval agent functionality.
"""

import pytest
from conftest import assert_agent_valid, assert_response_valid


class TestApprovalAgent:
    """Test approval agent functionality."""
    
    def test_approval_agent_info(self, approval_agent):
        """Test approval agent info retrieval."""
        assert_agent_valid(approval_agent)
        
        info = approval_agent.get_info()
        assert info['type'] == 'approval'
        assert info['total_tools'] > 0
    
    def test_approval_status_check(self, approval_agent):
        """Test approval status checking functionality."""
        test_queries = [
            "Check pending approvals",
            "What requests need approval?",
            "Show me all approval statuses"
        ]
        
        for query in test_queries:
            response = approval_agent.send_message(query)
            assert_response_valid(response)
    
    def test_approval_request_processing(self, approval_agent):
        """Test approval request processing."""
        response = approval_agent.send_message("Process approval request REQ001")
        assert_response_valid(response)
    
    def test_approval_workflow(self, approval_agent):
        """Test approval workflow functionality."""
        response = approval_agent.send_message("Show approval workflow for logistics requests")
        assert_response_valid(response)
    
    def test_pending_approvals(self, approval_agent):
        """Test pending approvals retrieval."""
        response = approval_agent.send_message("List all pending approval requests")
        assert_response_valid(response)
    
    def test_approval_history(self, approval_agent):
        """Test approval history functionality."""
        response = approval_agent.send_message("Show approval history for the last week")
        assert_response_valid(response)
    
    def test_approval_delegation(self, approval_agent):
        """Test approval delegation functionality."""
        response = approval_agent.send_message("Check who can approve high-value requests")
        assert_response_valid(response)