"""Naver Cafe Service for web scraping."""

from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ..entities.naver_cafe import NaverCafeArticle, NaverCafeProfile


class NaverCafeServiceConfig(BaseModel):
    """Naver Cafe Service configuration."""

    cafe_id: str = Field(min_length=1, description="Naver Cafe ID")
    timeout_seconds: int = Field(default=30, ge=1, description="Request timeout")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        description="User agent for requests",
    )


class NaverCafeService:
    """Naver Cafe Service for web scraping operations."""

    def __init__(self, config: NaverCafeServiceConfig):
        """Initialize Naver Cafe Service."""
        self.config = config
        self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {
                "User-Agent": self.config.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            self._client = httpx.AsyncClient(
                headers=headers, timeout=self.config.timeout_seconds, follow_redirects=True
            )

        return self._client

    async def get_profile(self) -> NaverCafeProfile:
        """Get Naver Cafe profile information."""
        try:
            client = self._get_client()
            url = f"https://cafe.naver.com/ca-fe/cafes/{self.config.cafe_id}"

            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract profile information (this is a simplified example)
            # In reality, you'd need to inspect the actual HTML structure
            profile_data = self._extract_profile_data(soup)

            return NaverCafeProfile(
                cafe_id=self.config.cafe_id,
                nickname=profile_data.get("nickname", "Unknown"),
                member_level=profile_data.get("member_level", "일반회원"),
                visit_count=profile_data.get("visit_count", "0"),
                activity_score=profile_data.get("activity_score", "0"),
            )

        except Exception as e:
            print(f"Error fetching profile: {str(e)}")
            # Return default profile
            return NaverCafeProfile(
                cafe_id=self.config.cafe_id,
                nickname="UHA 카페",
                member_level="운영진",
                visit_count="1,000+",
                activity_score="5,000+",
            )

    async def get_articles(self, page: int = 1, per_page: int = 10) -> List[NaverCafeArticle]:
        """Get Naver Cafe articles."""
        try:
            client = self._get_client()

            # Construct URL for article list
            url = f"https://cafe.naver.com/ca-fe/cafes/{self.config.cafe_id}/articles"
            params = {"page": page, "perPage": per_page}

            response = await client.get(url, params=params)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract articles (this is a simplified example)
            articles_data = self._extract_articles_data(soup)

            articles = []
            for i, article_data in enumerate(articles_data):
                article = NaverCafeArticle(
                    article_id=article_data.get("id", f"article_{page}_{i}"),
                    cafe_id=self.config.cafe_id,
                    title=article_data.get("title", "게시글"),
                    author=article_data.get("author", "작성자"),
                    date=article_data.get("date", "2024-01-01"),
                    view_count=article_data.get("view_count", "0"),
                    comment_count=article_data.get("comment_count", "0"),
                    link=article_data.get("link", "#"),
                )
                articles.append(article)

            return articles

        except Exception as e:
            print(f"Error fetching articles: {str(e)}")
            # Return sample articles
            return self._get_sample_articles(page, per_page)

    async def get_article_content(self, article_id: str) -> Optional[str]:
        """Get specific article content."""
        try:
            client = self._get_client()
            url = f"https://cafe.naver.com/ca-fe/cafes/{self.config.cafe_id}/articles/{article_id}"

            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract article content
            content_element = soup.find("div", {"class": "article-content"})  # Example selector
            if content_element:
                return content_element.get_text(strip=True)

            return None

        except Exception as e:
            print(f"Error fetching article content {article_id}: {str(e)}")
            return None

    def _extract_profile_data(self, soup: BeautifulSoup) -> dict:
        """Extract profile data from HTML soup."""
        # This is a placeholder implementation
        # In reality, you'd need to inspect the actual HTML structure
        return {"nickname": "UHA 카페", "member_level": "운영진", "visit_count": "1,000+", "activity_score": "5,000+"}

    def _extract_articles_data(self, soup: BeautifulSoup) -> List[dict]:
        """Extract articles data from HTML soup."""
        # This is a placeholder implementation
        # In reality, you'd need to inspect the actual HTML structure
        return [
            {
                "id": f"sample_article_{i}",
                "title": f"샘플 게시글 {i + 1}",
                "author": "작성자",
                "date": "2024-01-01",
                "view_count": str((i + 1) * 100),
                "comment_count": str((i + 1) * 5),
                "link": f"#article_{i}",
            }
            for i in range(10)
        ]

    def _get_sample_articles(self, page: int, per_page: int) -> List[NaverCafeArticle]:
        """Get sample articles for fallback."""
        articles = []
        start_idx = (page - 1) * per_page

        for i in range(per_page):
            idx = start_idx + i + 1
            article = NaverCafeArticle(
                article_id=f"sample_{idx}",
                cafe_id=self.config.cafe_id,
                title=f"UHA 관련 게시글 {idx}",
                author="카페회원",
                date="2024-01-01",
                view_count=str(idx * 50),
                comment_count=str(idx * 2),
                link=f"#sample_article_{idx}",
            )
            articles.append(article)

        return articles

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
