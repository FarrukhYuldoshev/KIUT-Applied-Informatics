from fastapi.params import Cookie

from .user import User
import auth.utils as auth_utils
from fastapi import APIRouter, Depends, HTTPException, Form, Response, Request, Header
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from .create_tokens import create_access_token, create_refresh_token
from pydantic import BaseModel, EmailStr
from jwt.exceptions import InvalidTokenError

http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt-login/login", scheme_name="Bearer")


class TokenInfo(BaseModel):
    refresh_token: str | None = None
    access_token: str
    token_type: str = "Bearer"


router = APIRouter(
    prefix="/jwt-login", tags=["JWT-auth"], dependencies=[Depends(http_bearer)]
)
farrukh = User(
    username="admin",
    password=auth_utils.hash_password(password="12345"),
    email="communityfarrukh@gmail.com",
)
javoxir = User(username="javoxir", password=auth_utils.hash_password(password="12345"))
users: dict[str, User] = {
    farrukh.username: farrukh,
    javoxir.username: javoxir,
}


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(...),
):
    un_authorized_exc = HTTPException(
        status_code=401, detail="Username or password incorrect"
    )
    if not (user := users.get(username)):
        raise un_authorized_exc
    if not auth_utils.check_password(password, user.password):
        raise un_authorized_exc
    if not user.active:
        raise HTTPException(status_code=403, detail="User inactive")
    return user


async def get_payload_auth_user(
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = auth_utils.decode_jwt(token)
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token error: {e}")
    return payload


async def get_current_user(payload: dict = Depends(get_payload_auth_user)) -> User:
    username: str | None = payload.get("sub")
    if user := users.get(username):
        return user
    raise HTTPException(status_code=401, detail="token invalid user not found")


async def get_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.active:
        raise HTTPException(status_code=403, detail="User inactive")
    else:
        return user


@router.post("/refresh", response_model=TokenInfo)
async def refresh_token(user: User = Depends(get_active_user)):
    access_token = create_access_token(user=user)
    return {"access_token": access_token}


@router.post("/login", response_model=TokenInfo)
async def login(response: Response, user: User = Depends(validate_auth_user)):
    access = create_access_token(user=user)
    refresh = create_refresh_token(user=user)
    response.set_cookie(key="Authorization", value=access)
    return {
        "refresh_token": refresh,
        "access_token": access,
    }


@router.get("/get/me")
async def get_me(
    user: User = Depends(get_active_user),
    payload: dict = Depends(get_payload_auth_user),
    cookie: str = Cookie(alias="Authorization"),
    # bu yerda ortiqchi payload ga yana murojaat qilmaydi
    # fastapi o'zi keshlagani uchun avotmatik buni keshdan topadi funksiyani ishga tushirmasdan
):
    print(cookie)
    return {
        "username": user.username,
        "email": user.email,
        "is_active": user.active,
        "logged_in_at": payload.get("iat"),
        "expires_at": payload.get("exp"),
    }
