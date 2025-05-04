from typing import List
from fastapi import HTTPException
from models.schemas import FileResult
from clients.qdrant import scroll_qdrant

COLLECTIONS = ["rawTranscript", "transcriptSummary"]
MAX_CONTENT_LENGTH = 5000


class FullDocumentService:
    @staticmethod
    async def load_full_document(collection: str, file_name: str, truncate: bool = True) -> FileResult:

        async def try_variants(col: str) -> list[dict]:
            # Попытка 1: без нормализации
            points = await scroll_qdrant(
                collection=col,
                scroll_filter={
                    "must": [{"key": "metadata.file_name", "match": {"text": file_name}}]
                },
                limit=100,
                with_payload=[
                    "metadata.file_name",
                    "metadata.record_date",
                    "metadata.loc",
                    "content"
                ]
            )
            if points:
                return points

            # Попытка 2: с нормализацией
            normalized = force_working_ij(file_name)
            if normalized != file_name:
                points = await scroll_qdrant(
                    collection=col,
                    scroll_filter={
                        "must": [{"key": "metadata.file_name", "match": {"text": normalized}}]
                    },
                    limit=100,
                    with_payload=[
                        "metadata.file_name",
                        "metadata.record_date",
                        "metadata.loc",
                        "content"
                    ]
                )
            return points

        # Попробовать сначала в указанной коллекции
        points = await try_variants(collection)

        # Если не найдено — попробовать в альтернативной коллекции
        if not points:
            alt_collection = next((c for c in COLLECTIONS if c != collection), None)
            if alt_collection:
                points = await try_variants(alt_collection)
                if points:
                    collection = alt_collection  # используем другую коллекцию

        if not points:
            raise HTTPException(status_code=404, detail=f"No data found for file_name '{file_name}'")

        # Правильная сортировка по loc.lines.from внутри metadata
        sorted_points = sorted(
            points,
            key=lambda p: p["payload"]
                .get("metadata", {})
                .get("loc", {})
                .get("lines", {})
                .get("from", 0)
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
            collection_used=collection
        )


def force_working_ij(text: str) -> str:
    return text.replace("й", "и\u0306").replace("Й", "И\u0306")
