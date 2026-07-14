from abc import ABC, abstractmethod
from typing import List
from app.domain.entities import Article, AnalyzedArticle


class IArticleRepository(ABC):
    """Repository interface for article persistence operations."""

    @abstractmethod
    async def save_analysis(self, article: AnalyzedArticle) -> None:
        """Save an analyzed article to the database."""
        pass

    @abstractmethod
    async def get_by_url(self, url: str) -> AnalyzedArticle | None:
        """Retrieve an analyzed article by its URL."""
        pass

    @abstractmethod
    async def get_all_analyzed_urls(self, urls: List[str]) -> set[str]:
        """Get set of URLs that have already been analyzed."""
        pass

    @abstractmethod
    async def get_history(self, limit: int) -> List[AnalyzedArticle]:
        """Get recent analyzed articles sorted by analysis date."""
        pass


class INewsService(ABC):
    """Interface for external news provider service."""

    @abstractmethod
    async def search_articles(self, query: str, max_results: int = 10) -> List[Article]:
        """Search for articles matching the query."""
        pass


class IAIService(ABC):
    """Interface for AI analysis service."""

    @abstractmethod
    async def analyze_article(self, title: str, description: str | None) -> dict:
        """Analyze an article and return summary and sentiment."""
        pass
