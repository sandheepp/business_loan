"""Orchestrator Agent — 15-stage India MSME LOS pipeline coordination.

No LLM needed. Pure deterministic state machine + event routing.
"""
from datetime import datetime, timezone
from backend.agents.base_agent import BaseAgent
from backend.core.state_machine import LoanState, can_transition, get_next_states, get_approval_level
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
                    target = self._auto_next(current)

                if not target or not can_transition(current, target):
                    return {"error": f"Cannot transition from {current} to {target}",
                            "valid_transitions": next_states}

                app.status = target
                app.updated_at = datetime.now(timezone.utc)
                db.commit()
                self.audit(application_id, "state_transition", {"from": current, "to": target})
                tasks = self._get_triggered_tasks(target)
                return {"new_state": target, "triggered_tasks": tasks}

            return {"current": current, "next_states": next_states}
        finally:
            db.close()

    async def submit_application(self, application_id: str) -> dict:
        """Submit a draft application — moves from lead_created → application_submitted."""
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}
            if app.status not in (
                LoanState.LEAD_CREATED.value,
                LoanState.APPLICATION_DRAFT.value,
            ):
                return {"error": f"Application is already {app.status}"}

            app.status = LoanState.APPLICATION_SUBMITTED.value
            app.updated_at = datetime.now(timezone.utc)
            db.commit()
            self.audit(application_id, "application_submitted")
            return {"status": LoanState.APPLICATION_SUBMITTED.value, "next": "kyc_verification"}
        finally:
            db.close()

    async def run_pipeline(self, application_id: str) -> dict:
        """Run the full automated pipeline:
        KYC → Document → Data Extraction → Enrichment → Financial → Collateral → Underwriting → CAM → Route Approval
        """
        from backend.agents.compliance_agent import compliance_agent
        from backend.agents.document_agent import document_agent
        from backend.agents.underwriting_agent import underwriting_agent
        from backend.agents.pricing_agent import pricing_agent

        results = {}

        # ── Stage 3: KYC Verification ────────────────────────
        self._transition(application_id, LoanState.KYC_PENDING.value)
        self.audit(application_id, "pipeline_step", {"step": "kyc_verification"})
        results["kyc"] = await compliance_agent.process(application_id)
        self._transition(application_id, LoanState.KYC_VERIFIED.value)

        # ── Stage 4: Document Collection ─────────────────────
        self._transition(application_id, LoanState.DOCUMENT_COLLECTION.value)
        self._transition(application_id, LoanState.DOCUMENT_REVIEW.value)
        self.audit(application_id, "pipeline_step", {"step": "document_review"})
        results["documents"] = await document_agent.process(application_id)

        # ── Stage 5: Data Extraction ──────────────────────────
        self._transition(application_id, LoanState.DATA_EXTRACTION.value)
        self.audit(application_id, "pipeline_step", {"step": "data_extraction"})

        # ── Stage 6: External Data Enrichment ────────────────
        self._transition(application_id, LoanState.DATA_ENRICHMENT.value)
        self.audit(application_id, "pipeline_step", {"step": "data_enrichment"})

        # ── Stage 7: Financial Analysis ───────────────────────
        self._transition(application_id, LoanState.FINANCIAL_ANALYSIS.value)
        self.audit(application_id, "pipeline_step", {"step": "financial_analysis"})
        results["underwriting"] = await underwriting_agent.process(application_id)

        # ── Stage 8: Collateral Assessment ────────────────────
        self._transition(application_id, LoanState.COLLATERAL_ASSESSMENT.value)
        self.audit(application_id, "pipeline_step", {"step": "collateral_assessment"})
        results["pricing"] = await pricing_agent.process(application_id)

        # ── Stage 9 → 10: Underwriting → CAM ─────────────────
        self._transition(application_id, LoanState.UNDERWRITING.value)
        self._transition(application_id, LoanState.CAM_DRAFT.value)
        self._transition(application_id, LoanState.CAM_FINALIZED.value)
        self.audit(application_id, "pipeline_step", {"step": "cam_finalized"})

        # ── Stage 11: Route to appropriate approval level ─────
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if app:
                approval_state = get_approval_level(app.loan_amount)
                app.status = approval_state
                app.approval_level = approval_state.replace("pending_", "")
                app.updated_at = datetime.now(timezone.utc)
                db.commit()
                self.audit(application_id, "approval_routed", {
                    "approval_level": approval_state,
                    "loan_amount": app.loan_amount,
                })
                results["approval_state"] = approval_state
        finally:
            db.close()

        self.audit(application_id, "pipeline_complete", {
            "dscr": results["underwriting"].get("dscr"),
            "risk_score": results["underwriting"].get("risk_score"),
            "cibil_score": results["kyc"].get("cibil_score"),
        })

        return results

    async def approve(self, application_id: str, data: dict) -> dict:
        """Approve a loan application → move to Sanctioned."""
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}

            approval_states = [
                LoanState.PENDING_BCM.value,
                LoanState.PENDING_RCH.value,
                LoanState.PENDING_CC.value,
            ]
            if app.status not in approval_states:
                return {"error": f"Cannot approve from status: {app.status}"}

            app.status = LoanState.SANCTIONED.value
            app.approved_by = data.get("approved_by", "")
            app.approved_at = datetime.now(timezone.utc)
            app.approval_conditions = data.get("conditions", [])
            app.sanction_amount = app.recommended_loan_amount or app.loan_amount
            app.sanction_interest_rate = app.recommended_interest_rate or 12.5
            app.sanction_tenure_months = app.loan_tenure_months or 60
            # Calculate EMI: P × r × (1+r)^n / ((1+r)^n - 1)
            p = app.sanction_amount
            r = app.sanction_interest_rate / 100 / 12
            n = app.sanction_tenure_months
            if r > 0:
                app.sanction_emi = p * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
            app.updated_at = datetime.now(timezone.utc)
            db.commit()

            self.audit(application_id, "loan_approved", {
                "approved_by": data.get("approved_by"),
                "amount": app.sanction_amount,
                "rate": app.sanction_interest_rate,
            })
            return {"status": "sanctioned", "sanction_amount": app.sanction_amount}
        finally:
            db.close()

    async def decline(self, application_id: str, data: dict) -> dict:
        """Decline a loan application."""
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}

            app.status = LoanState.DECLINED.value
            app.updated_at = datetime.now(timezone.utc)
            db.commit()
            self.audit(application_id, "loan_declined", {
                "declined_by": data.get("declined_by"),
                "reason": data.get("reason", ""),
            })
            return {"status": "declined"}
        finally:
            db.close()

    async def disburse(self, application_id: str, data: dict) -> dict:
        """Trigger disbursement — validates pre-conditions then disburses."""
        import random
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}

            # Pre-disbursement checklist
            checklist = {
                "kyc_verified": app.kyc_pan_status == "verified",
                "collateral_registered": app.property_registered,
                "sanction_signed": app.sanction_signed_at is not None,
            }
            if not all(checklist.values()):
                return {"error": "Pre-disbursement checklist incomplete", "checklist": checklist}

            app.status = LoanState.DISBURSED.value
            app.disbursed_amount = app.sanction_amount
            app.disbursed_at = datetime.now(timezone.utc)
            app.disbursement_reference = f"CBS{random.randint(1000000, 9999999)}"
            app.updated_at = datetime.now(timezone.utc)
            db.commit()

            self.audit(application_id, "loan_disbursed", {
                "amount": app.disbursed_amount,
                "reference": app.disbursement_reference,
            })
            return {"status": "disbursed", "reference": app.disbursement_reference}
        finally:
            db.close()

    def _transition(self, application_id: str, target_state: str):
        """Force a state transition (used internally by pipeline)."""
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if app:
                app.status = target_state
                app.updated_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

    def _auto_next(self, current: str) -> str | None:
        mapping = {
            LoanState.LEAD_CREATED.value: LoanState.APPLICATION_DRAFT.value,
            LoanState.APPLICATION_DRAFT.value: LoanState.APPLICATION_SUBMITTED.value,
            LoanState.APPLICATION_SUBMITTED.value: LoanState.KYC_PENDING.value,
            LoanState.KYC_PENDING.value: LoanState.KYC_IN_REVIEW.value,
            LoanState.KYC_IN_REVIEW.value: LoanState.KYC_VERIFIED.value,
            LoanState.KYC_VERIFIED.value: LoanState.DOCUMENT_COLLECTION.value,
            LoanState.DOCUMENT_COLLECTION.value: LoanState.DOCUMENT_REVIEW.value,
            LoanState.DOCUMENT_REVIEW.value: LoanState.DATA_EXTRACTION.value,
            LoanState.DATA_EXTRACTION.value: LoanState.DATA_ENRICHMENT.value,
            LoanState.DATA_ENRICHMENT.value: LoanState.FINANCIAL_ANALYSIS.value,
            LoanState.FINANCIAL_ANALYSIS.value: LoanState.COLLATERAL_ASSESSMENT.value,
            LoanState.COLLATERAL_ASSESSMENT.value: LoanState.UNDERWRITING.value,
            LoanState.UNDERWRITING.value: LoanState.CAM_DRAFT.value,
            LoanState.CAM_DRAFT.value: LoanState.CAM_FINALIZED.value,
        }
        return mapping.get(current)

    def _get_triggered_tasks(self, state: str) -> list[str]:
        triggers = {
            LoanState.KYC_PENDING.value: ["validate_pan", "verify_aadhaar", "fetch_ckyc"],
            LoanState.DOCUMENT_REVIEW.value: ["classify_documents", "ocr_extract", "check_completeness"],
            LoanState.DATA_EXTRACTION.value: ["extract_bank_statements", "parse_itr", "parse_balance_sheet"],
            LoanState.DATA_ENRICHMENT.value: ["fetch_cibil", "fetch_gstn", "fetch_mca", "bank_aggregation"],
            LoanState.FINANCIAL_ANALYSIS.value: ["calc_dscr", "calc_debt_equity", "calc_revenue_growth"],
            LoanState.COLLATERAL_ASSESSMENT.value: ["assign_valuer", "calc_ltv", "encumbrance_check"],
            LoanState.UNDERWRITING.value: ["risk_scoring", "financial_ratios", "anomaly_detection"],
            LoanState.CAM_DRAFT.value: ["generate_cam_draft"],
            LoanState.SANCTIONED.value: ["generate_sanction_letter"],
            LoanState.LEGAL_DOCS.value: ["generate_loan_agreement", "generate_mortgage_deed", "generate_guarantee"],
        }
        return triggers.get(state, [])


orchestrator = OrchestratorAgent()
