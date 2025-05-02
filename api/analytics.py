from fastapi import APIRouter, Query
from services.topic_analyzer import TopicAnalyzerService

router = APIRouter()

@router.get("/analyze-topics", response_model=list[str])
async def analyze_topics(year: int = Query(...)):
    return await TopicAnalyzerService.analyze_year(year)
