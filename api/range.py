from fastapi import APIRouter, Query
from services.time_range_service import TimeRangeService
from models.schemas import FileMeta

router = APIRouter()

@router.get("/summaries-by-range", response_model=list[FileMeta])
async def summaries_by_range(
    from_timestamp: int = Query(..., description="Начало периода (Unix timestamp)"),
    to_timestamp: int = Query(..., description="Конец периода (Unix timestamp)")
):
    return await TimeRangeService.get_summaries_by_range(from_timestamp, to_timestamp)
