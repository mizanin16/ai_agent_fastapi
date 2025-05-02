from fastapi import APIRouter, Query
from models.schemas import FileResult
from services.document import get_full_document

router = APIRouter()

@router.get("/full-document", response_model=FileResult)
async def full_document(file_name: str = Query(...), collection: str = Query(...)):
    return await get_full_document(collection, file_name)
