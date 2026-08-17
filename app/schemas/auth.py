from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthProviderRequest(BaseModel):
    provider: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str | None
    avatar_url: str | None
    role: str
    scopes: list[str]