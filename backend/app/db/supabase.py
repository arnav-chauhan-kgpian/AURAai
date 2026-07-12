"""Supabase client provider.

Thin factory around the Supabase Python client. Persistence and storage access
is centralised here so the rest of the codebase depends on a single, cached
client instance rather than constructing connections ad hoc.
"""

from app.config.config import Settings
from app.core.exceptions import ConfigurationError
from supabase import Client, create_client

SupabaseClient = Client

# Module-level singleton. Note: `Settings` is not hashable, so `@lru_cache`
# cannot be used here — it would raise TypeError on every call.
_client: Client | None = None


def get_supabase_client(settings: Settings) -> SupabaseClient:
    """Return a process-wide Supabase client built from application settings."""

    global _client
    if _client is not None:
        return _client

    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise ConfigurationError("Supabase URL and service role key must be configured")

    _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client
