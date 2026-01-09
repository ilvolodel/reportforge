"""FastAPI main application."""

from fastapi import FastAPI, Request, Cookie, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import os
import logging
from typing import Optional

from .config import get_settings
from .database import SessionLocal
from .models.user import UserSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(name)s - %(message)s'
)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Monthly Report Generator Dashboard",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = "/app/frontend/static"
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Setup templates
templates_path = "/app/frontend/templates"
templates = Jinja2Templates(directory=templates_path) if os.path.exists(templates_path) else None


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/k8s."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment
    }


@app.get("/")
async def root(request: Request):
    """Root endpoint - will serve login page or redirect to dashboard."""
    if templates:
        return templates.TemplateResponse("login.html", {"request": request})
    else:
        return JSONResponse({
            "message": "ReportForge API",
            "version": "1.0.0",
            "docs": "/api/docs"
        })


@app.get("/dashboard")
async def dashboard(request: Request, session_token: Optional[str] = Cookie(None)):
    """Dashboard page - main application interface (requires authentication)."""
    if not templates:
        return JSONResponse({
            "error": "Templates not configured"
        }, status_code=500)
    
    # Check authentication via session cookie
    if not session_token:
        return RedirectResponse(url="/", status_code=303)
    
    # Validate session
    db = SessionLocal()
    try:
        now_utc = datetime.now(timezone.utc)
        user_session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True,
            UserSession.expires_at > now_utc
        ).first()
        
        if not user_session:
            # Invalid or expired session - redirect to login
            return RedirectResponse(url="/", status_code=303)
        
        # Session valid - show dashboard
        return templates.TemplateResponse("dashboard.html", {"request": request})
    finally:
        db.close()


# Import and include API routers
from .api import auth, projects, clients, team, subscriptions, reports

app.include_router(auth.router)
app.include_router(auth.public_router)  # Public routes without /api/ prefix
app.include_router(projects.router)
app.include_router(clients.router)
app.include_router(team.router)
app.include_router(subscriptions.router)
app.include_router(reports.router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8030))
    uvicorn.run(app, host="0.0.0.0", port=port)
