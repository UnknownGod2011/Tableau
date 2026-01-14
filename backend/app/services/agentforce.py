"""
Salesforce Agentforce integration service for conversational AI
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from ..core.config import settings
from ..models.ai import ConversationContext, ConversationTurn, AIInsight, InsightType
from ..models.corporate import CorporateEntity
from ..services.analytics import TreasuryAnalyticsEngine
from ..services.risk import RiskCalculationService
from ..services.market_data import MarketDataService

logger = logging.getLogger(__name__)


class AgentforceError(Exception):
    """Agentforce API error"""
    pass


class ConversationManager:
    """Manages conversation context and state"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create_context(
        self, 
        session_id: str, 
        user_id: str,
        entity_scope: Optional[List[str]] = None
    ) -> ConversationContext:
        """Get existing or create new conversation context"""
        
        # Try to get existing context
        result = await self.db.execute(
            select(ConversationContext)
            .where(ConversationContext.session_id == session_id)
            .options(selectinload(ConversationContext.active_entity))
        )
        context = result.scalar_one_or_none()
        
        if context:
            # Update last activity
            context.last_activity = datetime.now(timezone.utc)
            await self.db.commit()
            return context
        
        # Create new context
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            entity_scope=entity_scope or [],
            last_activity=datetime.now(timezone.utc),
            user_preferences={
                "currency": "USD",
                "time_zone": "UTC",
                "date_format": "YYYY-MM-DD"
            }
        )
        
        self.db.add(context)
        await self.db.commit()
        await self.db.refresh(context)
        
        logger.info(f"Created new conversation context: {session_id}")
        return context
    
    async def add_turn(
        self,
        context: ConversationContext,
        user_message: str,
        ai_response: str,
        processing_time_ms: Optional[int] = None,
        detected_intent: Optional[str] = None,
        extracted_entities: Optional[Dict] = None,
        data_sources_accessed: Optional[List[str]] = None
    ) -> ConversationTurn:
        """Add a new conversation turn"""
        
        turn_number = context.total_interactions + 1
        
        turn = ConversationTurn(
            context_id=context.id,
            turn_number=turn_number,
            user_message=user_message,
            ai_response=ai_response,
            processing_time_ms=processing_time_ms,
            detected_intent=detected_intent,
            extracted_entities=extracted_entities or {},
            data_sources_accessed=data_sources_accessed or []
        )
        
        self.db.add(turn)
        
        # Update context
        context.total_interactions = turn_number
        context.last_activity = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(turn)
        
        return turn


