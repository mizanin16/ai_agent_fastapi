from fastapi import APIRouter
from models.schemas import UserQuery, SearchResponse
from services.semantic_search import SemanticSearchService

router = APIRouter()

@router.post("/semantic-search", response_model=SearchResponse)
async def semantic_search(query: UserQuery):
    result = await SemanticSearchService.search(query)
    return SearchResponse(**result)
