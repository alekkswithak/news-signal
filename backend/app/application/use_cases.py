from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException
from app.domain.entities import Article, AnalyzedArticle
from app.domain.repositories import IArticleRepository, INewsService, IAIService
from app.application.dtos import ArticleSearchResultDTO, AnalyzeRequestDTO, AnalyzedArticleDTO


class SearchArticlesUseCase:
    """Use case for searching articles and checking analysis status."""

    def __init__(
        self,
        news_service: INewsService,
        article_repository: IArticleRepository,
    ):
        self.news_service = news_service
        self.article_repository = article_repository

    async def execute(self, query: str, max_results: int = 10) -> List[ArticleSearchResultDTO]:
        """Search articles and flag which ones are already analyzed."""
        articles = await self.news_service.search_articles(query, max_results)
        urls = [article.url for article in articles]
        analyzed_urls = await self.article_repository.get_all_analyzed_urls(urls)

        dtos = []
        for article in articles:
            dto = ArticleSearchResultDTO(
                url=article.url,
                title=article.title,
                description=article.description,
                source=article.source,
                image=article.image,
                published_at=article.published_at,
                already_analyzed=article.url in analyzed_urls,
            )
            dtos.append(dto)

        return dtos


class AnalyzeArticleUseCase:
    """Use case for analyzing articles with caching."""

    def __init__(
        self,
        article_repository: IArticleRepository,
        ai_service: IAIService,
    ):
        self.article_repository = article_repository
        self.ai_service = ai_service

    async def execute(self, request: AnalyzeRequestDTO) -> AnalyzedArticleDTO:
        """Analyze an article, using cached results if available."""
        # Check for cached analysis
        cached = await self.article_repository.get_by_url(request.url)
        if cached:
            return self._entity_to_dto(cached, from_cache=True)

        # Perform new analysis
        analysis_result = await self.ai_service.analyze_article(
            request.title, request.description
        )

        # Create domain entity
        analyzed_article = AnalyzedArticle(
            url=request.url,
            title=request.title,
            description=request.description,
            source=request.source,
            published_at=request.published_at,
            summary=analysis_result["summary"],
            sentiment=analysis_result["sentiment"],
            sentiment_score=analysis_result["sentiment_score"],
            analyzed_at=datetime.now(timezone.utc),
        )

        # Save to repository
        try:
            await self.article_repository.save_analysis(analyzed_article)
        except Exception:
            # Handle race condition: another request may have analyzed first
            cached = await self.article_repository.get_by_url(request.url)
            if cached:
                return self._entity_to_dto(cached, from_cache=True)
            raise HTTPException(status_code=500, detail="Could not save analysis")

        return self._entity_to_dto(analyzed_article, from_cache=False)

    def _entity_to_dto(self, entity: AnalyzedArticle, from_cache: bool) -> AnalyzedArticleDTO:
        """Convert domain entity to DTO."""
        return AnalyzedArticleDTO(
            url=entity.url,
            title=entity.title,
            description=entity.description,
            source=entity.source,
            published_at=entity.published_at,
            summary=entity.summary,
            sentiment=entity.sentiment,
            sentiment_score=entity.sentiment_score,
            analyzed_at=entity.analyzed_at or datetime.now(timezone.utc),
            from_cache=from_cache,
        )


class GetAnalysisHistoryUseCase:
    """Use case for retrieving analysis history."""

    def __init__(self, article_repository: IArticleRepository):
        self.article_repository = article_repository

    async def execute(self, limit: int = 50) -> List[AnalyzedArticleDTO]:
        """Get recent analyzed articles."""
        articles = await self.article_repository.get_history(limit)
        return [self._entity_to_dto(article) for article in articles]

    def _entity_to_dto(self, entity: AnalyzedArticle) -> AnalyzedArticleDTO:
        """Convert domain entity to DTO."""
        return AnalyzedArticleDTO(
            url=entity.url,
            title=entity.title,
            description=entity.description,
            source=entity.source,
            published_at=entity.published_at,
            summary=entity.summary,
            sentiment=entity.sentiment,
            sentiment_score=entity.sentiment_score,
            analyzed_at=entity.analyzed_at or datetime.now(timezone.utc),
            from_cache=False,
        )
