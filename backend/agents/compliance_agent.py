"""Compliance Agent — India KYC/KYB: PAN, Aadhaar, CKYC, CIBIL verification.

Recommended models:
  - Rule engine: Deterministic (no LLM)
  - Report narrative: claude-sonnet-4-6
  - Watchlist matching: Fuzzy string matching (no LLM)
"""
import random
import re
from backend.agents.base_agent import BaseAgent
from backend.core.llm_gateway import llm_complete
from backend.database import SessionLocal, LoanApplication

# PAN format: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)
PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
# Aadhaar: 12 digits
AADHAAR_REGEX = re.compile(r"^\d{12}$")
# GST: 15-character GSTIN
GST_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

CIBIL_MIN = 650


def validate_pan(pan: str) -> tuple[bool, str]:
    """Validate PAN card format."""
    if not pan:
        return False, "PAN not provided"
    pan = pan.strip().upper()
    if not PAN_REGEX.match(pan):
        return False, f"Invalid PAN format: {pan}"
    return True, "PAN format valid"


def validate_aadhaar(aadhaar: str) -> tuple[bool, str]:
    """Validate Aadhaar number format (simulated — real uses UIDAI OTP)."""
    if not aadhaar:
        return False, "Aadhaar not provided"
    aadhaar = aadhaar.strip().replace(" ", "")
    if not AADHAAR_REGEX.match(aadhaar):
        return False, "Invalid Aadhaar format (must be 12 digits)"
    return True, "Aadhaar format valid"


def validate_gst(gst: str) -> tuple[bool, str]:
    """Validate GSTIN format."""
    if not gst:
        return False, "GST number not provided"
    gst = gst.strip().upper()
    if not GST_REGEX.match(gst):
        return False, f"Invalid GSTIN format: {gst}"
    return True, "GSTIN format valid"


def simulate_cibil_score(pan: str, years: int, revenue: float) -> int:
    """Simulate CIBIL score fetch. Production: call CIBIL / Experian API."""
    base = 680
    base += min(60, years * 8)
    if revenue > 5_000_000:    # ₹50L+
        base += 30
    elif revenue > 1_000_000:  # ₹10L+
        base += 15
    # Add noise
    base += random.randint(-30, 40)
    return max(300, min(900, base))


def simulate_ckyc(pan: str) -> tuple[str, str]:
    """Simulate CKYC registry fetch. Returns (ckyc_number, status)."""
    if pan:
        ckyc_num = f"CKYC{random.randint(10000000, 99999999)}"
        return ckyc_num, "found"
    return "", "not_found"


def screen_watchlist(name: str, pan: str) -> tuple[bool, list[str]]:
    """Screen against RBI defaulter list, OFAC, UN sanctions (simulated)."""
    # Production: fuzzy match against RBI wilful defaulters, OFAC SDN
    return True, []


def check_msme_eligibility(constitution: str, annual_revenue: float, loan_amount: float) -> tuple[bool, list[str]]:
    """Check MSME eligibility per RBI/MSMED Act guidelines."""
    flags = []
    eligible = True

    if annual_revenue > 250_000_000:  # ₹25 Cr — exceeds MSME classification
        flags.append(f"Turnover ₹{annual_revenue:,.0f} exceeds MSME limit of ₹25 Cr")
        eligible = False

    if loan_amount > 100_000_000:     # ₹10 Cr
        flags.append(f"Loan ₹{loan_amount:,.0f} exceeds maximum limit of ₹10 Cr")
        eligible = False

    if constitution and constitution.lower() not in [
        "proprietorship", "partnership", "llp", "pvt ltd", "private limited", "one person company"
    ]:
        flags.append(f"Business constitution '{constitution}' may not qualify as MSME")

    return eligible, flags


