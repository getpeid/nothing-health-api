from pydantic import BaseModel


VALID_SCOPES = [
    "heart_rate:read",
    "sleep:read",
    "spo2:read",
    "steps:read",
    "workouts:read",
    "profile:read",
]


class AuthorizeRequest(BaseModel):
    client_id: str
    redirect_uri: str
    scope: str  # space-separated scopes
    state: str | None = None
    response_type: str = "code"


class TokenRequest(BaseModel):
    grant_type: str  # "authorization_code" or "refresh_token"
    code: str | None = None
    refresh_token: str | None = None
    client_id: str
    client_secret: str
    redirect_uri: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: str


class RevokeRequest(BaseModel):
    token: str
    client_id: str
    client_secret: str


class AppRegistration(BaseModel):
    name: str
    redirect_uri: str
    scopes: str  # space-separated requested scopes


class AppRegistrationResponse(BaseModel):
    client_id: str
    client_secret: str
    name: str
    scopes: str
