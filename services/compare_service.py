from typing import List
from fastapi import HTTPException
from models.schemas import FileResult, FileMeta
from services.document_service import FullDocumentService
from clients.qdrant import scroll_qdrant

MAX_FULL_CHARS = 2000
DEFAULT_COLLECTION = "transcriptSummary"


class CompareMeetingsService:
    @staticmethod
    async def compare_latest(collection: str = DEFAULT_COLLECTION) -> List[FileResult]:
        files = await CompareMeetingsService._select_files_for_comparison(collection)
        truncate = len(files) > 4

        result: List[FileResult] = []
        for file in files:
            full_doc = await FullDocumentService.load_full_document(
                collection=collection,
                file_name=file.file_name,
                truncate=truncate
            )
            if not truncate and len(full_doc.content) > MAX_FULL_CHARS:
                full_doc.content = full_doc.content[:MAX_FULL_CHARS] + "\n\n... (текст обрезан)"
            result.append(full_doc)

        return result

    @staticmethod
    async def fallback_latest_file_list(collection: str = DEFAULT_COLLECTION) -> List[FileMeta]:
        """
        Возвращает только file_name и record_date последних встреч (без content).
        Используется при ResponseTooLargeError или по запросу.
        """
        return await CompareMeetingsService._select_files_for_comparison(collection, meta_only=True)

    @staticmethod
    async def _select_files_for_comparison(
        collection: str,
        meta_only: bool = False
    ) -> List[FileMeta | FileResult]:
        """
        Общий метод для логики сравнения последних встреч.
        Если meta_only=True — возвращает FileMeta.
        Иначе возвращается список FileResult через full-document.
        """
        points = await scroll_qdrant(
            collection=collection,
            scroll_filter={},
            limit=1000,
            order_by={"key": "timestamp", "direction": "desc"},
            with_payload=["metadata.file_name", "metadata.record_date", "timestamp"]
        )

        # Группируем по timestamp
        files_by_ts = {}
        for p in points:
            meta = p.get("payload", {}).get("metadata", {})
            ts = p.get("payload", {}).get("timestamp")
            fname = meta.get("file_name")
            rdate = meta.get("record_date")
            if not fname or not ts:
                continue
            files_by_ts.setdefault(ts, []).append(FileMeta(file_name=fname, record_date=rdate))

        if not files_by_ts:
            raise HTTPException(status_code=404, detail="No data found")

        sorted_ts = sorted(files_by_ts.keys(), reverse=True)
        first_ts_files = files_by_ts[sorted_ts[0]]

        if len(first_ts_files) >= 2:
            selected = first_ts_files
        elif len(sorted_ts) > 1:
            selected = first_ts_files + files_by_ts[sorted_ts[1]]
        else:
            selected = first_ts_files

        # Уникальные file_name
        seen = set()
        unique_files = []
        for f in selected:
            if f.file_name not in seen:
                seen.add(f.file_name)
                unique_files.append(f)

        return unique_files if meta_only else unique_files  # дальше вызывается full-document в compare_latest
