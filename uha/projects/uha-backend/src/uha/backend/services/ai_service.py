"""AI Service for LangChain-based analysis."""

import asyncio
import time
from decimal import Decimal
from typing import List

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..entities.ai_analysis import AIAnalysis, Keyword, KeywordType, Sentiment, SentimentType


class AIServiceConfig(BaseModel):
    """AI Service configuration."""

    lm_studio_url: str = Field(default="http://localhost:1234/v1", description="LM Studio API URL")
    model_name: str = Field(default="qwen/qwen3-4b", description="Model name")
    temperature: float = Field(default=0.4, ge=0, le=2, description="Model temperature")
    max_tokens: int = Field(default=500, ge=1, description="Maximum tokens")
    timeout_seconds: int = Field(default=30, ge=1, description="Request timeout")


class SummaryRequest(BaseModel):
    """Summary generation request."""

    title: str = Field(min_length=1, description="Content title")
    description: str = Field(default="", description="Content description")
    comments: List[str] = Field(default_factory=list, description="Comments")
    tags: List[str] = Field(default_factory=list, description="Tags")
    keywords: List[str] = Field(default_factory=list, description="Keywords")


class AIService:
    """AI Service using LangChain for analysis."""

    def __init__(self, config: AIServiceConfig):
        """Initialize AI Service."""
        self.config = config
        self._llm = None
        self._summary_chain = None
        self._sentiment_chain = None
        self._keyword_chain = None

    def _get_llm(self) -> ChatOpenAI:
        """Get or create LLM instance."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                base_url=self.config.lm_studio_url,
                api_key="lm-studio",  # LM Studio doesn't require real API key
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                request_timeout=self.config.timeout_seconds,
            )
        return self._llm

    def _get_summary_chain(self) -> LLMChain:
        """Get or create summary chain."""
        if self._summary_chain is None:
            template = """
당신은 한국어 전문 분석가입니다. 반드시 한국어로만 답변하세요.

다음 라이브 스트림 정보를 바탕으로 한국어로 2-3문장의 간결한 요약을 작성해주세요:

제목: {title}
설명: {description}
태그/키워드: {tags_keywords}
시청자 댓글: {comments}

요약 조건:
1. 스트림의 주요 내용과 특징을 간결하게 설명
2. 시청자들의 반응이나 하이라이트가 있다면 포함  
3. 한국어로만 작성, 2-3문장 이내
4. 구체적이고 흥미로운 내용 위주로 작성

요약:
"""

            prompt = PromptTemplate(
                template=template, input_variables=["title", "description", "tags_keywords", "comments"]
            )

            self._summary_chain = LLMChain(llm=self._get_llm(), prompt=prompt, verbose=False)

        return self._summary_chain

    def _get_sentiment_chain(self) -> LLMChain:
        """Get or create sentiment analysis chain."""
        if self._sentiment_chain is None:
            template = """
다음 텍스트의 감정을 분석하고 한국어로 답변해주세요.

텍스트: {text}

다음 형식으로 답변해주세요:
감정: [positive/negative/neutral]
점수: [0.0-1.0 사이의 숫자]
설명: [한국어로 간단한 설명]

