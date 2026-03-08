"""Dashboard and analytics API endpoints."""
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
    churned = db.query(func.count(LoanApplication.id)).filter(
        LoanApplication.churn_notified >= 1
    ).scalar() or 0

    return PipelineStats(
        total_applications=total,
        draft=status_counts.get("draft", 0),
        submitted=status_counts.get("submitted", 0),
        in_review=status_counts.get("officer_review", 0),
        approved=status_counts.get("approved", 0),
        declined=status_counts.get("declined", 0),
        avg_completion=round(avg_comp, 1),
        churned_count=churned,
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
    return db.query(AuditEntry).order_by(AuditEntry.created_at.desc()).limit(limit).all()
