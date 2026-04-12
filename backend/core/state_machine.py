"""Loan lifecycle state machine — India MSME Secured Loan LOS.

15-stage pipeline from Lead Creation through Post-Disbursement Monitoring.
The Orchestrator uses this to manage the loan pipeline.
"""
from enum import Enum


class LoanState(str, Enum):
    # Stage 1: Lead Created
    LEAD_CREATED = "lead_created"
    # Stage 2: Borrower Application
    APPLICATION_DRAFT = "application_draft"
    APPLICATION_SUBMITTED = "application_submitted"
    # Stage 3: KYC & Business Verification
    KYC_PENDING = "kyc_pending"
    KYC_IN_REVIEW = "kyc_in_review"
    KYC_VERIFIED = "kyc_verified"
    KYC_FAILED = "kyc_failed"
    # Stage 4: Document Collection
    DOCUMENT_COLLECTION = "document_collection"
    DOCUMENT_REVIEW = "document_review"
    # Stage 5: Data Extraction
    DATA_EXTRACTION = "data_extraction"
    # Stage 6: External Data Enrichment
    DATA_ENRICHMENT = "data_enrichment"
    # Stage 7: Financial Analysis
    FINANCIAL_ANALYSIS = "financial_analysis"
    # Stage 8: Collateral Assessment
    COLLATERAL_ASSESSMENT = "collateral_assessment"
    # Stage 9: Credit Underwriting
    UNDERWRITING = "underwriting"
    # Stage 10: Credit Memo (CAM)
    CAM_DRAFT = "cam_draft"
    CAM_FINALIZED = "cam_finalized"
    # Stage 11: Approval Workflow
    PENDING_BCM = "pending_bcm"       # Branch Credit Manager (<50L)
    PENDING_RCH = "pending_rch"       # Regional Credit Head (50L–2Cr)
    PENDING_CC = "pending_cc"         # Credit Committee (>2Cr)
    # Stage 12: Sanction Letter
    SANCTIONED = "sanctioned"
    SANCTION_ACCEPTED = "sanction_accepted"
    # Stage 13: Legal Documentation
    LEGAL_DOCS = "legal_docs"
    LEGAL_VERIFIED = "legal_verified"
    # Stage 14: Disbursement
    DISBURSEMENT_PENDING = "disbursement_pending"
    DISBURSED = "disbursed"
    # Stage 15: Post-Disbursement Monitoring
    MONITORING = "monitoring"
    # Terminal states
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"


# Valid transitions: current_state -> [allowed_next_states]
TRANSITIONS = {
    LoanState.LEAD_CREATED: [LoanState.APPLICATION_DRAFT, LoanState.WITHDRAWN],
    LoanState.APPLICATION_DRAFT: [LoanState.APPLICATION_SUBMITTED, LoanState.WITHDRAWN],
    LoanState.APPLICATION_SUBMITTED: [LoanState.KYC_PENDING, LoanState.WITHDRAWN],
    LoanState.KYC_PENDING: [LoanState.KYC_IN_REVIEW],
    LoanState.KYC_IN_REVIEW: [LoanState.KYC_VERIFIED, LoanState.KYC_FAILED],
    LoanState.KYC_FAILED: [LoanState.KYC_PENDING, LoanState.DECLINED],
    LoanState.KYC_VERIFIED: [LoanState.DOCUMENT_COLLECTION],
    LoanState.DOCUMENT_COLLECTION: [LoanState.DOCUMENT_REVIEW],
    LoanState.DOCUMENT_REVIEW: [LoanState.DATA_EXTRACTION, LoanState.DOCUMENT_COLLECTION],
    LoanState.DATA_EXTRACTION: [LoanState.DATA_ENRICHMENT],
    LoanState.DATA_ENRICHMENT: [LoanState.FINANCIAL_ANALYSIS],
    LoanState.FINANCIAL_ANALYSIS: [LoanState.COLLATERAL_ASSESSMENT],
    LoanState.COLLATERAL_ASSESSMENT: [LoanState.UNDERWRITING],
    LoanState.UNDERWRITING: [LoanState.CAM_DRAFT, LoanState.DECLINED],
    LoanState.CAM_DRAFT: [LoanState.CAM_FINALIZED],
    LoanState.CAM_FINALIZED: [
        LoanState.PENDING_BCM, LoanState.PENDING_RCH, LoanState.PENDING_CC
    ],
    LoanState.PENDING_BCM: [LoanState.SANCTIONED, LoanState.DECLINED, LoanState.UNDERWRITING],
    LoanState.PENDING_RCH: [LoanState.SANCTIONED, LoanState.DECLINED, LoanState.UNDERWRITING],
    LoanState.PENDING_CC: [LoanState.SANCTIONED, LoanState.DECLINED, LoanState.UNDERWRITING],
    LoanState.SANCTIONED: [LoanState.SANCTION_ACCEPTED, LoanState.WITHDRAWN],
    LoanState.SANCTION_ACCEPTED: [LoanState.LEGAL_DOCS],
    LoanState.LEGAL_DOCS: [LoanState.LEGAL_VERIFIED],
    LoanState.LEGAL_VERIFIED: [LoanState.DISBURSEMENT_PENDING],
    LoanState.DISBURSEMENT_PENDING: [LoanState.DISBURSED],
    LoanState.DISBURSED: [LoanState.MONITORING],
    LoanState.MONITORING: [],  # ongoing state
    LoanState.DECLINED: [],   # terminal
    LoanState.WITHDRAWN: [],  # terminal
}

