#!/usr/bin/env python3
"""
AI-Powered Approver Agent - Part of Manufacturing Replenishment System
=====================================================================

This intelligent agent manages approval workflows including:
- AI-driven cost approval with risk assessment
- Intelligent priority-based approval routing
- Smart business rule validation with context analysis
- AI-enhanced compliance checking
- Intelligent audit trail maintenance
- Predictive approval recommendations
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# LLM Integration for AI capabilities (using Ollama)
try:
    import requests
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Requests not installed. Run: pip install requests")

# Placeholder for Strands imports
try:
    from strands_agents import Agent, tool
except ImportError:
    class Agent:
        def __init__(self, name: str):
            self.name = name
    
    def tool(func):
        return func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApproverAgent(Agent):
    """
    AI-Powered Approver Agent that manages approval workflows with intelligent decision-making.
    Uses LLM for risk assessment, compliance validation, and approval routing decisions.
    """
    
    def __init__(self, name: str = "ApproverAgent", llm_model: str = "llama3:latest"):
        super().__init__(name=name)
        self.llm_model = llm_model
        self.llm_enabled = LLM_AVAILABLE
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Test Ollama connection
        if self.llm_enabled:
            try:
                # Test if Ollama is running
                test_response = requests.post(
                    self.ollama_url,
                    json={"model": self.llm_model, "prompt": "Hello", "stream": False},
                    timeout=15
                )
                if test_response.status_code == 200:
                    logger.info(f"⚖️  Ollama connected successfully for approval AI with model: {self.llm_model}")
                else:
                    self.llm_enabled = False
                    logger.warning(f"⚖️  Ollama connection failed - using rule-based approvals")
            except Exception as e:
                self.llm_enabled = False
                logger.warning(f"⚖️  Ollama not available ({str(e)}) - using rule-based approvals")
        else:
            logger.warning("⚖️  Requests library not available - using rule-based approvals")
        
        # Approval configuration
        self.approval_thresholds = {
            "auto_approve_limit": 500.00,  # Auto-approve below this amount
            "manager_approval_limit": 2000.00,  # Manager approval required
            "director_approval_limit": 10000.00  # Director approval required
        }
        
        # Priority-based approval rules
        self.priority_rules = {
            "URGENT": {"auto_approve_multiplier": 2.0, "expedite": True},
            "HIGH": {"auto_approve_multiplier": 1.5, "expedite": True},
            "MEDIUM": {"auto_approve_multiplier": 1.0, "expedite": False},
            "LOW": {"auto_approve_multiplier": 0.8, "expedite": False}
        }
        
        # Mock approvers database
        self.approvers = {
            "AUTO-SYSTEM": {
                "name": "Automated System",
                "role": "system",
                "approval_limit": self.approval_thresholds["auto_approve_limit"],
                "available": True
            },
            "MGR-001": {
                "name": "Production Manager Smith", 
                "role": "manager",
                "approval_limit": self.approval_thresholds["manager_approval_limit"],
                "available": True,
                "department": "Production"
            },
            "DIR-001": {
                "name": "Operations Director Jones",
                "role": "director", 
                "approval_limit": self.approval_thresholds["director_approval_limit"],
                "available": True,
                "department": "Operations"
            }
        }
        
        # Approval history (for audit trail)
        self.approval_history = []
        
        # Historical approval patterns for AI learning
        self.approval_patterns = {
            "cost_trends": [
                {"month": "2025-10", "avg_approved_cost": 1250.00, "approval_rate": 0.89},
                {"month": "2025-09", "avg_approved_cost": 1180.00, "approval_rate": 0.92},
                {"month": "2025-08", "avg_approved_cost": 1340.00, "approval_rate": 0.85}
            ],
            "priority_patterns": {
                "URGENT": {"approval_rate": 0.96, "avg_time_hours": 0.5},
                "HIGH": {"approval_rate": 0.91, "avg_time_hours": 2.0},
                "MEDIUM": {"approval_rate": 0.87, "avg_time_hours": 8.0},
                "LOW": {"approval_rate": 0.73, "avg_time_hours": 24.0}
            },
            "department_patterns": {
                "Production": {"approval_rate": 0.94, "cost_sensitivity": "low"},
                "Quality": {"approval_rate": 0.88, "cost_sensitivity": "medium"},
                "Maintenance": {"approval_rate": 0.91, "cost_sensitivity": "low"}
            }
        }
        
        logger.info(f"⚖️  AI ApproverAgent initialized with {len(self.approvers)} approvers and historical patterns")

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

Provide clear approval recommendations with risk assessment and reasoning. Be decisive and specific."""
            
            # Make request to Ollama
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.llm_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 200
                    }
                },
                timeout=60
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

    async def analyze_approval_risk(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to analyze approval risks and provide recommendations.
        
        Args:
            request_data: Request details for risk analysis
            
        Returns:
            AI-powered risk analysis
        """
        try:
            risk_context = {
                "estimated_cost": request_data.get("estimated_cost", 0),
                "priority": request_data.get("priority", "MEDIUM"),
                "department": request_data.get("department", "Production"),
                "historical_patterns": self.approval_patterns,
                "current_month_approvals": len(self.approval_history),
                "business_justification": request_data.get("business_justification", "")
            }
            
            risk_prompt = f"""
Analyze the approval risk for this request:
Cost: ${request_data.get('estimated_cost', 0)}
Priority: {request_data.get('priority', 'MEDIUM')}
Justification: {request_data.get('business_justification', 'N/A')}

Assess:
1. Financial risk level (LOW/MEDIUM/HIGH)
2. Operational impact assessment
3. Compliance considerations
4. Recommended approval path
5. Risk mitigation strategies

Provide structured risk assessment with clear recommendations.
"""
            
            llm_analysis = await self.llm_approval_decision(risk_prompt, risk_context)
            
            return {
                "success": True,
                "request_id": request_data.get("request_id", "N/A"),
                "risk_analysis": llm_analysis,
                "risk_context": risk_context,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Risk analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @tool
    async def review_replenishment_plan(
        self,
        request_id: str,
        original_request: Dict[str, Any],
        inventory_plan: Dict[str, Any],
        fleet_plan: Dict[str, Any],
        estimated_cost: float,
        business_justification: str,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Review and approve/reject a complete replenishment plan.
        
        Args:
            request_id: Request ID being reviewed
            original_request: Original replenishment request
            inventory_plan: Inventory availability results
            fleet_plan: Fleet delivery plan
            estimated_cost: Total estimated cost
            business_justification: Business justification
            priority: Request priority
            
        Returns:
            Dict with approval decision and details
        """
        logger.info(f"✅ Reviewing replenishment plan: {request_id} (Cost: ${estimated_cost})")
        
        try:
            await asyncio.sleep(0.2)  # Simulate review time
            
            # Use AI for comprehensive approval analysis
            approval_context = {
                "request_id": request_id,
                "estimated_cost": estimated_cost,
                "priority": priority,
                "business_justification": business_justification,
                "inventory_availability": inventory_plan.get("available", False),
                "fleet_scheduling": fleet_plan.get("scheduled", False),
                "historical_patterns": self.approval_patterns
            }
            
            approval_prompt = f"""
Review this replenishment plan for approval:

REQUEST: {request_id}
COST: ${estimated_cost}
PRIORITY: {priority}
JUSTIFICATION: {business_justification}

Inventory Status: {"✅ Available" if inventory_plan.get("available") else "❌ Limited"}
Fleet Status: {"✅ AGV Scheduled" if fleet_plan.get("scheduled") else "❌ No AGV Available"}

Decision needed: APPROVE, APPROVE_WITH_CONDITIONS, or REJECT
Consider:
1. Cost vs budget thresholds
2. Business justification strength
3. Priority level appropriateness
4. Resource availability
5. Risk factors

Provide decision with clear reasoning.
"""
            
            ai_recommendation = await self.llm_approval_decision(approval_prompt, approval_context)
            
            # Determine required approval level
            approval_level = self.determine_approval_level(estimated_cost, priority)
            
            # Get appropriate approver
            approver = self.get_approver_for_level(approval_level)
            
            if not approver:
                return {
                    "approved": False,
                    "error": f"No available approver for level: {approval_level}",
                    "required_action": "Escalate to higher authority",
                    "ai_recommendation": ai_recommendation
                }
            
            # Run approval checks with AI analysis
            approval_checks = await self.run_approval_checks_with_ai(
                original_request, inventory_plan, fleet_plan, estimated_cost, priority, ai_recommendation
            )
            
            # Make AI-enhanced approval decision
            approval_decision = self.make_ai_approval_decision(
                approval_checks, estimated_cost, priority, business_justification, ai_recommendation
            )
            
            # Record approval
            approval_record = {
                "approved": approval_decision["approved"],
                "request_id": request_id,
                "approver_id": approver["id"],
                "approver_name": approver["name"],
                "approver_role": approver["role"],
                "approval_level": approval_level,
                "estimated_cost": estimated_cost,
                "priority": priority,
                "approval_reason": approval_decision["reason"],
                "conditions": approval_decision.get("conditions", []),
                "checks_passed": approval_checks["all_passed"],
                "failed_checks": approval_checks.get("failed_checks", []),
                "business_justification": business_justification,
                "approved_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat() if approval_decision["approved"] else None
            }
            
            # Add to approval history
            self.approval_history.append(approval_record)
            
            logger.info(f"✅ Approval decision: {approval_decision['approved']} by {approver['name']}")
            
            return approval_record
            
        except Exception as e:
            logger.error(f"❌ Approval review failed: {str(e)}")
            return {
                "approved": False,
                "error": str(e),
                "request_id": request_id
            }

    @tool
    async def check_approval_status(self, request_id: str) -> Dict[str, Any]:
        """
        Check the approval status of a request.
        
        Args:
            request_id: Request ID to check
            
        Returns:
            Dict with approval status information
        """
        logger.info(f"🔍 Checking approval status: {request_id}")
        
        try:
            await asyncio.sleep(0.1)
            
            # Find approval record
            approval_record = None
            for record in self.approval_history:
                if record["request_id"] == request_id:
                    approval_record = record
                    break
            
            if not approval_record:
                return {
                    "found": False,
                    "error": f"No approval record found for {request_id}"
                }
            
            # Check if approval is still valid
            is_valid = True
            if approval_record.get("expires_at"):
                expiry_time = datetime.fromisoformat(approval_record["expires_at"])
                is_valid = datetime.now() < expiry_time
            
            return {
                "found": True,
                "request_id": request_id,
                "approved": approval_record["approved"],
                "approver": approval_record["approver_name"],
                "approval_level": approval_record["approval_level"],
                "approved_at": approval_record["approved_at"],
                "is_valid": is_valid,
                "conditions": approval_record.get("conditions", []),
                "approval_reason": approval_record["approval_reason"]
            }
            
        except Exception as e:
            logger.error(f"❌ Status check failed: {str(e)}")
            return {
                "found": False,
                "error": str(e)
            }

    @tool
    async def get_approval_requirements(
        self,
        estimated_cost: float,
        priority: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Get approval requirements for a given cost and priority.
        
        Args:
            estimated_cost: Estimated total cost
            priority: Request priority
            
        Returns:
            Dict with approval requirements
        """
        logger.info(f"📋 Getting approval requirements: ${estimated_cost} ({priority})")
        
        try:
            await asyncio.sleep(0.1)
            
            approval_level = self.determine_approval_level(estimated_cost, priority)
            required_approver = self.get_approver_for_level(approval_level)
            
            # Calculate effective cost limit based on priority
            priority_config = self.priority_rules.get(priority, self.priority_rules["MEDIUM"])
            effective_limit = self.approval_thresholds["auto_approve_limit"] * priority_config["auto_approve_multiplier"]
            
            requirements = {
                "estimated_cost": estimated_cost,
                "priority": priority,
                "approval_level": approval_level,
                "required_approver": {
                    "name": required_approver["name"],
                    "role": required_approver["role"],
                    "available": required_approver["available"]
                } if required_approver else None,
                "effective_auto_approve_limit": effective_limit,
                "expedited_processing": priority_config["expedite"],
                "estimated_approval_time": self.estimate_approval_time(approval_level, priority),
                "required_documentation": self.get_required_documentation(approval_level),
                "compliance_checks": self.get_compliance_requirements(estimated_cost, priority)
            }
            
            return {
                "success": True,
                "requirements": requirements
            }
            
        except Exception as e:
            logger.error(f"❌ Requirements check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def determine_approval_level(self, cost: float, priority: str) -> str:
        """Determine required approval level based on cost and priority"""
        
        # Adjust cost based on priority
        priority_config = self.priority_rules.get(priority, self.priority_rules["MEDIUM"])
        effective_cost = cost / priority_config["auto_approve_multiplier"]
        
        if effective_cost <= self.approval_thresholds["auto_approve_limit"]:
            return "auto"
        elif effective_cost <= self.approval_thresholds["manager_approval_limit"]:
            return "manager"
        elif effective_cost <= self.approval_thresholds["director_approval_limit"]:
            return "director"
        else:
            return "board"

    def get_approver_for_level(self, approval_level: str) -> Dict[str, Any]:
        """Get appropriate approver for the given level"""
        
        if approval_level == "auto":
            return {
                "id": "AUTO-SYSTEM",
                "name": self.approvers["AUTO-SYSTEM"]["name"],
                "role": self.approvers["AUTO-SYSTEM"]["role"],
                "available": True
            }
        elif approval_level == "manager":
            for approver_id, approver_data in self.approvers.items():
                if approver_data["role"] == "manager" and approver_data["available"]:
                    return {
                        "id": approver_id,
                        "name": approver_data["name"],
                        "role": approver_data["role"],
                        "available": approver_data["available"]
                    }
        elif approval_level == "director":
            for approver_id, approver_data in self.approvers.items():
                if approver_data["role"] == "director" and approver_data["available"]:
                    return {
                        "id": approver_id,
                        "name": approver_data["name"],
                        "role": approver_data["role"],
                        "available": approver_data["available"]
                    }
        
        return None

    async def run_approval_checks_with_ai(
        self,
        original_request: Dict[str, Any],
        inventory_plan: Dict[str, Any],
        fleet_plan: Dict[str, Any],
        estimated_cost: float,
        priority: str,
        ai_recommendation: str
    ) -> Dict[str, Any]:
        """Run approval checks enhanced with AI analysis"""
        
        # Traditional checks
        traditional_checks = {
            "budget_check": await self.check_budget_compliance(estimated_cost),
            "inventory_check": self.check_inventory_plan(inventory_plan),
            "fleet_check": self.check_fleet_plan(fleet_plan),
            "priority_check": self.check_priority_justification(original_request, priority),
            "business_rules_check": self.check_business_rules(original_request, estimated_cost)
        }
        
        # AI-enhanced risk assessment
        risk_analysis = await self.analyze_approval_risk({
            "request_id": original_request.get("request_id", "N/A"),
            "estimated_cost": estimated_cost,
            "priority": priority,
            "business_justification": original_request.get("business_justification", ""),
            "department": original_request.get("department", "Production")
        })
        
        # AI compliance check
        ai_compliance_check = {
            "passed": "APPROVE" in ai_recommendation.upper(),
            "ai_analysis": ai_recommendation,
            "risk_assessment": risk_analysis.get("risk_analysis", "N/A") if risk_analysis.get("success") else "Risk analysis failed"
        }
        
        # Combined results
        all_checks = {**traditional_checks, "ai_compliance_check": ai_compliance_check}
        failed_checks = [check_name for check_name, result in all_checks.items() if not result.get("passed", False)]
        
        return {
            "checks": all_checks,
            "all_passed": len(failed_checks) == 0,
            "failed_checks": failed_checks,
            "ai_recommendation": ai_recommendation,
            "risk_analysis": risk_analysis
        }

    async def run_approval_checks(
        self,
        original_request: Dict[str, Any],
        inventory_plan: Dict[str, Any],
        fleet_plan: Dict[str, Any],
        estimated_cost: float,
        priority: str
    ) -> Dict[str, Any]:
        """Run various approval checks (fallback method)"""
        
        checks = {
            "budget_check": await self.check_budget_compliance(estimated_cost),
            "inventory_check": self.check_inventory_plan(inventory_plan),
            "fleet_check": self.check_fleet_plan(fleet_plan),
            "priority_check": self.check_priority_justification(original_request, priority),
            "business_rules_check": self.check_business_rules(original_request, estimated_cost)
        }
        
        failed_checks = [check_name for check_name, result in checks.items() if not result["passed"]]
        
        return {
            "checks": checks,
            "all_passed": len(failed_checks) == 0,
            "failed_checks": failed_checks
        }

    async def check_budget_compliance(self, cost: float) -> Dict[str, Any]:
        """Check if cost is within budget limits"""
        # Simplified budget check
        monthly_budget_limit = 50000.00
        
        return {
            "passed": cost <= monthly_budget_limit,
            "details": f"Cost ${cost} vs Budget ${monthly_budget_limit}",
            "check_type": "budget_compliance"
        }

    def check_inventory_plan(self, inventory_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inventory plan"""
        return {
            "passed": inventory_plan.get("available", False),
            "details": "Inventory availability confirmed" if inventory_plan.get("available") else "Inventory not available",
            "check_type": "inventory_validation"
        }

    def check_fleet_plan(self, fleet_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fleet delivery plan"""
        return {
            "passed": fleet_plan.get("scheduled", False) if fleet_plan else True,
            "details": "Delivery scheduled" if fleet_plan and fleet_plan.get("scheduled") else "No delivery required or scheduled",
            "check_type": "fleet_validation"
        }

    def check_priority_justification(self, request: Dict[str, Any], priority: str) -> Dict[str, Any]:
        """Check if priority level is justified"""
        bin_level = request.get("current_bin_level", request.get("CurrentBinLevel", 100))
        
        if priority == "URGENT" and bin_level > 10:
            return {
                "passed": False,
                "details": f"URGENT priority not justified with bin level {bin_level}",
                "check_type": "priority_justification"
            }
        
        return {
            "passed": True,
            "details": f"Priority {priority} justified",
            "check_type": "priority_justification"
        }

    def check_business_rules(self, request: Dict[str, Any], cost: float) -> Dict[str, Any]:
        """Check compliance with business rules"""
        # Example business rule: Cost per unit shouldn't exceed $50
        quantity = request.get("quantity_requested", request.get("RemainingQuantityRequired", 1))
        cost_per_unit = cost / quantity if quantity > 0 else 0
        
        if cost_per_unit > 50.0:
            return {
                "passed": False,
                "details": f"Cost per unit ${cost_per_unit:.2f} exceeds limit of $50.00",
                "check_type": "business_rules"
            }
        
        return {
            "passed": True,
            "details": f"Cost per unit ${cost_per_unit:.2f} within limits",
            "check_type": "business_rules"
        }

    def make_ai_approval_decision(
        self,
        approval_checks: Dict[str, Any],
        cost: float,
        priority: str,
        justification: str,
        ai_recommendation: str
    ) -> Dict[str, Any]:
        """Make AI-enhanced approval decision"""
        
        # Extract AI decision
        ai_decision = "APPROVE" if "APPROVE" in ai_recommendation.upper() else "REJECT"
        ai_has_conditions = "CONDITIONS" in ai_recommendation.upper() or "CONDITION" in ai_recommendation.upper()
        
        # Check critical AI compliance
        ai_check = approval_checks.get("checks", {}).get("ai_compliance_check", {})
        if not ai_check.get("passed", False):
            return {
                "approved": False,
                "reason": f"AI analysis recommends rejection: {ai_recommendation[:100]}...",
                "conditions": [],
                "ai_recommendation": ai_recommendation,
                "risk_level": "HIGH"
            }
        
        # Auto-reject if critical traditional checks failed
        if not approval_checks["all_passed"]:
            critical_failures = [
                check for check in approval_checks["failed_checks"]
                if check in ["budget_check", "business_rules_check"]
            ]
            
            if critical_failures:
                return {
                    "approved": False,
                    "reason": f"Critical checks failed: {', '.join(critical_failures)} despite AI approval",
                    "conditions": [],
                    "ai_recommendation": ai_recommendation,
                    "risk_level": "HIGH"
                }
        
        # Conditional approval based on AI analysis
        conditions = []
        if ai_has_conditions:
            conditions.extend([
                "AI compliance monitoring required",
                "Enhanced audit trail mandatory",
                "Performance metrics tracking enabled"
            ])
        
        if priority == "URGENT" and cost > 1000:
            conditions.append("Executive notification required within 24 hours")
        
        approval_reason = f"AI-assisted approval: {ai_recommendation[:80]}..."
        
        return {
            "approved": True,
            "reason": approval_reason,
            "conditions": conditions,
            "ai_recommendation": ai_recommendation,
            "risk_level": "LOW" if ai_decision == "APPROVE" and not ai_has_conditions else "MEDIUM"
        }

    def make_approval_decision(
        self,
        approval_checks: Dict[str, Any],
        cost: float,
        priority: str,
        justification: str
    ) -> Dict[str, Any]:
        """Make the final approval decision (fallback method)"""
        
        # Auto-reject if critical checks failed
        if not approval_checks["all_passed"]:
            critical_failures = [
                check for check in approval_checks["failed_checks"]
                if check in ["budget_check", "business_rules_check"]
            ]
            
            if critical_failures:
                return {
                    "approved": False,
                    "reason": f"Critical checks failed: {', '.join(critical_failures)}",
                    "conditions": []
                }
        
        # Conditional approval for non-critical failures
        conditions = []
        if "inventory_check" in approval_checks.get("failed_checks", []):
            conditions.append("Alternative inventory source must be confirmed")
        
        if "fleet_check" in approval_checks.get("failed_checks", []):
            conditions.append("Delivery arrangement must be confirmed within 4 hours")
        
        # Approve with or without conditions
        return {
            "approved": True,
            "reason": f"Approved for {priority} priority replenishment (${cost})",
            "conditions": conditions
        }

    def estimate_approval_time(self, approval_level: str, priority: str) -> str:
        """Estimate approval processing time"""
        base_times = {
            "auto": "< 1 minute",
            "manager": "15-30 minutes", 
            "director": "1-2 hours",
            "board": "24-48 hours"
        }
        
        if priority in ["URGENT", "HIGH"]:
            return f"Expedited: {base_times.get(approval_level, 'Unknown')}"
        
        return base_times.get(approval_level, "Unknown")

    def get_required_documentation(self, approval_level: str) -> List[str]:
        """Get required documentation for approval level"""
        docs = {
            "auto": ["System generated request"],
            "manager": ["Business justification", "Cost breakdown"],
            "director": ["Business justification", "Cost breakdown", "Impact assessment"],
            "board": ["Business justification", "Cost breakdown", "Impact assessment", "Risk analysis", "Alternative analysis"]
        }
        
        return docs.get(approval_level, [])

    def get_compliance_requirements(self, cost: float, priority: str) -> List[str]:
        """Get compliance requirements"""
        requirements = ["Budget compliance verification"]
        
        if cost > 1000:
            requirements.append("Procurement policy compliance")
        
        if priority in ["HIGH", "URGENT"]:
            requirements.append("Emergency procurement justification")
        
        return requirements

    @tool
    async def get_ai_approval_insights(self) -> Dict[str, Any]:
        """
        Get AI-powered insights on approval patterns and optimization opportunities.
        
        Returns:
            Dict with LLM-generated approval optimization recommendations
        """
        logger.info(f"⚖️  Getting AI approval insights and optimization recommendations")
        
        try:
            # Gather comprehensive approval data for analysis
            approval_context = {
                "total_approvals": len(self.approval_history),
                "approval_thresholds": self.approval_thresholds,
                "historical_patterns": self.approval_patterns,
                "current_approvers": {aid: {"name": data["name"], "role": data["role"], "available": data["available"]} 
                                   for aid, data in self.approvers.items()},
                "recent_approvals": self.approval_history[-10:] if self.approval_history else []
            }
            
            insights_prompt = """
Analyze the current approval system and provide optimization recommendations:

1. APPROVAL EFFICIENCY: Are current thresholds optimal for business operations?
2. BOTTLENECK ANALYSIS: Identify potential approval process bottlenecks?
3. RISK OPTIMIZATION: Balance between control and operational speed?
4. AUTOMATION OPPORTUNITIES: What additional approvals can be automated?
5. COMPLIANCE IMPROVEMENTS: Enhanced compliance without slowing operations?

Provide specific, actionable recommendations with priorities.
"""
            
            llm_analysis = await self.llm_approval_decision(insights_prompt, approval_context)
            
            return {
                "success": True,
                "ai_insights": llm_analysis,
                "approval_metrics": approval_context,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI approval insights failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @tool
    async def predict_approval_outcome(
        self,
        estimated_cost: float,
        priority: str,
        business_justification: str,
        department: str = "Production"
    ) -> Dict[str, Any]:
        """
        Use AI to predict approval outcome before formal submission.
        
        Args:
            estimated_cost: Estimated cost of the request
            priority: Request priority level
            business_justification: Business justification text
            department: Requesting department
            
        Returns:
            Dict with AI-powered approval prediction
        """
        logger.info(f"🔮 Predicting approval outcome for ${estimated_cost} {priority} request")
        
        try:
            prediction_context = {
                "estimated_cost": estimated_cost,
                "priority": priority,
                "department": department,
                "historical_patterns": self.approval_patterns,
                "approval_thresholds": self.approval_thresholds
            }
            
            prediction_prompt = f"""
Predict the approval outcome for this request:

COST: ${estimated_cost}
PRIORITY: {priority}
DEPARTMENT: {department}
JUSTIFICATION: {business_justification}

Based on historical patterns and thresholds, predict:
1. Approval probability (percentage)
2. Expected approval level required
3. Potential concerns or objections
4. Recommended improvements to increase approval chances
5. Estimated processing time

Provide realistic assessment with actionable recommendations.
"""
            
            llm_prediction = await self.llm_approval_decision(prediction_prompt, prediction_context)
            
            return {
                "success": True,
                "cost": estimated_cost,
                "priority": priority,
                "department": department,
                "ai_prediction": llm_prediction,
                "prediction_context": prediction_context,
                "predicted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Approval prediction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

def create_approver_agent() -> ApproverAgent:
    """Factory function to create AI-powered ApproverAgent with Ollama"""
    return ApproverAgent(name="AI_ApproverAgent", llm_model="llama3:latest")

if __name__ == "__main__":
    # Test the AI-powered approver agent
    async def test_ai_approver_agent():
        agent = create_approver_agent()
        
        print("⚖️  Testing AI-Powered Approver Agent")
        print("=" * 50)
        
        # Test AI approval prediction
        print("\n🔮 Testing AI approval prediction...")
        prediction = await agent.predict_approval_outcome(
            estimated_cost=1250.00,
            priority="HIGH",
            business_justification="Critical production line shutdown requires immediate part replacement",
            department="Production"
        )
        if prediction.get("success"):
            print(f"AI Prediction: {prediction['ai_prediction'][:150]}...")
        
        # Test AI-enhanced approval process
        print("\n⚖️  Testing AI approval process...")
        mock_request = {"current_bin_level": 5, "quantity_requested": 50, "business_justification": "Critical production need", "department": "Production"}
        mock_inventory = {"available": True, "cost_per_unit": 10.0}
        mock_fleet = {"scheduled": True, "delivery_cost": 50.0}
        
        approval = await agent.review_replenishment_plan(
            "AI-TEST-REQ-001", mock_request, mock_inventory, mock_fleet,
            650.00, "Critical production part shortage affecting delivery schedules", "HIGH"
        )
        
        print(f"✅ Approved: {approval.get('approved', False)}")
        print(f"⚖️  Approver: {approval.get('approver_name', 'N/A')}")
        print(f"🎯 Risk Level: {approval.get('risk_level', 'N/A')}")
        if 'ai_recommendation' in approval:
            print(f"🧠 AI Decision: {approval['ai_recommendation'][:120]}...")
        
        # Test approval insights
        print("\n🧠 Testing AI approval insights...")
        insights = await agent.get_ai_approval_insights()
        if insights.get("success"):
            print(f"AI Insights: {insights['ai_insights'][:200]}...")
        
        # Test status check with AI context
        if approval.get("approved"):
            print("\n📊 Testing approval status check...")
            status = await agent.check_approval_status("AI-TEST-REQ-001")
            print(f"Status: {'✅ Valid' if status.get('is_valid') else '❌ Invalid'}")
            print(f"Conditions: {len(status.get('conditions', []))} conditions applied")
    
    asyncio.run(test_ai_approver_agent())
