"""AI REST controller."""

from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..containers.di import Container
from ..services.ai_service import AIService, SummaryRequest


# Request/Response Models
class AIAnalysisRequest(BaseModel):
    """Request model for AI analysis."""

    title: str = Field(min_length=1, description="Content title")
    description: str = Field(default="", description="Content description")
    comments: List[str] = Field(default_factory=list, description="Comments")
    tags: List[str] = Field(default_factory=list, description="Tags")
    keywords: List[str] = Field(default_factory=list, description="Keywords")


class AIAnalysisResponse(BaseModel):
    """Response model for AI analysis."""

    summary: str
    sentiment: str
    sentiment_score: float
    keywords: List[str]
    highlights: List[str]
    confidence_score: float
    processing_time_ms: int


# Router
router = APIRouter(prefix="/ai", tags=["AI Analysis"])


@router.post("/analyze", response_model=AIAnalysisResponse)
@inject
async def analyze_content(
    request: AIAnalysisRequest, ai_service: AIService = Depends(Provide[Container.ai_service])
) -> AIAnalysisResponse:
    """Analyze content with AI."""
    try:
        # Create summary request
        summary_request = SummaryRequest(
            title=request.title,
            description=request.description,
            comments=request.comments,
            tags=request.tags,
            keywords=request.keywords,
        )

        # Create full analysis
        analysis = await ai_service.create_full_analysis(
            target_id="temp_id", target_type="content", request=summary_request
        )

        return AIAnalysisResponse(
            summary=analysis.summary,
            sentiment=analysis.sentiment.description,
            sentiment_score=float(analysis.sentiment.score),
            keywords=[kw.text for kw in analysis.get_top_keywords(10)],
            highlights=analysis.highlights,
            confidence_score=float(analysis.confidence_score),
            processing_time_ms=analysis.processing_time_ms,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/summarize")
@inject
async def summarize_content(
    request: AIAnalysisRequest, ai_service: AIService = Depends(Provide[Container.ai_service])
) -> dict:
    """Generate summary for content."""
    try:
        summary_request = SummaryRequest(
            title=request.title,
            description=request.description,
            comments=request.comments,
            tags=request.tags,
            keywords=request.keywords,
        )

        summary = await ai_service.generate_summary(summary_request)

        return {"summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.get("/health")
async def health_check() -> dict:
    """Check AI service health."""
    return {"status": "healthy", "message": "AI service is running"}
