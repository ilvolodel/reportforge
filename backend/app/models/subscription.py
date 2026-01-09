"""Subscription and revenue models."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Date, Boolean, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class FinancialImpactType(str, enum.Enum):
    """Financial impact type enum."""
    REVENUE_CAPEX = "REVENUE_CAPEX"
    REVENUE_SUBSCRIPTION = "REVENUE_SUBSCRIPTION"
    SAVING_SUBSCRIPTION = "SAVING_SUBSCRIPTION"


class RevenueOneTime(Base):
    """One-time revenue or saving (CAPEX)."""
    
    __tablename__ = "revenue_one_time"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    impact_type = Column(SQLEnum(FinancialImpactType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text)
    date = Column(Date, nullable=False)
    is_forecast = Column(Boolean, default=False)  # True = forecast, False = actual
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="revenue_one_time")


class Subscription(Base):
    """Recurring subscription (annual forecast)."""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    impact_type = Column(SQLEnum(FinancialImpactType), nullable=False)
    annual_value = Column(Numeric(15, 2), nullable=False)  # Contractual annual value
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # null = ongoing
    description = Column(Text)
    is_forecast = Column(Boolean, default=False)  # True = future forecast, False = current
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="subscriptions")
    transactions = relationship("SubscriptionTransaction", back_populates="subscription", cascade="all, delete-orphan")


class SubscriptionTransaction(Base):
    """Monthly actual transaction for a subscription."""
    
    __tablename__ = "subscription_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)  # Actual amount for this month
    month = Column(Date, nullable=False)  # First day of month (e.g., 2025-10-01)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="transactions")
