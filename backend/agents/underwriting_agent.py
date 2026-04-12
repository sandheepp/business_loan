"""Underwriting Agent — India MSME Financial Analysis, DSCR, LTV, Risk Scoring.

Recommended models:
  - Financial calculations: DETERMINISTIC (never LLM)
  - CAM narrative / memo: claude-sonnet-4-6
"""
import random
from backend.agents.base_agent import BaseAgent
from backend.core.llm_gateway import llm_complete
from backend.database import SessionLocal, LoanApplication
from backend.config import settings


# ── Deterministic Financial Engine ───────────────────────────

def calculate_dscr(
    avg_monthly_cashflow: float,
    existing_emi: float,
    proposed_emi: float,
) -> float:
    """DSCR = Avg Monthly Cash Flow / (Existing EMI + Proposed EMI).

    RBI MSME guideline: DSCR >= 1.25 for secured loans.
    """
    total_emi = existing_emi + proposed_emi
    if total_emi <= 0:
        return 0.0
    return round(avg_monthly_cashflow / total_emi, 2)


def calculate_debt_equity_ratio(total_liabilities: float, total_assets: float) -> float:
    """D/E = Total Liabilities / (Total Assets - Total Liabilities)."""
    equity = total_assets - total_liabilities
    if equity <= 0:
        return 99.0  # High leverage
    return round(total_liabilities / equity, 2)


def calculate_ltv(loan_amount: float, collateral_value: float) -> float:
    """LTV = Loan Amount / Collateral Market Value × 100."""
    if collateral_value <= 0:
        return 0.0
    return round((loan_amount / collateral_value) * 100, 1)


def calculate_emi(principal: float, annual_rate_pct: float, tenure_months: int) -> float:
    """EMI = P × r × (1+r)^n / ((1+r)^n - 1)."""
    if annual_rate_pct <= 0 or tenure_months <= 0:
        return 0.0
    r = annual_rate_pct / 100 / 12
    emi = principal * r * ((1 + r) ** tenure_months) / (((1 + r) ** tenure_months) - 1)
    return round(emi, 2)


def determine_risk_rating(dscr: float, ltv: float, cibil: int, years: int) -> tuple[str, float]:
    """Score and rate the credit risk.

    Returns (rating, risk_score_0_to_100).
    Higher score = better creditworthiness.
    """
    score = 0

    # DSCR (30 pts)
    if dscr >= 2.0:
        score += 30
    elif dscr >= 1.5:
        score += 24
    elif dscr >= 1.25:
        score += 18
    elif dscr >= 1.0:
        score += 10
    else:
        score += 0

    # LTV (25 pts) — lower LTV is better
    if ltv <= 40:
        score += 25
    elif ltv <= 50:
        score += 20
    elif ltv <= 60:
        score += 15
    elif ltv <= 70:
        score += 8
    else:
        score += 0

    # CIBIL score (30 pts)
    if cibil >= 800:
        score += 30
    elif cibil >= 750:
        score += 25
    elif cibil >= 700:
        score += 20
    elif cibil >= 650:
        score += 12
    else:
        score += 0

    # Business vintage (15 pts)
    if years >= 10:
        score += 15
    elif years >= 5:
        score += 12
    elif years >= 3:
        score += 8
    elif years >= 1:
        score += 4
    else:
        score += 0

    # Determine rating bucket
    if score >= 80:
        rating = "A+"
    elif score >= 70:
        rating = "A"
    elif score >= 60:
        rating = "B+"
    elif score >= 50:
        rating = "B"
    elif score >= 35:
        rating = "C"
    else:
        rating = "D"

    return rating, float(score)


