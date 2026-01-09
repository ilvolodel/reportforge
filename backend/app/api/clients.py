"""Clients CRUD API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from ..database import get_db
from ..models.project import Client
from ..schemas.client import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all clients."""
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, db: Session = Depends(get_db)):
    """Get a specific client by ID."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client."""
    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client: ClientUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing client."""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    for key, value in client.dict(exclude_unset=True).items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client."""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(db_client)
    db.commit()
    return None
