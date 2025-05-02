from fastapi import APIRouter
from models.schemas import UserQuery, SearchResponse
from services.semantic import handle_semantic_search

router = APIRouter()

@router.post("/semantic-search", response_model=SearchResponse)
async def semantic_search(query: UserQuery):
    results = await handle_semantic_search(query)
    return SearchResponse(**results)
