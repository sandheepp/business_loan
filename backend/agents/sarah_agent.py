"""Sarah — Engagement Agent.

Handles all applicant communication, churn detection, and reactivation.

Recommended models:
  - Chat: claude-sonnet-4-20250514 (best conversational quality)
  - High-volume SMS: claude-haiku-4-5-20251001 (lower cost)
  - Fallback: gpt-4o-mini
"""
import json
from datetime import datetime, timezone, timedelta
from backend.agents.base_agent import BaseAgent
from backend.core.llm_gateway import llm_complete
from backend.database import SessionLocal, LoanApplication, ChatMessage
from backend.config import settings

SARAH_SYSTEM_PROMPT = """You are Sarah, a friendly and helpful AI assistant for {bank_name}.
You help small business owners complete their loan applications.

STRICT RULES:
1. You NEVER provide financial advice, interest rate predictions, or approval likelihood.
2. If asked about rates or approval odds, say: "A loan officer will be happy to discuss that with you once your application is reviewed."
3. You guide applicants through the application process, explain what documents are needed, and help with common questions.
4. You understand that TIN and EIN refer to the same 9-digit number.
5. You are warm, professional, and encouraging.
6. Keep responses concise — 2-3 sentences for simple questions, up to a short paragraph for complex ones.

APPLICANT CONTEXT:
- Name: {applicant_name}
- Business: {business_name}
- Loan: ${loan_amount:,.0f} {loan_product}
- Application step: {current_step}/5
- Completion: {completion_pct:.0f}%
- Missing: {missing_info}
"""


class SarahAgent(BaseAgent):
    """Customer-facing engagement agent."""

    agent_name = "sarah"

    async def process(self, application_id: str, **kwargs) -> dict:
        """Not used directly — Sarah works through chat and churn detection."""
        return {"status": "ok"}

    async def chat(self, application_id: str, user_message: str, channel: str = "web") -> str:
        """Process a user message and return Sarah's response."""
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return "I'm sorry, I couldn't find your application. Please start a new one."

            # Build context-aware system prompt
            missing = self._get_missing_info(app)
            system = SARAH_SYSTEM_PROMPT.format(
                bank_name=settings.bank_name,
                applicant_name=app.applicant_name or "there",
                business_name=app.business_name or "your business",
                loan_amount=app.loan_amount or 0,
                loan_product=app.loan_product or "loan",
                current_step=app.current_step,
                completion_pct=app.completion_pct,
                missing_info=", ".join(missing) if missing else "none — application looks complete!",
            )

            # Get recent conversation history for context
            recent = (
                db.query(ChatMessage)
                .filter_by(application_id=application_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(6)
                .all()
            )
            history = "\n".join(
                f"{'Applicant' if m.role == 'user' else 'Sarah'}: {m.content}"
                for m in reversed(recent)
            )

            prompt = f"Recent conversation:\n{history}\n\nApplicant: {user_message}\n\nSarah:"

            # Call LLM
            response = await llm_complete(prompt=prompt, system=system)

            # Save messages
            db.add(ChatMessage(
                application_id=application_id, role="user",
                content=user_message, channel=channel,
            ))
            db.add(ChatMessage(
                application_id=application_id, role="assistant",
                content=response, channel=channel,
            ))

            # Update last activity
            app.last_activity = datetime.now(timezone.utc)
            db.commit()

            self.audit(application_id, "chat_response", {
                "channel": channel,
                "user_message_length": len(user_message),
                "response_length": len(response),
            })

            return response

        finally:
            db.close()

    async def check_churn(self) -> list[dict]:
        """Scan for applications that may have churned and generate reactivation messages."""
        db = SessionLocal()
        try:
            threshold = datetime.now(timezone.utc) - timedelta(minutes=30)
            churned = (
                db.query(LoanApplication)
                .filter(
                    LoanApplication.status == "draft",
                    LoanApplication.last_activity < threshold,
                    LoanApplication.churn_notified == 0,
                    LoanApplication.applicant_email != "",
                )
                .all()
            )

            results = []
            for app in churned:
                missing = self._get_missing_info(app)
                msg = await self._generate_reactivation_message(app, missing)
                app.churn_notified = 1
                results.append({
                    "application_id": app.id,
                    "email": app.applicant_email,
                    "message": msg,
                })
                self.audit(app.id, "churn_reactivation_sent", {
                    "missing_fields": missing,
                    "message_preview": msg[:100],
                })

            db.commit()
            return results

        finally:
            db.close()

    async def _generate_reactivation_message(self, app, missing: list[str]) -> str:
        """Generate a personalized churn reactivation message."""
        system = (
            f"You are Sarah from {settings.bank_name}. Write a brief, warm SMS message "
            "to re-engage a loan applicant who left their application incomplete. "
            "Be helpful and specific about what they need to complete. Keep it under 160 characters if possible."
        )
        prompt = (
            f"Applicant: {app.applicant_name or 'there'}\n"
            f"Business: {app.business_name or 'their business'}\n"
            f"Stopped at step: {app.current_step}\n"
            f"Missing info: {', '.join(missing)}\n"
            "Write a re-engagement message:"
        )
        return await llm_complete(prompt=prompt, system=system)

    def _get_missing_info(self, app) -> list[str]:
        """Determine what information is still missing from the application."""
        missing = []
        if not app.applicant_name:
            missing.append("contact name")
        if not app.applicant_email:
            missing.append("email address")
        if not app.loan_amount:
            missing.append("loan amount")
        if not app.loan_purpose:
            missing.append("loan purpose")
        if not app.business_name:
            missing.append("business name")
        if not app.business_ein:
            missing.append("EIN/TIN")
        if not app.business_address:
            missing.append("business address")
        if not app.owners_json:
            missing.append("ownership information")
        if not app.documents_json:
            missing.append("financial documents")
        return missing


# Singleton
sarah = SarahAgent()
