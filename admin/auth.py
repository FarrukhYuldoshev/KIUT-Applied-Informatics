from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from demo_auth.demo_auth_jwt import (
    User,
    create_access_token,
    check_user,
    get_payload_auth_user,
)
from auth.utils import hash_password


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        if check_user(username, password):
            password = hash_password(password)
            user = User(username=username, password=password)
            token = create_access_token(user)
            request.session.update({"token": token})
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        user = await get_payload_auth_user(token=token)
        if user is None:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        return True


authentication_backend = AdminAuth(secret_key="...")
# admin = Admin(app=..., authentication_backend=authentication_backend، ...)
