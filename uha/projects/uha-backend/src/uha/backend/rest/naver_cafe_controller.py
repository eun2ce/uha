"""Naver Cafe REST controller."""

from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..containers.di import Container
from ..entities.naver_cafe import NaverCafeArticle, NaverCafeProfile
from ..services.naver_cafe_service import NaverCafeService


# Response Models
class NaverCafeProfileResponse(BaseModel):
    """Response model for Naver Cafe profile."""

    cafe_id: str
    nickname: str
    member_level: str
    visit_count: str
    activity_score: str
    profile_image_url: str = None

    @classmethod
    def from_entity(cls, profile: NaverCafeProfile) -> "NaverCafeProfileResponse":
        """Create response from profile entity."""
        return cls(
            cafe_id=profile.cafe_id,
            nickname=profile.nickname,
            member_level=profile.member_level,
            visit_count=profile.visit_count,
            activity_score=profile.activity_score,
            profile_image_url=str(profile.profile_image_url) if profile.profile_image_url else None,
        )


class NaverCafeArticleResponse(BaseModel):
    """Response model for Naver Cafe article."""

    article_id: str
    cafe_id: str
    title: str
    author: str
    date: str
    view_count: str
    comment_count: str
    link: str

    @classmethod
    def from_entity(cls, article: NaverCafeArticle) -> "NaverCafeArticleResponse":
        """Create response from article entity."""
        return cls(
            article_id=article.article_id,
            cafe_id=article.cafe_id,
            title=article.title,
            author=article.author,
            date=article.date,
            view_count=article.view_count,
            comment_count=article.comment_count,
            link=article.link,
        )


class PaginatedArticlesResponse(BaseModel):
    """Paginated articles response."""

    articles: List[NaverCafeArticleResponse]
    current_page: int
    per_page: int
    total_articles: int


# Router
router = APIRouter(prefix="/naver-cafe", tags=["Naver Cafe"])


@router.get("/profile", response_model=NaverCafeProfileResponse)
@inject
async def get_profile(
    naver_cafe_service: NaverCafeService = Depends(Provide[Container.naver_cafe_service]),
) -> NaverCafeProfileResponse:
    """Get Naver Cafe profile."""
    try:
        profile = await naver_cafe_service.get_profile()
        return NaverCafeProfileResponse.from_entity(profile)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")


@router.get("/articles", response_model=PaginatedArticlesResponse)
@inject
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Articles per page"),
    naver_cafe_service: NaverCafeService = Depends(Provide[Container.naver_cafe_service]),
) -> PaginatedArticlesResponse:
    """Get Naver Cafe articles."""
    try:
        articles = await naver_cafe_service.get_articles(page=page, per_page=per_page)

        article_responses = [NaverCafeArticleResponse.from_entity(article) for article in articles]

        return PaginatedArticlesResponse(
            articles=article_responses,
            current_page=page,
            per_page=per_page,
            total_articles=len(article_responses),  # This would come from actual pagination
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")


@router.get("/articles/{article_id}/content")
@inject
async def get_article_content(
    article_id: str,
    naver_cafe_service: NaverCafeService = Depends(Provide[Container.naver_cafe_service]),
) -> dict:
    """Get specific article content."""
    try:
        content = await naver_cafe_service.get_article_content(article_id)

        if content is None:
            raise HTTPException(status_code=404, detail="Article content not found")

        return {"article_id": article_id, "content": content}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch article content: {str(e)}")
