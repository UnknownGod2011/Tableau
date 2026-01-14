"""
Cash positions API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_cash_positions(db: AsyncSession = Depends(get_db)):
    """Get all cash positions"""
    return [{"message": "Cash positions endpoint - implementation pending"}]


@router.get("/{position_id}", response_model=dict)
async def get_cash_position(position_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific cash position"""
    return {"message": f"Cash position {position_id} - implementation pending"}