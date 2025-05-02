from typing import List
from fastapi import APIRouter

from services.topic_analyzer import TopicAnalyzerService
from models.schemas import FileMeta

router = APIRouter()


@router.get("/analyze-topics", response_model=List[FileMeta])
async def analyze_topics(year: int):
    return await TopicAnalyzerService.analyze_year(year)
