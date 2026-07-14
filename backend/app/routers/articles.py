from typing import Annotated
from fastapi import APIRouter, Depends, Query
from app.application.dtos import ArticleSearchResultDTO, AnalyzeRequestDTO, AnalyzedArticleDTO
from app.application.use_cases import (
    SearchArticlesUseCase,
    AnalyzeArticleUseCase,
    GetAnalysisHistoryUseCase,
)
from app.dependencies import (
    get_search_articles_use_case,
    get_analyze_article_use_case,
    get_analysis_history_use_case,
)

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("/search", response_model=list[ArticleSearchResultDTO])
async def search(
    search_use_case: Annotated[SearchArticlesUseCase, Depends(get_search_articles_use_case)],
    q: str = Query(..., min_length=1),
):
    return await search_use_case.execute(q)


@router.post("/analyze", response_model=AnalyzedArticleDTO)
async def analyze(
    analyze_use_case: Annotated[AnalyzeArticleUseCase, Depends(get_analyze_article_use_case)],
    payload: AnalyzeRequestDTO,
):
    return await analyze_use_case.execute(payload)


@router.get("/history", response_model=list[AnalyzedArticleDTO])
async def history(
    history_use_case: Annotated[GetAnalysisHistoryUseCase, Depends(get_analysis_history_use_case)],
    limit: int = Query(50, ge=1, le=200),
):
    return await history_use_case.execute(limit)
