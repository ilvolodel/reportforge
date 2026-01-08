"""FastAPI main application."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from .config import get_settings

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
async def dashboard(request: Request):
    """Dashboard page - main application interface."""
    if templates:
        # TODO: Add authentication check via session cookie
        return templates.TemplateResponse("dashboard.html", {"request": request})
    else:
        return JSONResponse({
            "error": "Templates not configured"
        }, status_code=500)


# Import and include API routers
from .api import auth

app.include_router(auth.router)
app.include_router(auth.public_router)  # Public routes without /api/ prefix

# Additional routers (will add later)
# from .api import projects, team_members, clients, subscriptions, reports
# app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
# ... etc


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8030))
    uvicorn.run(app, host="0.0.0.0", port=port)
