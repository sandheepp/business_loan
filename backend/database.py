"""Database models and session management."""
import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def now():
    return datetime.datetime.now(datetime.timezone.utc)


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(String, primary_key=True)
    status = Column(String, default="draft")  # draft, submitted, in_review, approved, declined
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    # Step 1: Contact
    applicant_name = Column(String, default="")
    applicant_email = Column(String, default="")
    applicant_phone = Column(String, default="")

    # Step 2: Loan Request
    loan_amount = Column(Float, default=0)
    loan_purpose = Column(String, default="")
    loan_product = Column(String, default="")  # sba_7a, sba_504, conventional, etc.

    # Step 3: Business Info
    business_name = Column(String, default="")
    business_ein = Column(String, default="")
    business_address = Column(String, default="")
    business_entity_type = Column(String, default="")
    business_naics = Column(String, default="")
    business_state = Column(String, default="")
    business_employees = Column(Integer, default=0)
    business_annual_revenue = Column(Float, default=0)
    business_years_in_operation = Column(Integer, default=0)

    # Step 4: Ownership
    owners_json = Column(JSON, default=list)  # [{name, ownership_pct, ssn, dob}]

    # Step 5: Documents (tracked as metadata)
    documents_json = Column(JSON, default=list)  # [{filename, doc_type, uploaded_at}]

    # Agent outputs
    compliance_report = Column(JSON, default=dict)
    underwriting_memo = Column(Text, default="")
    risk_score = Column(Float, default=0)
    dscr = Column(Float, default=0)
    credit_score = Column(Integer, default=0)
    spss_score = Column(Integer, default=0)
    pricing_data = Column(JSON, default=dict)

    # Tracking
    current_step = Column(Integer, default=1)
    completion_pct = Column(Float, default=0)
    last_activity = Column(DateTime, default=now)
    churn_notified = Column(Integer, default=0)  # 0=no, 1=yes


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, index=True)
    role = Column(String)  # user, assistant
    content = Column(Text)
    channel = Column(String, default="web")  # web, sms, email
    created_at = Column(DateTime, default=now)


class AuditEntry(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, index=True)
    agent = Column(String)  # sarah, compliance, underwriting, document, pricing, orchestrator
    action = Column(String)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=now)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
