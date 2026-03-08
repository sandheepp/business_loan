"""Sarah chat API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db, ChatMessage
from backend.models.schemas import ChatRequest, ChatResponse
from backend.agents.sarah_agent import sarah

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def send_message(data: ChatRequest):
    response = await sarah.chat(data.application_id, data.message, data.channel)
    return ChatResponse(
        role="assistant",
        content=response,
        created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )


@router.get("/{app_id}/history", response_model=list[ChatResponse])
def get_history(app_id: str, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .filter_by(application_id=app_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [ChatResponse(role=m.role, content=m.content, created_at=m.created_at) for m in messages]


@router.post("/check-churn")
async def check_churn():
    results = await sarah.check_churn()
    return {"churned_count": len(results), "reactivations": results}
