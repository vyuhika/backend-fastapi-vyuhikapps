from fastapi import Cookie, Depends, HTTPException, Security
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ACCESS_COOKIE_NAME
from app.db.session import SessionLocal
from app.models.user import User
from app.services.users import get_user_by_id


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user(
    security_scopes: SecurityScopes,
    access_token: str | None = Cookie(default=None, alias=ACCESS_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = get_user_by_id(db, payload.get("sub"))

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    token_scopes = set(payload.get("scopes", []))
    required_scopes = set(security_scopes.scopes)

    if not required_scopes.issubset(token_scopes):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return user


def require_admin(user: User = Security(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return user