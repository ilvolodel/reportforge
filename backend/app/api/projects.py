"""Projects CRUD API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from ..database import get_db
from ..models.project import Project, ProjectActivity, ProjectCost
from ..schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectActivityCreate, ProjectActivityUpdate, ProjectActivityResponse,
    ProjectCostCreate, ProjectCostUpdate, ProjectCostResponse
)
from .auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])


# ==================== PROJECTS ====================

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all projects."""
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new project."""
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing project."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project.dict(exclude_unset=True).items():
        setattr(db_project, key, value)
    
    db_project.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a project."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return None


# ==================== PROJECT ACTIVITIES ====================

@router.get("/{project_id}/activities", response_model=List[ProjectActivityResponse])
async def list_project_activities(project_id: int, db: Session = Depends(get_db)):
    """List all activities for a project."""
    activities = db.query(ProjectActivity).filter(ProjectActivity.project_id == project_id).all()
    return activities


@router.post("/{project_id}/activities", response_model=ProjectActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_project_activity(
    project_id: int,
    activity: ProjectActivityCreate,
    db: Session = Depends(get_db)
):
    """Create a new activity for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_activity = ProjectActivity(**activity.dict(), project_id=project_id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@router.put("/activities/{activity_id}", response_model=ProjectActivityResponse)
async def update_project_activity(
    activity_id: int,
    activity: ProjectActivityUpdate,
    db: Session = Depends(get_db)
):
    """Update a project activity."""
    db_activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    for key, value in activity.dict(exclude_unset=True).items():
        setattr(db_activity, key, value)
    
    db.commit()
    db.refresh(db_activity)
    return db_activity


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_activity(activity_id: int, db: Session = Depends(get_db)):
    """Delete a project activity."""
    db_activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(db_activity)
    db.commit()
    return None


# ==================== PROJECT COSTS ====================

@router.get("/{project_id}/costs", response_model=List[ProjectCostResponse])
async def list_project_costs(project_id: int, db: Session = Depends(get_db)):
    """List all costs for a project."""
    costs = db.query(ProjectCost).filter(ProjectCost.project_id == project_id).all()
    return costs


@router.post("/{project_id}/costs", response_model=ProjectCostResponse, status_code=status.HTTP_201_CREATED)
async def create_project_cost(
    project_id: int,
    cost: ProjectCostCreate,
    db: Session = Depends(get_db)
):
    """Create a new cost for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_cost = ProjectCost(**cost.dict(), project_id=project_id)
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost


@router.put("/costs/{cost_id}", response_model=ProjectCostResponse)
async def update_project_cost(
    cost_id: int,
    cost: ProjectCostUpdate,
    db: Session = Depends(get_db)
):
    """Update a project cost."""
    db_cost = db.query(ProjectCost).filter(ProjectCost.id == cost_id).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    
    for key, value in cost.dict(exclude_unset=True).items():
        setattr(db_cost, key, value)
    
    db.commit()
    db.refresh(db_cost)
    return db_cost


@router.delete("/costs/{cost_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_cost(cost_id: int, db: Session = Depends(get_db)):
    """Delete a project cost."""
    db_cost = db.query(ProjectCost).filter(ProjectCost.id == cost_id).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    
    db.delete(db_cost)
    db.commit()
    return None
