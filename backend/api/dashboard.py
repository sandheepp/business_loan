"""Dashboard and analytics API endpoints — India MSME LOS."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db, LoanApplication, AuditEntry
from backend.models.schemas import PipelineStats, AuditEntryResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=PipelineStats)
def get_pipeline_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(LoanApplication.id)).scalar() or 0
    status_counts = dict(
        db.query(LoanApplication.status, func.count(LoanApplication.id))
        .group_by(LoanApplication.status)
        .all()
    )
    avg_comp = db.query(func.avg(LoanApplication.completion_pct)).scalar() or 0
    total_loan_value = db.query(func.sum(LoanApplication.loan_amount)).scalar() or 0

    # Aggregate KYC pending (all KYC states)
    kyc_pending = (
        status_counts.get("kyc_pending", 0)
        + status_counts.get("kyc_in_review", 0)
    )

    # Aggregate underwriting (stages 7-10)
    underwriting_count = (
        status_counts.get("financial_analysis", 0)
        + status_counts.get("collateral_assessment", 0)
        + status_counts.get("underwriting", 0)
        + status_counts.get("cam_draft", 0)
        + status_counts.get("cam_finalized", 0)
    )

    # Sanctioned = actively in approval/sanction pipeline
    sanctioned = (
        status_counts.get("pending_bcm", 0)
        + status_counts.get("pending_rch", 0)
        + status_counts.get("pending_cc", 0)
        + status_counts.get("sanctioned", 0)
        + status_counts.get("sanction_accepted", 0)
    )

    return PipelineStats(
        total_applications=total,
        lead_created=status_counts.get("lead_created", 0),
        application_draft=status_counts.get("application_draft", 0),
        kyc_pending=kyc_pending,
        document_collection=status_counts.get("document_collection", 0) + status_counts.get("document_review", 0),
        underwriting=underwriting_count,
        sanctioned=sanctioned,
        disbursed=status_counts.get("disbursed", 0),
        declined=status_counts.get("declined", 0),
        avg_completion=round(avg_comp, 1),
        total_loan_value=total_loan_value,
    )


@router.get("/audit/{app_id}", response_model=list[AuditEntryResponse])
def get_audit_log(app_id: str, db: Session = Depends(get_db)):
    entries = (
        db.query(AuditEntry)
        .filter_by(application_id=app_id)
        .order_by(AuditEntry.created_at.desc())
        .all()
    )
    return entries


@router.get("/audit", response_model=list[AuditEntryResponse])
def get_all_audit(limit: int = 100, db: Session = Depends(get_db)):
    return (
        db.query(AuditEntry)
        .order_by(AuditEntry.created_at.desc())
        .limit(limit)
        .all()
    )
