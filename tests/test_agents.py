"""Unit tests for CASA agents."""
import pytest
import asyncio
from backend.agents.underwriting_agent import calculate_dscr, score_credit_policy
from backend.agents.compliance_agent import check_sba_eligibility, calculate_spss
from backend.agents.pricing_agent import calculate_rate, calculate_monthly_payment, risk_tier
from backend.core.state_machine import can_transition, get_next_states, LoanState


# ── Underwriting Tests ───────────────────────────────────────

def test_dscr_calculation():
    """Test DSCR with the California Dental LLC scenario."""
    result = calculate_dscr(
        net_income=263819,
        officer_salary=85000,
        depreciation=14177,
        interest_expense=12000,
        non_recurring=0,
        monthly_personal_debt=3000,
        existing_annual_debt_service=42000,
        new_annual_debt_service=63000,
    )
    assert result["adjusted_income"] == 374996
    assert result["annual_personal_debt"] == 36000
    assert result["total_debt_service"] == 105000
    # (374996 - 36000) / 105000 = 3.228...
    assert 3.2 <= result["dscr"] <= 3.3


def test_dscr_zero_debt():
    """DSCR should be 0 if total debt service is 0."""
    result = calculate_dscr(100000, 0, 0, 0, 0, 0, 0, 0)
    assert result["dscr"] == 0


def test_credit_policy_scoring():
    """Test scoring for a strong deal."""
    result = score_credit_policy(
        dscr=3.23, credit_score=780,
        years_in_business=8, revenue=917000, employees=12,
    )
    assert result["total_score"] >= 90
    assert result["max_score"] == 100


def test_credit_policy_weak_deal():
    """Test scoring for a weak deal."""
    result = score_credit_policy(
        dscr=1.0, credit_score=620,
        years_in_business=1, revenue=50000, employees=2,
    )
    assert result["total_score"] < 50


# ── Compliance Tests ─────────────────────────────────────────

def test_sba_eligibility_pass():
    eligible, flags = check_sba_eligibility("621210", 300000, "LLC")
    assert eligible is True
    assert len(flags) == 0


def test_sba_eligibility_over_limit():
    eligible, flags = check_sba_eligibility("621210", 6000000, "LLC")
    assert eligible is False
    assert any("$5M" in f for f in flags)


def test_sba_ineligible_industry():
    eligible, flags = check_sba_eligibility("524110", 300000, "LLC")
    assert eligible is False


def test_spss_calculation():
    score = calculate_spss(credit_score=780, years=8, revenue=917000)
    assert score >= 165  # Should pass SBA minimum


def test_spss_low_credit():
    score = calculate_spss(credit_score=580, years=0, revenue=0)
    assert score < 165  # Should fail SBA minimum


# ── Pricing Tests ────────────────────────────────────────────

def test_rate_excellent():
    rate = calculate_rate(95)
    assert rate == 10.0  # 7.75 + 2.25


def test_rate_poor():
    rate = calculate_rate(30)
    assert rate == 13.75  # 7.75 + 6.00


def test_monthly_payment():
    payment = calculate_monthly_payment(300000, 10.5, 120)
    assert 4000 <= payment <= 4200  # ~$4,053


def test_risk_tier():
    assert risk_tier(95) == "excellent"
    assert risk_tier(80) == "good"
    assert risk_tier(65) == "fair"
    assert risk_tier(50) == "marginal"
    assert risk_tier(30) == "poor"


# ── State Machine Tests ──────────────────────────────────────

def test_valid_transition():
    assert can_transition("draft", "submitted") is True
    assert can_transition("submitted", "compliance_check") is True


def test_invalid_transition():
    assert can_transition("draft", "approved") is False
    assert can_transition("approved", "draft") is False


def test_terminal_states():
    assert get_next_states("approved") == []
    assert get_next_states("declined") == []


def test_next_states():
    states = get_next_states("officer_review")
    assert "approved" in states
    assert "declined" in states


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
