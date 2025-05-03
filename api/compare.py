from fastapi import APIRouter, Query
from typing import List
from models.schemas import FileResult
from services.compare_service import CompareMeetingsService

router = APIRouter()

@router.get("/compare-latest", response_model=List[FileResult])
async def compare_latest(collection: str = Query("transcriptSummary", enum=["transcriptSummary", "rawTranscript"])):
    return await CompareMeetingsService.compare_last_meetings(collection)