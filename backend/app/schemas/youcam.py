"""Shared YouCam transport schemas.

Models that describe the shape of the YouCam asynchronous task workflow — the
file-upload handshake and the generic task envelope — independent of any single
capability (skin analysis or try-on).
"""

from enum import Enum

from pydantic import Field

from app.schemas.common import APIModel


class TaskState(str, Enum):
    """Terminal and non-terminal states a YouCam task may report."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


# States that are considered a successful terminal outcome.
SUCCESS_STATES: frozenset[str] = frozenset({"success", "succeed", "completed", "done"})
# States that are considered a failed terminal outcome.
ERROR_STATES: frozenset[str] = frozenset({"error", "failed", "fail", "rejected"})


class FileUploadTarget(APIModel):
    """A presigned upload destination returned by the File API.

    The File API does not accept the binary itself; it returns a ``file_id`` and
    the presigned ``url`` (plus any required ``headers``) that the client must
    then ``PUT`` the image bytes to.
    """

    file_id: str
    url: str
    method: str = "PUT"
    headers: dict[str, str] = Field(default_factory=dict)


class TaskResponse(APIModel):
    """Generic envelope describing the current state of a YouCam task."""

    task_id: str
    status: TaskState
    error: str | None = None
    raw: dict[str, object] = Field(default_factory=dict)
