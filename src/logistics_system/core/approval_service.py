#!/usr/bin/env python3
"""
Approval Service - Core Business Logic
=====================================

Extracted business logic from ApproverAgent for better separation of concerns.
This service handles all approval operations independent of the Strands framework.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass

# LLM Integration for AI capabilities (using Ollama)
try:
    import requests
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Configuration loader import
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config_loader import get_approver_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    ESCALATED = "escalated"


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ApprovalRequest:
    """Approval request data structure"""
    request_id: str
    request_type: str
    cost: float
    priority: str
    description: str
    requested_by: str
    created_at: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    risk_level: Optional[RiskLevel] = None


class ApprovalService:
    """
    Core approval business logic service.
    
    This class contains all the business logic for approval operations,
    separated from Strands framework concerns. Can be used independently
    or wrapped by ApproverAgent.
    """
    
    def __init__(self, llm_model: str = None):
        # Load configuration from .env file
        import os
        llm_backend = os.getenv('LLM_BACKEND', 'ollama').lower()
        self.llm_model = llm_model or os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
        self.llm_enabled = LLM_AVAILABLE and (llm_backend == 'ollama')
        
        # Get Ollama URL from .env with fallback
        ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_url = f"{ollama_base_url}/api/generate" if not ollama_base_url.endswith('/api/generate') else ollama_base_url
        
        # Test LLM connection
        if self.llm_enabled and llm_backend == 'ollama':
            try:
                test_response = requests.post(
                    self.ollama_url,
                    json={"model": self.llm_model, "prompt": "Hello", "stream": False},
                    timeout=15
                )
                if test_response.status_code == 200:
                    logger.info(f"✅ Ollama connected successfully for approval AI with model: {self.llm_model}")
                else:
                    self.llm_enabled = False
                    logger.warning(f"✅ Ollama connection failed - using rule-based approval logic")
            except Exception as e:
                self.llm_enabled = False
                logger.warning(f"✅ Ollama not available ({str(e)}) - using rule-based approval logic")
        else:
            logger.warning("✅ Requests library not available - using rule-based approval logic")
        
        # Load approval configuration
        self._load_approval_configuration()

    def _load_approval_configuration(self):
        """Load approval data from configuration files"""
        try:
            approver_config = get_approver_config()
            
            # Load approval policies and thresholds
            self.approval_policies = approver_config.get('approval_policies', {})
            
            # Default policies if config fails
            if not self.approval_policies:
                self.approval_policies = {
                    "cost_thresholds": {
                        "auto_approve": 1000.0,
                        "manager_approval": 5000.0,
                        "director_approval": 25000.0,
                        "board_approval": 100000.0
                    },
                    "priority_rules": {
                        "URGENT": {"auto_approve_limit": 2000.0, "escalate_immediately": True},
                        "HIGH": {"auto_approve_limit": 1500.0, "escalate_immediately": False},
                        "MEDIUM": {"auto_approve_limit": 1000.0, "escalate_immediately": False},
                        "LOW": {"auto_approve_limit": 500.0, "escalate_immediately": False}
                    },
                    "business_rules": {
                        "require_justification_above": 2000.0,
                        "require_multiple_quotes_above": 10000.0,
                        "require_budget_verification": True,
                        "compliance_checks_required": True
                    }
                }
            
            # Load approval authorities
            self.approval_authorities = approver_config.get('approval_authorities', [])
            if not self.approval_authorities:
                self.approval_authorities = [
                    {"role": "system", "max_amount": 1000.0, "authority_level": 1},
                    {"role": "supervisor", "max_amount": 5000.0, "authority_level": 2},
                    {"role": "manager", "max_amount": 25000.0, "authority_level": 3},
                    {"role": "director", "max_amount": 100000.0, "authority_level": 4}
                ]
            
            # Initialize approval tracking
            self.approval_requests = {}
            self.approval_history = []
            
            logger.info(f"✅ Loaded approval config: {len(self.approval_authorities)} authorities")
            
        except Exception as e:
            logger.error(f"❌ Failed to load approval configuration: {e}")
            # Use minimal fallback configuration
            self.approval_policies = {
                "cost_thresholds": {"auto_approve": 1000.0, "manager_approval": 5000.0},
                "priority_rules": {"URGENT": {"auto_approve_limit": 2000.0}},
                "business_rules": {"require_justification_above": 2000.0}
            }
            self.approval_authorities = [
                {"role": "system", "max_amount": 1000.0, "authority_level": 1}
            ]
            self.approval_requests = {}
            self.approval_history = []
        
        logger.info(f"✅ ApprovalService initialized with {len(self.approval_authorities)} approval authorities")

    async def llm_approval_decision(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Use Ollama LLM for intelligent approval decisions and risk assessment.
        
        Args:
            prompt: Decision prompt for the LLM
            context: Additional approval context data
            
        Returns:
            LLM response for approval decision-making
        """
        if not self.llm_enabled:
            return "LLM not available - using rule-based approval logic"
        
        try:
            # Prepare context for LLM
            context_str = ""
            if context:
                context_str = f"\nApproval Context: {json.dumps(context, indent=2)}"
            
            full_prompt = f"""You are an AI Approval Manager for a manufacturing facility.
Make intelligent approval decisions based on the following:

{prompt}{context_str}

Provide clear recommendations with reasoning, risk assessment, and compliance considerations. Be specific and actionable."""
            
            # Make request to Ollama
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.llm_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 250
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from Ollama").strip()
            else:
                logger.error(f"❌ Ollama API error: {response.status_code}")
                return f"Ollama API error - using rule-based approval logic"
            
        except Exception as e:
            logger.error(f"❌ Approval LLM decision failed: {str(e)}")
            return f"LLM error: {str(e)} - using rule-based approval logic"

    async def review_replenishment_plan(
        self,
        request_id: str,
        cost: float,
        priority: str = "MEDIUM",
        description: str = "",
        requested_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Review a replenishment plan request with AI-powered analysis.
        
        Args:
            request_id: Unique request identifier
            cost: Total cost of the replenishment plan
            priority: Request priority (LOW, MEDIUM, HIGH, URGENT)
            description: Description of the replenishment need
            requested_by: Who requested the approval
            
        Returns:
            Dict with approval decision, reasoning, and next steps
        """
        logger.info(f"✅ Reviewing replenishment plan: {request_id} (Cost: ${cost}, Priority: {priority})")
        
        try:
            await asyncio.sleep(0.2)  # Simulate processing time
            
            # Create approval request
            request = ApprovalRequest(
                request_id=request_id,
                request_type="replenishment_plan",
                cost=cost,
                priority=priority,
                description=description,
                requested_by=requested_by,
                created_at=datetime.now().isoformat()
            )
            
            # Perform risk assessment
            risk_assessment = await self.analyze_approval_risk({
                "request_id": request_id,
                "cost": cost,
                "priority": priority,
                "description": description,
                "type": "replenishment_plan"
            })
            
            request.risk_level = RiskLevel(risk_assessment.get("risk_level", "medium"))
            
            # Run business rules validation
            business_rules_result = await self.run_approval_checks_with_ai(cost, priority, description)
            
            # Make approval decision
            approval_decision = await self._make_approval_decision(request, risk_assessment, business_rules_result)
            
            # Store request
            self.approval_requests[request_id] = request
            
            # Generate audit trail entry
            audit_entry = {
                "request_id": request_id,
                "action": "review_initiated",
                "decision": approval_decision["decision"],
                "cost": cost,
                "priority": priority,
                "risk_level": request.risk_level.value,
                "reviewed_by": "approval_service",
                "reviewed_at": datetime.now().isoformat(),
                "reasoning": approval_decision.get("reasoning", "Automated decision")
            }
            
            self.approval_history.append(audit_entry)
            
            return {
                "success": True,
                "request_id": request_id,
                "decision": approval_decision["decision"],
                "status": approval_decision["status"].value,
                "risk_assessment": risk_assessment,
                "business_rules": business_rules_result,
                "reasoning": approval_decision["reasoning"],
                "next_steps": approval_decision.get("next_steps", []),
                "requires_escalation": approval_decision.get("requires_escalation", False),
                "reviewed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Replenishment plan review failed: {str(e)}")
            return {
                "success": False,
                "request_id": request_id,
                "error": str(e)
            }

    async def analyze_approval_risk(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze approval risk using AI-enhanced assessment.
        
        Args:
            request_data: Request details for risk analysis
            
        Returns:
            Dict with risk assessment and recommendations
        """
        try:
            cost = request_data.get("cost", 0)
            priority = request_data.get("priority", "MEDIUM")
            description = request_data.get("description", "")
            
            # Base risk assessment rules
            risk_factors = []
            risk_score = 0
            
            # Cost-based risk
            if cost > 50000:
                risk_factors.append("high_cost")
                risk_score += 30
            elif cost > 10000:
                risk_factors.append("medium_cost")
                risk_score += 15
            elif cost > 5000:
                risk_factors.append("elevated_cost")
                risk_score += 10
            
            # Priority-based risk
            if priority == "URGENT":
                risk_factors.append("urgent_priority")
                risk_score += 20
            elif priority == "HIGH":
                risk_factors.append("high_priority")
                risk_score += 10
            
            # Description-based risk (simplified keyword analysis)
            high_risk_keywords = ["emergency", "critical", "failure", "breakdown", "urgent"]
            if any(keyword in description.lower() for keyword in high_risk_keywords):
                risk_factors.append("emergency_keywords")
                risk_score += 15
            
            # Determine risk level
            if risk_score >= 40:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 25:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 15:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Get AI analysis
            risk_context = {
                "cost": cost,
                "priority": priority,
                "description": description,
                "calculated_risk_score": risk_score,
                "risk_factors": risk_factors
            }
            
            ai_risk_analysis = await self.llm_approval_decision(
                f"Assess the risk level for this approval request:\n"
                f"Cost: ${cost}\n"
                f"Priority: {priority}\n"
                f"Description: {description}\n"
                f"Risk Score: {risk_score}\n"
                f"Risk Factors: {', '.join(risk_factors)}\n\n"
                f"Provide risk assessment with specific concerns and mitigation recommendations.",
                risk_context
            )
            
            return {
                "success": True,
                "risk_level": risk_level.value,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "ai_analysis": ai_risk_analysis,
                "recommendations": self._get_risk_mitigation_recommendations(risk_level, risk_factors),
                "assessed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Risk analysis failed: {str(e)}")
            return {
                "success": False,
                "risk_level": "medium",
                "error": str(e)
            }

    async def run_approval_checks_with_ai(
        self,
        cost: float,
        priority: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Run comprehensive approval checks with AI assistance.
        
        Args:
            cost: Request cost
            priority: Request priority
            description: Request description
            
        Returns:
            Dict with validation results and recommendations
        """
        try:
            checks_results = {
                "budget_compliance": await self.check_budget_compliance(cost),
                "business_rules": await self.run_approval_checks(cost, priority, description),
                "policy_validation": self._validate_approval_policies(cost, priority),
                "authority_check": self._check_approval_authority(cost)
            }
            
            # Get AI validation
            validation_context = {
                "cost": cost,
                "priority": priority,
                "description": description,
                "checks_results": checks_results
            }
            
            ai_validation = await self.llm_approval_decision(
                f"Validate this approval request against business rules and policies:\n"
                f"Cost: ${cost}\n"
                f"Priority: {priority}\n"
                f"Description: {description}\n\n"
                f"Review the validation results and identify any compliance concerns or recommendations.",
                validation_context
            )
            
            # Determine overall validation status
            all_passed = all(
                result.get("compliant", True) for result in checks_results.values()
                if isinstance(result, dict)
            )
            
            return {
                "success": True,
                "overall_status": "passed" if all_passed else "failed",
                "checks_results": checks_results,
                "ai_validation": ai_validation,
                "compliance_score": self._calculate_compliance_score(checks_results),
                "validated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Approval checks failed: {str(e)}")
            return {
                "success": False,
                "overall_status": "error",
                "error": str(e)
            }

    async def run_approval_checks(
        self,
        cost: float,
        priority: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Run basic business rule checks for approval validation.
        """
        try:
            await asyncio.sleep(0.1)
            
            checks = {
                "cost_validation": cost > 0,
                "priority_validation": priority in ["LOW", "MEDIUM", "HIGH", "URGENT"],
                "description_provided": len(description.strip()) > 0,
                "within_policy_limits": cost <= self.approval_policies["cost_thresholds"]["board_approval"],
                "justification_required": cost > self.approval_policies["business_rules"]["require_justification_above"]
            }
            
            return {
                "checks": checks,
                "all_passed": all(checks.values()),
                "failed_checks": [check for check, passed in checks.items() if not passed]
            }
            
        except Exception as e:
            logger.error(f"❌ Basic approval checks failed: {str(e)}")
            return {"checks": {}, "all_passed": False, "error": str(e)}

    async def check_budget_compliance(self, cost: float) -> Dict[str, Any]:
        """
        Check budget compliance for the requested cost.
        """
        try:
            await asyncio.sleep(0.1)
            
            # Simplified budget check (would integrate with actual budget system)
            monthly_budget_limit = 100000.0  # Example limit
            current_month_spent = 25000.0    # Example current spending
            remaining_budget = monthly_budget_limit - current_month_spent
            
            compliant = cost <= remaining_budget
            utilization_percent = ((current_month_spent + cost) / monthly_budget_limit) * 100
            
            return {
                "compliant": compliant,
                "remaining_budget": remaining_budget,
                "requested_cost": cost,
                "budget_utilization_percent": round(utilization_percent, 1),
                "budget_limit": monthly_budget_limit,
                "warning": utilization_percent > 80,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Budget compliance check failed: {str(e)}")
            return {"compliant": False, "error": str(e)}

    async def check_approval_status(self, request_id: str) -> Dict[str, Any]:
        """
        Check the current status of an approval request.
        
        Args:
            request_id: Request identifier to check
            
        Returns:
            Dict with current approval status and history
        """
        try:
            await asyncio.sleep(0.1)
            
            # Find request
            if request_id not in self.approval_requests:
                return {
                    "success": False,
                    "request_id": request_id,
                    "error": "Approval request not found"
                }
            
            request = self.approval_requests[request_id]
            
            # Get related history
            request_history = [
                entry for entry in self.approval_history
                if entry["request_id"] == request_id
            ]
            
            # Calculate processing time
            created_time = datetime.fromisoformat(request.created_at)
            processing_time_minutes = (datetime.now() - created_time).total_seconds() / 60
            
            return {
                "success": True,
                "request_id": request_id,
                "status": request.status.value,
                "risk_level": request.risk_level.value if request.risk_level else "unknown",
                "cost": request.cost,
                "priority": request.priority,
                "description": request.description,
                "requested_by": request.requested_by,
                "created_at": request.created_at,
                "processing_time_minutes": round(processing_time_minutes, 1),
                "history": request_history,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Approval status check failed: {str(e)}")
            return {
                "success": False,
                "request_id": request_id,
                "error": str(e)
            }

    async def get_approval_requirements(
        self,
        cost: float,
        priority: str = "MEDIUM",
        request_type: str = "replenishment"
    ) -> Dict[str, Any]:
        """
        Get approval requirements for a given request.
        """
        try:
            await asyncio.sleep(0.1)
            
            # Determine required authority level
            required_authority = self._get_required_authority(cost)
            
            # Get applicable policies
            priority_rules = self.approval_policies.get("priority_rules", {}).get(priority, {})
            
            # Check if auto-approval is possible
            auto_approve_limit = priority_rules.get("auto_approve_limit", 
                                                    self.approval_policies["cost_thresholds"]["auto_approve"])
            can_auto_approve = cost <= auto_approve_limit
            
            requirements = {
                "approval_required": cost > 0,
                "can_auto_approve": can_auto_approve,
                "required_authority": required_authority,
                "estimated_processing_time_hours": self._estimate_processing_time(cost, priority),
                "documents_required": self._get_required_documents(cost, request_type),
                "justification_required": cost > self.approval_policies["business_rules"]["require_justification_above"],
                "multiple_quotes_required": cost > self.approval_policies["business_rules"]["require_multiple_quotes_above"]
            }
            
            return {
                "success": True,
                "cost": cost,
                "priority": priority,
                "requirements": requirements,
                "applicable_policies": priority_rules,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Get approval requirements failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    # Helper methods
    
    async def _make_approval_decision(
        self,
        request: ApprovalRequest,
        risk_assessment: Dict[str, Any],
        business_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make the final approval decision based on all assessments"""
        try:
            cost = request.cost
            priority = request.priority
            risk_level = risk_assessment.get("risk_level", "medium")
            
            # Auto-approval logic
            auto_approve_limit = self.approval_policies["priority_rules"].get(priority, {}).get(
                "auto_approve_limit", self.approval_policies["cost_thresholds"]["auto_approve"]
            )
            
            if cost <= auto_approve_limit and risk_level == "low" and business_rules.get("overall_status") == "passed":
                request.status = ApprovalStatus.APPROVED
                return {
                    "decision": "auto_approved",
                    "status": ApprovalStatus.APPROVED,
                    "reasoning": f"Auto-approved: Cost ${cost} within limit ${auto_approve_limit}, low risk, compliant",
                    "next_steps": ["Process immediately"],
                    "requires_escalation": False
                }
            
            # High-risk or high-cost requires review
            elif risk_level in ["high", "critical"] or cost > self.approval_policies["cost_thresholds"]["director_approval"]:
                request.status = ApprovalStatus.ESCALATED
                return {
                    "decision": "escalated",
                    "status": ApprovalStatus.ESCALATED,
                    "reasoning": f"Escalated: {risk_level} risk or high cost ${cost}",
                    "next_steps": ["Route to senior approval", "Additional review required"],
                    "requires_escalation": True
                }
            
            # Standard approval required
            else:
                request.status = ApprovalStatus.REQUIRES_REVIEW
                return {
                    "decision": "requires_review",
                    "status": ApprovalStatus.REQUIRES_REVIEW,
                    "reasoning": f"Standard review required for ${cost} {priority} priority request",
                    "next_steps": ["Route to appropriate approver", "Standard processing"],
                    "requires_escalation": False
                }
                
        except Exception as e:
            logger.error(f"❌ Approval decision failed: {str(e)}")
            return {
                "decision": "error",
                "status": ApprovalStatus.REQUIRES_REVIEW,
                "reasoning": f"Error in decision process: {str(e)}",
                "requires_escalation": True
            }

    def _validate_approval_policies(self, cost: float, priority: str) -> Dict[str, Any]:
        """Validate request against approval policies"""
        try:
            thresholds = self.approval_policies["cost_thresholds"]
            priority_rules = self.approval_policies["priority_rules"].get(priority, {})
            
            validations = {
                "within_auto_approve": cost <= thresholds["auto_approve"],
                "within_manager_limit": cost <= thresholds["manager_approval"],
                "within_director_limit": cost <= thresholds["director_approval"],
                "within_board_limit": cost <= thresholds["board_approval"],
                "priority_valid": priority in self.approval_policies["priority_rules"]
            }
            
            return {
                "validations": validations,
                "compliant": all(validations.values()),
                "applicable_threshold": self._get_applicable_threshold(cost)
            }
            
        except Exception as e:
            return {"validations": {}, "compliant": False, "error": str(e)}

    def _check_approval_authority(self, cost: float) -> Dict[str, Any]:
        """Check required approval authority for cost"""
        try:
            required_authority = None
            for authority in sorted(self.approval_authorities, key=lambda x: x["max_amount"]):
                if cost <= authority["max_amount"]:
                    required_authority = authority
                    break
            
            if not required_authority:
                required_authority = max(self.approval_authorities, key=lambda x: x["max_amount"])
            
            return {
                "required_authority": required_authority,
                "authority_available": True,  # Simplified
                "compliant": True
            }
            
        except Exception as e:
            return {"required_authority": None, "compliant": False, "error": str(e)}

    def _get_risk_mitigation_recommendations(self, risk_level: RiskLevel, risk_factors: List[str]) -> List[str]:
        """Get risk mitigation recommendations"""
        recommendations = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Require senior management approval")
            recommendations.append("Conduct additional vendor verification")
        
        if "high_cost" in risk_factors:
            recommendations.append("Obtain multiple quotes for comparison")
            recommendations.append("Verify budget availability")
        
        if "urgent_priority" in risk_factors:
            recommendations.append("Validate urgency justification")
            recommendations.append("Consider expedited approval process")
        
        return recommendations

    def _calculate_compliance_score(self, checks_results: Dict[str, Any]) -> float:
        """Calculate overall compliance score"""
        try:
            total_checks = 0
            passed_checks = 0
            
            for result in checks_results.values():
                if isinstance(result, dict) and "compliant" in result:
                    total_checks += 1
                    if result["compliant"]:
                        passed_checks += 1
            
            return round((passed_checks / total_checks) * 100, 1) if total_checks > 0 else 0.0
            
        except Exception:
            return 0.0

    def _get_required_authority(self, cost: float) -> Dict[str, Any]:
        """Get required approval authority for cost"""
        for authority in sorted(self.approval_authorities, key=lambda x: x["max_amount"]):
            if cost <= authority["max_amount"]:
                return authority
        
        return max(self.approval_authorities, key=lambda x: x["max_amount"])

    def _estimate_processing_time(self, cost: float, priority: str) -> int:
        """Estimate processing time in hours"""
        base_time = 2  # Base 2 hours
        
        if cost > 50000:
            base_time += 24  # Add 1 day for high cost
        elif cost > 10000:
            base_time += 8   # Add 8 hours for medium cost
        
        if priority == "URGENT":
            base_time = max(1, base_time // 2)  # Expedite urgent requests
        elif priority == "LOW":
            base_time += 24  # Add delay for low priority
        
        return base_time

    def _get_required_documents(self, cost: float, request_type: str) -> List[str]:
        """Get list of required documents"""
        documents = ["Request justification"]
        
        if cost > 10000:
            documents.extend(["Budget approval", "Vendor quotes"])
        
        if cost > 50000:
            documents.extend(["Executive approval", "Risk assessment"])
        
        if request_type == "capital_expenditure":
            documents.extend(["Capital approval form", "ROI analysis"])
        
        return documents

    def _get_applicable_threshold(self, cost: float) -> str:
        """Get the applicable approval threshold name"""
        thresholds = self.approval_policies["cost_thresholds"]
        
        if cost <= thresholds["auto_approve"]:
            return "auto_approve"
        elif cost <= thresholds["manager_approval"]:
            return "manager_approval"
        elif cost <= thresholds["director_approval"]:
            return "director_approval"
        else:
            return "board_approval"


# Global service instance
_approval_service = None

def get_approval_service() -> ApprovalService:
    """Get or create global approval service instance"""
    global _approval_service
    if _approval_service is None:
        _approval_service = ApprovalService()
    return _approval_service