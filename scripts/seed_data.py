"""CASA MVP — Seed sample data for demo."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from backend.core.database import db
from backend.models.schemas import (
    Application, ContactInfo, LoanRequest, BusinessInfo, OwnerInfo,
    LoanStatus, LoanProduct, ChatMessage,
)
from datetime import datetime, timedelta


def seed():
    """Create sample loan applications for demo."""

    # Application 1: California Dental (completed pipeline)
    app1 = Application(
        id="APP-DEMO0001",
        contact=ContactInfo(first_name="Shelley", last_name="Johnson", email="shel@gmail.com", phone="(619) 555-0101"),
        loan_request=LoanRequest(amount=300000, purpose="Hire 2 dentists and purchase CT scanner", product_type=LoanProduct.SBA_7A),
        business=BusinessInfo(
            legal_name="California Dental LLC", ein="82-1234567",
            address="4320 Cherokee Avenue", city="San Diego", state="CA", zip_code="92104",
            entity_type="llc", naics_code="621210",
            years_in_business=8, employee_count=12, annual_revenue=917000,
        ),
        owners=[OwnerInfo(name="Shelley Johnson", ownership_pct=100, ssn_last_four="4321", credit_score=800)],
        status=LoanStatus.REVIEW,
        completion_pct=100,
        current_step=5,
        created_at=datetime.utcnow() - timedelta(days=2),
    )
    db.create_application(app1)

    # Add Sarah chat history for app1
    messages = [
        ("user", "Hi, I started the application but I don't know my EIN"),
        ("sarah", "No problem! Your EIN is the same as your TIN — the 9-digit number you file your business taxes under. You can find it on the IRS confirmation letter from when you incorporated, or on any previously filed tax return."),
        ("user", "I found it on my tax return. Thanks!"),
        ("sarah", "Great! Just enter it in the EIN field and you're all set. Let me know if you need help with anything else."),
    ]
    for role, content in messages:
        db.add_chat_message(ChatMessage(application_id=app1.id, role=role, content=content))

    # Application 2: In progress
    app2 = Application(
        id="APP-DEMO0002",
        contact=ContactInfo(first_name="Marcus", last_name="Chen", email="marcus@techshop.com", phone="(415) 555-0202"),
        loan_request=LoanRequest(amount=150000, purpose="Inventory and working capital", product_type=LoanProduct.SBA_EXPRESS),
        business=BusinessInfo(
            legal_name="Bay Area Tech Shop Inc", ein="45-6789012",
            address="1200 Market Street", city="San Francisco", state="CA",
            entity_type="s-corp", naics_code="443142",
            years_in_business=3, employee_count=6, annual_revenue=420000,
        ),
        owners=[OwnerInfo(name="Marcus Chen", ownership_pct=80, ssn_last_four="9876", credit_score=720)],
        status=LoanStatus.UNDERWRITING,
        completion_pct=100,
        current_step=5,
        created_at=datetime.utcnow() - timedelta(days=1),
    )
    db.create_application(app2)

    # Application 3: Draft (churned)
    app3 = Application(
        id="APP-DEMO0003",
        contact=ContactInfo(first_name="Patricia", last_name="Williams", email="pwilliams@greenleaf.com"),
        loan_request=LoanRequest(amount=500000, purpose="Commercial real estate acquisition"),
        business=BusinessInfo(legal_name="Green Leaf Landscaping LLC", city="Austin", state="TX"),
        status=LoanStatus.DRAFT,
        completion_pct=35,
        current_step=3,
        created_at=datetime.utcnow() - timedelta(hours=6),
        updated_at=datetime.utcnow() - timedelta(hours=5),
    )
    db.create_application(app3)

    # Application 4: Recently submitted
    app4 = Application(
        id="APP-DEMO0004",
        contact=ContactInfo(first_name="James", last_name="Rivera", email="james@riverapainting.com", phone="(305) 555-0404"),
        loan_request=LoanRequest(amount=75000, purpose="Equipment purchase", product_type=LoanProduct.SBA_EXPRESS),
        business=BusinessInfo(
            legal_name="Rivera Painting Services", ein="33-5678901",
            address="800 Brickell Avenue", city="Miami", state="FL",
            entity_type="sole_proprietorship", naics_code="238320",
            years_in_business=5, employee_count=4, annual_revenue=280000,
        ),
        owners=[OwnerInfo(name="James Rivera", ownership_pct=100, ssn_last_four="5555", credit_score=695)],
        status=LoanStatus.COMPLIANCE_REVIEW,
        completion_pct=100,
        current_step=5,
        created_at=datetime.utcnow() - timedelta(hours=3),
    )
    db.create_application(app4)

    print(f"Seeded {len(db.applications)} demo applications:")
    for app_id, app in db.applications.items():
        print(f"  {app_id}: {app.business.legal_name or 'Unknown'} — {app.status.value} — ${app.loan_request.amount:,.0f}")


if __name__ == "__main__":
    seed()
    print("\nDone! Start the servers to see the demo data.")
