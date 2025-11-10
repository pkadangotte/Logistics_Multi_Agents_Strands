#!/usr/bin/env python3
"""
AI-Powered Approver Agent - Strands Framework Wrapper
===================================================

REFACTORED VERSION - Clean separation of concerns.

This is a thin wrapper around ApprovalService that handles:
- Strands framework integration
- Tool registration with @tool decorators  
- Service initialization and delegation
- Backward compatibility interfaces

The actual business logic is in ApprovalService.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Strands Agent imports
from strands import Agent, tool

# Import the service layer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.logistics_system.core.approval_service import ApprovalService, get_approval_service
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    print(f"Warning: ApprovalService not available - {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApproverAgent:
    """
    Strands Framework Wrapper for ApprovalService.
    
    This class is a thin wrapper that delegates all business logic to ApprovalService
    while handling Strands framework concerns like tool registration and agent creation.
    
    Architecture:
    - ApproverAgent: Strands integration (this class - minimal code)
    - ApprovalService: Business logic (separate service - core functionality)
    """
    
    def __init__(self, llm_model: str = None):
        self.llm_model = llm_model or os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
        
        if SERVICE_AVAILABLE:
            # Use the service layer for all business logic
            self.service = get_approval_service()
            logger.info("✅ ApproverAgent using ApprovalService architecture")
            
            # Expose service properties for backward compatibility
            self.approval_policies = getattr(self.service, 'approval_policies', {})
            self.approval_authorities = getattr(self.service, 'approval_authorities', [])
            self.llm_enabled = getattr(self.service, 'llm_enabled', False)
        else:
            # Graceful degradation if service unavailable
            logger.error("❌ ApprovalService not available - agent will not function properly")
            self.service = None
            self.approval_policies = {}
            self.approval_authorities = []
            self.llm_enabled = False
        
        logger.info(f"✅ ApproverAgent initialized - Service: {SERVICE_AVAILABLE}, Authorities: {len(self.approval_authorities)}")

    # =============================================================================
    # DELEGATION METHODS - All business logic delegated to ApprovalService
    # =============================================================================

    async def review_replenishment_plan(
        self,
        request_id: str,
        cost: float,
        priority: str = "MEDIUM",
        description: str = "",
        requested_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Review replenishment plan - delegates to ApprovalService.
        """
        if not self.service:
            return {
                "success": False,
                "request_id": request_id,
                "error": "ApprovalService not available"
            }
        
        return await self.service.review_replenishment_plan(
            request_id, cost, priority, description, requested_by
        )

    async def check_approval_status(self, request_id: str) -> Dict[str, Any]:
        """
        Check approval status - delegates to ApprovalService.
        """
        if not self.service:
            return {
                "success": False,
                "request_id": request_id,
                "error": "ApprovalService not available"
            }
        
        return await self.service.check_approval_status(request_id)

    async def get_approval_requirements(
        self,
        cost: float,
        priority: str = "MEDIUM",
        request_type: str = "replenishment"
    ) -> Dict[str, Any]:
        """
        Get approval requirements - delegates to ApprovalService.
        """
        if not self.service:
            return {
                "success": False,
                "error": "ApprovalService not available"
            }
        
        return await self.service.get_approval_requirements(cost, priority, request_type)

    async def analyze_approval_risk(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze approval risk - delegates to ApprovalService.
        """
        if not self.service:
            return {
                "success": False,
                "error": "ApprovalService not available"
            }
        
        return await self.service.analyze_approval_risk(request_data)

    async def run_approval_checks_with_ai(
        self,
        cost: float,
        priority: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Run approval checks with AI - delegates to ApprovalService.
        """
        if not self.service:
            return {
                "success": False,
                "error": "ApprovalService not available"
            }
        
        return await self.service.run_approval_checks_with_ai(cost, priority, description)

    async def run_approval_checks(
        self,
        cost: float,
        priority: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Run basic approval checks - delegates to ApprovalService.
        """
        if not self.service:
            return {
                "checks": {},
                "all_passed": False,
                "error": "ApprovalService not available"
            }
        
        return await self.service.run_approval_checks(cost, priority, description)

    async def check_budget_compliance(self, cost: float) -> Dict[str, Any]:
        """
        Check budget compliance - delegates to ApprovalService.
        """
        if not self.service:
            return {
                "compliant": False,
                "error": "ApprovalService not available"
            }
        
        return await self.service.check_budget_compliance(cost)

    async def get_ai_approval_insights(self) -> Dict[str, Any]:
        """
        Get AI approval insights - uses ApprovalService capabilities.
        """
        if not self.service:
            return {
                "success": False,
                "error": "ApprovalService not available"
            }
        
        try:
            # Get recent approval data for analysis
            recent_requests = list(self.service.approval_requests.values())[-10:]  # Last 10 requests
            recent_history = self.service.approval_history[-20:]  # Last 20 history entries
            
            insights_context = {
                "total_requests": len(self.service.approval_requests),
                "recent_requests": len(recent_requests),
                "approval_policies": self.service.approval_policies,
                "recent_trends": {
                    "avg_cost": sum(req.cost for req in recent_requests) / len(recent_requests) if recent_requests else 0,
                    "priority_distribution": {
                        priority: sum(1 for req in recent_requests if req.priority == priority)
                        for priority in ["LOW", "MEDIUM", "HIGH", "URGENT"]
                    }
                }
            }
            
            insights_prompt = f"""
Analyze approval patterns and provide management insights:

Current System Status:
- Total approval requests processed: {insights_context['total_requests']}
- Recent requests (last 10): {insights_context['recent_requests']}
- Average recent cost: ${insights_context['recent_trends']['avg_cost']:.2f}

Priority Distribution:
- Urgent: {insights_context['recent_trends']['priority_distribution']['URGENT']}
- High: {insights_context['recent_trends']['priority_distribution']['HIGH']}
- Medium: {insights_context['recent_trends']['priority_distribution']['MEDIUM']}
- Low: {insights_context['recent_trends']['priority_distribution']['LOW']}

Provide insights on:
1. Approval process efficiency opportunities
2. Risk pattern analysis and trends
3. Policy optimization recommendations
4. Cost management insights
5. Process automation opportunities

Be specific and actionable for management decision-making.
"""
            
            ai_insights = await self.service.llm_approval_decision(insights_prompt, insights_context)
            
            return {
                "success": True,
                "ai_insights": ai_insights,
                "system_metrics": insights_context,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI approval insights failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def predict_approval_outcome(
        self,
        cost: float,
        priority: str,
        description: str,
        request_type: str = "replenishment"
    ) -> Dict[str, Any]:
        """
        Predict approval outcome - uses ApprovalService AI capabilities.
        """
        if not self.service:
            return {
                "success": False,
                "error": "ApprovalService not available"
            }
        
        try:
            # Get requirements and risk assessment
            requirements = await self.service.get_approval_requirements(cost, priority, request_type)
            risk_assessment = await self.service.analyze_approval_risk({
                "cost": cost,
                "priority": priority,
                "description": description,
                "type": request_type
            })
            
            if not requirements.get("success") or not risk_assessment.get("success"):
                return {
                    "success": False,
                    "error": "Unable to assess requirements or risk"
                }
            
            prediction_context = {
                "cost": cost,
                "priority": priority,
                "description": description,
                "requirements": requirements["requirements"],
                "risk_assessment": risk_assessment,
                "policies": self.service.approval_policies
            }
            
            prediction_prompt = f"""
Predict the approval outcome for this request:

Request Details:
- Cost: ${cost}
- Priority: {priority}
- Type: {request_type}
- Description: {description}

Risk Assessment: {risk_assessment.get('risk_level', 'unknown')} risk
Can Auto-Approve: {requirements['requirements'].get('can_auto_approve', False)}
Required Authority: {requirements['requirements'].get('required_authority', {}).get('role', 'unknown')}

Predict:
1. Likely approval outcome (approved/rejected/escalated)
2. Probability percentage (0-100%)
3. Expected processing time
4. Potential roadblocks or concerns
5. Recommendations to improve approval chances

Provide specific, actionable predictions.
"""
            
            ai_prediction = await self.service.llm_approval_decision(prediction_prompt, prediction_context)
            
            # Calculate simple rule-based probability
            base_probability = 80  # Base 80% approval chance
            
            if cost > self.service.approval_policies["cost_thresholds"]["director_approval"]:
                base_probability -= 30
            elif cost > self.service.approval_policies["cost_thresholds"]["manager_approval"]:
                base_probability -= 15
            
            if risk_assessment.get("risk_level") == "high":
                base_probability -= 20
            elif risk_assessment.get("risk_level") == "critical":
                base_probability -= 40
            
            if priority == "URGENT":
                base_probability += 10
            elif priority == "LOW":
                base_probability -= 10
            
            base_probability = max(10, min(95, base_probability))  # Clamp between 10-95%
            
            return {
                "success": True,
                "predicted_outcome": "approved" if base_probability > 60 else "requires_review" if base_probability > 30 else "likely_rejected",
                "approval_probability": base_probability,
                "ai_prediction": ai_prediction,
                "contributing_factors": prediction_context,
                "estimated_processing_time_hours": requirements["requirements"].get("estimated_processing_time_hours", 2),
                "predicted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Approval outcome prediction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# =============================================================================
# GLOBAL AGENT INSTANCE - Used by Strands tools
# =============================================================================

# Global ApproverAgent instance for tools to use
_approver_agent = ApproverAgent(llm_model="qwen2.5:7b")


# =============================================================================
# STRANDS TOOL FUNCTIONS - @tool decorated functions for Strands framework
# =============================================================================

@tool
async def process_approval_request(query: str) -> str:
    """
    Process a natural language approval request with intelligent routing and analysis.
    
    Args:
        query: Natural language description of the approval request
        
    Returns:
        String response with approval decision and reasoning
    """
    try:
        # Parse query for key information (simplified - would use more sophisticated NLP)
        import re
        
        # Extract cost information
        cost_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
        cost = float(cost_match.group(1).replace(',', '')) if cost_match else 1000.0
        
        # Extract priority
        priority = "MEDIUM"
        if any(word in query.lower() for word in ["urgent", "emergency", "critical"]):
            priority = "URGENT"
        elif any(word in query.lower() for word in ["high", "important", "asap"]):
            priority = "HIGH"
        elif any(word in query.lower() for word in ["low", "whenever", "routine"]):
            priority = "LOW"
        
        # Generate request ID
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Process through ApprovalService
        result = await _approver_agent.review_replenishment_plan(
            request_id=request_id,
            cost=cost,
            priority=priority,
            description=query,
            requested_by="user"
        )
        
        if result.get("success"):
            decision = result["decision"]
            reasoning = result["reasoning"]
            status = result["status"]
            
            return f"""
Approval Request Processed: {request_id}
Decision: {decision.upper()}
Status: {status}
Cost: ${cost:,.2f}
Priority: {priority}

Reasoning: {reasoning}

Next Steps: {', '.join(result.get('next_steps', ['Contact approver']))}
Risk Level: {result.get('risk_assessment', {}).get('risk_level', 'unknown')}
"""
        else:
            return f"Error processing approval request: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        logger.error(f"❌ Process approval request failed: {str(e)}")
        return f"Error: Unable to process approval request - {str(e)}"


@tool
async def check_approval_status(request_id: str) -> Dict[str, Any]:
    """
    Check the current status and history of an approval request.
    
    Args:
        request_id: Unique identifier of the approval request
        
    Returns:
        Dict with current status, history, and processing information
    """
    return await _approver_agent.check_approval_status(request_id)


@tool
async def get_approval_requirements(
    cost: float,
    priority: str = "MEDIUM",
    request_type: str = "replenishment"
) -> Dict[str, Any]:
    """
    Get approval requirements and policies for a given request.
    
    Args:
        cost: Total cost requiring approval
        priority: Request priority (LOW, MEDIUM, HIGH, URGENT)
        request_type: Type of request (replenishment, capital, etc.)
        
    Returns:
        Dict with approval requirements, authority levels, and processing estimates
    """
    return await _approver_agent.get_approval_requirements(cost, priority, request_type)


@tool
async def analyze_approval_risk(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the risk level of an approval request with AI assessment.
    
    Args:
        request_data: Dict containing request details (cost, priority, description, etc.)
        
    Returns:
        Dict with risk assessment, factors, and mitigation recommendations
    """
    return await _approver_agent.analyze_approval_risk(request_data)


@tool
async def get_ai_approval_insights() -> Dict[str, Any]:
    """
    Get AI-powered insights on approval patterns and process optimization.
    
    Returns:
        Dict with management insights, trends, and optimization recommendations
    """
    return await _approver_agent.get_ai_approval_insights()


# =============================================================================
# STRANDS AGENT FACTORY FUNCTION
# =============================================================================

def create_approver_agent(use_local_model: bool = False, hooks=None) -> Agent:
    """
    Factory function to create Strands Agent with ApproverAgent tools.
    
    Args:
        use_local_model: If True, uses local Ollama model instead of AWS Bedrock
        hooks: Optional observability hooks for monitoring
    
    Returns:
        Strands Agent configured with approval management tools
    """
    system_prompt = """You are an AI-powered Approval Manager for a manufacturing facility's procurement and expenditure processes.

Your responsibilities include:
- Processing and routing approval requests based on cost, priority, and risk factors
- Conducting intelligent risk assessment and compliance validation
- Managing approval workflows with appropriate authority levels
- Providing AI-driven insights on approval patterns and process optimization
- Ensuring adherence to business rules, budget constraints, and compliance requirements

You have access to advanced approval management tools that use AI/LLM capabilities for:
- Intelligent risk assessment with contextual analysis
- AI-powered approval routing and decision support
- Smart business rule validation and compliance checking
- Predictive approval outcome analysis
- Process optimization and efficiency recommendations

Approval capabilities:
- Multi-tier approval authority: System ($1K), Supervisor ($5K), Manager ($25K), Director ($100K+)
- Priority-based processing: URGENT (expedited), HIGH, MEDIUM, LOW (standard)
- Risk-based routing: Auto-approve low risk, escalate high risk requests
- Budget compliance validation with real-time utilization tracking
- Audit trail maintenance for compliance and reporting

Current approval policies:
- Auto-approval limit: $1,000 for standard priority, low-risk requests
- Manager approval required: $5,000+ or medium risk requests
- Director approval required: $25,000+ or high risk requests
- Board approval required: $100,000+ or critical risk requests
- Justification required: $2,000+ requests must include detailed rationale
- Multiple quotes required: $10,000+ capital expenditures

Be thorough, risk-conscious, and always ensure proper authorization levels.
Prioritize compliance and audit trail integrity while optimizing for processing efficiency."""

    # Configure agent with tools
    agent_kwargs = {
        "system_prompt": system_prompt,
        "tools": [
            process_approval_request,
            check_approval_status,
            get_approval_requirements,
            analyze_approval_risk,
            get_ai_approval_insights
        ]
    }
    
    # Add observability hooks if provided
    if hooks:
        agent_kwargs["hooks"] = hooks
        logger.info("🪝 Adding observability hooks to approver agent")
    
    # Configure model based on preference
    if use_local_model:
        try:
            from strands.models.ollama import OllamaModel
            agent_kwargs["model"] = OllamaModel(
                host="http://localhost:11434",
                model_id="qwen2.5:7b",
                keep_alive=300
            )
            logger.info("🤖 Using local Ollama model for approver agent")
        except ImportError:
            logger.warning("⚠️ OllamaModel not available, using default model")

    return Agent(**agent_kwargs)


# =============================================================================
# MAIN EXECUTION - For testing
# =============================================================================

if __name__ == "__main__":
    # Test the approver agent
    async def main():
        # Create agent
        agent = create_approver_agent(use_local_model=True)
        
        # Test approval processing
        result = await process_approval_request("I need approval for $15,000 emergency equipment repair")
        print(f"Approval processing result: {result}")
    
    asyncio.run(main())