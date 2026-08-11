import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.models.user import User



def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "scopes": user.scopes.split(),
        "type": "access",
        "iat": int(
            now.timestamp()
        ),
        "exp": int(
            (now + timedelta(
                minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )).timestamp()
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm = settings.JWT_ALGORITHM,
    )

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_refresh_token(db: Session, user: User) -> str:
    raw_token = secrets.token_urlsafe(64)

    expires_at = datetime.utcnow() + timedelta(
        days = settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    db_token = RefreshToken(
        user_id = user.id,
        token_hash = hash_refresh_token(raw_token),
        expires_at = expires_at,
    )

    db.add(db_token)
    db.commit()

    return raw_token

def issue_tokens(db: Session, user: User) -> dict:
    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(db, user),
        "token_type": "bearer",
    }