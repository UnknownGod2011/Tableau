"""
API v1 router
"""

from fastapi import APIRouter

from .endpoints import entities, cash, investments, fx, risk, recommendations, ai, market_data, analytics, predictive, tableau

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(cash.router, prefix="/cash", tags=["cash"])
api_router.include_router(investments.router, prefix="/investments", tags=["investments"])
api_router.include_router(fx.router, prefix="/fx", tags=["foreign-exchange"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(predictive.router, prefix="/predictive", tags=["predictive-analytics"])
api_router.include_router(tableau.router, prefix="/tableau", tags=["tableau"])