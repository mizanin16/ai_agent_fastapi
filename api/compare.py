from fastapi import APIRouter
from typing import List
from models.schemas import FileResult, FileMeta
from services.compare_service import CompareMeetingsService

router = APIRouter()

@router.get("/compare-latest", response_model=List[FileResult])
async def compare_latest(collection: str = "transcriptSummary"):
    return await CompareMeetingsService.compare_latest(collection)


@router.get("/compare-latest/fallback", response_model=List[FileMeta])
async def compare_latest_fallback(collection: str = "transcriptSummary"):
    return await CompareMeetingsService.fallback_latest_file_list(collection)
