from fastapi import APIRouter, Depends, HTTPException, Header, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status
import secrets

from starlette.responses import Response

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBasic()


users = {
    "admin": "mypassword",
    "user": "user123",
}

tokens = {
    "65bbfda3707dab2d5063b19cab84858cda89054e398516ffe999ad68aae9aa82": "admin",
    "fdfa5713515d8ff426195c7efac2fec9f961d5b62809259c1680c54714f9efdf": "user",
}


async def get_user(user: HTTPBasicCredentials = Depends(security)):
    un_auth = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Username or password incorrect",
        headers={"WWW-Authenticate": "Basic"},
    )
    if user.username not in users:
        raise un_auth
    if not secrets.compare_digest(
        users[user.username].encode("utf-8"), user.password.encode("utf-8")
    ):
        raise un_auth
    return user


async def authorize_with_token(token: str = Header(alias="x-auth-token")):
    un_auth = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
    )
    if token not in tokens:
        raise un_auth
    else:
        return {"username": tokens[token], "password": users[tokens[token]]}


COOKIE_ID_KEY_NAME = "web-session-id"
COOKIE: dict[str, dict[str, str]] = {}


@router.post("/login")
async def login(response: Response, user: HTTPBasicCredentials = Depends(get_user)):
    token = secrets.token_hex()
    response.set_cookie(COOKIE_ID_KEY_NAME, token, max_age=5)
    COOKIE[token] = user.model_dump()
    return {"success": True}


@router.get("/getme")
async def get_me(token: str = Cookie(alias=COOKIE_ID_KEY_NAME)):
    user = COOKIE.get(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return {"message": "Hi! " + user.get("username"), **user}


# @router.get("/")
# async def authorize(user: HTTPBasicCredentials = Depends(get_user)):
#     return user


# @router.get("/")
# async def authorize(user: HTTPBasicCredentials = Depends(authorize_with_token)):
#     return user
