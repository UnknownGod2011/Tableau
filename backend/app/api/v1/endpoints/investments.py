"""
Investments API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_investments(db: AsyncSession = Depends(get_db)):
    """Get all investments"""
    return [{"message": "Investments endpoint - implementation pending"}]


@router.get("/{investment_id}", response_model=dict)
async def get_investment(investment_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific investment"""
    return {"message": f"Investment {investment_id} - implementation pending"}