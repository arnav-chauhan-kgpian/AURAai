"""Object storage abstraction.

Wraps Supabase Storage behind a narrow interface so the persistence backend can
evolve without touching calling code. Handles bucket-scoped object writes and
signed URL generation.
"""

from app.config.config import Settings
from app.db.supabase import SupabaseClient


class ObjectStore:
    """Bucket-scoped object storage backed by Supabase Storage."""

    def __init__(self, settings: Settings, supabase: SupabaseClient) -> None:
        self._settings = settings
        self._supabase = supabase
        self._bucket = settings.supabase_storage_bucket

    async def put(self, key: str, content: bytes, content_type: str) -> str:
        """Persist an object and return its storage key."""

        raise NotImplementedError

    async def signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Return a time-limited signed URL for the given object key."""

        raise NotImplementedError
