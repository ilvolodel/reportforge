"""Subscriptions and Revenue CRUD API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.subscription import Subscription, SubscriptionTransaction, RevenueOneTime
from ..models.project import Project
from ..schemas.subscription import (
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    SubscriptionTransactionCreate, SubscriptionTransactionUpdate, SubscriptionTransactionResponse,
    RevenueOneTimeCreate, RevenueOneTimeUpdate, RevenueOneTimeResponse
)

router = APIRouter(prefix="/api", tags=["subscriptions"])


# ==================== SUBSCRIPTIONS ====================

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    skip: int = 0,
    limit: int = 100,
    project_id: int = None,
    db: Session = Depends(get_db)
):
    """List all subscriptions."""
    query = db.query(Subscription)
    if project_id:
        query = query.filter(Subscription.project_id == project_id)
    subscriptions = query.offset(skip).limit(limit).all()
    return subscriptions


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Get a specific subscription by ID."""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.post("/projects/{project_id}/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    project_id: int,
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Create a new subscription for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_subscription = Subscription(**subscription.dict(), project_id=project_id)
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing subscription."""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    for key, value in subscription.dict(exclude_unset=True).items():
        setattr(db_subscription, key, value)
    
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@router.delete("/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Delete a subscription."""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db.delete(db_subscription)
    db.commit()
    return None


# ==================== SUBSCRIPTION TRANSACTIONS ====================

@router.get("/subscriptions/{subscription_id}/transactions", response_model=List[SubscriptionTransactionResponse])
async def list_subscription_transactions(subscription_id: int, db: Session = Depends(get_db)):
    """List all transactions for a subscription."""
    transactions = db.query(SubscriptionTransaction).filter(
        SubscriptionTransaction.subscription_id == subscription_id
    ).all()
    return transactions


@router.post("/subscriptions/{subscription_id}/transactions", response_model=SubscriptionTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription_transaction(
    subscription_id: int,
    transaction: SubscriptionTransactionCreate,
    db: Session = Depends(get_db)
):
    """Create a new transaction for a subscription."""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db_transaction = SubscriptionTransaction(**transaction.dict(), subscription_id=subscription_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.put("/transactions/{transaction_id}", response_model=SubscriptionTransactionResponse)
async def update_subscription_transaction(
    transaction_id: int,
    transaction: SubscriptionTransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update a subscription transaction."""
    db_transaction = db.query(SubscriptionTransaction).filter(SubscriptionTransaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    for key, value in transaction.dict(exclude_unset=True).items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Delete a subscription transaction."""
    db_transaction = db.query(SubscriptionTransaction).filter(SubscriptionTransaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(db_transaction)
    db.commit()
    return None


# ==================== REVENUE ONE-TIME ====================

@router.get("/revenue-one-time", response_model=List[RevenueOneTimeResponse])
async def list_revenue_one_time(
    skip: int = 0,
    limit: int = 100,
    project_id: int = None,
    db: Session = Depends(get_db)
):
    """List all one-time revenue entries."""
    query = db.query(RevenueOneTime)
    if project_id:
        query = query.filter(RevenueOneTime.project_id == project_id)
    revenue = query.offset(skip).limit(limit).all()
    return revenue


@router.get("/revenue-one-time/{revenue_id}", response_model=RevenueOneTimeResponse)
async def get_revenue_one_time(revenue_id: int, db: Session = Depends(get_db)):
    """Get a specific one-time revenue entry by ID."""
    revenue = db.query(RevenueOneTime).filter(RevenueOneTime.id == revenue_id).first()
    if not revenue:
        raise HTTPException(status_code=404, detail="Revenue entry not found")
    return revenue


@router.post("/projects/{project_id}/revenue-one-time", response_model=RevenueOneTimeResponse, status_code=status.HTTP_201_CREATED)
async def create_revenue_one_time(
    project_id: int,
    revenue: RevenueOneTimeCreate,
    db: Session = Depends(get_db)
):
    """Create a new one-time revenue entry for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_revenue = RevenueOneTime(**revenue.dict(), project_id=project_id)
    db.add(db_revenue)
    db.commit()
    db.refresh(db_revenue)
    return db_revenue


@router.put("/revenue-one-time/{revenue_id}", response_model=RevenueOneTimeResponse)
async def update_revenue_one_time(
    revenue_id: int,
    revenue: RevenueOneTimeUpdate,
    db: Session = Depends(get_db)
):
    """Update a one-time revenue entry."""
    db_revenue = db.query(RevenueOneTime).filter(RevenueOneTime.id == revenue_id).first()
    if not db_revenue:
        raise HTTPException(status_code=404, detail="Revenue entry not found")
    
    for key, value in revenue.dict(exclude_unset=True).items():
        setattr(db_revenue, key, value)
    
    db.commit()
    db.refresh(db_revenue)
    return db_revenue


@router.delete("/revenue-one-time/{revenue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_revenue_one_time(revenue_id: int, db: Session = Depends(get_db)):
    """Delete a one-time revenue entry."""
    db_revenue = db.query(RevenueOneTime).filter(RevenueOneTime.id == revenue_id).first()
    if not db_revenue:
        raise HTTPException(status_code=404, detail="Revenue entry not found")
    
    db.delete(db_revenue)
    db.commit()
    return None
