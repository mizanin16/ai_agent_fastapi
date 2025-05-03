from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from services.topic_analyzer import TopicAnalyzerService
from models.schemas import FileMeta
from utils.time import get_year_range

router = APIRouter()


@router.get("/analyze-topics", response_model=List[FileMeta])
async def analyze_topics(
    year: Optional[int] = None,
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
    file_names: Optional[List[str]] = Query(default=None)
):
    if file_names:
        return await TopicAnalyzerService.analyze(file_names=file_names)

    if year is not None:
        start_ts, end_ts = get_year_range(year)
        return await TopicAnalyzerService.analyze(start_ts=start_ts, end_ts=end_ts)

    if start_ts is not None and end_ts is not None:
        return await TopicAnalyzerService.analyze(start_ts=start_ts, end_ts=end_ts)

    raise HTTPException(
        status_code=400,
        detail="Укажите либо year, либо диапазон start_ts/end_ts, либо file_names[]"
    )