class UnderwritingAgent(BaseAgent):
    agent_name = "underwriting"

    async def process(self, application_id: str, **kwargs) -> dict:
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}

            self.audit(application_id, "underwriting_started")

            loan_amount = app.loan_amount or 5_000_000  # ₹50L default
            annual_rate = 12.5  # Standard MSME secured rate %
            tenure_months = app.loan_tenure_months or 60

            # Simulate financial data (production: extracted from documents)
            annual_revenue = app.business_annual_revenue or random.randint(3_000_000, 15_000_000)
            net_profit_pct = random.uniform(8, 18)  # 8–18% net margin
            net_profit = annual_revenue * net_profit_pct / 100
            avg_monthly_cashflow = (annual_revenue * 0.12) / 12  # ~12% cashflow margin

            total_assets = random.uniform(loan_amount * 2, loan_amount * 4)
            total_liabilities = random.uniform(loan_amount * 0.5, loan_amount * 1.5)
            existing_emi = kwargs.get("existing_emi", random.uniform(20_000, 80_000))
            proposed_emi = calculate_emi(loan_amount, annual_rate, tenure_months)

            # Revenue growth (simulated)
            prev_revenue = annual_revenue * random.uniform(0.8, 1.1)
            revenue_growth_pct = ((annual_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
            operating_margin_pct = random.uniform(10, 22)

            # ── Core Financial Calculations (DETERMINISTIC) ───
            dscr = calculate_dscr(avg_monthly_cashflow, existing_emi, proposed_emi)
            debt_equity = calculate_debt_equity_ratio(total_liabilities, total_assets)

            collateral_value = app.collateral_market_value or (
                app.collateral_estimated_value or loan_amount * 2
            )
            ltv = calculate_ltv(loan_amount, collateral_value)

            cibil = app.cibil_score or app.credit_score or 720
            years = app.business_years_in_operation or 3
            risk_rating, risk_score = determine_risk_rating(dscr, ltv, cibil, years)

            # ── Generate CAM Draft (LLM) ──────────────────────
            cam_draft = await llm_complete(
                system=(
                    "You are a senior credit analyst at an Indian NBFC specializing in MSME secured loans. "
                    "Write a professional Credit Appraisal Memorandum (CAM) in a structured format with sections: "
                    "1. Borrower Profile, 2. Business Overview, 3. Financial Analysis, "
                    "4. Collateral Assessment, 5. Credit Risk Assessment, 6. Recommendation. "
                    "Use Indian financial terminology. Format numbers in Indian system (Lakhs, Crores)."
                ),
                prompt=(
                    f"Application ID: {application_id}\n"
                    f"Business: {app.business_name}, {app.business_constitution}\n"
                    f"Industry: {app.industry_type or 'Manufacturing'}, "
                    f"GST: {app.business_gst or 'N/A'}\n"
                    f"Promoter: {app.applicant_name}, PAN: {app.promoter_pan or 'N/A'}\n"
                    f"City: {app.city or 'N/A'}, Years in operation: {years}\n\n"
                    f"Loan requested: ₹{loan_amount/100000:.1f} Lakhs, "
                    f"Tenure: {tenure_months} months, Purpose: {app.loan_purpose or 'Business Expansion'}\n"
                    f"Proposed Rate: {annual_rate}% p.a., EMI: ₹{proposed_emi:,.0f}/month\n\n"
                    f"Financial Metrics:\n"
                    f"  Annual Revenue: ₹{annual_revenue/100000:.1f} Lakhs\n"
                    f"  Net Profit: ₹{net_profit/100000:.1f} Lakhs ({net_profit_pct:.1f}% margin)\n"
                    f"  Avg Monthly Cashflow: ₹{avg_monthly_cashflow:,.0f}\n"
                    f"  DSCR: {dscr} ({'above' if dscr >= 1.25 else 'below'} RBI min 1.25)\n"
                    f"  Debt/Equity: {debt_equity}\n"
                    f"  Revenue Growth: {revenue_growth_pct:.1f}%\n"
                    f"  Operating Margin: {operating_margin_pct:.1f}%\n\n"
                    f"Collateral:\n"
                    f"  Type: {app.collateral_type or 'Residential Property'}\n"
                    f"  Estimated Value: ₹{collateral_value/100000:.1f} Lakhs\n"
                    f"  LTV: {ltv}% (limit 60%)\n\n"
                    f"CIBIL Score: {cibil}\n"
                    f"Risk Rating: {risk_rating} (Score: {risk_score}/100)\n"
                    f"Write the complete CAM."
                ),
            )

            # ── Save Results ──────────────────────────────────
            app.avg_monthly_cashflow = avg_monthly_cashflow
            app.annual_revenue_reported = annual_revenue
            app.net_profit = net_profit
            app.total_assets = total_assets
            app.total_liabilities = total_liabilities
            app.existing_emi_obligations = existing_emi
            app.dscr = dscr
            app.debt_equity_ratio = debt_equity
            app.revenue_growth_pct = round(revenue_growth_pct, 1)
            app.operating_margin_pct = round(operating_margin_pct, 1)
            app.collateral_market_value = collateral_value
            app.ltv_ratio = ltv
            app.risk_score = risk_score
            app.risk_rating = risk_rating
            app.underwriting_memo = cam_draft
            app.cam_draft = cam_draft
            app.recommended_loan_amount = loan_amount if dscr >= 1.25 and ltv <= 60 else loan_amount * 0.8
            app.recommended_interest_rate = annual_rate
            db.commit()

            result = {
                "dscr": dscr,
                "ltv": ltv,
                "debt_equity": debt_equity,
                "revenue_growth_pct": round(revenue_growth_pct, 1),
                "operating_margin_pct": round(operating_margin_pct, 1),
                "risk_rating": risk_rating,
                "risk_score": risk_score,
                "cibil_score": cibil,
                "proposed_emi": proposed_emi,
                "recommended_amount": app.recommended_loan_amount,
                "cam_draft": cam_draft,
            }

            self.audit(application_id, "underwriting_completed", {
                "dscr": dscr,
                "ltv": ltv,
                "risk_rating": risk_rating,
                "risk_score": risk_score,
            })
            return result
        finally:
            db.close()


underwriting_agent = UnderwritingAgent()
