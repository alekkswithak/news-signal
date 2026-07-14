from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from app.domain.entities import AnalyzedArticle
from app.domain.repositories import IArticleRepository
from app.config import settings


class MongoArticleRepository(IArticleRepository):
    """MongoDB implementation of article repository."""

    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
        self._collection = None

    @property
    def collection(self):
        """Lazy initialization of collection."""
        if self._collection is None:
            self._collection = self.client[settings.mongodb_db_name]["analyzed_articles"]
        return self._collection

    async def save_analysis(self, article: AnalyzedArticle) -> None:
        """Save an analyzed article to MongoDB."""
        document = {
            "url": article.url,
            "title": article.title,
            "description": article.description,
            "source": article.source,
            "published_at": article.published_at,
            "summary": article.summary,
            "sentiment": article.sentiment,
            "sentiment_score": article.sentiment_score,
            "analyzed_at": article.analyzed_at,
        }
        await self.collection.insert_one(document)

    async def get_by_url(self, url: str) -> AnalyzedArticle | None:
        """Retrieve an analyzed article by URL."""
        doc = await self.collection.find_one({"url": url})
        if not doc:
            return None
        return self._document_to_entity(doc)

    async def get_all_analyzed_urls(self, urls: List[str]) -> set[str]:
        """Get set of URLs that have already been analyzed."""
        cursor = self.collection.find({"url": {"$in": urls}}, {"url": 1})
        docs = await cursor.to_list(length=len(urls))
        return {doc["url"] for doc in docs}

    async def get_history(self, limit: int) -> List[AnalyzedArticle]:
        """Get recent analyzed articles sorted by analysis date."""
        cursor = self.collection.find().sort("analyzed_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._document_to_entity(doc) for doc in docs]

    def _document_to_entity(self, doc: dict) -> AnalyzedArticle:
        """Convert MongoDB document to domain entity."""
        return AnalyzedArticle(
            url=doc["url"],
            title=doc["title"],
            description=doc.get("description"),
            source=doc.get("source"),
            published_at=doc.get("published_at"),
            summary=doc["summary"],
            sentiment=doc["sentiment"],
            sentiment_score=doc["sentiment_score"],
            analyzed_at=doc.get("analyzed_at"),
        )
