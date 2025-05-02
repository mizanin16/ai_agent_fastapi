from fastapi import HTTPException
from models.schemas import FileResult
from clients.qdrant import scroll_qdrant


class FullDocumentService:
    @staticmethod
    async def load_full_document(collection: str, file_name: str) -> FileResult:
        points = await scroll_qdrant(
            collection=collection,
            scroll_filter={
                "must": [{
                    "key": "metadata.file_name",
                    "match": {"text": file_name}
                }]
            },
            limit=100,
            with_payload=["metadata.file_name", "metadata.record_date", "content"]
        )

        if not points:
            raise HTTPException(status_code=404, detail=f"No data found for file_name '{file_name}'")

        sorted_points = sorted(
            points,
            key=lambda p: p["payload"].get("loc", {}).get("lines", {}).get("from", 0)
        )

        content = "\n".join(p["payload"].get("content", "") for p in sorted_points)
        meta = sorted_points[0]["payload"].get("metadata", {})

        return FileResult(
            id=file_name,
            score=1.0,
            file_name=meta.get("file_name", ""),
            record_date=meta.get("record_date", ""),
            content=content
        )
