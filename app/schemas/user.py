from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str | None
    avatar_url: str | None
    role: str
    scopes: list[str]
    is_active: bool