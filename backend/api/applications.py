"""Loan application API endpoints."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db, LoanApplication
from backend.models.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from backend.core.audit_log import log_event

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _calc_completion(app: LoanApplication) -> float:
    fields = [
        bool(app.applicant_name), bool(app.applicant_email), bool(app.applicant_phone),
        bool(app.loan_amount), bool(app.loan_purpose),
        bool(app.business_name), bool(app.business_ein), bool(app.business_address),
        bool(app.owners_json),
        bool(app.documents_json),
    ]
    return round(sum(fields) / len(fields) * 100, 1)


@router.post("/", response_model=ApplicationResponse)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    app_id = str(uuid.uuid4())[:8]
    app = LoanApplication(
        id=app_id,
        applicant_name=data.applicant_name,
        applicant_email=data.applicant_email,
        applicant_phone=data.applicant_phone,
        status="draft",
        current_step=1,
    )
    app.completion_pct = _calc_completion(app)
    db.add(app)
    db.commit()
    db.refresh(app)
    log_event(app_id, "orchestrator", "application_created", {"email": data.applicant_email})
    return app


@router.get("/", response_model=list[ApplicationResponse])
def list_applications(status: str = None, db: Session = Depends(get_db)):
    q = db.query(LoanApplication)
    if status:
        q = q.filter(LoanApplication.status == status)
    return q.order_by(LoanApplication.updated_at.desc()).all()


@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application(app_id: str, db: Session = Depends(get_db)):
    app = db.query(LoanApplication).filter_by(id=app_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    return app


@router.patch("/{app_id}", response_model=ApplicationResponse)
def update_application(app_id: str, data: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(LoanApplication).filter_by(id=app_id).first()
    if not app:
        raise HTTPException(404, "Application not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(app, key, value)

    app.completion_pct = _calc_completion(app)
    app.last_activity = datetime.now(timezone.utc)
    app.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(app)
    log_event(app_id, "orchestrator", "application_updated", {"fields": list(update_data.keys())})
    return app


@router.post("/{app_id}/submit")
async def submit_application(app_id: str, db: Session = Depends(get_db)):
    from backend.agents.orchestrator import orchestrator
    result = await orchestrator.submit_application(app_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/{app_id}/run-pipeline")
async def run_pipeline(app_id: str):
    from backend.agents.orchestrator import orchestrator
    result = await orchestrator.run_pipeline(app_id)
    return result
