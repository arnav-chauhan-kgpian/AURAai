"""Cryptographic helpers for provider authentication.

YouCam (Perfect Corp) server-to-server authentication requires an ``id_token``:
the string ``client_id=<api_key>&timestamp=<epoch_ms>`` RSA-encrypted with the
account's public key (the "secret key") and base64-encoded. This module isolates
that construction so the client and its tests do not embed crypto details.
"""

import base64
import time

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

_PEM_HEADER = "-----BEGIN PUBLIC KEY-----"
_PEM_FOOTER = "-----END PUBLIC KEY-----"


def _normalise_pem(secret_key: str) -> bytes:
    """Return the secret key wrapped in PEM armour if it is not already."""

    key = secret_key.strip()
    if _PEM_HEADER in key:
        return key.encode("utf-8")
    body = "\n".join(key[i : i + 64] for i in range(0, len(key), 64))
    return f"{_PEM_HEADER}\n{body}\n{_PEM_FOOTER}\n".encode("utf-8")


def build_id_token(api_key: str, secret_key: str, *, timestamp_ms: int | None = None) -> str:
    """Build the base64 RSA ``id_token`` for the auth handshake.

    Args:
        api_key: The account API key (``client_id``).
        secret_key: The RSA public key (PEM or bare base64 body).
        timestamp_ms: Optional epoch milliseconds; defaults to the current time.
    """

    stamp = timestamp_ms if timestamp_ms is not None else int(time.time() * 1000)
    payload = f"client_id={api_key}&timestamp={stamp}".encode("utf-8")
    public_key = load_pem_public_key(_normalise_pem(secret_key))
    encrypted = public_key.encrypt(payload, padding.PKCS1v15())  # type: ignore[union-attr]
    return base64.b64encode(encrypted).decode("utf-8")
