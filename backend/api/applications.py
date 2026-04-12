"""Loan application API endpoints — India MSME LOS."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db, LoanApplication
from backend.models.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from backend.core.audit_log import log_event

router = APIRouter(prefix="/api/applications", tags=["applications"])

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Chandigarh", "Puducherry",
]


def _calc_completion(app: LoanApplication) -> float:
    """Calculate application completion percentage across all stages."""
    fields = [
        # Stage 1 — Lead info
        bool(app.applicant_name),
        bool(app.applicant_email),
        bool(app.applicant_phone),
        bool(app.city),
        # Stage 2 — Promoter
        bool(app.promoter_pan),
        bool(app.promoter_aadhaar),
        bool(app.promoter_dob),
        # Stage 2 — Business
        bool(app.business_name),
        bool(app.business_constitution),
        bool(app.business_gst),
        bool(app.business_address),
        bool(app.industry_type),
        bool(app.business_years_in_operation),
        # Stage 2 — Loan
        bool(app.loan_amount),
        bool(app.loan_purpose),
        # Stage 2 — Collateral
        bool(app.collateral_type),
        bool(app.collateral_estimated_value),
        # Stage 4 — Documents
        bool(app.documents_json),
    ]
    return round(sum(fields) / len(fields) * 100, 1)


@router.post("/", response_model=ApplicationResponse)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    app_id = f"MSME{str(uuid.uuid4())[:6].upper()}"
    app = LoanApplication(
        id=app_id,
        applicant_name=data.applicant_name,
        applicant_email=data.applicant_email,
        applicant_phone=data.applicant_phone,
        city=data.city,
        business_name=data.business_name,
        loan_amount=data.loan_amount,
        lead_source=data.lead_source,
        status="lead_created",
        current_step=1,
    )
    app.completion_pct = _calc_completion(app)
    db.add(app)
    db.commit()
    db.refresh(app)
    log_event(app_id, "orchestrator", "lead_created", {
        "email": data.applicant_email,
        "city": data.city,
        "source": data.lead_source,
    })
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
        if hasattr(app, key):
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


@router.post("/{app_id}/approve")
async def approve_application(app_id: str, data: dict, db: Session = Depends(get_db)):
    """Approve a loan application — sets sanctioned state."""
    from backend.agents.orchestrator import orchestrator
    result = await orchestrator.approve(app_id, data)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/{app_id}/decline")
async def decline_application(app_id: str, data: dict, db: Session = Depends(get_db)):
    """Decline a loan application."""
    from backend.agents.orchestrator import orchestrator
    result = await orchestrator.decline(app_id, data)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/{app_id}/disburse")
async def disburse_loan(app_id: str, data: dict, db: Session = Depends(get_db)):
    """Trigger disbursement after all pre-conditions are met."""
    from backend.agents.orchestrator import orchestrator
    result = await orchestrator.disburse(app_id, data)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.get("/meta/indian-states")
def get_indian_states():
    return INDIAN_STATES
