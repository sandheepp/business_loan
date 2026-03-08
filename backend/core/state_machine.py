"""Loan lifecycle state machine.

Defines valid states and transitions for a loan application.
The Orchestrator uses this to manage the loan pipeline.
"""
from enum import Enum


class LoanState(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    COMPLIANCE_CHECK = "compliance_check"
    DOCUMENT_REVIEW = "document_review"
    UNDERWRITING = "underwriting"
    PRICING = "pricing"
    OFFICER_REVIEW = "officer_review"
    APPROVED = "approved"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"


# Valid transitions: current_state -> [allowed_next_states]
TRANSITIONS = {
    LoanState.DRAFT: [LoanState.SUBMITTED, LoanState.WITHDRAWN],
    LoanState.SUBMITTED: [LoanState.COMPLIANCE_CHECK, LoanState.WITHDRAWN],
    LoanState.COMPLIANCE_CHECK: [LoanState.DOCUMENT_REVIEW, LoanState.DECLINED],
    LoanState.DOCUMENT_REVIEW: [LoanState.UNDERWRITING, LoanState.COMPLIANCE_CHECK],
    LoanState.UNDERWRITING: [LoanState.PRICING, LoanState.DECLINED],
    LoanState.PRICING: [LoanState.OFFICER_REVIEW],
    LoanState.OFFICER_REVIEW: [LoanState.APPROVED, LoanState.DECLINED, LoanState.UNDERWRITING],
    LoanState.APPROVED: [],  # terminal
    LoanState.DECLINED: [],  # terminal
    LoanState.WITHDRAWN: [],  # terminal
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
