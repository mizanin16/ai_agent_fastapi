from fastapi import HTTPException
from models.schemas import FileResult
from clients.qdrant import scroll_qdrant

COLLECTIONS = ["rawTranscript", "transcriptSummary"]
MAX_CONTENT_LENGTH = 5000


class FullDocumentService:
    @staticmethod
    async def load_full_document(collection: str, file_name: str, truncate: bool = True) -> FileResult:
        async def try_load(col: str) -> list[dict]:
            return await scroll_qdrant(
                collection=col,
                scroll_filter={
                    "must": [{
                        "key": "metadata.file_name",
                        "match": {
                            "text": file_name  # поддержка частичного поиска
                        }
                    }]
                },
                limit=100,
                with_payload=["metadata.file_name", "metadata.record_date", "content"]
            )

        # Попытка 1: основной запрос
        points = await try_load(collection)

        # Попытка 2: fallback, если ничего не найдено
        fallback_collection = next((col for col in COLLECTIONS if col != collection), None)
        if not points and fallback_collection:
            points = await try_load(fallback_collection)
            collection = fallback_collection  # используем новую коллекцию

        if not points:
            raise HTTPException(status_code=404, detail=f"No data found for file_name '{file_name}'")

        sorted_points = sorted(
            points,
            key=lambda p: p["payload"].get("loc", {}).get("lines", {}).get("from", 0)
        )

        content = "\n".join(p["payload"].get("content", "") for p in sorted_points)
        if truncate and len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "\n\n... (текст обрезан)"

        meta = sorted_points[0]["payload"].get("metadata", {})

        return FileResult(
            id=file_name,
            score=1.0,
            file_name=meta.get("file_name", ""),
            record_date=meta.get("record_date", ""),
            content=content,
            collection_used = collection

        )
