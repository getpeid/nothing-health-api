from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    pwd_context,
)
from app.models.oauth import OAuthApp, AuthorizationCode, RefreshToken
from app.schemas.oauth import (
    VALID_SCOPES,
    AuthorizeRequest,
    TokenRequest,
    TokenResponse,
    RevokeRequest,
    AppRegistration,
    AppRegistrationResponse,
)

router = APIRouter(prefix="/oauth", tags=["OAuth 2.0"])


@router.post("/register", response_model=AppRegistrationResponse)
async def register_app(body: AppRegistration, db: AsyncSession = Depends(get_db)):
    """Register a new third-party application. Returns client credentials."""
    import secrets

    raw_secret = secrets.token_urlsafe(48)
    app = OAuthApp(
        name=body.name,
        client_secret_hash=pwd_context.hash(raw_secret),
        redirect_uri=body.redirect_uri,
        scopes=body.scopes,
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)

    return AppRegistrationResponse(
        client_id=app.client_id,
        client_secret=raw_secret,
        name=app.name,
        scopes=app.scopes,
    )


@router.post("/authorize")
async def authorize(body: AuthorizeRequest, db: AsyncSession = Depends(get_db)):
    """
    Issue an authorization code. In production this would render a consent screen
    in Nothing X — here we simulate the consent grant.
    """
    # Validate app
    result = await db.execute(select(OAuthApp).where(OAuthApp.client_id == body.client_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=400, detail="Unknown client_id")
    if not app.is_approved:
        raise HTTPException(status_code=403, detail="App not yet approved for production use")
    if app.redirect_uri != body.redirect_uri:
        raise HTTPException(status_code=400, detail="redirect_uri mismatch")

    # Validate scopes
    requested = body.scope.split()
    for s in requested:
        if s not in VALID_SCOPES:
            raise HTTPException(status_code=400, detail=f"Invalid scope: {s}")

    # Create auth code (in real flow, user_id comes from authenticated session)
    code = AuthorizationCode(
        client_id=body.client_id,
        user_id="placeholder-user",  # replaced by real auth in production
        scopes=body.scope,
        redirect_uri=body.redirect_uri,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    db.add(code)
    await db.commit()
    await db.refresh(code)

    return {"code": code.code, "state": body.state}


@router.post("/token", response_model=TokenResponse)
async def exchange_token(body: TokenRequest, db: AsyncSession = Depends(get_db)):
    """Exchange authorization code or refresh token for access + refresh tokens."""
    # Verify client credentials
    result = await db.execute(select(OAuthApp).where(OAuthApp.client_id == body.client_id))
    app = result.scalar_one_or_none()
    if not app or not pwd_context.verify(body.client_secret, app.client_secret_hash):
        raise HTTPException(status_code=401, detail="Invalid client credentials")

    if body.grant_type == "authorization_code":
        if not body.code:
            raise HTTPException(status_code=400, detail="code is required")

        result = await db.execute(
            select(AuthorizationCode).where(AuthorizationCode.code == body.code)
        )
        auth_code = result.scalar_one_or_none()
        if not auth_code or auth_code.used:
            raise HTTPException(status_code=400, detail="Invalid or used authorization code")
        if auth_code.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Authorization code expired")
        if auth_code.client_id != body.client_id:
            raise HTTPException(status_code=400, detail="client_id mismatch")

        auth_code.used = True
        scopes = auth_code.scopes.split()
        user_id = auth_code.user_id

    elif body.grant_type == "refresh_token":
        if not body.refresh_token:
            raise HTTPException(status_code=400, detail="refresh_token is required")

        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Not a refresh token")

        # Check revocation
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.jti == payload.get("jti"))
        )
        stored = result.scalar_one_or_none()
        if stored and stored.revoked:
            raise HTTPException(status_code=400, detail="Token has been revoked")

        scopes = payload.get("scopes", [])
        user_id = payload.get("sub")
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant_type")

    # Issue tokens
    access_token = create_access_token({"sub": user_id}, scopes)
    refresh_token = create_refresh_token({"sub": user_id, "scopes": scopes})

    # Store refresh token for revocation tracking
    refresh_payload = decode_token(refresh_token)
    db.add(RefreshToken(
        jti=refresh_payload["jti"],
        user_id=user_id,
        client_id=body.client_id,
    ))
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        scope=" ".join(scopes) if isinstance(scopes, list) else scopes,
    )


@router.post("/revoke")
async def revoke_token(body: RevokeRequest, db: AsyncSession = Depends(get_db)):
    """Revoke a refresh token (one-tap revoke from Nothing X)."""
    result = await db.execute(select(OAuthApp).where(OAuthApp.client_id == body.client_id))
    app = result.scalar_one_or_none()
    if not app or not pwd_context.verify(body.client_secret, app.client_secret_hash):
        raise HTTPException(status_code=401, detail="Invalid client credentials")

    payload = decode_token(body.token)
    jti = payload.get("jti")
    if jti:
        result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        stored = result.scalar_one_or_none()
        if stored:
            stored.revoked = True
            await db.commit()

    return {"status": "revoked"}
