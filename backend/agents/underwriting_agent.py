"""Underwriting Agent — Financial analysis, DSCR, credit policy scoring.

Recommended models:
  - Tax return extraction: claude-sonnet-4-20250514 (vision)
  - Financial calculations: DETERMINISTIC (never LLM)
  - Underwriting memo: claude-sonnet-4-20250514
  - Deal matching: text-embedding-3-small
"""
from backend.agents.base_agent import BaseAgent
from backend.core.llm_gateway import llm_complete
from backend.database import SessionLocal, LoanApplication


# ── Deterministic Financial Engine ───────────────────────────

def calculate_dscr(
    net_income: float,
    officer_salary: float,
    depreciation: float,
    interest_expense: float,
    non_recurring: float,
    monthly_personal_debt: float,
    existing_annual_debt_service: float,
    new_annual_debt_service: float,
) -> dict:
    """Calculate DSCR using deterministic formula. NO LLM INVOLVED.

    Formula:
        adjusted = net_income + officer_salary + depreciation + interest + non_recurring
        dscr = (adjusted - annual_personal_debt) / (existing_debt + new_debt)
    """
    add_backs = {
        "officer_salary": officer_salary,
        "depreciation": depreciation,
        "interest_expense": interest_expense,
        "non_recurring": non_recurring,
    }
    adjusted_income = net_income + sum(add_backs.values())
    annual_personal_debt = monthly_personal_debt * 12
    total_debt_service = existing_annual_debt_service + new_annual_debt_service

    dscr = (adjusted_income - annual_personal_debt) / total_debt_service if total_debt_service > 0 else 0

    return {
        "net_income": net_income,
        "add_backs": add_backs,
        "adjusted_income": round(adjusted_income, 2),
        "annual_personal_debt": round(annual_personal_debt, 2),
        "existing_debt_service": round(existing_annual_debt_service, 2),
        "new_debt_service": round(new_annual_debt_service, 2),
        "total_debt_service": round(total_debt_service, 2),
        "dscr": round(dscr, 2),
    }


def score_credit_policy(
    dscr: float,
    credit_score: int,
    years_in_business: int,
    revenue: float,
    employees: int,
    industry_risk: str = "low",
) -> dict:
    """Weighted multi-factor credit policy scoring. Deterministic."""
    scores = {}

    # Financial strength (35%)
    if dscr >= 2.0:
        scores["financials"] = 35
    elif dscr >= 1.5:
        scores["financials"] = 28
    elif dscr >= 1.25:
        scores["financials"] = 20
    else:
        scores["financials"] = 10

    # Credit score (25%)
    if credit_score >= 750:
        scores["credit"] = 25
    elif credit_score >= 700:
        scores["credit"] = 20
    elif credit_score >= 650:
        scores["credit"] = 15
    else:
        scores["credit"] = 8

    # Business maturity (15%)
    if years_in_business >= 5:
        scores["maturity"] = 15
    elif years_in_business >= 3:
        scores["maturity"] = 12
    elif years_in_business >= 1:
        scores["maturity"] = 8
    else:
        scores["maturity"] = 4

    # Industry risk (15%)
    risk_scores = {"low": 15, "medium": 10, "high": 5}
    scores["industry"] = risk_scores.get(industry_risk, 10)

    # Employment & scale (10%)
    if employees >= 10:
        scores["scale"] = 10
    elif employees >= 5:
        scores["scale"] = 7
    else:
        scores["scale"] = 4

    total = sum(scores.values())
    return {"component_scores": scores, "total_score": total, "max_score": 100}


class UnderwritingAgent(BaseAgent):
    agent_name = "underwriting"

    async def process(self, application_id: str, **kwargs) -> dict:
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}

            self.audit(application_id, "underwriting_started")

            # In production, these values come from Document Agent extraction.
            # For MVP, use demo values matching the California Dental LLC scenario.
            net_income = kwargs.get("net_income", 263819)
            officer_salary = kwargs.get("officer_salary", 85000)
            depreciation = kwargs.get("depreciation", 14177)
            interest_expense = kwargs.get("interest_expense", 12000)
            non_recurring = kwargs.get("non_recurring", 0)
            monthly_personal_debt = kwargs.get("monthly_personal_debt", 3000)
            existing_annual_debt_service = kwargs.get("existing_debt_service", 42000)

            # Calculate new debt service from loan terms
            loan_amount = app.loan_amount or 300000
            rate = 0.105  # 10.5% — will come from Pricing Agent
            term_months = 120
            monthly_rate = rate / 12
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
            new_annual_debt_service = monthly_payment * 12

            # DSCR calculation — fully deterministic
            dscr_result = calculate_dscr(
                net_income, officer_salary, depreciation, interest_expense,
                non_recurring, monthly_personal_debt,
                existing_annual_debt_service, new_annual_debt_service,
            )

            # Credit policy scoring — fully deterministic
            policy_score = score_credit_policy(
                dscr=dscr_result["dscr"],
                credit_score=app.credit_score or 780,
                years_in_business=app.business_years_in_operation or 8,
                revenue=app.business_annual_revenue or 917000,
                employees=app.business_employees or 12,
            )

            # Generate narrative memo — this is where LLM is used
            memo = await llm_complete(
                system="You are an underwriting analyst. Write a professional underwriting memo.",
                prompt=(
                    f"Business: {app.business_name}\n"
                    f"Loan: ${loan_amount:,.0f} SBA 7(a)\n"
                    f"DSCR: {dscr_result['dscr']}\n"
                    f"Adjusted income: ${dscr_result['adjusted_income']:,.0f}\n"
                    f"Add-backs: {dscr_result['add_backs']}\n"
                    f"Policy score: {policy_score['total_score']}/100\n"
                    f"Credit score: {app.credit_score or 780}\n"
                    f"Employees: {app.business_employees or 12}\n"
                    f"Revenue: ${app.business_annual_revenue or 917000:,.0f}\n"
                    "Write the underwriting memo."
                ),
            )

            # Save results
            app.dscr = dscr_result["dscr"]
            app.risk_score = policy_score["total_score"]
            app.underwriting_memo = memo
            db.commit()

            result = {
                "dscr": dscr_result,
                "policy_score": policy_score,
                "memo": memo,
            }
            self.audit(application_id, "underwriting_completed", {
                "dscr": dscr_result["dscr"],
                "risk_score": policy_score["total_score"],
            })
            return result
        finally:
            db.close()


underwriting_agent = UnderwritingAgent()
