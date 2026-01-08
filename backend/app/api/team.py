"""Team and Stakeholders CRUD API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.project import TeamMember, Stakeholder
from ..schemas.team import (
    TeamMemberCreate, TeamMemberUpdate, TeamMemberResponse,
    StakeholderCreate, StakeholderUpdate, StakeholderResponse
)

router = APIRouter(prefix="/api", tags=["team"])


# ==================== TEAM MEMBERS ====================

@router.get("/team-members", response_model=List[TeamMemberResponse])
async def list_team_members(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all team members."""
    team_members = db.query(TeamMember).offset(skip).limit(limit).all()
    return team_members


@router.get("/team-members/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(member_id: int, db: Session = Depends(get_db)):
    """Get a specific team member by ID."""
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    return member


@router.post("/team-members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_team_member(member: TeamMemberCreate, db: Session = Depends(get_db)):
    """Create a new team member."""
    db_member = TeamMember(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.put("/team-members/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    member_id: int,
    member: TeamMemberUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing team member."""
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    for key, value in member.dict(exclude_unset=True).items():
        setattr(db_member, key, value)
    
    db.commit()
    db.refresh(db_member)
    return db_member


@router.delete("/team-members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(member_id: int, db: Session = Depends(get_db)):
    """Delete a team member."""
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    db.delete(db_member)
    db.commit()
    return None


# ==================== STAKEHOLDERS ====================

@router.get("/stakeholders", response_model=List[StakeholderResponse])
async def list_stakeholders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all stakeholders."""
    stakeholders = db.query(Stakeholder).offset(skip).limit(limit).all()
    return stakeholders


@router.get("/stakeholders/{stakeholder_id}", response_model=StakeholderResponse)
async def get_stakeholder(stakeholder_id: int, db: Session = Depends(get_db)):
    """Get a specific stakeholder by ID."""
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    return stakeholder


@router.post("/stakeholders", response_model=StakeholderResponse, status_code=status.HTTP_201_CREATED)
async def create_stakeholder(stakeholder: StakeholderCreate, db: Session = Depends(get_db)):
    """Create a new stakeholder."""
    db_stakeholder = Stakeholder(**stakeholder.dict())
    db.add(db_stakeholder)
    db.commit()
    db.refresh(db_stakeholder)
    return db_stakeholder


@router.put("/stakeholders/{stakeholder_id}", response_model=StakeholderResponse)
async def update_stakeholder(
    stakeholder_id: int,
    stakeholder: StakeholderUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing stakeholder."""
    db_stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not db_stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    
    for key, value in stakeholder.dict(exclude_unset=True).items():
        setattr(db_stakeholder, key, value)
    
    db.commit()
    db.refresh(db_stakeholder)
    return db_stakeholder


@router.delete("/stakeholders/{stakeholder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stakeholder(stakeholder_id: int, db: Session = Depends(get_db)):
    """Delete a stakeholder."""
    db_stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not db_stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    
    db.delete(db_stakeholder)
    db.commit()
    return None
