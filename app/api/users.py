from fastapi import APIRouter, Security

from app.core.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter()


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "scopes": user.scopes.split(),
        "is_active": user.is_active,
    }


@router.get("/me")
def me(user: User = Security(get_current_user, scopes=["me:read"])):
    return serialize_user(user)


@router.get("/admin-only")
def admin_only(user: User = Security(require_admin)):
    return {
        "message": "Admin access granted",
        "user": serialize_user(user),
    }