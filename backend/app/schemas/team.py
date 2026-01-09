"""Pydantic schemas for Team models."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class TeamMemberBase(BaseModel):
    """Base schema for TeamMember."""
    full_name: str = Field(..., max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, max_length=255)


class TeamMemberCreate(TeamMemberBase):
    """Schema for creating a team member."""
    pass


class TeamMemberUpdate(BaseModel):
    """Schema for updating a team member."""
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, max_length=255)


class TeamMemberResponse(TeamMemberBase):
    """Schema for TeamMember response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StakeholderBase(BaseModel):
    """Base schema for Stakeholder."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class StakeholderCreate(StakeholderBase):
    """Schema for creating a stakeholder."""
    pass


class StakeholderUpdate(BaseModel):
    """Schema for updating a stakeholder."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class StakeholderResponse(StakeholderBase):
    """Schema for Stakeholder response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
