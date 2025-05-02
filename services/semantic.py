from typing import Dict
from models.schemas import UserQuery, FileResult
from clients.openai import get_embedding
from services.qdrant import search_qdrant


async def handle_semantic_search(request: UserQuery) -> Dict[str, list[FileResult]]:
    embedding = await get_embedding(request.query)

    results_summary = await search_qdrant("transcriptSummary", embedding, request.limit)
    results_raw = await search_qdrant("rawTranscript", embedding, request.limit)

    def process_results(results, collection: str) -> list[FileResult]:
        output = []
        for item in results:
            if item["score"] < request.min_score:
                continue

            payload = item.get("payload", {})
            meta = payload.get("metadata", {})
            output.append(FileResult(
                id=item["id"],
                score=item["score"],
                file_name=meta.get("file_name", ""),
                record_date=meta.get("record_date", ""),
                content=payload.get("pageContent", "")
            ))
        return sorted(output, key=lambda x: x.score, reverse=True)

    return {
        "transcriptSummary": process_results(results_summary, "transcriptSummary"),
        "rawTranscript": process_results(results_raw, "rawTranscript")
    }
