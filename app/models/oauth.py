import uuid
import secrets
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OAuthApp(Base):
    """Registered third-party application."""

    __tablename__ = "oauth_apps"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200))
    client_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, default=lambda: secrets.token_urlsafe(32)
    )
    client_secret_hash: Mapped[str] = mapped_column(String(128))
    redirect_uri: Mapped[str] = mapped_column(String(500))
    scopes: Mapped[str] = mapped_column(Text, default="")  # space-separated
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)  # app review gate
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class AuthorizationCode(Base):
    """Short-lived code exchanged for tokens during OAuth flow."""

    __tablename__ = "authorization_codes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, default=lambda: secrets.token_urlsafe(64)
    )
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("oauth_apps.client_id"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    scopes: Mapped[str] = mapped_column(Text)
    redirect_uri: Mapped[str] = mapped_column(String(500))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class RefreshToken(Base):
    """Tracks issued refresh tokens for revocation."""

    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("oauth_apps.client_id"))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
