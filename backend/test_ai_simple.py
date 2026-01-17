"""
Simple test for AI integration
"""

import asyncio
from app.services.agentforce import AgentforceService
from app.core.database import get_db


async def test_ai_service():
    """Test AI service initialization and mock functionality"""
    
    print("Testing AI Service...")
    
    # Create a mock database session
    class MockDB:
        async def execute(self, query):
            return MockResult()
        
        async def commit(self):
            pass
        
        async def refresh(self, obj):
            pass
        
        def add(self, obj):
            pass
    
    class MockResult:
        def scalar_one_or_none(self):
            return None
        
        def scalars(self):
            return MockScalars()
    
    class MockScalars:
        def all(self):
            return []
    
    # Initialize service
    db = MockDB()
    service = AgentforceService(db)
    
    print("✅ AgentforceService initialized successfully")
    
    # Test mock intent analysis
    intent_result = await service._mock_intent_analysis("What's my cash optimization opportunity?")
    print(f"✅ Intent analysis: {intent_result}")
    
    # Test general query handling
    general_result = await service._handle_general_query(
        "What can you help me with?", 
        {}, 
        None
    )
    print(f"✅ General query handling: {general_result['confidence']}")
    
    print("🎉 All AI service tests passed!")


if __name__ == "__main__":
    asyncio.run(test_ai_service())