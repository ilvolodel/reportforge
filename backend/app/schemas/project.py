"""Pydantic schemas for Project models."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class ProjectType(str, Enum):
    """Project type enum."""
    INTERNAL = "INTERNAL"
    PARTNER = "PARTNER"
    CLIENT = "CLIENT"


class ProjectStatus(str, Enum):
    """Project status enum."""
    FORECAST = "FORECAST"
    PROPOSAL = "PROPOSAL"
    SOLD = "SOLD"
    IN_DEVELOPMENT = "IN_DEVELOPMENT"
    GO_LIVE = "GO_LIVE"
    OPERATIONAL = "OPERATIONAL"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ActivityStatus(str, Enum):
    """Activity status enum."""
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CostCategory(str, Enum):
    """Cost category enum."""
    INTERNAL = "INTERNAL"
    VENDOR = "VENDOR"
    INFRASTRUCTURE = "INFRASTRUCTURE"


# ==================== PROJECT ====================

class ProjectBase(BaseModel):
    """Base schema for Project."""
    name: str = Field(..., max_length=255)
    project_type: ProjectType
    status: ProjectStatus = ProjectStatus.FORECAST
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, max_length=255)
    project_type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectResponse(ProjectBase):
    """Schema for Project response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== PROJECT ACTIVITY ====================

class ProjectActivityBase(BaseModel):
    """Base schema for ProjectActivity."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: ActivityStatus = ActivityStatus.PLANNED
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectActivityCreate(ProjectActivityBase):
    """Schema for creating a project activity."""
    pass


class ProjectActivityUpdate(BaseModel):
    """Schema for updating a project activity."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[ActivityStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectActivityResponse(ProjectActivityBase):
    """Schema for ProjectActivity response."""
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== PROJECT COST ====================

class ProjectCostBase(BaseModel):
    """Base schema for ProjectCost."""
    category: CostCategory
    amount: float
    description: Optional[str] = None
    date: Optional[date] = None


class ProjectCostCreate(ProjectCostBase):
    """Schema for creating a project cost."""
    pass


class ProjectCostUpdate(BaseModel):
    """Schema for updating a project cost."""
    category: Optional[CostCategory] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[date] = None


class ProjectCostResponse(ProjectCostBase):
    """Schema for ProjectCost response."""
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True
