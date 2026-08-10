import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String,
        primary_key = True,
        default = lambda: str (uuid.uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String,
        unique = True,
        index = True,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable = True,
    )

    avtar_url: Mapped[str | None] = mapped_column(
        String,
        nullable = True,
    )

    password_hash: Mapped[str | None] = mapped_column(
        String,
        nullable = True,
    )

    role: Mapped[str] = mapped_column(
        String,
        default = "user",
    )

    scopes: Mapped[str] = mapped_column(
        String,
        default = "me:read"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default = True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default = datetime.utcnow,
    )

    identities = relationship("UserIdentity", back_populates = "user")
    refresh_tokens = relationship("RefreshToken", back_populates = "user")