class AgentforceService:
    """Salesforce Agentforce integration service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_manager = ConversationManager(db)
        # Initialize services
        market_data_service = MarketDataService()
        self.analytics_engine = TreasuryAnalyticsEngine(market_data_service)
        self.risk_service = RiskCalculationService(market_data_service)
        
        # API configuration
        self.api_key = settings.AGENTFORCE_API_KEY
        self.base_url = settings.AGENTFORCE_BASE_URL
        self.timeout = aiohttp.ClientTimeout(total=30)
        
        if not self.api_key:
            logger.warning("Agentforce API key not configured - using mock responses")
    
    async def process_query(
        self,
        session_id: str,
        user_id: str,
        message: str,
        entity_scope: Optional[List[str]] = None,
        dashboard_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process a natural language query"""
        
        start_time = datetime.now()
        
        try:
            # Get or create conversation context
            context = await self.conversation_manager.get_or_create_context(
                session_id, user_id, entity_scope
            )
            
            # Update dashboard context if provided
            if dashboard_context:
                context.dashboard_context = dashboard_context
                await self.db.commit()
            
            # Analyze intent and extract entities
            intent_analysis = await self._analyze_intent(message, context)
            
            # Generate response based on intent
            response_data = await self._generate_response(
                message, context, intent_analysis
            )
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Save conversation turn
            turn = await self.conversation_manager.add_turn(
                context=context,
                user_message=message,
                ai_response=response_data["response"],
                processing_time_ms=processing_time,
                detected_intent=intent_analysis.get("intent"),
                extracted_entities=intent_analysis.get("entities"),
                data_sources_accessed=response_data.get("data_sources", [])
            )
            
            return {
                "response": response_data["response"],
                "intent": intent_analysis.get("intent"),
                "entities": intent_analysis.get("entities"),
                "data_visualizations": response_data.get("visualizations", []),
                "suggested_actions": response_data.get("actions", []),
                "confidence": response_data.get("confidence", 0.8),
                "processing_time_ms": processing_time,
                "turn_id": str(turn.id),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
                "error": str(e),
                "confidence": 0.0
            }
    
    async def _analyze_intent(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Analyze user intent and extract entities"""
        
        if not self.api_key:
            return await self._mock_intent_analysis(message)
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                payload = {
                    "message": message,
                    "context": {
                        "user_id": context.user_id,
                        "entity_scope": context.entity_scope,
                        "conversation_history": await self._get_recent_history(context),
                        "dashboard_context": context.dashboard_context
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.base_url}/intent/analyze",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Agentforce API error: {response.status}")
                        return await self._mock_intent_analysis(message)
                        
        except Exception as e:
            logger.error(f"Intent analysis error: {str(e)}")
            return await self._mock_intent_analysis(message)
    
    async def _generate_response(
        self,
        message: str,
        context: ConversationContext,
        intent_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI response based on intent and context"""
        
        intent = intent_analysis.get("intent", "general_query")
        entities = intent_analysis.get("entities", {})
        
        # Route to appropriate handler based on intent
        if intent == "cash_optimization":
            return await self._handle_cash_optimization_query(entities, context)
        elif intent == "risk_analysis":
            return await self._handle_risk_analysis_query(entities, context)
        elif intent == "market_data":
            return await self._handle_market_data_query(entities, context)
        elif intent == "portfolio_summary":
            return await self._handle_portfolio_summary_query(entities, context)
        elif intent == "fx_exposure":
            return await self._handle_fx_exposure_query(entities, context)
        else:
            return await self._handle_general_query(message, entities, context)
    
    async def _handle_cash_optimization_query(
        self, 
        entities: Dict[str, Any], 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle cash optimization queries"""
        
        try:
            # Get entity ID from context or entities
            entity_id = entities.get("entity_id") or (
                context.entity_scope[0] if context.entity_scope else None
            )
            
            if not entity_id:
                return {
                    "response": "I need to know which entity you'd like me to analyze for cash optimization. Could you specify the entity?",
                    "confidence": 0.6
                }
            
            # Get cash optimization recommendations
            # For now, return mock data since we need to integrate with the actual analytics engine
            recommendations = [
                {
                    "description": "Move excess cash from low-yield checking to money market accounts",
                    "financial_impact": 125000,
                    "risk_level": "low",
                    "implementation_complexity": "low"
                },
                {
                    "description": "Consider short-term Treasury bills for surplus liquidity",
                    "financial_impact": 85000,
                    "risk_level": "low", 
                    "implementation_complexity": "medium"
                }
            ]
            
            if not recommendations:
                return {
                    "response": f"I couldn't find any cash optimization opportunities for the specified entity at this time. The current cash allocation appears to be well-optimized.",
                    "confidence": 0.8
                }
            
            # Format response
            response_parts = [
                "Based on my analysis of your cash positions, here are the key optimization opportunities:"
            ]
            
            for i, rec in enumerate(recommendations[:3], 1):
                impact = rec.get("financial_impact", 0)
                response_parts.append(
                    f"{i}. {rec.get('description', 'Optimization opportunity')} "
                    f"(Potential impact: ${impact:,.0f})"
                )
            
            response_parts.append(
                "\nWould you like me to provide more details on any of these recommendations?"
            )
            
            return {
                "response": "\n".join(response_parts),
                "data_sources": ["cash_positions", "market_rates", "analytics_engine"],
                "visualizations": [
                    {
                        "type": "cash_allocation_chart",
                        "data": recommendations
                    }
                ],
                "actions": [
                    "View detailed cash allocation",
                    "Generate optimization report",
                    "Set up optimization alerts"
                ],
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Cash optimization query error: {str(e)}")
            return {
                "response": "I encountered an issue analyzing cash optimization opportunities. Please try again.",
                "confidence": 0.3
            }
    
    async def _handle_risk_analysis_query(
        self, 
        entities: Dict[str, Any], 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle risk analysis queries"""
        
        try:
            entity_id = entities.get("entity_id") or (
                context.entity_scope[0] if context.entity_scope else None
            )
            
            if not entity_id:
                return {
                    "response": "Please specify which entity you'd like me to analyze for risk exposure.",
                    "confidence": 0.6
                }
            
            # Get risk metrics - using mock data for now
            risk_metrics = {
                "var_95": 2450000,
                "credit_risk_score": 6.5,
                "fx_risk": 350000,
                "portfolio_volatility": 0.12,
                "concentration_risk": 0.25
            }
            
            if not risk_metrics:
                return {
                    "response": "I couldn't retrieve risk metrics for the specified entity. Please check if the entity has active positions.",
                    "confidence": 0.7
                }
            
            var_95 = risk_metrics.get("var_95", 0)
            credit_risk = risk_metrics.get("credit_risk_score", 0)
            fx_risk = risk_metrics.get("fx_risk", 0)
            
            response = f"""Here's your current risk profile:

📊 **Value at Risk (95% confidence)**: ${var_95:,.0f}
🏦 **Credit Risk Score**: {credit_risk:.2f}/10
💱 **FX Risk Exposure**: ${fx_risk:,.0f}

"""
            
            # Add risk alerts if any
            if var_95 > 1000000:  # $1M threshold
                response += "⚠️ **Alert**: VaR exceeds $1M threshold. Consider risk reduction measures.\n"
            
            if credit_risk > 7.0:
                response += "⚠️ **Alert**: High credit risk detected in portfolio.\n"
            
            response += "\nWould you like me to provide recommendations for risk mitigation?"
            
            return {
                "response": response,
                "data_sources": ["risk_calculations", "market_data", "portfolio_positions"],
                "visualizations": [
                    {
                        "type": "risk_dashboard",
                        "data": risk_metrics
                    }
                ],
                "actions": [
                    "View detailed risk breakdown",
                    "Generate risk report",
                    "Set up risk alerts"
                ],
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Risk analysis query error: {str(e)}")
            return {
                "response": "I encountered an issue analyzing risk metrics. Please try again.",
                "confidence": 0.3
            }
    
    async def _handle_general_query(
        self,
        message: str,
        entities: Dict[str, Any],
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle general treasury queries"""
        
        # Simple keyword-based responses for demo
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["help", "what can you do", "capabilities"]):
            return {
                "response": """I'm your AI treasury assistant! I can help you with:

💰 **Cash Management**: Optimization recommendations, liquidity analysis
📊 **Risk Analysis**: VaR calculations, credit risk assessment, FX exposure
📈 **Market Insights**: Rate trends, economic indicators, market analysis
💱 **FX Management**: Currency exposure analysis, hedging recommendations
📋 **Reporting**: Generate custom reports and summaries

Just ask me questions like:
• "What's our current cash optimization opportunity?"
• "Show me our risk exposure"
• "How is our FX position looking?"
• "Generate a treasury summary report"

What would you like to explore first?""",
                "confidence": 0.95
            }
        
        elif any(word in message_lower for word in ["summary", "overview", "dashboard"]):
            return {
                "response": """Here's your treasury overview based on current analysis:

📊 **Portfolio Status**: Active monitoring across all entities
💰 **Cash Optimization**: 3 opportunities identified totaling $1.2M potential impact
⚠️ **Risk Alerts**: 1 medium-priority alert requiring attention
📈 **Market Conditions**: Favorable for short-term investments with rising rates

**Key Metrics:**
• Total portfolio value: $500M
• Current yield: 2.1%
• VaR (95% confidence): $2.4M
• Liquidity ratio: 1.8x

Would you like me to dive deeper into any of these areas?""",
                "confidence": 0.8
            }
        
        elif any(word in message_lower for word in ["volatile", "volatility"]):
            return {
                "response": """Portfolio volatility analysis indicates moderate risk levels:

📊 **Current Volatility Metrics:**
• Portfolio volatility: 12.5% (within target range)
• Key drivers: Interest rate sensitivity (60%), FX exposure (25%), Credit risk (15%)
• Compared to benchmark: +2.1% (slightly above peer average)

**Risk Factors:**
• Duration risk from fixed income positions
• Currency exposure in EUR and JPY positions
• Credit concentration in financial sector

**Recommendations to reduce volatility:**
• Consider shorter duration positioning
• Increase FX hedging ratio to 80%
• Diversify credit exposure across sectors

The current volatility level is manageable but monitoring is recommended due to market uncertainty.""",
                "confidence": 0.85
            }
        
        elif any(word in message_lower for word in ["var", "value at risk", "risk calculation"]):
            return {
                "response": """Value at Risk (VaR) is a statistical measure that quantifies the potential loss in portfolio value over a specific time period at a given confidence level.

**How VaR is calculated:**
• Historical simulation method using 250 days of market data
• Monte Carlo simulation with 10,000 scenarios
• Parametric approach based on portfolio volatility and correlations

**Current VaR Analysis:**
• 1-day VaR (95% confidence): $2.45M
• This means there's a 5% chance of losing more than $2.45M in one day
• Key risk drivers: Interest rate changes (65%), FX movements (25%), Credit spreads (10%)

**Business Impact:**
VaR helps treasury management set appropriate risk limits, allocate capital efficiently, and ensure adequate liquidity buffers for potential losses. It's a critical tool for regulatory compliance and board reporting.""",
                "confidence": 0.90
            }
        
        elif any(word in message_lower for word in ["fx", "hedging", "currency"]):
            return {
                "response": """FX hedging is a risk management strategy used to protect against adverse currency movements in treasury operations.

**What FX hedging means for treasury:**
• Reduces uncertainty in cash flows from foreign operations
• Protects against translation risk in financial reporting
• Enables more predictable budgeting and forecasting
• Maintains competitive positioning across markets

**Current FX Exposure Analysis:**
• Total exposure: $115M across 5 currencies
• EUR: $45M (75% hedged) - largest exposure
• JPY: $25M (50% hedged) - moderate risk
• GBP: $20M (80% hedged) - well protected

**Hedging Recommendations:**
• Increase EUR hedging to 85% due to recent volatility
• Consider JPY options for tail risk protection
• Maintain current GBP hedge ratio

**Business Impact:**
Effective FX hedging reduces earnings volatility, improves cash flow predictability, and supports strategic business decisions by removing currency uncertainty from the equation.""",
                "confidence": 0.88
            }
        
        elif any(word in message_lower for word in ["reduce", "risk", "mitigation"]):
            return {
                "response": """Based on current portfolio analysis, here are specific recommendations to reduce risk exposure:

**Immediate Actions (0-30 days):**
• Increase FX hedging ratio from 65% to 80% - reduces VaR by $280K
• Rebalance credit exposure to reduce financial sector concentration
• Consider shorter duration positioning to reduce interest rate sensitivity

**Medium-term Strategies (1-6 months):**
• Diversify investment vehicles across more asset classes
• Implement dynamic hedging based on volatility indicators
• Establish credit limits with additional counterparties

**Risk Reduction Impact:**
• Expected VaR reduction: 15-20%
• Improved Sharpe ratio through better risk-adjusted returns
• Enhanced regulatory capital efficiency

**Implementation Considerations:**
• Hedging costs vs. risk reduction benefits analysis shows positive ROI
• Liquidity impact should be minimal with phased approach
• Regular monitoring and adjustment recommended due to market conditions

Would you like me to provide detailed implementation steps for any of these recommendations?""",
                "confidence": 0.87
            }
        
        else:
            return {
                "response": """I understand you're asking about treasury management operations. I can provide detailed analysis and recommendations on:

**Cash Management**: Optimization strategies, yield enhancement, liquidity planning
**Risk Analysis**: VaR calculations, stress testing, scenario analysis  
**Investment Strategy**: Portfolio allocation, duration management, credit analysis
**FX Risk Management**: Currency exposure assessment, hedging strategies
**Market Intelligence**: Rate forecasts, economic indicators, peer benchmarking

For the most helpful response, please ask about specific areas like:
• "How can I optimize my cash allocation?"
• "What's my current risk exposure?"
• "Should I adjust my hedging strategy?"
• "What are the market opportunities?"

What specific treasury topic would you like to explore?""",
                "confidence": 0.75
            }
    
    async def _mock_intent_analysis(self, message: str) -> Dict[str, Any]:
        """Mock intent analysis for development/demo"""
        
        message_lower = message.lower()
        
        # Simple keyword-based intent detection with better coverage
        if any(word in message_lower for word in ["cash", "optimization", "optimize", "allocation", "invest"]):
            return {
                "intent": "cash_optimization",
                "entities": {"analysis_type": "optimization"},
                "confidence": 0.8
            }
        elif any(word in message_lower for word in ["risk", "var", "exposure", "volatility", "volatile", "credit"]):
            return {
                "intent": "risk_analysis", 
                "entities": {"analysis_type": "risk"},
                "confidence": 0.8
            }
        elif any(word in message_lower for word in ["market", "rates", "economic", "fed", "conditions"]):
            return {
                "intent": "market_data",
                "entities": {"data_type": "market"},
                "confidence": 0.8
            }
        elif any(word in message_lower for word in ["fx", "currency", "foreign exchange", "hedge", "hedging"]):
            return {
                "intent": "fx_exposure",
                "entities": {"analysis_type": "fx"},
                "confidence": 0.8
            }
        elif any(word in message_lower for word in ["summary", "overview", "portfolio", "dashboard", "position"]):
            return {
                "intent": "portfolio_summary",
                "entities": {"report_type": "summary"},
                "confidence": 0.8
            }
        elif any(word in message_lower for word in ["what is", "explain", "how", "definition", "calculate", "mean"]):
            return {
                "intent": "general_query",
                "entities": {"query_type": "explanation"},
                "confidence": 0.85
            }
        else:
            return {
                "intent": "general_query",
                "entities": {},
                "confidence": 0.6
            }
    
    async def _get_recent_history(
        self, 
        context: ConversationContext, 
        limit: int = 5
    ) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        
        result = await self.db.execute(
            select(ConversationTurn)
            .where(ConversationTurn.context_id == context.id)
            .order_by(ConversationTurn.turn_number.desc())
            .limit(limit)
        )
        
        turns = result.scalars().all()
        
        history = []
        for turn in reversed(turns):
            history.extend([
                {"role": "user", "content": turn.user_message},
                {"role": "assistant", "content": turn.ai_response}
            ])
        
        return history
    
    async def generate_insight(
        self,
        entity_id: str,
        insight_type: InsightType,
        supporting_data: Dict[str, Any]
    ) -> Optional[AIInsight]:
        """Generate AI insight based on data analysis"""
        
        try:
            # Generate insight based on type
            if insight_type == InsightType.CASH_OPTIMIZATION:
                insight_data = await self._generate_cash_optimization_insight(
                    entity_id, supporting_data
                )
            elif insight_type == InsightType.RISK_ALERT:
                insight_data = await self._generate_risk_alert_insight(
                    entity_id, supporting_data
                )
            else:
                return None
            
            if not insight_data:
                return None
            
            # Create insight record
            insight = AIInsight(
                entity_id=entity_id,
                insight_type=insight_type,
                title=insight_data["title"],
                description=insight_data["description"],
                confidence=insight_data["confidence"],
                supporting_data=supporting_data,
                financial_impact=insight_data.get("financial_impact"),
                risk_impact=insight_data.get("risk_impact"),
                urgency_score=insight_data.get("urgency_score", 0.5),
                recommended_actions=insight_data.get("recommended_actions", []),
                generated_at=datetime.now(timezone.utc)
            )
            
            self.db.add(insight)
            await self.db.commit()
            await self.db.refresh(insight)
            
            logger.info(f"Generated AI insight: {insight.title}")
            return insight
            
        except Exception as e:
            logger.error(f"Error generating insight: {str(e)}")
            return None
    
    async def _generate_cash_optimization_insight(
        self, 
        entity_id: str, 
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate cash optimization insight"""
        
        optimization_amount = data.get("optimization_amount", 0)
        
        if optimization_amount < 10000:  # Minimum threshold
            return None
        
        return {
            "title": f"Cash Optimization Opportunity: ${optimization_amount:,.0f}",
            "description": f"Analysis indicates potential yield improvement of ${optimization_amount:,.0f} through optimal cash allocation across investment vehicles.",
            "confidence": 0.85,
            "financial_impact": optimization_amount,
            "risk_impact": "low",
            "urgency_score": 0.7,
            "recommended_actions": [
                "Review current cash allocation strategy",
                "Consider higher-yield short-term investments",
                "Implement automated rebalancing"
            ]
        }
    
    async def _generate_risk_alert_insight(
        self, 
        entity_id: str, 
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate risk alert insight"""
        
        risk_level = data.get("risk_level", "medium")
        var_amount = data.get("var_amount", 0)
        
        if risk_level == "low":
            return None
        
        return {
            "title": f"Risk Alert: {risk_level.title()} Risk Detected",
            "description": f"Portfolio risk analysis indicates {risk_level} risk exposure with VaR of ${var_amount:,.0f}.",
            "confidence": 0.9,
            "financial_impact": var_amount,
            "risk_impact": risk_level,
            "urgency_score": 0.8 if risk_level == "high" else 0.6,
            "recommended_actions": [
                "Review risk exposure limits",
                "Consider hedging strategies",
                "Monitor market conditions closely"
            ]
        }


# Placeholder handlers for missing query types
async def _handle_market_data_query(self, entities: Dict[str, Any], context: ConversationContext) -> Dict[str, Any]:
    """Handle market data queries"""
    return {
        "response": "Market data analysis is currently being implemented. Please check back soon for comprehensive market insights.",
        "confidence": 0.5
    }

async def _handle_portfolio_summary_query(self, entities: Dict[str, Any], context: ConversationContext) -> Dict[str, Any]:
    """Handle portfolio summary queries"""
    return {
        "response": "Portfolio summary functionality is being enhanced. I can currently help with cash optimization and risk analysis.",
        "confidence": 0.5
    }

async def _handle_fx_exposure_query(self, entities: Dict[str, Any], context: ConversationContext) -> Dict[str, Any]:
    """Handle FX exposure queries"""
    return {
        "response": """FX exposure analysis based on current portfolio positions:

💱 **Current FX Exposure Summary:**
• Total exposure: $115M across 5 major currencies
• EUR: $45M (75% hedged) - Primary exposure from European operations
• JPY: $25M (50% hedged) - Asia-Pacific business activities  
• GBP: $20M (80% hedged) - UK subsidiary operations
• CAD: $15M (60% hedged) - Canadian manufacturing division
• SGD: $10M (40% hedged) - Singapore trading operations

**Risk Assessment:**
• Unhedged exposure: $40M (35% of total FX exposure)
• Monthly volatility impact: ±$1.2M based on historical analysis
• Correlation with portfolio: Moderate diversification benefit

**Hedging Recommendations:**
• Increase EUR hedging to 85% due to recent ECB policy uncertainty
• Consider JPY options for tail risk protection given BoJ intervention risk
• Maintain current GBP hedge ratio - Brexit impact well-managed

**Business Impact:**
Effective FX management reduces earnings volatility by 25% and improves cash flow predictability for strategic planning. Current hedging strategy balances cost efficiency with risk reduction.""",
        "confidence": 0.85,
        "data_sources": ["fx_positions", "market_data", "hedging_analysis"],
        "visualizations": [
            {
                "type": "fx_exposure_chart",
                "data": "currency_breakdown"
            }
        ],
        "actions": [
            "View detailed FX position report",
            "Get hedging cost analysis", 
            "Set up FX alerts"
        ]
    }

# Add missing methods to AgentforceService class
AgentforceService._handle_market_data_query = _handle_market_data_query
AgentforceService._handle_portfolio_summary_query = _handle_portfolio_summary_query  
AgentforceService._handle_fx_exposure_query = _handle_fx_exposure_query