# Human-readable stage labels for UI
STAGE_LABELS = {
    LoanState.LEAD_CREATED: "Lead Created",
    LoanState.APPLICATION_DRAFT: "Application Draft",
    LoanState.APPLICATION_SUBMITTED: "Application Submitted",
    LoanState.KYC_PENDING: "KYC Pending",
    LoanState.KYC_IN_REVIEW: "KYC In Review",
    LoanState.KYC_VERIFIED: "KYC Verified",
    LoanState.KYC_FAILED: "KYC Failed",
    LoanState.DOCUMENT_COLLECTION: "Document Collection",
    LoanState.DOCUMENT_REVIEW: "Document Review",
    LoanState.DATA_EXTRACTION: "Data Extraction",
    LoanState.DATA_ENRICHMENT: "Data Enrichment",
    LoanState.FINANCIAL_ANALYSIS: "Financial Analysis",
    LoanState.COLLATERAL_ASSESSMENT: "Collateral Assessment",
    LoanState.UNDERWRITING: "Credit Underwriting",
    LoanState.CAM_DRAFT: "CAM Draft",
    LoanState.CAM_FINALIZED: "CAM Finalized",
    LoanState.PENDING_BCM: "Pending BCM Approval",
    LoanState.PENDING_RCH: "Pending RCH Approval",
    LoanState.PENDING_CC: "Pending Credit Committee",
    LoanState.SANCTIONED: "Sanctioned",
    LoanState.SANCTION_ACCEPTED: "Sanction Accepted",
    LoanState.LEGAL_DOCS: "Legal Documentation",
    LoanState.LEGAL_VERIFIED: "Legal Verified",
    LoanState.DISBURSEMENT_PENDING: "Disbursement Pending",
    LoanState.DISBURSED: "Disbursed",
    LoanState.MONITORING: "Post-Disbursement Monitoring",
    LoanState.DECLINED: "Declined",
    LoanState.WITHDRAWN: "Withdrawn",
}

# Stage grouping for pipeline display (stage number -> list of states)
STAGE_GROUPS = {
    1: [LoanState.LEAD_CREATED],
    2: [LoanState.APPLICATION_DRAFT, LoanState.APPLICATION_SUBMITTED],
    3: [LoanState.KYC_PENDING, LoanState.KYC_IN_REVIEW, LoanState.KYC_VERIFIED, LoanState.KYC_FAILED],
    4: [LoanState.DOCUMENT_COLLECTION, LoanState.DOCUMENT_REVIEW],
    5: [LoanState.DATA_EXTRACTION],
    6: [LoanState.DATA_ENRICHMENT],
    7: [LoanState.FINANCIAL_ANALYSIS],
    8: [LoanState.COLLATERAL_ASSESSMENT],
    9: [LoanState.UNDERWRITING],
    10: [LoanState.CAM_DRAFT, LoanState.CAM_FINALIZED],
    11: [LoanState.PENDING_BCM, LoanState.PENDING_RCH, LoanState.PENDING_CC],
    12: [LoanState.SANCTIONED, LoanState.SANCTION_ACCEPTED],
    13: [LoanState.LEGAL_DOCS, LoanState.LEGAL_VERIFIED],
    14: [LoanState.DISBURSEMENT_PENDING, LoanState.DISBURSED],
    15: [LoanState.MONITORING],
}


def can_transition(current: str, target: str) -> bool:
    """Check if a state transition is valid."""
    try:
        current_state = LoanState(current)
        target_state = LoanState(target)
        return target_state in TRANSITIONS.get(current_state, [])
    except ValueError:
        return False


def get_next_states(current: str) -> list[str]:
    """Get all valid next states from the current state."""
    try:
        current_state = LoanState(current)
        return [s.value for s in TRANSITIONS.get(current_state, [])]
    except ValueError:
        return []


def get_stage_number(state: str) -> int:
    """Return which LOS stage (1-15) the state belongs to."""
    try:
        s = LoanState(state)
        for stage_num, states in STAGE_GROUPS.items():
            if s in states:
                return stage_num
    except ValueError:
        pass
    return 0


def get_approval_level(loan_amount: float) -> str:
    """Determine approval authority based on loan amount (INR)."""
    if loan_amount < 5_000_000:       # < ₹50L
        return LoanState.PENDING_BCM.value
    elif loan_amount < 20_000_000:    # ₹50L – ₹2Cr
        return LoanState.PENDING_RCH.value
    else:                              # > ₹2Cr
        return LoanState.PENDING_CC.value
