from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import jwt
from jwt import InvalidTokenError

from app.core.config import settings


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update(
        {
            "type": "access",
            "jti": str(uuid4()),
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "iat": datetime.now(UTC),
            "nbf": datetime.now(UTC),
            "exp": expire,
        }
    )
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update(
        {
            "type": "refresh",
            "jti": str(uuid4()),
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "iat": datetime.now(UTC),
            "nbf": datetime.now(UTC),
            "exp": expire,
        }
    )
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
    except InvalidTokenError:
        raise InvalidTokenError()
