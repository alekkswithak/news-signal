import pytest
from datetime import datetime, timezone
from app.domain.entities import Article, AnalyzedArticle


class TestArticle:
    """Tests for Article entity."""

    def test_article_creation(self):
        """Test creating an article with all fields."""
        article = Article(
            url="https://example.com/article",
            title="Test Title",
            description="Test Description",
            source="Test Source",
            image="https://example.com/image.jpg",
            published_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        assert article.url == "https://example.com/article"
        assert article.title == "Test Title"
        assert article.description == "Test Description"
        assert article.source == "Test Source"
        assert article.image == "https://example.com/image.jpg"
        assert article.published_at == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_article_creation_with_optional_fields(self):
        """Test creating an article with only required fields."""
        article = Article(
            url="https://example.com/article",
            title="Test Title",
        )
        assert article.url == "https://example.com/article"
        assert article.title == "Test Title"
        assert article.description is None
        assert article.source is None
        assert article.image is None
        assert article.published_at is None


class TestAnalyzedArticle:
    """Tests for AnalyzedArticle entity."""

    def test_analyzed_article_creation(self):
        """Test creating an analyzed article with all fields."""
        article = AnalyzedArticle(
            url="https://example.com/article",
            title="Test Title",
            description="Test Description",
            source="Test Source",
            published_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            summary="This is a summary",
            sentiment="positive",
            sentiment_score=0.8,
            analyzed_at=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
        )
        assert article.url == "https://example.com/article"
        assert article.title == "Test Title"
        assert article.summary == "This is a summary"
        assert article.sentiment == "positive"
        assert article.sentiment_score == 0.8
        assert article.analyzed_at == datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)

    def test_analyzed_article_sentiment_values(self):
        """Test valid sentiment values."""
        valid_sentiments = ["positive", "neutral", "negative"]
        for sentiment in valid_sentiments:
            article = AnalyzedArticle(
                url="https://example.com/article",
                title="Test Title",
                sentiment=sentiment,
            )
            assert article.sentiment == sentiment

    def test_analyzed_article_sentiment_score_range(self):
        """Test sentiment score is within valid range."""
        article = AnalyzedArticle(
            url="https://example.com/article",
            title="Test Title",
            sentiment_score=0.5,
        )
        assert -1.0 <= article.sentiment_score <= 1.0

    def test_analyzed_article_defaults(self):
        """Test default values for optional fields."""
        article = AnalyzedArticle(
            url="https://example.com/article",
            title="Test Title",
        )
        assert article.description is None
        assert article.source is None
        assert article.published_at is None
        assert article.summary == ""
        assert article.sentiment == "neutral"
        assert article.sentiment_score == 0.0
        assert article.analyzed_at is None
