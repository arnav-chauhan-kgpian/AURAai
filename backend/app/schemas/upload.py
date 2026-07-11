"""Schemas for asset uploads."""

from app.schemas.common import APIModel


class UploadResponse(APIModel):
    """Result of uploading an image to the YouCam File API."""

    file_id: str
    file_name: str
    content_type: str
    size_bytes: int
