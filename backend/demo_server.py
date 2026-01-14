"""
TreasuryIQ Demo Server - Simplified version for local demo
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import random

# Create FastAPI application
app = FastAPI(
    title="TreasuryIQ Demo API",
    description="AI-Powered Corporate Treasury Management Platform - Demo Mode",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo data
DEMO_DATA = {
    "portfolio_value": 500660000,  # $500.66M
    "cash_positions": 300000000,   # $300M
    "investments": 200660000,      # $200.66M
    "entities": [
        {"name": "GlobalTech US", "value": 120000000, "currency": "USD"},
        {"name": "GlobalTech Europe", "value": 75000000, "currency": "EUR"},
        {"name": "GlobalTech APAC", "value": 60000000, "currency": "SGD"},
        {"name": "GlobalTech Canada", "value": 30000000, "currency": "CAD"},
        {"name": "GlobalTech Japan", "value": 15000000, "currency": "JPY"},
    ]
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TreasuryIQ Demo - AI-Powered Corporate Treasury Management",
        "version": "1.0.0",
        "mode": "demo",
        "docs": "/docs",
        "portfolio_value": "$500.66M",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "TreasuryIQ Demo API",
            "version": "1.0.0",
            "mode": "demo",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/api/v1/treasury/overview")
async def get_treasury_overview():
    """Get treasury portfolio overview"""
    return {
        "total_portfolio_value": DEMO_DATA["portfolio_value"],
        "cash_positions": DEMO_DATA["cash_positions"],
        "investments": DEMO_DATA["investments"],
        "entities": DEMO_DATA["entities"],
        "performance": {
            "daily_change": random.uniform(-0.5, 1.2),
            "weekly_change": random.uniform(-2.1, 3.5),
            "monthly_change": random.uniform(-5.2, 8.7)
        },
        "risk_metrics": {
            "var_95": random.uniform(2.1, 4.8),
            "credit_exposure": random.uniform(15.2, 25.8),
            "fx_exposure": random.uniform(8.5, 15.2)
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/analytics/cash-optimization")
async def get_cash_optimization():
    """Get cash optimization recommendations"""
    return {
        "recommendations": [
            {
                "type": "cash_placement",
                "description": "Move $50M from low-yield checking to treasury bills",
                "potential_savings": 1250000,  # $1.25M annually
                "confidence": 0.92,
                "priority": "high"
            },
            {
                "type": "fx_hedging", 
                "description": "Hedge EUR exposure with forward contracts",
                "potential_savings": 850000,
                "confidence": 0.87,
                "priority": "medium"
            }
        ],
        "total_opportunity": 2100000,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/risk/dashboard")
async def get_risk_dashboard():
    """Get risk dashboard data"""
    return {
        "var_metrics": {
            "var_95_1day": random.uniform(2.1, 4.8),
            "var_99_1day": random.uniform(3.2, 6.5),
            "expected_shortfall": random.uniform(4.5, 8.2)
        },
        "credit_risk": {
            "total_exposure": random.uniform(45.2, 65.8),
            "high_risk_counterparties": random.randint(2, 8),
            "avg_credit_rating": "A-"
        },
        "fx_risk": {
            "total_exposure": random.uniform(25.5, 45.2),
            "major_currencies": ["EUR", "GBP", "JPY", "SGD"],
            "hedged_percentage": random.uniform(65.2, 85.7)
        },
        "alerts": [
            {
                "type": "credit_rating_change",
                "message": "Supplier XYZ credit rating downgraded to BBB+",
                "severity": "medium",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/ai/chat")
async def ai_chat_demo():
    """Demo AI chat responses"""
    responses = [
        "Based on current market conditions, I recommend optimizing your cash allocation to capture higher yields.",
        "Your EUR exposure has increased 15% this week. Consider hedging strategies to mitigate FX risk.",
        "Treasury bill rates are attractive at 5.2%. Moving $50M from checking could generate $2.6M annually.",
        "Credit spreads are widening. Review counterparty exposure and consider diversification."
    ]
    return {
        "response": random.choice(responses),
        "confidence": random.uniform(0.85, 0.98),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/data-sources/demo/sample-data")
async def get_sample_treasury_data():
    """Get sample treasury data for demo purposes"""
    sample_data = {
        'treasury_balances': {
            'operating_cash_balance': 450000000000,  # $450B
            'treasury_general_account': 420000000000,  # $420B
            'federal_reserve_account': 30000000000,   # $30B
            'last_updated': datetime.now().isoformat()
        },
        'interest_rates': {
            'treasury_3m': 5.25,
            'treasury_6m': 5.35,
            'treasury_1y': 5.15,
            'treasury_2y': 4.95,
            'treasury_5y': 4.75,
            'treasury_10y': 4.65,
            'treasury_30y': 4.85,
            'fed_funds': 5.50
        },
        'exchange_rates': {
            'EUR': 0.92,
            'GBP': 0.79,
            'JPY': 148.50,
            'SGD': 1.34,
            'CAD': 1.36,
            'CHF': 0.88,
            'AUD': 1.52
        },
        'economic_indicators': {
            'gdp_growth': 2.4,
            'inflation_rate': 3.2,
            'unemployment_rate': 3.7,
            'consumer_confidence': 102.3
        },
        'market_volatility': {
            'vix': 18.5,
            'treasury_volatility': 12.3,
            'fx_volatility': 8.7
        },
        'timestamp': datetime.now().isoformat(),
        'source': 'demo_data',
        'status': 'success'
    }
    return sample_data

@app.get("/api/v1/tableau/health")
async def tableau_health():
    """Enhanced Tableau integration health check with detailed API status"""
    return {
        "status": "connected",
        "server": "prod-useast-b.online.tableau.com",
        "site_id": "treasuryiq-demo",
        "workbooks": 5,
        "views": 23,
        "api_version": "3.21",
        "features": {
            "rest_api": True,
            "embedding_api": True,
            "webhooks": True,
            "extensions": True,
            "data_sources": 8,
            "real_time_refresh": True
        },
        "last_refresh": datetime.now().isoformat(),
        "performance": {
            "avg_response_time": "1.2s",
            "uptime": "99.9%",
            "data_freshness": "< 5 minutes"
        }
    }

@app.get("/api/v1/tableau/workbooks")
async def get_tableau_workbooks():
    """Get list of Tableau workbooks for treasury analysis"""
    return {
        "workbooks": [
            {
                "id": "wb-001",
                "name": "Treasury Cash Flow Analysis",
                "description": "Real-time cash position tracking and forecasting",
                "views": ["Cash Dashboard", "Flow Forecast", "Liquidity Analysis"],
                "last_updated": datetime.now().isoformat(),
                "data_sources": ["Treasury API", "Market Data", "Bank Feeds"]
            },
            {
                "id": "wb-002", 
                "name": "Risk Management Dashboard",
                "description": "VaR calculations, credit risk, and FX exposure monitoring",
                "views": ["Risk Overview", "VaR Analysis", "Credit Monitoring"],
                "last_updated": datetime.now().isoformat(),
                "data_sources": ["Risk Engine", "Market Data", "Credit Ratings"]
            },
            {
                "id": "wb-003",
                "name": "AI Treasury Insights",
                "description": "Machine learning predictions and optimization recommendations",
                "views": ["AI Recommendations", "Predictive Models", "Optimization"],
                "last_updated": datetime.now().isoformat(),
                "data_sources": ["AI Engine", "Historical Data", "Market Indicators"]
            }
        ],
        "total_count": 3,
        "api_usage": {
            "requests_today": 1247,
            "rate_limit": "100/hour",
            "remaining": 87
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/tableau/views/{view_id}")
async def get_tableau_view(view_id: str):
    """Get specific Tableau view details"""
    views = {
        "cash-dashboard": {
            "id": "cash-dashboard",
            "name": "Treasury Cash Dashboard",
            "workbook": "Treasury Cash Flow Analysis", 
            "url": f"https://prod-useast-b.online.tableau.com/views/TreasuryCashFlow/CashDashboard",
            "embed_code": "<tableau-viz id='tableau-viz' src='https://prod-useast-b.online.tableau.com/views/TreasuryCashFlow/CashDashboard' width='100%' height='600' hide-tabs toolbar='bottom'></tableau-viz>",
            "filters": ["Entity", "Currency", "Date Range"],
            "parameters": ["Forecast Period", "Risk Threshold"],
            "data_freshness": "2 minutes ago",
            "performance": "1.1s avg load time"
        },
        "risk-overview": {
            "id": "risk-overview", 
            "name": "Risk Management Overview",
            "workbook": "Risk Management Dashboard",
            "url": f"https://prod-useast-b.online.tableau.com/views/RiskManagement/Overview",
            "embed_code": "<tableau-viz id='risk-viz' src='https://prod-useast-b.online.tableau.com/views/RiskManagement/Overview' width='100%' height='600' hide-tabs toolbar='bottom'></tableau-viz>",
            "filters": ["Risk Type", "Entity", "Time Period"],
            "parameters": ["Confidence Level", "VaR Method"],
            "data_freshness": "1 minute ago", 
            "performance": "0.9s avg load time"
        }
    }
    
    view = views.get(view_id, {
        "id": view_id,
        "name": f"Treasury View {view_id}",
        "status": "available",
        "embed_ready": True
    })
    
    return view

if __name__ == "__main__":
    print("🚀 Starting TreasuryIQ Demo Server...")
    print("📊 Portfolio: $500.66M GlobalTech Industries")
    print("🌐 Frontend: http://localhost:3000")
    print("📡 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "demo_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )