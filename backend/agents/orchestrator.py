"""Orchestrator Agent — Workflow coordination, state machine, escalation.

No LLM needed. Pure deterministic state machine + event routing.
"""
from datetime import datetime, timezone
from backend.agents.base_agent import BaseAgent
from backend.core.state_machine import LoanState, can_transition, get_next_states
from backend.core.audit_log import log_event
from backend.database import SessionLocal, LoanApplication


class OrchestratorAgent(BaseAgent):
    agent_name = "orchestrator"

    async def process(self, application_id: str, **kwargs) -> dict:
        """Advance the loan through its lifecycle."""
        action = kwargs.get("action", "check")
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}

            current = app.status
            next_states = get_next_states(current)

            if action == "check":
                return {"current": current, "next_states": next_states}

            if action == "advance":
                target = kwargs.get("target_state")
                if not target:
                    # Auto-advance to next logical state
                    target = self._auto_next(current)

                if not target or not can_transition(current, target):
                    return {"error": f"Cannot transition from {current} to {target}",
                            "valid_transitions": next_states}

                app.status = target
                app.updated_at = datetime.now(timezone.utc)
                db.commit()

                self.audit(application_id, "state_transition", {
                    "from": current, "to": target,
                })

                # Trigger downstream agents based on new state
                tasks = self._get_triggered_tasks(target)
                return {"new_state": target, "triggered_tasks": tasks}

            return {"current": current, "next_states": next_states}
        finally:
            db.close()

    async def submit_application(self, application_id: str) -> dict:
        """Submit a draft application — kicks off the full pipeline."""
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}
            if app.status != "draft":
                return {"error": f"Application is {app.status}, not draft"}

            app.status = LoanState.SUBMITTED.value
            app.updated_at = datetime.now(timezone.utc)
            db.commit()

            self.audit(application_id, "application_submitted")

            return {"status": "submitted", "next": "compliance_check"}
        finally:
            db.close()

    async def run_pipeline(self, application_id: str) -> dict:
        """Run the full automated pipeline: compliance -> underwriting -> pricing."""
        from backend.agents.compliance_agent import compliance_agent
        from backend.agents.underwriting_agent import underwriting_agent
        from backend.agents.pricing_agent import pricing_agent

        results = {}

        # Step 1: Compliance
        self.audit(application_id, "pipeline_step", {"step": "compliance"})
        results["compliance"] = await compliance_agent.process(application_id)

        # Check if compliance passed
        comp = results["compliance"]
        if comp.get("flags"):
            self.audit(application_id, "pipeline_flagged", {"flags": comp["flags"]})

        # Step 2: Underwriting
        self.audit(application_id, "pipeline_step", {"step": "underwriting"})
        results["underwriting"] = await underwriting_agent.process(application_id)

        # Step 3: Pricing
        self.audit(application_id, "pipeline_step", {"step": "pricing"})
        results["pricing"] = await pricing_agent.process(application_id)

        # Update status to officer review
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if app:
                app.status = LoanState.OFFICER_REVIEW.value
                app.updated_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

        self.audit(application_id, "pipeline_complete", {
            "dscr": results["underwriting"].get("dscr", {}).get("dscr"),
            "risk_score": results["underwriting"].get("policy_score", {}).get("total_score"),
            "rate": results["pricing"].get("interest_rate"),
        })

        return results

    def _auto_next(self, current: str) -> str | None:
        mapping = {
            LoanState.DRAFT.value: LoanState.SUBMITTED.value,
            LoanState.SUBMITTED.value: LoanState.COMPLIANCE_CHECK.value,
            LoanState.COMPLIANCE_CHECK.value: LoanState.DOCUMENT_REVIEW.value,
            LoanState.DOCUMENT_REVIEW.value: LoanState.UNDERWRITING.value,
            LoanState.UNDERWRITING.value: LoanState.PRICING.value,
            LoanState.PRICING.value: LoanState.OFFICER_REVIEW.value,
        }
        return mapping.get(current)

    def _get_triggered_tasks(self, state: str) -> list[str]:
        triggers = {
            LoanState.COMPLIANCE_CHECK.value: ["run_kyb", "run_kyc", "screen_watchlist", "check_sba_eligibility"],
            LoanState.DOCUMENT_REVIEW.value: ["classify_documents", "extract_fields", "check_completeness"],
            LoanState.UNDERWRITING.value: ["financial_spreading", "calculate_dscr", "score_credit_policy"],
            LoanState.PRICING.value: ["calculate_rate", "generate_term_sheet"],
            LoanState.OFFICER_REVIEW.value: ["generate_underwriting_memo", "prepare_loan_file"],
        }
        return triggers.get(state, [])


orchestrator = OrchestratorAgent()
