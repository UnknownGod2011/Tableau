"""
Foreign exchange API endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db

router = APIRouter()


@router.get("/exposures", response_model=List[dict])
async def get_fx_exposures(db: AsyncSession = Depends(get_db)):
    """Get all FX exposures"""
    return [{"message": "FX exposures endpoint - implementation pending"}]


@router.get("/exposures/{exposure_id}", response_model=dict)
async def get_fx_exposure(exposure_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific FX exposure"""
    return {"message": f"FX exposure {exposure_id} - implementation pending"}