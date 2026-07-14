import pytest
import respx
from app.infrastructure.external_services.gnews_service import GNewsService
from app.infrastructure.external_services.openai_service import OpenAIService


class TestGNewsService:
    """Tests for GNewsService."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_articles_success(self):
        """Test successful article search."""
        mock_response = {
            "articles": [
                {
                    "url": "https://example.com/article1",
                    "title": "Test Article 1",
                    "description": "Test description 1",
                    "source": {"name": "Test Source"},
                    "image": "https://example.com/image1.jpg",
                    "publishedAt": "2024-01-01T12:00:00Z",
                },
                {
                    "url": "https://example.com/article2",
                    "title": "Test Article 2",
                    "description": "Test description 2",
                    "source": {"name": "Another Source"},
                    "image": "https://example.com/image2.jpg",
                    "publishedAt": "2024-01-01T13:00:00Z",
                },
            ]
        }

        respx.get("https://gnews.io/api/v4/search").mock(
            return_value=respx.Response(200, json=mock_response)
        )

        service = GNewsService()
        results = await service.search_articles("test query", max_results=10)

        assert len(results) == 2
        assert results[0].url == "https://example.com/article1"
        assert results[0].title == "Test Article 1"
        assert results[0].source == "Test Source"

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_articles_empty_results(self):
        """Test search with no results."""
        mock_response = {"articles": []}

        respx.get("https://gnews.io/api/v4/search").mock(
            return_value=respx.Response(200, json=mock_response)
        )

        service = GNewsService()
        results = await service.search_articles("test query")

        assert len(results) == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_articles_http_error(self):
        """Test handling HTTP errors from GNews."""
        respx.get("https://gnews.io/api/v4/search").mock(
            return_value=respx.Response(500)
        )

        service = GNewsService()
        with pytest.raises(Exception) as exc_info:
            await service.search_articles("test query")
        assert "News provider error" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_articles_request_error(self):
        """Test handling request errors."""
        respx.get("https://gnews.io/api/v4/search").mock(side_effect=Exception("Network error"))

        service = GNewsService()
        with pytest.raises(Exception) as exc_info:
            await service.search_articles("test query")
        assert "Could not reach news provider" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_articles_max_results(self):
        """Test max_results parameter is respected."""
        mock_response = {
            "articles": [
                {"url": f"https://example.com/article{i}", "title": f"Article {i}"}
                for i in range(20)
            ]
        }

        respx.get("https://gnews.io/api/v4/search").mock(
            return_value=respx.Response(200, json=mock_response)
        )

        service = GNewsService()
        results = await service.search_articles("test query", max_results=5)

        assert len(results) == 5


class TestOpenAIService:
    """Tests for OpenAIService."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_analyze_article_success(self):
        """Test successful article analysis."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"summary": "Test summary", "sentiment": "positive", "sentiment_score": 0.8}'
                    }
                }
            ]
        }

        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=respx.Response(200, json=mock_response)
        )

        service = OpenAIService()
        result = await service.analyze_article("Test Title", "Test Description")

        assert result["summary"] == "Test summary"
        assert result["sentiment"] == "positive"
        assert result["sentiment_score"] == 0.8

    @pytest.mark.asyncio
    @respx.mock
    async def test_analyze_article_with_none_description(self):
        """Test analysis with None description."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"summary": "Test summary", "sentiment": "neutral", "sentiment_score": 0.0}'
                    }
                }
            ]
        }

        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=respx.Response(200, json=mock_response)
        )

        service = OpenAIService()
        result = await service.analyze_article("Test Title", None)

        assert result["summary"] == "Test summary"
        assert result["sentiment"] == "neutral"

    @pytest.mark.asyncio
    @respx.mock
    async def test_analyze_article_api_error(self):
        """Test handling OpenAI API errors."""
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=respx.Response(500)
        )

        service = OpenAIService()
        with pytest.raises(Exception) as exc_info:
            await service.analyze_article("Test Title", "Test Description")
        assert "AI provider error" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_analyze_article_invalid_json(self):
        """Test handling invalid JSON response."""
        mock_response = {
            "choices": [
                {"message": {"content": "This is not valid JSON"}}
            ]
        }

        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=respx.Response(200, json=mock_response)
        )

        service = OpenAIService()
        with pytest.raises(Exception) as exc_info:
            await service.analyze_article("Test Title", "Test Description")
        assert "AI returned an unparseable response" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_analyze_article_missing_fields(self):
        """Test handling response with missing fields."""
        mock_response = {
            "choices": [
                {"message": {"content": '{"summary": "Test summary"}'}}
            ]
        }

        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=respx.Response(200, json=mock_response)
        )

        service = OpenAIService()
        with pytest.raises(Exception) as exc_info:
            await service.analyze_article("Test Title", "Test Description")
        assert "AI returned an unparseable response" in str(exc_info.value)
