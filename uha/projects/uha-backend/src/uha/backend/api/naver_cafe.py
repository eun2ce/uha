"""Naver Cafe API endpoints."""

from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from uha.backend.container import ApplicationContainer
from uha.backend.settings import Settings

router = APIRouter(prefix="/naver-cafe", tags=["Naver Cafe"])


class CafeProfile(BaseModel):
    name: str
    thumbnail: str
    members: str


class CafeArticle(BaseModel):
    title: str
    author: str
    date: str
    link: str
    image: Optional[str] = None
    text: str


class CafeArticlesResponse(BaseModel):
    result: List[CafeArticle]
    page: int


async def get_settings() -> Settings:
    """Get application settings."""
    container = ApplicationContainer()
    return container.settings.provided()


async def get_html(url: str) -> str:
    """Get HTML content from URL."""
    headers = {"User-Agent": "Mozilla/5.0"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="페이지를 가져올 수 없습니다.")

    # Set encoding for Korean content
    response.encoding = "cp949"
    return response.text


@router.get("/profile", response_model=CafeProfile)
async def get_cafe_profile(settings: Settings = Depends(get_settings)):
    """Get Naver Cafe profile information."""
    try:
        url = f"https://cafe.naver.com/CafeProfileView.nhn?clubid={settings.naver_cafe_id}"
        html = await get_html(url)

        soup = BeautifulSoup(html, "html.parser")

        # Extract cafe information
        name_elem = soup.select_one(".cafe_name")
        thumbnail_elem = soup.select_one(".mcafe_icon img")
        members_elem = soup.select_one("#main-area > div > table > tbody > tr:nth-child(14) > td > span:nth-child(1)")

        if not all([name_elem, thumbnail_elem, members_elem]):
            raise HTTPException(status_code=404, detail="카페 정보를 찾을 수 없습니다.")

        profile = CafeProfile(
            name=name_elem.text.strip(), thumbnail=thumbnail_elem["src"], members=members_elem.text.strip()
        )

        return profile

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/articles/{menu_id}/{page_id}", response_model=CafeArticlesResponse)
async def get_cafe_articles(menu_id: int, page_id: int, settings: Settings = Depends(get_settings)):
    """Get Naver Cafe articles."""
    try:
        club_id = settings.naver_cafe_id
        url = (
            f"https://cafe.naver.com/ArticleList.nhn"
            f"?search.clubid={club_id}"
            f"&userDisplay=50"
            f"&search.boardtype=C"
            f"&search.cafeId={club_id}"
            f"&search.page={page_id}"
            f"&search.menuid={menu_id}"
        )

        html = await get_html(url)
        soup = BeautifulSoup(html, "html.parser")

        # Extract articles
        article_elements = soup.select("#main-area > .article-movie-sub > li")

        articles = []
        for li in article_elements:
            inner_elem = li.select_one(".inner")
            author_elem = li.select_one(".m-tcol-c")
            date_elem = li.select_one(".date")
            link_elem = li.select_one("a")
            image_elem = li.select_one(".movie-img img")

            if all([inner_elem, author_elem, date_elem, link_elem]):
                article = CafeArticle(
                    title=inner_elem.text.replace("\\s+", " ").strip(),
                    author=author_elem.text,
                    date=date_elem.text,
                    link="https://m.cafe.naver.com" + link_elem["href"],
                    image=image_elem["src"] if image_elem else None,
                    text=link_elem.text,
                )
                articles.append(article)

        return CafeArticlesResponse(result=articles, page=page_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
