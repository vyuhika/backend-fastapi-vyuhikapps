import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserIdentity(Base):
    __tablename__ = "user_identities"

    id: Mapped[str] = mapped_column(
        String, 
        primary_key = True,
        default = lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        index = True,
    )

    provide: Mapped[str] = mapped_column(
        String, 
        index = True,
    )
    provider_subject: Mapped[str] = mapped_column(
        String, 
        index = True,
    )

    email: Mapped[str | None] = mapped_column(
        String, 
        nullable = True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow
    )

    user = relationship("User", back_populates="identities")

    __table_args__ = (
        UniqueConstraint("provider", "provider_subject", name="uq_provider_subject"),
    )