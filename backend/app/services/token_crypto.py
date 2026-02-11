import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import get_settings

settings = get_settings()


def _resolve_fernet_key() -> bytes:
    configured = settings.TOKEN_ENCRYPTION_KEY.strip()
    if configured:
        return configured.encode("utf-8")

    # Deterministic fallback for local use when dedicated key is not set.
    digest = hashlib.sha256(settings.JWT_SECRET_KEY.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


_fernet = Fernet(_resolve_fernet_key())


def encrypt_secret(value: str) -> str:
    token = _fernet.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_secret(value: str) -> str:
    decrypted = _fernet.decrypt(value.encode("utf-8"))
    return decrypted.decode("utf-8")
