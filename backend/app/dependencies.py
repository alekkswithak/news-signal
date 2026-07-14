from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from app.config import settings
from app.infrastructure.persistence.mongodb_article_repository import MongoArticleRepository
from app.infrastructure.external_services.gnews_service import GNewsService
from app.infrastructure.external_services.openai_service import OpenAIService
from app.application.use_cases import (
    SearchArticlesUseCase,
    AnalyzeArticleUseCase,
    GetAnalysisHistoryUseCase,
)


# Database client singleton
_mongo_client: AsyncIOMotorClient | None = None


async def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create MongoDB client."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.mongodb_uri, tz_aware=True)
    return _mongo_client


async def close_mongo_client():
    """Close MongoDB connection."""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None


# Repository dependencies
async def get_article_repository(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> MongoArticleRepository:
    """Get article repository instance."""
    return MongoArticleRepository(client)


# Service dependencies
def get_news_service() -> GNewsService:
    """Get news service instance."""
    return GNewsService()


def get_ai_service() -> OpenAIService:
    """Get AI service instance."""
    return OpenAIService()


# Use case dependencies
async def get_search_articles_use_case(
    news_service: GNewsService = Depends(get_news_service),
    article_repository: MongoArticleRepository = Depends(get_article_repository),
) -> SearchArticlesUseCase:
    """Get search articles use case instance."""
    return SearchArticlesUseCase(news_service, article_repository)


async def get_analyze_article_use_case(
    article_repository: MongoArticleRepository = Depends(get_article_repository),
    ai_service: OpenAIService = Depends(get_ai_service),
) -> AnalyzeArticleUseCase:
    """Get analyze article use case instance."""
    return AnalyzeArticleUseCase(article_repository, ai_service)


async def get_analysis_history_use_case(
    article_repository: MongoArticleRepository = Depends(get_article_repository),
) -> GetAnalysisHistoryUseCase:
    """Get analysis history use case instance."""
    return GetAnalysisHistoryUseCase(article_repository)
