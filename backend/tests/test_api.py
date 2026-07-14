import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_mongo_client, close_mongo_client
from mongomock import MongoClient


@pytest.fixture
def mock_mongo_client():
    """Mock MongoDB client for testing."""
    return MongoClient()


@pytest.fixture
def override_dependencies(mock_mongo_client):
    """Override dependencies for testing."""
    app.dependency_overrides[get_mongo_client] = lambda: mock_mongo_client
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_dependencies):
    """Create test client with overridden dependencies."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns ok status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestSearchArticlesEndpoint:
    """Tests for article search endpoint."""

    def test_search_articles_missing_query(self, client):
        """Test search without query parameter."""
        response = client.get("/api/articles/search")
        assert response.status_code == 422  # Validation error


class TestAnalyzeArticleEndpoint:
    """Tests for article analysis endpoint."""

    def test_analyze_article_missing_payload(self, client):
        """Test analyze without payload."""
        response = client.post("/api/articles/analyze")
        assert response.status_code == 422  # Validation error

    def test_analyze_article_invalid_payload(self, client):
        """Test analyze with invalid payload."""
        response = client.post("/api/articles/analyze", json={"invalid": "data"})
        assert response.status_code == 422  # Validation error


class TestHistoryEndpoint:
    """Tests for analysis history endpoint."""

    def test_history_default_limit(self, client):
        """Test history with default limit."""
        response = client.get("/api/articles/history")
        assert response.status_code == 200
        assert response.json() == []

    def test_history_custom_limit(self, client):
        """Test history with custom limit."""
        response = client.get("/api/articles/history?limit=10")
        assert response.status_code == 200
        assert response.json() == []

    def test_history_invalid_limit_too_low(self, client):
        """Test history with limit below minimum."""
        response = client.get("/api/articles/history?limit=0")
        assert response.status_code == 422  # Validation error

    def test_history_invalid_limit_too_high(self, client):
        """Test history with limit above maximum."""
        response = client.get("/api/articles/history?limit=500")
        assert response.status_code == 422  # Validation error
