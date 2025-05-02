from fastapi import APIRouter, Query
from services.document_service import FullDocumentService
from models.schemas import FileResult

router = APIRouter()

@router.get("/full-document", response_model=FileResult)
async def full_document(
    file_name: str = Query(...),
    collection: str = Query(...),
    truncate: bool = Query(True)
):
    return await FullDocumentService.load_full_document(collection, file_name, truncate)
