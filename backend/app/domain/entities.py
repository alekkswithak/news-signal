from datetime import datetime
from typing import Literal
from dataclasses import dataclass


@dataclass
class Article:
    """Domain entity representing a news article."""
    url: str
    title: str
    description: str | None = None
    source: str | None = None
    image: str | None = None
    published_at: datetime | None = None


@dataclass
class AnalyzedArticle:
    """Domain entity representing an analyzed article with AI-generated insights."""
    url: str
    title: str
    description: str | None = None
    source: str | None = None
    published_at: datetime | None = None
    summary: str = ""
    sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    sentiment_score: float = 0.0
    analyzed_at: datetime | None = None
