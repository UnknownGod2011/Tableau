"""
Simple property test runner for AI interactions
"""

import asyncio
from datetime import datetime, timezone
from hypothesis import given, strategies as st, settings
from app.services.agentforce import AgentforceService


# Mock database session
class MockDB:
    def __init__(self):
        self.objects = []
    
    async def execute(self, query):
        return MockResult()
    
    async def commit(self):
        pass
    
    async def refresh(self, obj):
        # Set default values for refreshed objects
        if hasattr(obj, 'total_interactions') and obj.total_interactions is None:
            obj.total_interactions = 0
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = f"mock_id_{len(self.objects)}"
        pass
    
    def add(self, obj):
        # Set default values for new objects
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = f"mock_id_{len(self.objects)}"
        self.objects.append(obj)

class MockResult:
    def scalar_one_or_none(self):
        # Return a mock context with proper defaults
        from app.models.ai import ConversationContext
        context = ConversationContext(
            session_id="mock_session",
            user_id="mock_user",
            entity_scope=[],
            last_activity=datetime.now(timezone.utc),
            total_interactions=0,
            user_preferences={}
        )
        context.id = "mock_context_id"
        return None  # Return None to trigger new context creation
    
    def scalars(self):
        return MockScalars()

class MockScalars:
    def all(self):
        return []


def test_property_11_natural_language_processing_simple():
    """
    Property 11: Natural Language Processing
    **Feature: treasuryiq-corporate-ai, Property 11: Natural Language Processing**
    **Validates: Requirements 3.1**
    
    For any natural language query about treasury operations,
    the AI system should interpret intent and provide a meaningful response.
    """
    
    async def run_test(query):
        db = MockDB()
        service = AgentforceService(db)
        
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
        
        print(f"✅ Query: '{query}' -> Intent: {result['intent']}, Confidence: {result['confidence']:.2f}")
    
    # Test with sample queries
    test_queries = [
        "What's my cash optimization opportunity?",
        "Show me portfolio risk analysis", 
        "How can I optimize my investments?",
        "What are current market conditions?"
    ]
    
    for query in test_queries:
        asyncio.run(run_test(query))


if __name__ == "__main__":
    print("Testing AI Property 11: Natural Language Processing")
    
    try:
        test_property_11_natural_language_processing_simple()
        print("🎉 All Property 11 tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")