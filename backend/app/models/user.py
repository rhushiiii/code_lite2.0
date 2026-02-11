from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    github_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    github_token_encrypted: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    github_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

    @property
    def github_connected(self) -> bool:
        return bool(self.github_token_encrypted)
