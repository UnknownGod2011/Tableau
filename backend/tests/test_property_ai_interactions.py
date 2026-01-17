"""
Property-based tests for AI interactions and conversational interface
**Feature: treasuryiq-corporate-ai**

These tests validate the correctness properties for AI-powered conversational analytics,
natural language processing, and predictive insights as specified in the design document.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, example
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize, invariant
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
import asyncio
import json
import re

from app.services.agentforce import AgentforceService, ConversationManager
from app.models.ai import ConversationContext, ConversationTurn, AIInsight, InsightType
from app.models.corporate import CorporateEntity


# Test Data Generators
@st.composite
def generate_natural_language_query(draw):
    """Generate realistic natural language queries for treasury operations"""
    
    query_templates = [
        # Cash optimization queries
        "What's my current cash optimization opportunity?",
        "How can I optimize cash allocation for {entity}?",
        "Show me cash placement recommendations",
        "What's the yield improvement potential?",
        "How much can I save by optimizing cash?",
        
        # Risk analysis queries  
        "What's my portfolio risk exposure?",
        "Show me the VaR calculation",
        "What are the FX risks for {currency}?",
        "How volatile is my portfolio?",
        "What's the credit risk in my investments?",
        
        # Market data queries
        "What are current market conditions?",
        "How are interest rates trending?",
        "Show me Fed rate forecasts",
        "What's the economic outlook?",
        "How is market volatility?",
        
        # General queries
        "Help me understand my treasury position",
        "What should I focus on today?",
        "Give me a portfolio summary",
        "What are my biggest risks?",
        "Show me optimization opportunities"
    ]
    
    template = draw(st.sampled_from(query_templates))
    
    # Fill in template variables
    if "{entity}" in template:
        entity = draw(st.sampled_from(["US operations", "European division", "APAC region"]))
        template = template.replace("{entity}", entity)
    
    if "{currency}" in template:
        currency = draw(st.sampled_from(["EUR", "JPY", "GBP", "CAD", "SGD"]))
        template = template.replace("{currency}", currency)
    
    return template


@st.composite
def generate_conversation_context(draw):
    """Generate conversation context data"""
    
    session_id = f"session_{draw(st.integers(min_value=1000, max_value=9999))}"
    user_id = f"user_{draw(st.integers(min_value=100, max_value=999))}"
    
    entity_scope = draw(st.lists(
        st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        min_size=1,
        max_size=5
    ))
    
    dashboard_context = {
        "current_page": draw(st.sampled_from(["dashboard", "risk", "cash", "analytics"])),
        "filters": {
            "entity": draw(st.sampled_from(["all", "us", "eu", "apac"])),
            "timeframe": draw(st.sampled_from(["1M", "3M", "6M", "1Y"]))
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return {
        "session_id": session_id,
        "user_id": user_id,
        "entity_scope": entity_scope,
        "dashboard_context": dashboard_context
    }


@st.composite
def generate_ai_response_data(draw):
    """Generate AI response data for testing"""
    
    response_text = draw(st.text(min_size=50, max_size=1000))
    confidence = draw(st.floats(min_value=0.0, max_value=1.0))
    intent = draw(st.sampled_from([
        "cash_optimization", "risk_analysis", "market_data", 
        "portfolio_summary", "fx_exposure", "general_query"
    ]))
    
    entities = {
        "analysis_type": draw(st.sampled_from(["optimization", "risk", "summary"])),
        "entity_id": draw(st.text(min_size=5, max_size=20)),
        "timeframe": draw(st.sampled_from(["1M", "3M", "6M", "1Y"]))
    }
    
    return {
        "response": response_text,
        "confidence": confidence,
        "intent": intent,
        "entities": entities,
        "processing_time_ms": draw(st.integers(min_value=100, max_value=5000))
    }


# Property Tests
class TestAIInteractionProperties:
    """Property-based tests for AI interaction correctness"""

    @pytest.mark.asyncio
    @given(query=generate_natural_language_query())
    @settings(max_examples=50, deadline=10000)
    async def test_property_11_natural_language_processing(self, query, db_session):
        """
        Property 11: Natural Language Processing
        **Validates: Requirements 3.1**
        
        For any natural language query about treasury operations,
        the AI system should interpret intent and provide a meaningful response
        with confidence score above minimum threshold.
        """
        
        service = AgentforceService(db_session)
        
        # Process the natural language query
        result = await service.process_query(
            session_id="test_session_nlp",
            user_id="test_user",
            message=query,
            entity_scope=["demo_entity"]
        )
        
        # Verify response structure
        assert "response" in result
        assert "confidence" in result
        assert "intent" in result
        
        # Verify response quality
        assert len(result["response"]) > 10, "Response should be meaningful"
        assert result["confidence"] >= 0.0, "Confidence should be non-negative"
        assert result["confidence"] <= 1.0, "Confidence should not exceed 1.0"
        
        # Verify intent detection
        valid_intents = [
            "cash_optimization", "risk_analysis", "market_data",
            "portfolio_summary", "fx_exposure", "general_query"
        ]
        assert result["intent"] in valid_intents, f"Intent should be recognized: {result['intent']}"
        
        # For treasury-specific queries, confidence should be reasonable
        treasury_keywords = ["cash", "risk", "portfolio", "optimization", "var", "fx"]
        if any(keyword in query.lower() for keyword in treasury_keywords):
            assert result["confidence"] >= 0.6, "Treasury queries should have reasonable confidence"


    @pytest.mark.asyncio
    @given(context_data=generate_conversation_context())
    @settings(max_examples=30, deadline=10000)
    async def test_property_12_complex_analysis_explanation(self, context_data, db_session):
        """
        Property 12: Complex Analysis Explanation
        **Validates: Requirements 3.2**
        
        For any complex financial analysis request, the AI should break down
        insights into understandable explanations with supporting data.
        """
        
        service = AgentforceService(db_session)
        
        # Test complex analysis queries
        complex_queries = [
            "Explain my portfolio's risk-adjusted returns and optimization opportunities",
            "Break down the VaR calculation and show me the key risk drivers",
            "Analyze my FX exposure and explain hedging recommendations"
        ]
        
        for query in complex_queries:
            result = await service.process_query(
                session_id=context_data["session_id"],
                user_id=context_data["user_id"],
                message=query,
                entity_scope=context_data["entity_scope"],
                dashboard_context=context_data["dashboard_context"]
            )
            
            # Verify explanation quality
            assert len(result["response"]) > 100, "Complex analysis should provide detailed explanation"
            
            # Check for structured explanation elements
            response_lower = result["response"].lower()
            explanation_indicators = [
                "analysis", "calculation", "based on", "indicates", "shows",
                "recommendation", "because", "due to", "impact", "result"
            ]
            
            explanation_count = sum(1 for indicator in explanation_indicators 
                                  if indicator in response_lower)
            assert explanation_count >= 2, "Response should contain explanation elements"
            
            # Verify confidence for complex queries
            assert result["confidence"] >= 0.5, "Complex analysis should have reasonable confidence"


    @pytest.mark.asyncio
    @given(
        query=st.text(min_size=10, max_size=200),
        context_data=generate_conversation_context()
    )
    @settings(max_examples=40, deadline=10000)
    async def test_property_13_recommendation_reasoning(self, query, context_data, db_session):
        """
        Property 13: Recommendation Reasoning
        **Validates: Requirements 3.3**
        
        For any query that results in recommendations, the AI should explain
        the reasoning behind recommendations and include confidence levels.
        """
        
        service = AgentforceService(db_session)
        
        # Focus on queries that typically generate recommendations
        recommendation_queries = [
            "What should I do with my excess cash?",
            "How can I reduce portfolio risk?",
            "What's the best cash allocation strategy?",
            "Should I hedge my FX exposure?",
            "How can I optimize my investment portfolio?"
        ]
        
        test_query = recommendation_queries[hash(query) % len(recommendation_queries)]
        
        result = await service.process_query(
            session_id=context_data["session_id"],
            user_id=context_data["user_id"],
            message=test_query,
            entity_scope=context_data["entity_scope"]
        )
        
        # Verify recommendation structure
        assert "response" in result
        assert "confidence" in result
        
        # Check for reasoning indicators in response
        response_lower = result["response"].lower()
        reasoning_indicators = [
            "recommend", "suggest", "should", "consider", "because",
            "due to", "based on", "analysis shows", "opportunity",
            "potential", "impact", "benefit"
        ]
        
        reasoning_count = sum(1 for indicator in reasoning_indicators 
                            if indicator in response_lower)
        
        # If response contains recommendations, it should include reasoning
        if any(word in response_lower for word in ["recommend", "suggest", "should"]):
            assert reasoning_count >= 3, "Recommendations should include reasoning"
            assert result["confidence"] > 0.0, "Recommendations should have confidence score"
        
        # Check for suggested actions if available
        if "suggested_actions" in result and result["suggested_actions"]:
            assert len(result["suggested_actions"]) > 0, "Should provide actionable suggestions"
            for action in result["suggested_actions"]:
                assert len(action) > 5, "Actions should be meaningful"


    @pytest.mark.asyncio
    @given(
        queries=st.lists(generate_natural_language_query(), min_size=2, max_size=5),
        session_id=st.text(min_size=10, max_size=50)
    )
    @settings(max_examples=25, deadline=15000)
    async def test_property_14_conversational_context_maintenance(self, queries, session_id, db_session):
        """
        Property 14: Conversational Context Maintenance
        **Validates: Requirements 3.4**
        
        For any sequence of related queries in a conversation,
        the AI should maintain context and provide coherent follow-up responses.
        """
        
        service = AgentforceService(db_session)
        user_id = "test_context_user"
        
        # Process queries in sequence
        previous_intents = []
        
        for i, query in enumerate(queries):
            result = await service.process_query(
                session_id=session_id,
                user_id=user_id,
                message=query,
                entity_scope=["demo_entity"]
            )
            
            # Verify basic response structure
            assert "response" in result
            assert "session_id" in result
            assert result["session_id"] == session_id, "Session ID should be maintained"
            
            # Track conversation progression
            if "intent" in result:
                previous_intents.append(result["intent"])
            
            # After first query, verify context is maintained
            if i > 0:
                # Get conversation history
                context = await service.conversation_manager.get_or_create_context(
                    session_id, user_id
                )
                
                assert context.total_interactions == i + 1, "Interaction count should increment"
                
                # Verify conversation history exists
                history = await service._get_recent_history(context, limit=10)
                assert len(history) >= 2 * (i + 1), "History should contain all turns"
        
        # Verify final conversation state
        final_context = await service.conversation_manager.get_or_create_context(
            session_id, user_id
        )
        assert final_context.total_interactions == len(queries), "Final interaction count should match"


    @pytest.mark.asyncio
    @given(
        technical_query=st.sampled_from([
            "What is Value at Risk and how is it calculated?",
            "Explain the difference between duration and convexity",
            "What does FX hedging mean for treasury operations?",
            "How do you calculate credit risk scores?",
            "What is cash optimization in treasury management?"
        ])
    )
    @settings(max_examples=20, deadline=10000)
    async def test_property_15_technical_term_explanation(self, technical_query, db_session):
        """
        Property 15: Technical Term Explanation
        **Validates: Requirements 3.5**
        
        For any query containing technical financial terms,
        the AI should provide definitions and business context.
        """
        
        service = AgentforceService(db_session)
        
        result = await service.process_query(
            session_id="test_technical_session",
            user_id="test_user",
            message=technical_query,
            entity_scope=["demo_entity"]
        )
        
        # Verify response contains explanation
        assert "response" in result
        assert len(result["response"]) > 50, "Technical explanations should be detailed"
        
        # Check for explanation patterns
        response_lower = result["response"].lower()
        explanation_patterns = [
            "is", "means", "refers to", "defined as", "calculated",
            "measures", "indicates", "represents", "used to"
        ]
        
        explanation_count = sum(1 for pattern in explanation_patterns 
                              if pattern in response_lower)
        assert explanation_count >= 2, "Should contain definitional language"
        
        # Verify business context is provided
        business_context_words = [
            "treasury", "financial", "risk", "portfolio", "investment",
            "cash", "management", "business", "operations", "impact"
        ]
        
        context_count = sum(1 for word in business_context_words 
                          if word in response_lower)
        assert context_count >= 3, "Should provide business context"
        
        # Technical queries should have reasonable confidence
        assert result["confidence"] >= 0.7, "Technical explanations should be confident"


# Stateful Property Testing
class AIConversationStateMachine(RuleBasedStateMachine):
    """
    Stateful property testing for AI conversation flows
    Tests conversation state management and consistency
    """
    
    def __init__(self):
        super().__init__()
        self.conversations = {}
        self.db_session = None
        self.service = None
    
    @initialize()
    def setup(self):
        """Initialize the state machine"""
        # This would be set up with a real database session in practice
        pass
    
    @rule(
        session_id=st.text(min_size=5, max_size=20),
        user_id=st.text(min_size=5, max_size=15),
        query=generate_natural_language_query()
    )
    def start_conversation(self, session_id, user_id, query):
        """Start a new conversation or continue existing one"""
        
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                "user_id": user_id,
                "turns": [],
                "total_interactions": 0
            }
        
        # Simulate conversation turn
        turn_data = {
            "query": query,
            "turn_number": len(self.conversations[session_id]["turns"]) + 1,
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.conversations[session_id]["turns"].append(turn_data)
        self.conversations[session_id]["total_interactions"] += 1
    
    @invariant()
    def conversation_consistency(self):
        """Verify conversation state consistency"""
        
        for session_id, conversation in self.conversations.items():
            # Turn numbers should be sequential
            for i, turn in enumerate(conversation["turns"]):
                assert turn["turn_number"] == i + 1, "Turn numbers should be sequential"
            
            # Total interactions should match turn count
            assert conversation["total_interactions"] == len(conversation["turns"]), \
                "Total interactions should match turn count"
            
            # Each turn should have required fields
            for turn in conversation["turns"]:
                assert "query" in turn, "Each turn should have a query"
                assert "turn_number" in turn, "Each turn should have a turn number"
                assert "timestamp" in turn, "Each turn should have a timestamp"


# Integration Tests with Property-Based Data
@pytest.mark.asyncio
@given(
    conversation_data=st.lists(
        st.tuples(
            generate_natural_language_query(),
            generate_conversation_context()
        ),
        min_size=1,
        max_size=3
    )
)
@settings(max_examples=15, deadline=20000)
async def test_end_to_end_conversation_flow(conversation_data, db_session):
    """
    End-to-end property test for complete conversation flows
    Tests the entire AI interaction pipeline with realistic data
    """
    
    service = AgentforceService(db_session)
    
    for query, context in conversation_data:
        result = await service.process_query(
            session_id=context["session_id"],
            user_id=context["user_id"],
            message=query,
            entity_scope=context["entity_scope"],
            dashboard_context=context["dashboard_context"]
        )
        
        # Verify complete response structure
        required_fields = ["response", "session_id", "confidence"]
        for field in required_fields:
            assert field in result, f"Response should contain {field}"
        
        # Verify response quality
        assert len(result["response"]) > 0, "Response should not be empty"
        assert 0.0 <= result["confidence"] <= 1.0, "Confidence should be in valid range"
        
        # Verify session consistency
        assert result["session_id"] == context["session_id"], "Session ID should be preserved"


# Performance Property Tests
@pytest.mark.asyncio
@given(query=generate_natural_language_query())
@settings(max_examples=20, deadline=15000)
async def test_response_time_property(query, db_session):
    """
    Property test for AI response time requirements
    Verifies that processing time is within acceptable limits
    """
    
    service = AgentforceService(db_session)
    
    start_time = datetime.now()
    
    result = await service.process_query(
        session_id="perf_test_session",
        user_id="perf_test_user", 
        message=query,
        entity_scope=["demo_entity"]
    )
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds() * 1000
    
    # Verify response time is reasonable (under 10 seconds for property tests)
    assert processing_time < 10000, f"Processing time {processing_time}ms should be under 10s"
    
    # Verify processing time is reported if available
    if "processing_time_ms" in result:
        reported_time = result["processing_time_ms"]
        assert reported_time > 0, "Reported processing time should be positive"
        # Allow some variance in timing measurements
        assert abs(processing_time - reported_time) < 2000, "Reported time should be reasonably accurate"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])