"""Supabase client provider.

Thin factory around the Supabase Python client. Persistence and storage access
is centralised here so the rest of the codebase depends on a single, cached
client instance rather than constructing connections ad hoc.
"""

from functools import lru_cache

from supabase import Client, create_client

from app.config.config import Settings
from app.core.exceptions import ConfigurationError

SupabaseClient = Client


@lru_cache
def get_supabase_client(settings: Settings) -> SupabaseClient:
    """Return a cached Supabase client built from application settings."""

    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise ConfigurationError("Supabase URL and service role key must be configured")

    return create_client(settings.supabase_url, settings.supabase_service_role_key)
