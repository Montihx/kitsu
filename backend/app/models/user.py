import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .refresh_token import RefreshToken
    from .user_role import UserRole
    from .favorite import Favorite
    from .watch_progress import WatchProgress
    from .anime import Anime
    from .episode import Episode
    from .audit_log import AuditLog


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        foreign_keys="[UserRole.user_id]",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    granted_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        foreign_keys="[UserRole.granted_by]",
        back_populates="granter"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )
    watch_progress: Mapped[list["WatchProgress"]] = relationship(
        "WatchProgress", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Anime ownership relationships
    created_anime: Mapped[list["Anime"]] = relationship(
        "Anime",
        foreign_keys="[Anime.created_by]",
        back_populates="creator"
    )
    updated_anime: Mapped[list["Anime"]] = relationship(
        "Anime",
        foreign_keys="[Anime.updated_by]",
        back_populates="updater"
    )
    locked_anime: Mapped[list["Anime"]] = relationship(
        "Anime",
        foreign_keys="[Anime.locked_by]",
        back_populates="locker"
    )
    deleted_anime: Mapped[list["Anime"]] = relationship(
        "Anime",
        foreign_keys="[Anime.deleted_by]",
        back_populates="deleter"
    )
    
    # Episode ownership relationships
    created_episodes: Mapped[list["Episode"]] = relationship(
        "Episode",
        foreign_keys="[Episode.created_by]",
        back_populates="creator"
    )
    updated_episodes: Mapped[list["Episode"]] = relationship(
        "Episode",
        foreign_keys="[Episode.updated_by]",
        back_populates="updater"
    )
    locked_episodes: Mapped[list["Episode"]] = relationship(
        "Episode",
        foreign_keys="[Episode.locked_by]",
        back_populates="locker"
    )
    deleted_episodes: Mapped[list["Episode"]] = relationship(
        "Episode",
        foreign_keys="[Episode.deleted_by]",
        back_populates="deleter"
    )
    
    # Audit logs
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="actor"
    )
