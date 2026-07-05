from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from fastapi import Header, HTTPException

from app.config import Settings, get_settings

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthUser:
    uid: str
    email: str | None
    name: str | None
    picture: str | None
    claims: dict[str, Any]


class FirebaseAuthVerifier:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._initialized = False

    def _ensure_app(self) -> None:
        if self._initialized:
            return
        if not self._settings.firebase_project_id:
            raise HTTPException(status_code=503, detail="Firebase auth is not configured.")

        import firebase_admin
        from firebase_admin import credentials

        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(
                credentials.ApplicationDefault(),
                {"projectId": self._settings.firebase_project_id},
            )
        self._initialized = True

    def verify(self, token: str) -> AuthUser:
        self._ensure_app()
        from firebase_admin import auth

        try:
            claims = auth.verify_id_token(token, check_revoked=False)
        except Exception as exc:
            log.warning("firebase_token_invalid", extra={"error": str(exc)})
            raise HTTPException(status_code=401, detail="Invalid Firebase ID token.") from exc

        uid = claims.get("uid") or claims.get("sub")
        if not isinstance(uid, str) or not uid:
            raise HTTPException(status_code=401, detail="Firebase token missing uid.")
        return AuthUser(
            uid=uid,
            email=claims.get("email") if isinstance(claims.get("email"), str) else None,
            name=claims.get("name") if isinstance(claims.get("name"), str) else None,
            picture=claims.get("picture") if isinstance(claims.get("picture"), str) else None,
            claims=dict(claims),
        )


@lru_cache(maxsize=1)
def get_auth_verifier() -> FirebaseAuthVerifier:
    return FirebaseAuthVerifier(get_settings())


async def get_optional_user(
    authorization: str | None = Header(default=None),
) -> AuthUser | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="Expected Authorization: Bearer <token>.")
    return get_auth_verifier().verify(token.strip())


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> AuthUser:
    user = await get_optional_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Sign in to access this resource.")
    return user
