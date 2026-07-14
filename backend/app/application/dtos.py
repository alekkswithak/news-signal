from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ArticleSearchResultDTO(BaseModel):
    """DTO for article search results."""
    url: str
    title: str
    description: str | None = None
    source: str | None = None
    image: str | None = None
    published_at: datetime | None = None
    already_analyzed: bool = False


class AnalyzeRequestDTO(BaseModel):
    """DTO for article analysis request."""
    url: str
    title: str
    description: str | None = None
    source: str | None = None
    published_at: datetime | None = None


class AnalyzedArticleDTO(BaseModel):
    """DTO for analyzed article response."""
    url: str
    title: str
    description: str | None = None
    source: str | None = None
    published_at: datetime | None = None
    summary: str
    sentiment: Literal["positive", "neutral", "negative"]
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    analyzed_at: datetime
    from_cache: bool = False
