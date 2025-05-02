from typing import Dict, List
from models.schemas import UserQuery, FileResult, FileMeta
from clients.openai import get_embedding
from clients.qdrant import search_qdrant


class SemanticSearchService:
    @staticmethod
    async def search(request: UserQuery) -> Dict[str, list[FileResult]]:
        embedding = await get_embedding(request.query)

        results_summary = await search_qdrant("transcriptSummary", embedding, request.limit)
        results_raw = await search_qdrant("rawTranscript", embedding, request.limit)

        def process_results(points: list[dict]) -> list[FileResult]:
            output = []
            for item in points:
                if item["score"] < request.min_score:
                    continue

                payload = item.get("payload", {})
                meta = payload.get("metadata", {})

                output.append(FileResult(
                    id=item["id"],
                    score=item["score"],
                    file_name=meta.get("file_name", ""),
                    record_date=meta.get("record_date", ""),
                    content=payload.get("content", "")
                ))
            return sorted(output, key=lambda x: x.score, reverse=True)

        return {
            "transcriptSummary": process_results(results_summary),
            "rawTranscript": process_results(results_raw)
        }

    @staticmethod
    async def search_unique_files_only(request: UserQuery) -> List[FileMeta]:
        embedding = await get_embedding(request.query)

        results_raw = await search_qdrant("rawTranscript", embedding, request.limit)
        results_summary = await search_qdrant("transcriptSummary", embedding, request.limit)

        all_results = results_raw + results_summary
        all_results = [r for r in all_results if r["score"] >= request.min_score]

        grouped = {}
        for item in all_results:
            meta = item.get("payload", {}).get("metadata", {})
            fname = meta.get("file_name")
            if not fname:
                continue
            if fname not in grouped or item["score"] > grouped[fname]["score"]:
                grouped[fname] = {
                    "file_name": fname,
                    "record_date": meta.get("record_date"),
                    "score": item["score"]
                }

        # сортируем по score ↓
        sorted_files = sorted(grouped.values(), key=lambda x: x["score"], reverse=True)

        return [FileMeta(file_name=f["file_name"], record_date=f["record_date"]) for f in sorted_files]
