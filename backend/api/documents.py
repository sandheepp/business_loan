"""Document upload API endpoints."""
from fastapi import APIRouter, UploadFile, File, Form

from backend.agents.document_agent import document_agent

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    application_id: str = Form(...),
    file: UploadFile = File(...),
):
    content = await file.read()
    result = await document_agent.process(
        application_id, filename=file.filename, content=content,
    )
    return result


@router.get("/completeness/{app_id}")
async def check_completeness(app_id: str):
    return await document_agent.check_completeness(app_id)
