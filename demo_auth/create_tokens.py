from datetime import timedelta
from auth import utils as auth_utils
from .user import User
from core.settings import settings

TOKEN_TYPE = "type"
ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"


def create_token(
    payload: dict,
    type_token: str,
    expire_minutes: int = settings.auth_jwt.access_token_expires_minutes,
    expires_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE: type_token}
    jwt_payload.update(payload)
    return auth_utils.encode_jwt(
        jwt_payload, expire_minutes=expire_minutes, expires_timedelta=expires_timedelta
    )


def create_access_token(user: User) -> str:
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
        "is_active": user.active,
    }
    return create_token(
        payload=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expires_minutes,
        type_token=ACCESS_TOKEN,
    )


def create_refresh_token(user: User):
    jwt_payload = {
        "sub": user.username,
    }
    return create_token(
        payload=jwt_payload,
        type_token=REFRESH_TOKEN,
        expires_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expires_days),
    )
