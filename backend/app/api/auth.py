import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database import SessionLocal
from ..models.user import User, MagicLink, UserSession
from ..services.email_service import email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
public_router = APIRouter(tags=["Authentication - Public"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkResponse(BaseModel):
    success: bool
    message: str


@router.post("/request-magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    db: Session = Depends(get_db)
):
    """
    Generate and send magic link to user's email
    
    Only allows @infocert.it emails
    """
    email = request.email.lower().strip()
    
    # Validate email domain
    if not email.endswith("@infocert.it"):
        raise HTTPException(
            status_code=400,
            detail="Only @infocert.it email addresses are allowed"
        )
    
    try:
        # Check if user exists, create if not
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Extract name from email
            name_part = email.split("@")[0].replace(".", " ").title()
            user = User(
                email=email,
                full_name=name_part,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {email}")
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Calculate expiry time
        expiry_minutes = int(os.getenv("MAGIC_LINK_EXPIRY_MINUTES", "15"))
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        # Save magic link to database
        magic_link = MagicLink(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            is_used=False
        )
        db.add(magic_link)
        db.commit()
        
        # Build magic link URL
        app_url = os.getenv("APP_URL", "https://reportforge.brainaihub.tech")
        magic_link_url = f"{app_url}/auth/verify?token={token}"
        
        # Send email
        logger.info(f"📧 About to send magic link to {email}")
        logger.info(f"🔗 Magic link URL: {magic_link_url}")
        email_sent = email_service.send_magic_link(
            to_email=email,
            magic_link=magic_link_url,
            user_name=user.full_name
        )
        logger.info(f"📬 Email send result: {email_sent}")
        
        if not email_sent:
            logger.error(f"Failed to send email to {email}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send magic link email. Please try again."
            )
        
        logger.info(f"Magic link sent to {email}, expires at {expires_at}")
        
        return MagicLinkResponse(
            success=True,
            message=f"Magic link sent to {email}. Check your inbox!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting magic link for {email}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred. Please try again."
        )


@public_router.get("/auth/verify")
async def verify_magic_link(
    token: str,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Verify magic link token and create user session
    
    Returns redirect to dashboard on success
    """
    try:
        # Find magic link
        magic_link = db.query(MagicLink).filter(
            and_(
                MagicLink.token == token,
                MagicLink.is_used == False,
                MagicLink.expires_at > datetime.utcnow()
            )
        ).first()
        
        if not magic_link:
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Invalid Link - ReportForge</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #0072CE 0%, #005a9e 100%); color: white; }
                        .container { background: white; color: #333; padding: 40px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                        h1 { color: #dc3545; }
                        a { color: #0072CE; text-decoration: none; font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>❌ Link non valido o scaduto</h1>
                        <p>Questo magic link non è valido o è già stato utilizzato.</p>
                        <p>I link scadono dopo 15 minuti per sicurezza.</p>
                        <p><a href="/">← Torna alla pagina di login</a></p>
                    </div>
                </body>
                </html>
                """,
                status_code=400
            )
        
        # Mark magic link as used
        magic_link.is_used = True
        magic_link.used_at = datetime.utcnow()
        
        # Get user
        user = db.query(User).filter(User.id == magic_link.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=403, detail="User not found or inactive")
        
        # Update user last login
        user.last_login_at = datetime.utcnow()
        
        # Create session token
        session_token = secrets.token_urlsafe(48)
        session_expiry_days = int(os.getenv("SESSION_EXPIRY_DAYS", "30"))
        session_expires_at = datetime.utcnow() + timedelta(days=session_expiry_days)
        
        # Save session to database
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=session_expires_at,
            is_active=True
        )
        db.add(user_session)
        db.commit()
        
        logger.info(f"User {user.email} logged in successfully, session expires at {session_expires_at}")
        
        # Create redirect response
        redirect_response = RedirectResponse(url="/dashboard", status_code=303)
        
        # Set session cookie (httponly for security)
        redirect_response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=session_expiry_days * 24 * 60 * 60,
            httponly=True,
            secure=True,  # HTTPS only
            samesite="lax"
        )
        
        return redirect_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying magic link: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during login")


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Logout user by invalidating session
    """
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Invalidate session in database
        user_session = db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()
        
        if user_session:
            user_session.is_active = False
            db.commit()
            logger.info(f"User {user_session.user_id} logged out")
    
    # Clear cookie
    response.delete_cookie("session_token")
    
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user from session
    """
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find active session
    user_session = db.query(UserSession).filter(
        and_(
            UserSession.session_token == session_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        )
    ).first()
    
    if not user_session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Get user
    user = db.query(User).filter(User.id == user_session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User not found or inactive")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "last_login": user.last_login_at.isoformat() if user.last_login_at else None
    }
