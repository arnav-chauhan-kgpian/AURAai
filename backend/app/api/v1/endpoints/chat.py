"""Conversational stylist agent endpoints.

The agent decides which capabilities to invoke — these handlers contain no
business logic; they marshal the request into the agent and stream/return its
result.
"""

import json

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from app.core.dependencies import AuraAgentDep
from app.schemas.agent import AgentImages
from app.schemas.chat import ChatResponse

router = APIRouter()


async def _build_images(
    face_image: UploadFile | None,
    garment_image: UploadFile | None,
    garment_category: str,
) -> AgentImages:
    return AgentImages(
        face_image=await face_image.read() if face_image else None,
        face_content_type=(face_image.content_type if face_image else "image/jpeg") or "image/jpeg",
        garment_image=await garment_image.read() if garment_image else None,
        garment_content_type=(garment_image.content_type if garment_image else "image/jpeg")
        or "image/jpeg",
        garment_category=garment_category,
    )


@router.post("", response_model=ChatResponse)
async def chat(
    agent: AuraAgentDep,
    session_id: str = Form(...),
    message: str = Form(...),
    face_image: UploadFile | None = File(default=None),
    garment_image: UploadFile | None = File(default=None),
    garment_category: str = Form(default="upper_body"),
) -> ChatResponse:
    """Run one turn of the autonomous stylist agent."""

    images = await _build_images(face_image, garment_image, garment_category)
    return await agent.run(session_id=session_id, message=message, images=images)


@router.post("/stream")
async def chat_stream(
    agent: AuraAgentDep,
    session_id: str = Form(...),
    message: str = Form(...),
    face_image: UploadFile | None = File(default=None),
    garment_image: UploadFile | None = File(default=None),
    garment_category: str = Form(default="upper_body"),
) -> StreamingResponse:
    """Run one turn, streaming intent, tool steps and reply tokens as SSE."""

    images = await _build_images(face_image, garment_image, garment_category)

    async def event_stream():
        async for event in agent.stream(session_id=session_id, message=message, images=images):
            yield f"data: {json.dumps(event.model_dump())}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
