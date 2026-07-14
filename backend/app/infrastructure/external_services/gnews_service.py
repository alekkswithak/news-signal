import httpx
from typing import List
from fastapi import HTTPException
from app.domain.entities import Article
from app.domain.repositories import INewsService
from app.config import settings


class GNewsService(INewsService):
    """GNews implementation of news service."""

    async def search_articles(self, query: str, max_results: int = 10) -> List[Article]:
        """Search recent news articles via GNews."""
        params = {
            "q": query,
            "lang": "en",
            "max": max_results,
            "apikey": settings.gnews_api_key,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{settings.gnews_base_url}/search", params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"News provider error: {exc.response.status_code}",
                ) from exc
            except httpx.RequestError as exc:
                raise HTTPException(status_code=502, detail="Could not reach news provider") from exc

        payload = response.json()
        articles = []
        for item in payload.get("articles", []):
            articles.append(
                Article(
                    url=item.get("url"),
                    title=item.get("title", ""),
                    description=item.get("description"),
                    source=(item.get("source") or {}).get("name"),
                    image=item.get("image"),
                    published_at=item.get("publishedAt"),
                )
            )
        return articles
