from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True
