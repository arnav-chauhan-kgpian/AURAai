"""Unit test for the auth id_token construction."""

import base64

from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from app.utils.crypto import build_id_token


def test_build_id_token_round_trips() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_pem = (
        private_key.public_key()
        .public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        .decode("utf-8")
    )

    token = build_id_token("my-api-key", public_pem, timestamp_ms=1_700_000_000_000)

    decrypted = private_key.decrypt(base64.b64decode(token), padding.PKCS1v15())
    assert decrypted.decode("utf-8") == "client_id=my-api-key&timestamp=1700000000000"
