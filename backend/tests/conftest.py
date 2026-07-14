import pytest
from datetime import datetime, timezone
from app.domain.entities import Article, AnalyzedArticle
from app.domain.repositories import IArticleRepository, INewsService, IAIService


@pytest.fixture
def sample_article():
    """Sample article entity for testing."""
    return Article(
        url="https://example.com/article1",
        title="Test Article",
        description="A test article description",
        source="Test Source",
        image="https://example.com/image.jpg",
        published_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_analyzed_article():
    """Sample analyzed article entity for testing."""
    return AnalyzedArticle(
        url="https://example.com/article1",
        title="Test Article",
        description="A test article description",
        source="Test Source",
        published_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        summary="This is a summary of the article.",
        sentiment="neutral",
        sentiment_score=0.0,
        analyzed_at=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_article_repository():
    """Mock article repository for testing."""
    class MockArticleRepository(IArticleRepository):
        def __init__(self):
            self._storage = {}

        async def save_analysis(self, article: AnalyzedArticle) -> None:
            self._storage[article.url] = article

        async def get_by_url(self, url: str) -> AnalyzedArticle | None:
            return self._storage.get(url)

        async def get_all_analyzed_urls(self, urls: list[str]) -> set[str]:
            return {url for url in urls if url in self._storage}

        async def get_history(self, limit: int) -> list[AnalyzedArticle]:
            articles = list(self._storage.values())
            articles.sort(key=lambda a: a.analyzed_at or datetime.min, reverse=True)
            return articles[:limit]

    return MockArticleRepository()


@pytest.fixture
def mock_news_service():
    """Mock news service for testing."""
    class MockNewsService(INewsService):
        def __init__(self):
            self._articles = []

        def set_articles(self, articles: list[Article]):
            self._articles = articles

        async def search_articles(self, query: str, max_results: int = 10) -> list[Article]:
            return self._articles[:max_results]

    return MockNewsService()


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    class MockAIService(IAIService):
        def __init__(self):
            self._response = {
                "summary": "Mock summary",
                "sentiment": "neutral",
                "sentiment_score": 0.0,
            }

        def set_response(self, response: dict):
            self._response = response

        async def analyze_article(self, title: str, description: str | None) -> dict:
            return self._response.copy()

    return MockAIService()
