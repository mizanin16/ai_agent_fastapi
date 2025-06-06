from pydantic import BaseModel
from typing import List, Optional


class UserQuery(BaseModel):
    query: str
    limit: Optional[int] = 100
    min_score: Optional[float] = 0.4


class FileResult(BaseModel):
    id: str
    score: float
    file_name: str
    record_date: Optional[str]
    content: str
    collection_used: Optional[str] = None

class FileMeta(BaseModel):
    file_name: str
    record_date: Optional[str]

class AgentErrorLog(BaseModel):
    query: str
    error: str
    context: dict | None = None

class SearchResponse(BaseModel):
    transcriptSummary: List[FileResult]
    rawTranscript: List[FileResult]
