"""DEVELOPMENT-ONLY access policy for session endpoints. This is NOT authentication.

Until Google sign-in exists (Batch 04), the caller names itself with the X-Dev-User header
(default "dev-user"). Anyone can claim any identity, so this protects nothing; it exists so that
ownership checks are written and tested now and keep working when real identities replace it.
Outside APP_ENV=development the session endpoints refuse to run (503)."""
from fastapi import Header

from .config import settings
from .errors import ApiError


def dev_owner(x_dev_user: str = Header(default="dev-user", alias="X-Dev-User", pattern=r"^[A-Za-z0-9_.@-]{1,64}$",
              description="DEV ONLY. Claimed identity; not verified. Replaced by real authentication in Batch 04.")) -> str:
    if settings.app_env != "development":
        raise ApiError(503, "auth_not_available", "Session endpoints are disabled outside development until authentication is implemented.")
    return x_dev_user
