"""
Tests for AI integration and Agentforce service
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from app.services.agentforce import AgentforceService, ConversationManager
from app.models.ai import ConversationContext, ConversationTurn, AIInsight, InsightType


@pytest.mark.asyncio
async def test_conversation_manager_create_context(db_session):
    """Test creating a new conversation context"""
    
    manager = ConversationManager(db_session)
    
    context = await manager.get_or_create_context(
        session_id="test_session_123",
        user_id="test_user",
        entity_scope=["entity_1", "entity_2"]
    )
    
    assert context.session_id == "test_session_123"
    assert context.user_id == "test_user"
    assert context.entity_scope == ["entity_1", "entity_2"]
    assert context.total_interactions == 0
    assert context.user_preferences is not None


@pytest.mark.asyncio
async def test_conversation_manager_add_turn(db_session):
    """Test adding a conversation turn"""
    
    manager = ConversationManager(db_session)
    
    # Create context
    context = await manager.get_or_create_context(
        session_id="test_session_456",
        user_id="test_user"
    )
    
    # Add turn
    turn = await manager.add_turn(
        context=context,
        user_message="What's my cash optimization opportunity?",
        ai_response="Based on analysis, you have a $1.2M optimization opportunity.",
        processing_time_ms=1500,
        detected_intent="cash_optimization",
        extracted_entities={"analysis_type": "optimization"},
        data_sources_accessed=["cash_positions", "market_rates"]
    )
    
    assert turn.turn_number == 1
    assert turn.user_message == "What's my cash optimization opportunity?"
    assert turn.detected_intent == "cash_optimization"
    assert turn.processing_time_ms == 1500
    assert context.total_interactions == 1


@pytest.mark.asyncio
async def test_agentforce_service_mock_intent_analysis(db_session):
    """Test mock intent analysis"""
    
    service = AgentforceService(db_session)
    
    # Test cash optimization intent
    result = await service._mock_intent_analysis("What's my cash optimization opportunity?")
    assert result["intent"] == "cash_optimization"
    assert result["confidence"] > 0.5
    
    # Test risk analysis intent
    result = await service._mock_intent_analysis("Show me the portfolio risk analysis")
    assert result["intent"] == "risk_analysis"
    
    # Test general query
    result = await service._mock_intent_analysis("Hello, how are you?")
    assert result["intent"] == "general_query"


@pytest.mark.asyncio
async def test_agentforce_service_process_query(db_session):
    """Test processing a complete query"""
    
    service = AgentforceService(db_session)
    
    # Mock the analytics service methods
    with patch.object(service.analytics_service, 'get_cash_optimization_recommendations') as mock_analytics:
        mock_analytics.return_value = [
            {
                "description": "Move funds to higher-yield account",
                "financial_impact": 125000,
                "confidence": 0.9
            }
        ]
        
        result = await service.process_query(
            session_id="test_session_789",
            user_id="test_user",
            message="What's my current cash optimization opportunity?",
            entity_scope=["demo_entity"]
        )
        
        assert "response" in result
        assert "session_id" in result
        assert "confidence" in result
        assert result["intent"] == "cash_optimization"
        assert result["confidence"] > 0.5


@pytest.mark.asyncio
async def test_agentforce_service_handle_cash_optimization(db_session):
    """Test cash optimization query handling"""
    
    service = AgentforceService(db_session)
    
    # Create context
    context = await service.conversation_manager.get_or_create_context(
        session_id="test_session_cash",
        user_id="test_user",
        entity_scope=["demo_entity"]
    )
    
    # Mock analytics service
    with patch.object(service.analytics_service, 'get_cash_optimization_recommendations') as mock_analytics:
        mock_analytics.return_value = [
            {
                "description": "Optimize cash allocation for higher yields",
                "financial_impact": 250000,
                "risk_level": "low"
            }
        ]
        
        result = await service._handle_cash_optimization_query(
            entities={"entity_id": "demo_entity"},
            context=context
        )
        
        assert "response" in result
        assert "confidence" in result
        assert result["confidence"] > 0.8
        assert "250,000" in result["response"]


@pytest.mark.asyncio
async def test_agentforce_service_handle_risk_analysis(db_session):
    """Test risk analysis query handling"""
    
    service = AgentforceService(db_session)
    
    # Create context
    context = await service.conversation_manager.get_or_create_context(
        session_id="test_session_risk",
        user_id="test_user",
        entity_scope=["demo_entity"]
    )
    
    # Mock risk service
    with patch.object(service.risk_service, 'calculate_portfolio_risk') as mock_risk:
        mock_risk.return_value = {
            "var_95": 2450000,
            "credit_risk_score": 6.5,
            "fx_risk": 350000
        }
        
        result = await service._handle_risk_analysis_query(
            entities={"entity_id": "demo_entity"},
            context=context
        )
        
        assert "response" in result
        assert "confidence" in result
        assert result["confidence"] > 0.8
        assert "2,450,000" in result["response"]


@pytest.mark.asyncio
async def test_agentforce_service_generate_insight(db_session):
    """Test AI insight generation"""
    
    service = AgentforceService(db_session)
    
    # Test cash optimization insight
    insight = await service.generate_insight(
        entity_id="demo_entity",
        insight_type=InsightType.CASH_OPTIMIZATION,
        supporting_data={"optimization_amount": 150000}
    )
    
    assert insight is not None
    assert insight.insight_type == InsightType.CASH_OPTIMIZATION
    assert insight.financial_impact == 150000
    assert insight.confidence > 0.8
    assert "150,000" in insight.title


@pytest.mark.asyncio
async def test_agentforce_service_generate_risk_insight(db_session):
    """Test risk alert insight generation"""
    
    service = AgentforceService(db_session)
    
    # Test risk alert insight
    insight = await service.generate_insight(
        entity_id="demo_entity",
        insight_type=InsightType.RISK_ALERT,
        supporting_data={
            "risk_level": "high",
            "var_amount": 5000000
        }
    )
    
    assert insight is not None
    assert insight.insight_type == InsightType.RISK_ALERT
    assert insight.risk_impact == "high"
    assert insight.urgency_score == 0.8


@pytest.mark.asyncio
async def test_conversation_history_retrieval(db_session):
    """Test retrieving conversation history"""
    
    manager = ConversationManager(db_session)
    service = AgentforceService(db_session)
    
    # Create context and add multiple turns
    context = await manager.get_or_create_context(
        session_id="test_history_session",
        user_id="test_user"
    )
    
    # Add several turns
    for i in range(3):
        await manager.add_turn(
            context=context,
            user_message=f"Test message {i+1}",
            ai_response=f"Test response {i+1}",
            detected_intent="general_query"
        )
    
    # Get recent history
    history = await service._get_recent_history(context, limit=5)
    
    assert len(history) == 6  # 3 user + 3 assistant messages
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert "Test message 1" in history[0]["content"]


def test_agentforce_service_initialization(db_session):
    """Test AgentforceService initialization"""
    
    service = AgentforceService(db_session)
    
    assert service.db == db_session
    assert service.conversation_manager is not None
    assert service.analytics_service is not None
    assert service.risk_service is not None
    assert service.base_url is not None
    assert service.timeout is not None


@pytest.mark.asyncio
async def test_error_handling_in_process_query(db_session):
    """Test error handling in query processing"""
    
    service = AgentforceService(db_session)
    
    # Mock analytics service to raise an exception
    with patch.object(service.analytics_service, 'get_cash_optimization_recommendations') as mock_analytics:
        mock_analytics.side_effect = Exception("Database connection failed")
        
        result = await service.process_query(
            session_id="test_error_session",
            user_id="test_user",
            message="What's my cash optimization opportunity?",
            entity_scope=["demo_entity"]
        )
        
        assert "response" in result
        assert "error" in result
        assert result["confidence"] == 0.0
        assert "error" in result["response"].lower()


@pytest.mark.asyncio
async def test_general_query_handling(db_session):
    """Test general query handling"""
    
    service = AgentforceService(db_session)
    
    context = await service.conversation_manager.get_or_create_context(
        session_id="test_general_session",
        user_id="test_user"
    )
    
    # Test help query
    result = await service._handle_general_query(
        message="What can you help me with?",
        entities={},
        context=context
    )
    
    assert "response" in result
    assert "confidence" in result
    assert "cash management" in result["response"].lower()
    assert "risk analysis" in result["response"].lower()


if __name__ == "__main__":
    pytest.main([__file__])