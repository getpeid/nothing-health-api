from fastapi import APIRouter, Depends

from app.core.security import get_current_user, ScopeChecker
from app.models.user import User

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me")
async def get_profile(
    _scope=Depends(ScopeChecker("profile:read")),
    user: User = Depends(get_current_user),
):
    """Basic profile — no PII beyond display name."""
    return {
        "id": user.id,
        "display_name": user.display_name,
        "created_at": user.created_at,
    }
