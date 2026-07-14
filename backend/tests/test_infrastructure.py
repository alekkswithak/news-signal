import pytest
from datetime import datetime, timezone
from mongomock import MongoClient
from app.infrastructure.persistence.mongodb_article_repository import MongoArticleRepository
from app.domain.entities import AnalyzedArticle


@pytest.fixture
def mongo_client():
    """Create a mock MongoDB client for testing."""
    return MongoClient()


@pytest.fixture
def mongo_repository(mongo_client):
    """Create a MongoDB repository with mock client."""
    repo = MongoArticleRepository(mongo_client)
    # Initialize the collection
    _ = repo.collection
    return repo


class TestMongoArticleRepository:
    """Tests for MongoArticleRepository."""

    @pytest.mark.asyncio
    async def test_save_analysis(self, mongo_repository, sample_analyzed_article):
        """Test saving an analyzed article."""
        await mongo_repository.save_analysis(sample_analyzed_article)

        retrieved = await mongo_repository.get_by_url(sample_analyzed_article.url)
        assert retrieved is not None
        assert retrieved.url == sample_analyzed_article.url
        assert retrieved.title == sample_analyzed_article.title

    @pytest.mark.asyncio
    async def test_get_by_url_not_found(self, mongo_repository):
        """Test getting a non-existent article."""
        result = await mongo_repository.get_by_url("https://example.com/nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_url_found(self, mongo_repository, sample_analyzed_article):
        """Test getting an existing article."""
        await mongo_repository.save_analysis(sample_analyzed_article)

        result = await mongo_repository.get_by_url(sample_analyzed_article.url)
        assert result is not None
        assert result.url == sample_analyzed_article.url

    @pytest.mark.asyncio
    async def test_get_all_analyzed_urls_empty(self, mongo_repository):
        """Test getting analyzed URLs when none exist."""
        urls = ["https://example.com/1", "https://example.com/2"]
        result = await mongo_repository.get_all_analyzed_urls(urls)
        assert result == set()

    @pytest.mark.asyncio
    async def test_get_all_analyzed_urls_partial(self, mongo_repository, sample_analyzed_article):
        """Test getting analyzed URLs with some matches."""
        await mongo_repository.save_analysis(sample_analyzed_article)

        urls = [
            sample_analyzed_article.url,
            "https://example.com/nonexistent",
        ]
        result = await mongo_repository.get_all_analyzed_urls(urls)
        assert result == {sample_analyzed_article.url}

    @pytest.mark.asyncio
    async def test_get_all_analyzed_urls_all(self, mongo_repository, sample_analyzed_article):
        """Test getting analyzed URLs when all match."""
        await mongo_repository.save_analysis(sample_analyzed_article)

        urls = [sample_analyzed_article.url]
        result = await mongo_repository.get_all_analyzed_urls(urls)
        assert result == {sample_analyzed_article.url}

    @pytest.mark.asyncio
    async def test_get_history_empty(self, mongo_repository):
        """Test getting history when empty."""
        result = await mongo_repository.get_history(10)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_history_with_articles(self, mongo_repository, sample_analyzed_article):
        """Test getting history with articles."""
        await mongo_repository.save_analysis(sample_analyzed_article)

        result = await mongo_repository.get_history(10)
        assert len(result) == 1
        assert result[0].url == sample_analyzed_article.url

    @pytest.mark.asyncio
    async def test_get_history_sorted_by_date(self, mongo_repository):
        """Test history is sorted by analyzed_at descending."""
        article1 = AnalyzedArticle(
            url="https://example.com/1",
            title="Article 1",
            summary="Summary 1",
            sentiment="neutral",
            sentiment_score=0.0,
            analyzed_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        )
        article2 = AnalyzedArticle(
            url="https://example.com/2",
            title="Article 2",
            summary="Summary 2",
            sentiment="positive",
            sentiment_score=0.5,
            analyzed_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        article3 = AnalyzedArticle(
            url="https://example.com/3",
            title="Article 3",
            summary="Summary 3",
            sentiment="negative",
            sentiment_score=-0.5,
            analyzed_at=datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
        )

        await mongo_repository.save_analysis(article1)
        await mongo_repository.save_analysis(article2)
        await mongo_repository.save_analysis(article3)

        result = await mongo_repository.get_history(10)
        assert len(result) == 3
        assert result[0].url == "https://example.com/2"  # Most recent
        assert result[1].url == "https://example.com/3"
        assert result[2].url == "https://example.com/1"  # Oldest

    @pytest.mark.asyncio
    async def test_get_history_limit(self, mongo_repository):
        """Test history limit is respected."""
        for i in range(5):
            article = AnalyzedArticle(
                url=f"https://example.com/{i}",
                title=f"Article {i}",
                summary=f"Summary {i}",
                sentiment="neutral",
                sentiment_score=0.0,
                analyzed_at=datetime(2024, 1, 1, i, 0, 0, tzinfo=timezone.utc),
            )
            await mongo_repository.save_analysis(article)

        result = await mongo_repository.get_history(3)
        assert len(result) == 3
