from typing import List, Optional
from models.schemas import FileResult, FileMeta
from clients.qdrant import scroll_qdrant
from services.document_service import FullDocumentService


class TopicAnalyzerService:
    @staticmethod
    async def analyze(
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
        file_names: Optional[List[str]] = None
    ) -> List[FileResult | FileMeta]:
        if not file_names and (start_ts is None or end_ts is None):
            raise ValueError("Either file_names or both start_ts and end_ts must be provided")

        # 🧩 Сценарий 1: Выдан список файлов — вернуть контент
        if file_names:
            results: List[FileResult] = []
            for fname in file_names:
                try:
                    document = await FullDocumentService.load_full_document(
                        collection="transcriptSummary",
                        file_name=fname,
                        truncate=True
                    )
                    results.append(document)
                except Exception:
                    continue  # Пропустить, если файл не найден
            return results

        # 🧩 Сценарий 2: Временной диапазон — вернуть только мета-данные
        points = await scroll_qdrant(
            collection="transcriptSummary",
            scroll_filter={
                "must": [{
                    "key": "timestamp",
                    "range": {"gte": start_ts, "lte": end_ts}
                }]
            },
            limit=5000,
            order_by={"key": "timestamp", "direction": "desc"},
            with_payload=["metadata.file_name", "metadata.record_date"]
        )

        seen = set()
        result: List[FileMeta] = []

        for point in points:
            meta = point.get("payload", {}).get("metadata", {})
            fname = meta.get("file_name")
            if not fname or fname in seen:
                continue
            seen.add(fname)
            result.append(FileMeta(
                file_name=fname,
                record_date=meta.get("record_date")
            ))

        return result
