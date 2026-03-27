from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.rate_limit import RateLimitMiddleware
from app.routers import oauth, health, profile

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Public REST API for Nothing watch health data. "
    "Enables third-party integrations including MCP servers, dashboards, and AI coaching tools.",
    docs_url="/docs",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# Routes
PREFIX = f"/api/{settings.api_version}"
app.include_router(oauth.router, prefix=PREFIX)
app.include_router(health.router, prefix=PREFIX)
app.include_router(profile.router, prefix=PREFIX)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}
