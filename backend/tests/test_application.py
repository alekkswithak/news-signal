import pytest
from datetime import datetime, timezone
from app.application.dtos import ArticleSearchResultDTO, AnalyzeRequestDTO, AnalyzedArticleDTO
from app.application.use_cases import (
    SearchArticlesUseCase,
    AnalyzeArticleUseCase,
    GetAnalysisHistoryUseCase,
)


class TestSearchArticlesUseCase:
    """Tests for SearchArticlesUseCase."""

    @pytest.mark.asyncio
    async def test_search_articles_success(
        self, mock_news_service, mock_article_repository, sample_article
    ):
        """Test successful article search."""
        mock_news_service.set_articles([sample_article])
        use_case = SearchArticlesUseCase(mock_news_service, mock_article_repository)

        results = await use_case.execute("test query")

        assert len(results) == 1
        assert results[0].url == sample_article.url
        assert results[0].title == sample_article.title
        assert results[0].already_analyzed is False

    @pytest.mark.asyncio
    async def test_search_articles_with_analyzed(
        self, mock_news_service, mock_article_repository, sample_analyzed_article
    ):
        """Test search with already analyzed articles."""
        mock_news_service.set_articles([sample_analyzed_article])
        await mock_article_repository.save_analysis(sample_analyzed_article)
        use_case = SearchArticlesUseCase(mock_news_service, mock_article_repository)

        results = await use_case.execute("test query")

        assert len(results) == 1
        assert results[0].already_analyzed is True

    @pytest.mark.asyncio
    async def test_search_articles_empty_results(
        self, mock_news_service, mock_article_repository
    ):
        """Test search with no results."""
        mock_news_service.set_articles([])
        use_case = SearchArticlesUseCase(mock_news_service, mock_article_repository)

        results = await use_case.execute("test query")

        assert len(results) == 0


class TestAnalyzeArticleUseCase:
    """Tests for AnalyzeArticleUseCase."""

    @pytest.mark.asyncio
    async def test_analyze_article_new(
        self, mock_ai_service, mock_article_repository, sample_analyzed_article
    ):
        """Test analyzing a new article."""
        mock_ai_service.set_response({
            "summary": "Test summary",
            "sentiment": "positive",
            "sentiment_score": 0.8,
        })
        use_case = AnalyzeArticleUseCase(mock_article_repository, mock_ai_service)

        request = AnalyzeRequestDTO(
            url="https://example.com/new",
            title="New Article",
            description="New description",
        )

        result = await use_case.execute(request)

        assert result.url == "https://example.com/new"
        assert result.summary == "Test summary"
        assert result.sentiment == "positive"
        assert result.sentiment_score == 0.8
        assert result.from_cache is False

    @pytest.mark.asyncio
    async def test_analyze_article_from_cache(
        self, mock_ai_service, mock_article_repository, sample_analyzed_article
    ):
        """Test analyzing an article that's already cached."""
        await mock_article_repository.save_analysis(sample_analyzed_article)
        use_case = AnalyzeArticleUseCase(mock_article_repository, mock_ai_service)

        request = AnalyzeRequestDTO(
            url=sample_analyzed_article.url,
            title="Title",
            description="Description",
        )

        result = await use_case.execute(request)

        assert result.from_cache is True
        assert result.summary == sample_analyzed_article.summary

    @pytest.mark.asyncio
    async def test_analyze_article_race_condition(
        self, mock_ai_service, mock_article_repository, sample_analyzed_article
    ):
        """Test handling race condition when saving."""
        call_count = 0

        async def failing_save(article):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Simulated race condition")
            await mock_article_repository._storage.__setitem__(article.url, article)

        mock_article_repository.save_analysis = failing_save
        await mock_article_repository.save_analysis(sample_analyzed_article)
        mock_ai_service.set_response({
            "summary": "Test summary",
            "sentiment": "neutral",
            "sentiment_score": 0.0,
        })
        use_case = AnalyzeArticleUseCase(mock_article_repository, mock_ai_service)

        request = AnalyzeRequestDTO(
            url=sample_analyzed_article.url,
            title="Title",
            description="Description",
        )

        result = await use_case.execute(request)

        assert result.from_cache is True


class TestGetAnalysisHistoryUseCase:
    """Tests for GetAnalysisHistoryUseCase."""

    @pytest.mark.asyncio
    async def test_get_history_empty(self, mock_article_repository):
        """Test getting history when empty."""
        use_case = GetAnalysisHistoryUseCase(mock_article_repository)

        results = await use_case.execute(10)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_get_history_with_articles(
        self, mock_article_repository, sample_analyzed_article
    ):
        """Test getting history with articles."""
        await mock_article_repository.save_analysis(sample_analyzed_article)
        use_case = GetAnalysisHistoryUseCase(mock_article_repository)

        results = await use_case.execute(10)

        assert len(results) == 1
        assert results[0].url == sample_analyzed_article.url

    @pytest.mark.asyncio
    async def test_get_history_limit(
        self, mock_article_repository, sample_analyzed_article
    ):
        """Test history limit is respected."""
        for i in range(5):
            article = sample_analyzed_article.model_copy(
                update={"url": f"https://example.com/article{i}"}
            )
            await mock_article_repository.save_analysis(article)

        use_case = GetAnalysisHistoryUseCase(mock_article_repository)

        results = await use_case.execute(3)

        assert len(results) == 3
