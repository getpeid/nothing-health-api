import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"/api/{settings.api_version}/oauth/authorize",
    tokenUrl=f"/api/{settings.api_version}/oauth/token",
)


def create_access_token(data: dict, scopes: list[str]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {**data, "exp": expire, "scopes": scopes, "type": "access"}
    return jwt.encode(to_encode, settings.oauth_secret_key, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {**data, "exp": expire, "type": "refresh", "jti": secrets.token_urlsafe(32)}
    return jwt.encode(to_encode, settings.oauth_secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.oauth_secret_key, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    from app.models.user import User

    user = await db.get(User, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


class ScopeChecker:
    """Dependency that verifies the token has a required scope."""

    def __init__(self, required_scope: str):
        self.required_scope = required_scope

    async def __call__(self, token: str = Depends(oauth2_scheme)):
        payload = decode_token(token)
        scopes = payload.get("scopes", [])
        if self.required_scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope '{self.required_scope}' required",
            )
        return payload
