"""Pydantic schemas for Subscription and Revenue models."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum
from decimal import Decimal


class FinancialImpactType(str, Enum):
    """Financial impact type enum."""
    REVENUE_CAPEX = "REVENUE_CAPEX"
    REVENUE_SUBSCRIPTION = "REVENUE_SUBSCRIPTION"
    SAVING_SUBSCRIPTION = "SAVING_SUBSCRIPTION"


# ==================== REVENUE ONE-TIME ====================

class RevenueOneTimeBase(BaseModel):
    """Base schema for RevenueOneTime."""
    impact_type: FinancialImpactType
    amount: Decimal
    description: Optional[str] = None
    date: date
    is_forecast: bool = False


class RevenueOneTimeCreate(RevenueOneTimeBase):
    """Schema for creating a one-time revenue."""
    pass


class RevenueOneTimeUpdate(BaseModel):
    """Schema for updating a one-time revenue."""
    impact_type: Optional[FinancialImpactType] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    date: Optional[date] = None
    is_forecast: Optional[bool] = None


class RevenueOneTimeResponse(RevenueOneTimeBase):
    """Schema for RevenueOneTime response."""
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== SUBSCRIPTION ====================

class SubscriptionBase(BaseModel):
    """Base schema for Subscription."""
    impact_type: FinancialImpactType
    annual_value: Decimal
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_forecast: bool = False


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a subscription."""
    pass


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription."""
    impact_type: Optional[FinancialImpactType] = None
    annual_value: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_forecast: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase):
    """Schema for Subscription response."""
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== SUBSCRIPTION TRANSACTION ====================

class SubscriptionTransactionBase(BaseModel):
    """Base schema for SubscriptionTransaction."""
    amount: Decimal
    month: date
    notes: Optional[str] = None


class SubscriptionTransactionCreate(SubscriptionTransactionBase):
    """Schema for creating a subscription transaction."""
    pass


class SubscriptionTransactionUpdate(BaseModel):
    """Schema for updating a subscription transaction."""
    amount: Optional[Decimal] = None
    month: Optional[date] = None
    notes: Optional[str] = None


class SubscriptionTransactionResponse(SubscriptionTransactionBase):
    """Schema for SubscriptionTransaction response."""
    id: int
    subscription_id: int
    created_at: datetime

    class Config:
        from_attributes = True
