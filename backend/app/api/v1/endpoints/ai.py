"""
AI and conversational interface API endpoints
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....services.agentforce import AgentforceService
from ....models.ai import ConversationContext, ConversationTurn, AIInsight

router = APIRouter()


# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    entity_scope: Optional[List[str]] = Field(None, description="Entity IDs user has access to")
    dashboard_context: Optional[Dict[str, Any]] = Field(None, description="Current dashboard context")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Conversation session ID")
    turn_id: str = Field(..., description="Conversation turn ID")
    intent: Optional[str] = Field(None, description="Detected user intent")
    entities: Optional[Dict[str, Any]] = Field(None, description="Extracted entities")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence score")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    data_visualizations: Optional[List[Dict[str, Any]]] = Field(None, description="Suggested visualizations")
    suggested_actions: Optional[List[str]] = Field(None, description="Suggested follow-up actions")
    error: Optional[str] = Field(None, description="Error message if any")


class ConversationHistoryResponse(BaseModel):
    """Conversation history response"""
    session_id: str
    total_turns: int
    turns: List[Dict[str, Any]]
    context: Dict[str, Any]


class InsightResponse(BaseModel):
    """AI insight response"""
    id: str
    insight_type: str
    title: str
    description: str
    confidence: float
    financial_impact: Optional[float]
    risk_impact: Optional[str]
    urgency_score: float
    recommended_actions: List[str]
    generated_at: datetime
    is_expired: bool


class FeedbackRequest(BaseModel):
    """User feedback model"""
    turn_id: str = Field(..., description="Conversation turn ID")
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating from 1.0 to 5.0")
    feedback: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    message: ChatMessage,
    user_id: str = "demo_user",  # In production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the AI assistant and get a response
    """
    try:
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid4())
        
        # Initialize Agentforce service
        agentforce = AgentforceService(db)
        
        # Process the query
        result = await agentforce.process_query(
            session_id=session_id,
            user_id=user_id,
            message=message.message,
            entity_scope=message.entity_scope,
            dashboard_context=message.dashboard_context
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=result.get("session_id", session_id),
            turn_id=result.get("turn_id", ""),
            intent=result.get("intent"),
            entities=result.get("entities"),
            confidence=result.get("confidence", 0.0),
            processing_time_ms=result.get("processing_time_ms", 0),
            data_visualizations=result.get("data_visualizations"),
            suggested_actions=result.get("suggested_actions"),
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.get("/conversations/{session_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    limit: int = 20,
    user_id: str = "demo_user",  # In production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation history for a session
    """
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Get conversation context
        result = await db.execute(
            select(ConversationContext)
            .where(ConversationContext.session_id == session_id)
            .where(ConversationContext.user_id == user_id)
            .options(selectinload(ConversationContext.turns))
        )
        
        context = result.scalar_one_or_none()
        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get recent turns
        turns_result = await db.execute(
            select(ConversationTurn)
            .where(ConversationTurn.context_id == context.id)
            .order_by(ConversationTurn.turn_number.desc())
            .limit(limit)
        )
        
        turns = turns_result.scalars().all()
        
        # Format turns
        formatted_turns = []
        for turn in reversed(turns):
            formatted_turns.append({
                "turn_number": turn.turn_number,
                "user_message": turn.user_message,
                "ai_response": turn.ai_response,
                "timestamp": turn.created_at,
                "intent": turn.detected_intent,
                "confidence": turn.confidence_score,
                "processing_time_ms": turn.processing_time_ms
            })
        
        return ConversationHistoryResponse(
            session_id=session_id,
            total_turns=context.total_interactions,
            turns=formatted_turns,
            context={
                "entity_scope": context.entity_scope,
                "active_entity_id": context.active_entity_id,
                "user_preferences": context.user_preferences,
                "dashboard_context": context.dashboard_context
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation history: {str(e)}"
        )


@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    user_id: str = "demo_user",  # In production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Submit user feedback for an AI response
    """
    try:
        from sqlalchemy import select, update
        
        # Update the conversation turn with feedback
        result = await db.execute(
            update(ConversationTurn)
            .where(ConversationTurn.id == feedback.turn_id)
            .values(
                user_rating=feedback.rating,
                user_feedback=feedback.feedback
            )
        )
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation turn not found"
            )
        
        await db.commit()
        
        return {"message": "Feedback submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )


@router.get("/insights", response_model=List[InsightResponse])
async def get_ai_insights(
    entity_id: Optional[str] = None,
    insight_type: Optional[str] = None,
    limit: int = 10,
    user_id: str = "demo_user",  # In production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated insights
    """
    try:
        from sqlalchemy import select, and_
        
        # Build query
        query = select(AIInsight).order_by(AIInsight.generated_at.desc()).limit(limit)
        
        conditions = []
        if entity_id:
            conditions.append(AIInsight.entity_id == entity_id)
        if insight_type:
            conditions.append(AIInsight.insight_type == insight_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await db.execute(query)
        insights = result.scalars().all()
        
        # Format response
        formatted_insights = []
        for insight in insights:
            formatted_insights.append(InsightResponse(
                id=str(insight.id),
                insight_type=insight.insight_type.value,
                title=insight.title,
                description=insight.description,
                confidence=float(insight.confidence),
                financial_impact=float(insight.financial_impact) if insight.financial_impact else None,
                risk_impact=insight.risk_impact,
                urgency_score=float(insight.urgency_score),
                recommended_actions=insight.recommended_actions or [],
                generated_at=insight.generated_at,
                is_expired=insight.is_expired
            ))
        
        return formatted_insights
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving insights: {str(e)}"
        )


@router.post("/insights/{insight_id}/acknowledge")
async def acknowledge_insight(
    insight_id: str,
    user_id: str = "demo_user",  # In production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Mark an insight as acknowledged/acted upon
    """
    try:
        from sqlalchemy import select, update
        
        # Update insight
        result = await db.execute(
            update(AIInsight)
            .where(AIInsight.id == insight_id)
            .values(acted_upon='Y')
        )
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insight not found"
            )
        
        await db.commit()
        
        return {"message": "Insight acknowledged successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error acknowledging insight: {str(e)}"
        )


@router.get("/health")
async def ai_health_check():
    """
    Health check for AI services
    """
    return {
        "status": "healthy",
        "agentforce_configured": bool(settings.AGENTFORCE_API_KEY),
        "timestamp": datetime.now().isoformat()
    }


# Add missing import
from ....core.config import settings