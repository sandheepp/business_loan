"""Immutable audit logging for all agent actions.

Every agent action, decision, and data transformation is recorded
in an append-only audit log for regulatory compliance.
"""
import logging
from datetime import datetime, timezone
from backend.database import SessionLocal, AuditEntry

logger = logging.getLogger(__name__)


def log_event(
    application_id: str,
    agent: str,
    action: str,
    details: dict | None = None,
) -> None:
    """Append an immutable audit entry.

    Args:
        application_id: The loan application this event relates to.
        agent: Which agent performed the action (sarah, compliance, etc.).
        action: Short description of what happened.
        details: Arbitrary JSON-serializable data about the event.
    """
    db = SessionLocal()
    try:
        entry = AuditEntry(
            application_id=application_id,
            agent=agent,
            action=action,
            details=details or {},
            created_at=datetime.now(timezone.utc),
        )
        db.add(entry)
        db.commit()
        logger.info(f"[AUDIT] {agent} | {action} | app={application_id}")
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")
        db.rollback()
    finally:
        db.close()