답변:
"""

            prompt = PromptTemplate(template=template, input_variables=["text"])

            self._sentiment_chain = LLMChain(llm=self._get_llm(), prompt=prompt, verbose=False)

        return self._sentiment_chain

    async def generate_summary(self, request: SummaryRequest) -> str:
        """Generate AI summary for content."""
        try:
            # Prepare input data
            tags_keywords = ", ".join(request.tags + request.keywords) if request.tags or request.keywords else "없음"
            comments_text = " ".join(request.comments[:10]) if request.comments else "없음"

            # Run chain
            chain = self._get_summary_chain()
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: chain.run(
                    title=request.title,
                    description=request.description[:200] if request.description else "없음",
                    tags_keywords=tags_keywords,
                    comments=comments_text[:300],
                ),
            )

            # Clean response
            summary = self._clean_response(response)

            # Fallback if response is invalid
            if not summary or len(summary.strip()) < 10:
                summary = f"{request.title}에서 진행된 라이브 스트리밍입니다."
                if request.tags:
                    summary += f" 주요 내용은 {', '.join(request.tags[:3])} 관련이며,"
                summary += " 시청자들과의 실시간 소통이 활발했습니다."

            return summary.strip()

        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return f"{request.title}에서 진행된 라이브 스트리밍입니다."

    async def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment of text."""
        try:
            chain = self._get_sentiment_chain()
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: chain.run(text=text[:500]),  # Limit text length
            )

            # Parse response
            sentiment_type, score, description = self._parse_sentiment_response(response)

            return Sentiment(type=sentiment_type, score=Decimal(str(score)), description=description)

        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return Sentiment(type=SentimentType.NEUTRAL, score=Decimal("0.5"), description="중립적인 반응의 스트림")

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[Keyword]:
        """Extract keywords from text using frequency analysis."""
        try:
            import re
            from collections import Counter

            # Extract words (Korean, English, numbers)
            words = re.findall(r"[가-힣a-zA-Z0-9]{2,}", text.lower())

            # Remove stop words
            stop_words = {
                "그래서",
                "그런데",
                "하지만",
                "그리고",
                "그러나",
                "그냥",
                "정말",
                "진짜",
                "완전",
                "the",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
            }

            filtered_words = [word for word in words if word not in stop_words and len(word) > 1]

            # Calculate frequency
            counter = Counter(filtered_words)

            # Convert to Keyword objects
            keywords = []
            for word, frequency in counter.most_common(max_keywords):
                relevance_score = min(frequency / len(filtered_words) * 10, 1.0)  # Normalize
                keywords.append(
                    Keyword(
                        text=word,
                        type=KeywordType.EXTRACTED,
                        frequency=frequency,
                        relevance_score=Decimal(str(round(relevance_score, 3))),
                    )
                )

            return keywords

        except Exception as e:
            print(f"Error extracting keywords: {str(e)}")
            return []

    async def create_full_analysis(self, target_id: str, target_type: str, request: SummaryRequest) -> AIAnalysis:
        """Create comprehensive AI analysis."""
        start_time = time.time()

        try:
            # Generate summary and sentiment in parallel
            summary_task = self.generate_summary(request)
            sentiment_task = self.analyze_sentiment(f"{request.title} {request.description}")

            summary, sentiment = await asyncio.gather(summary_task, sentiment_task)

            # Extract keywords
            full_text = f"{request.title} {request.description} {' '.join(request.comments[:10])}"
            keywords = self.extract_keywords(full_text)

            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)

            # Calculate confidence score based on data availability
            confidence = self._calculate_confidence_score(request)

            return AIAnalysis(
                target_id=target_id,
                target_type=target_type,
                summary=summary,
                highlights=self._extract_highlights(request.comments),
                sentiment=sentiment,
                keywords=keywords,
                model_name=self.config.model_name,
                confidence_score=Decimal(str(confidence)),
                processing_time_ms=processing_time,
                metadata={
                    "comment_count": len(request.comments),
                    "tag_count": len(request.tags),
                    "keyword_count": len(request.keywords),
                },
            )

        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            print(f"Error creating full analysis: {str(e)}")

            # Return fallback analysis
            return AIAnalysis(
                target_id=target_id,
                target_type=target_type,
                summary=f"{request.title}에서 진행된 라이브 스트리밍입니다.",
                highlights=["📺 라이브 방송"],
                sentiment=Sentiment(
                    type=SentimentType.NEUTRAL, score=Decimal("0.5"), description="중립적인 반응의 스트림"
                ),
                keywords=[],
                model_name=self.config.model_name,
                confidence_score=Decimal("0.3"),
                processing_time_ms=processing_time,
            )

    def _clean_response(self, response: str) -> str:
        """Clean AI response."""
        import re

        # Remove thinking tags and XML-like tags
        response = re.sub(r"<[^>]*>", "", response)

        # Limit to first 4 sentences
        sentences = response.split(".")
        if len(sentences) > 4:
            response = ".".join(sentences[:4]) + "."

        return response.strip()

    def _parse_sentiment_response(self, response: str) -> tuple:
        """Parse sentiment analysis response."""
        try:
            lines = response.strip().split("\n")
            sentiment_type = SentimentType.NEUTRAL
            score = 0.5
            description = "중립적인 반응의 스트림"

            for line in lines:
                line = line.strip()
                if line.startswith("감정:"):
                    sentiment_str = line.split(":", 1)[1].strip().lower()
                    if "positive" in sentiment_str or "긍정" in sentiment_str:
                        sentiment_type = SentimentType.POSITIVE
                    elif "negative" in sentiment_str or "부정" in sentiment_str:
                        sentiment_type = SentimentType.NEGATIVE
                elif line.startswith("점수:"):
                    try:
                        score = float(line.split(":", 1)[1].strip())
                        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
                    except ValueError:
                        pass
                elif line.startswith("설명:"):
                    desc = line.split(":", 1)[1].strip()
                    if desc and len(desc) > 5:
                        description = desc

            return sentiment_type, score, description

        except Exception:
            return SentimentType.NEUTRAL, 0.5, "중립적인 반응의 스트림"

    def _extract_highlights(self, comments: List[str]) -> List[str]:
        """Extract highlights from comments."""
        if not comments:
            return ["📺 라이브 방송"]

        highlights = []
        highlight_keywords = [
            "대박",
            "최고",
            "웃겨",
            "재밌",
            "감동",
            "놀라",
            "신기",
            "멋지",
            "완벽",
            "훌륭",
            "funny",
            "amazing",
            "great",
            "awesome",
            "perfect",
            "incredible",
            "wow",
        ]

        for comment in comments[:20]:
            comment_lower = comment.lower()
            if any(keyword in comment_lower for keyword in highlight_keywords):
                clean_comment = comment.strip()[:50]
                if clean_comment and clean_comment not in highlights:
                    highlights.append(clean_comment)
                    if len(highlights) >= 3:
                        break

        if not highlights:
            highlights = ["📺 라이브 방송"]

        return highlights

    def _calculate_confidence_score(self, request: SummaryRequest) -> float:
        """Calculate confidence score based on available data."""
        score = 0.3  # Base score

        if request.title:
            score += 0.2
        if request.description:
            score += 0.2
        if request.comments:
            score += min(len(request.comments) * 0.05, 0.2)
        if request.tags or request.keywords:
            score += 0.1

        return min(score, 1.0)
