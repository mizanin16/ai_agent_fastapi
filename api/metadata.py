from fastapi import APIRouter, Query
from models.schemas import FileResult
from services.summary_service import ScrollSummaryService
from utils.time import get_month_range

router = APIRouter()

@router.get("/summaries-by-month", response_model=list[FileResult])
async def summaries_by_month(year: int, month: int):
    start_ts, end_ts = get_month_range(year, month)
    return await ScrollSummaryService.get_by_date_range(start_ts, end_ts)
