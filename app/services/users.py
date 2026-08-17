from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_identity import UserIdentity
from app.services.password import hash_password, verify_password


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()


def create_password_user(
    db: Session,
    email: str,
    password: str,
    name: str | None = None,
) -> User:
    existing = get_user_by_email(db, email)

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=email.lower(),
        name=name,
        password_hash=hash_password(password),
        role="user",
        scopes="me:read",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    identity = UserIdentity(
        user_id=user.id,
        provider="password",
        provider_subject=user.email,
        email=user.email,
    )

    db.add(identity)
    db.commit()

    return user


def authenticate_password_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    return user


def get_or_create_oauth_user(
    db: Session,
    provider: str,
    provider_subject: str,
    email: str,
    name: str | None = None,
    avatar_url: str | None = None,
) -> User:
    identity = (
        db.query(UserIdentity)
        .filter(
            UserIdentity.provider == provider,
            UserIdentity.provider_subject == provider_subject,
        )
        .first()
    )

    if identity:
        return identity.user

    user = get_user_by_email(db, email)

    if not user:
        user = User(
            email=email.lower(),
            name=name,
            avatar_url=avatar_url,
            role="user",
            scopes="me:read",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    identity = UserIdentity(
        user_id=user.id,
        provider=provider,
        provider_subject=provider_subject,
        email=email.lower(),
    )

    db.add(identity)
    db.commit()

    return user