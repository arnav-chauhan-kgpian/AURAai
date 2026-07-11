"""Domain and infrastructure exception hierarchy.

A single, explicit exception tree lets the API layer translate failures into
consistent HTTP responses without leaking implementation details. Upstream
provider failures (YouCam) are modelled precisely so callers and the API layer
can react to specific conditions such as "no face detected" or "rate limited".
"""


class AuraError(Exception):
    """Base class for all application-specific errors."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.__doc__)
        self.message = message or (self.__doc__ or "")


class ConfigurationError(AuraError):
    """A required configuration value is missing or invalid."""

    status_code = 500
    error_code = "configuration_error"


class AuthenticationError(AuraError):
    """Authentication against the upstream provider failed."""

    status_code = 502
    error_code = "authentication_error"


class UpstreamServiceError(AuraError):
    """An upstream provider (YouCam, Gemini, Supabase) returned an error."""

    status_code = 502
    error_code = "upstream_error"


# --- YouCam provider errors -----------------------------------------------


class YouCamError(UpstreamServiceError):
    """Base class for YouCam (Perfect Corp) provider errors."""

    error_code = "youcam_error"


class InvalidImageError(YouCamError):
    """The supplied image was rejected (unsupported, corrupt or out of bounds)."""

    status_code = 422
    error_code = "invalid_image"


class NoFaceDetectedError(YouCamError):
    """No face was detected in the supplied image."""

    status_code = 422
    error_code = "no_face_detected"


class MultipleFacesError(YouCamError):
    """More than one face was detected when exactly one was required."""

    status_code = 422
    error_code = "multiple_faces_detected"


class RateLimitError(YouCamError):
    """The provider rate limit was exceeded (HTTP 429)."""

    status_code = 429
    error_code = "rate_limited"

    def __init__(self, message: str | None = None, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class ExpiredTaskError(YouCamError):
    """The referenced task has expired or no longer exists."""

    status_code = 410
    error_code = "task_expired"


class TaskFailedError(YouCamError):
    """The provider reported the task finished in an error state."""

    status_code = 502
    error_code = "task_failed"


class ServerError(YouCamError):
    """The provider returned a 5xx server error after exhausting retries."""

    status_code = 502
    error_code = "provider_server_error"


class PollingTimeoutError(YouCamError):
    """A task did not reach a terminal state within the polling timeout."""

    status_code = 504
    error_code = "polling_timeout"


# --- Local application errors ---------------------------------------------


class UploadError(AuraError):
    """An uploaded asset could not be validated or persisted."""

    status_code = 400
    error_code = "upload_error"


class AgentError(AuraError):
    """The AI agent failed to complete its plan."""

    status_code = 500
    error_code = "agent_error"


class ResourceNotFoundError(AuraError):
    """A requested resource does not exist."""

    status_code = 404
    error_code = "not_found"
