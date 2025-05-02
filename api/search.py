from fastapi import APIRouter
from typing import List
from models.schemas import UserQuery, SearchResponse, FileMeta
from services.semantic_search import SemanticSearchService

router = APIRouter()

@router.post("/semantic-search", response_model=SearchResponse)
async def semantic_search(query: UserQuery):
    result = await SemanticSearchService.search(query)
    return SearchResponse(**result)

@router.post("/semantic-search/fallback", response_model=List[FileMeta])
async def semantic_search_fallback(request: UserQuery):
    return await SemanticSearchService.search_unique_files_only(request)