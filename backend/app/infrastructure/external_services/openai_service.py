import json
from openai import AsyncOpenAI
from fastapi import HTTPException
from app.domain.repositories import IAIService
from app.config import settings


class OpenAIService(IAIService):
    """OpenAI implementation of AI analysis service."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    SYSTEM_PROMPT = """You are a news analysis assistant. Given an article's title and \
description, respond with ONLY a JSON object (no markdown, no prose) matching this \
exact shape:

{"summary": "<2-3 sentence neutral summary>", "sentiment": "positive|neutral|negative", \
"sentiment_score": <float between -1.0 and 1.0>}

sentiment_score should be -1.0 for very negative, 0.0 for neutral, 1.0 for very positive, \
and should agree with the sentiment label."""

    async def analyze_article(self, title: str, description: str | None) -> dict:
        """Analyze an article and return summary and sentiment."""
        content = f"Title: {title}\nDescription: {description or '(no description available)'}"

        try:
            response = await self._client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"AI provider error: {exc}") from exc

        raw = response.choices[0].message.content
        try:
            parsed = json.loads(raw)
            return {
                "summary": parsed["summary"],
                "sentiment": parsed["sentiment"],
                "sentiment_score": float(parsed["sentiment_score"]),
            }
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            raise HTTPException(status_code=502, detail="AI returned an unparseable response") from exc
