from fastapi import APIRouter, Query
from services.time_range_service import TimeRangeService
from models.schemas import FileMeta

router = APIRouter()

@router.get("/summaries-by-range", response_model=list[FileMeta])
async def summaries_by_range(
    start_ts: int = Query(..., description="Начало периода (Unix timestamp)"),
    end_ts: int = Query(..., description="Конец периода (Unix timestamp)")
):
    return await TimeRangeService.get_summaries_by_range(start_ts, end_ts)