class ComplianceAgent(BaseAgent):
    agent_name = "kyc"

    async def process(self, application_id: str, **kwargs) -> dict:
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}

            self.audit(application_id, "kyc_check_started")
            flags = []

            # ── PAN Validation ────────────────────────────────
            pan_valid, pan_msg = validate_pan(app.promoter_pan or "")
            pan_status = "verified" if pan_valid else "failed"
            if not pan_valid:
                flags.append(f"PAN: {pan_msg}")

            # ── Aadhaar Validation ────────────────────────────
            aadhaar_valid, aadhaar_msg = validate_aadhaar(app.promoter_aadhaar or "")
            aadhaar_status = "verified" if aadhaar_valid else "failed"
            if not aadhaar_valid:
                flags.append(f"Aadhaar: {aadhaar_msg}")

            # ── GST Validation ────────────────────────────────
            gst_valid, gst_msg = validate_gst(app.business_gst or "")
            if not gst_valid:
                flags.append(f"GST: {gst_msg}")

            # ── CKYC Fetch ────────────────────────────────────
            ckyc_number, ckyc_status = simulate_ckyc(app.promoter_pan or "")

            # ── CIBIL Score ───────────────────────────────────
            cibil_score = simulate_cibil_score(
                app.promoter_pan or "",
                app.business_years_in_operation or 0,
                app.business_annual_revenue or 0,
            )
            if cibil_score < CIBIL_MIN:
                flags.append(f"CIBIL score {cibil_score} below minimum {CIBIL_MIN}")

            # ── Watchlist Screening ───────────────────────────
            watchlist_clear, wl_flags = screen_watchlist(
                app.applicant_name or "", app.promoter_pan or ""
            )
            flags.extend(wl_flags)

            # ── MSME Eligibility ──────────────────────────────
            msme_eligible, msme_flags = check_msme_eligibility(
                app.business_constitution or "",
                app.business_annual_revenue or 0,
                app.loan_amount or 0,
            )
            flags.extend(msme_flags)

            # ── AI Summary ────────────────────────────────────
            summary = await llm_complete(
                system=(
                    "You are a compliance officer at an Indian NBFC reviewing an MSME secured loan application. "
                    "Write a concise 2-3 sentence compliance summary covering KYC status, credit profile, "
                    "and any flags. Use professional language."
                ),
                prompt=(
                    f"Business: {app.business_name}, Constitution: {app.business_constitution}, "
                    f"GST: {'valid' if gst_valid else 'invalid'}, "
                    f"PAN: {pan_status}, Aadhaar: {aadhaar_status}, "
                    f"CKYC: {ckyc_status}, CIBIL: {cibil_score}, "
                    f"MSME eligible: {msme_eligible}, Watchlist clear: {watchlist_clear}, "
                    f"Flags: {flags or 'None'}"
                ),
            )

            report = {
                "pan_status": pan_status,
                "aadhaar_status": aadhaar_status,
                "gst_valid": gst_valid,
                "ckyc_number": ckyc_number,
                "ckyc_status": ckyc_status,
                "cibil_score": cibil_score,
                "watchlist_clear": watchlist_clear,
                "msme_eligible": msme_eligible,
                "flags": flags,
                "summary": summary,
            }

            # Update application
            from datetime import datetime, timezone
            app.kyc_pan_status = pan_status
            app.kyc_aadhaar_status = aadhaar_status
            app.kyc_ckyc_number = ckyc_number
            app.kyc_ckyc_status = ckyc_status
            app.kyc_flags = flags
            app.cibil_score = cibil_score
            app.credit_score = cibil_score
            app.compliance_report = report
            if not flags or all("CIBIL" not in f for f in flags if "PAN" not in f and "Aadhaar" not in f):
                app.kyc_verified_at = datetime.now(timezone.utc)
            db.commit()

            self.audit(application_id, "kyc_check_completed", {
                "pan": pan_status,
                "aadhaar": aadhaar_status,
                "cibil": cibil_score,
                "flags_count": len(flags),
            })
            return report
        finally:
            db.close()


compliance_agent = ComplianceAgent()
