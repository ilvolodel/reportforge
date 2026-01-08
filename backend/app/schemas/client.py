"""Pydantic schemas for Client models."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ClientBase(BaseModel):
    """Base schema for Client."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class ClientCreate(ClientBase):
    """Schema for creating a client."""
    pass


class ClientUpdate(BaseModel):
    """Schema for updating a client."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class ClientResponse(ClientBase):
    """Schema for Client response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
