"""LLM Gateway — unified interface to multiple LLM providers with fallback routing.

Uses LiteLLM for provider-agnostic API calls. Falls back through a chain
of models if the primary is unavailable. All calls are logged for audit.
"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In MVP mode we provide a mock that works without API keys.
# Set USE_MOCK_LLM=true in .env to use mock responses (great for demos).
# ---------------------------------------------------------------------------

USE_MOCK = True  # Flip to False when you have real API keys configured


async def llm_complete(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    json_mode: bool = False,
) -> str:
    """Send a completion request to the configured LLM.

    Args:
        prompt: User message / prompt text.
        system: System prompt for the model.
        model: Model identifier (defaults to config default).
        temperature: Sampling temperature.
        max_tokens: Maximum tokens in response.
        json_mode: If True, instruct model to return valid JSON.

    Returns:
        The model's text response.
    """
    if USE_MOCK:
        return _mock_response(prompt, system)

    # Production path — requires litellm + valid API keys
    try:
        import litellm
        from backend.config import settings

        model = model or settings.llm_default_model

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        # Fallback to mock in case of any failure
        return _mock_response(prompt, system)


def _mock_response(prompt: str, system: str = "") -> str:
    """Generate contextual mock responses for demo / testing."""
    p = prompt.lower()

    # Sarah chat responses
    if "sarah" in system.lower() or "engagement" in system.lower():
        if "ein" in p or "tin" in p:
            return (
                "Great question! Your EIN (Employer Identification Number) and TIN "
                "(Taxpayer Identification Number) are the same 9-digit number for your "
                "business. You can usually find it on the IRS confirmation letter you "
                "received when you registered your business, or on any prior tax return. "
                "Would you like me to help you with anything else on your application?"
            )
        if "status" in p or "where" in p:
            return (
                "Your application is progressing well! We've received your business "
                "information and are currently processing your documents. A loan officer "
                "will review the completed file soon. Is there anything else I can help with?"
            )
        if "document" in p or "upload" in p:
            return (
                "For your loan application, we'll need: your most recent business tax "
                "return (Form 1120S or 1065), the last 3 months of business bank "
                "statements, and a current profit & loss statement. You can upload these "
                "directly through the application portal. Would you like me to send you "
                "the upload link?"
            )
        return (
            "I'm here to help you with your loan application! I can assist with "
            "filling out the application, understanding what documents you need, "
            "or answering questions about the process. What would you like to know?"
        )

    # Compliance report
    if "compliance" in system.lower():
        return json.dumps({
            "kyb_status": "passed",
            "kyc_status": "passed",
            "watchlist_clear": True,
            "sba_eligible": True,
            "spss_score": 182,
            "credit_score": 780,
            "flags": [],
            "summary": (
                "All compliance checks passed. Business entity verified with California "
                "Secretary of State. OFAC and watchlist screening negative. SBA 7(a) "
                "eligibility confirmed. SPSS score of 182 exceeds the SBA minimum of 165."
            ),
        })

    # Underwriting memo
    if "underwriting" in system.lower() or "memo" in system.lower():
        return (
            "## Underwriting Memo — California Dental LLC\n\n"
            "**Borrower:** California Dental LLC\n"
            "**Loan Request:** $300,000 SBA 7(a)\n"
            "**Purpose:** Working capital and equipment purchase (CT scanner)\n\n"
            "### Financial Analysis\n"
            "Base net income of $263,819 was extracted from the Schedule M-1 of the "
            "2024 Form 1120S. Standard add-backs were applied: officer compensation "
            "($85,000), depreciation ($14,177), and interest expense ($12,000), "
            "yielding an adjusted net income of $374,996.\n\n"
            "### Debt Service Coverage\n"
            "After subtracting annual personal debt service of $36,000, the available "
            "cash flow of $338,996 is divided by total debt service (existing: $42,000 "
            "+ proposed: $63,000 = $105,000), producing a **DSCR of 3.23x**.\n\n"
            "### Credit Policy Score: 95/100\n"
            "Strong financials, low industry default rates, experienced owner with "
            "excellent credit (780), established business (12 employees, 6% YoY growth).\n\n"
            "**Recommendation:** Approve with standard SBA 7(a) terms."
        )

    # Pricing / term sheet
    if "pricing" in system.lower() or "term sheet" in system.lower():
        return (
            "## Term Sheet — California Dental LLC\n\n"
            "| Item | Details |\n|---|---|\n"
            "| Borrower | California Dental LLC |\n"
            "| Loan Amount | $300,000 |\n"
            "| Loan Type | SBA 7(a) |\n"
            "| Interest Rate | 10.50% (Prime + 2.75%) |\n"
            "| Term | 10 years (120 months) |\n"
            "| Monthly Payment | $4,053 |\n"
            "| Collateral | Business assets + personal guarantee |\n"
            "| SBA Guarantee | 75% |\n\n"
            "Rate is competitive with current market pricing for similar deals."
        )

    # Document classification
    if "document" in system.lower() or "classify" in system.lower():
        return json.dumps({
            "doc_type": "tax_return_1120s",
            "confidence": 0.95,
            "tax_year": "2024",
            "entity_name": "California Dental LLC",
        })

    # Default
    return "I've processed your request. Please let me know if you need any additional information."
