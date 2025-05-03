from typing import List
from fastapi import HTTPException
from models.schemas import FileResult
from services.document_service import FullDocumentService
from clients.qdrant import scroll_qdrant

MAX_FULL_CHARS = 2000
DEFAULT_COLLECTION = "transcriptSummary"


class CompareMeetingsService:
    @staticmethod
    async def compare_latest(collection: str = DEFAULT_COLLECTION) -> List[FileResult]:
        # 1. Получаем все точки, отсортированные по timestamp ↓
        points = await scroll_qdrant(
            collection=collection,
            scroll_filter={},  # нет фильтра — получаем все
            limit=1000,
            order_by={"key": "timestamp", "direction": "desc"},
            with_payload=["metadata.file_name", "metadata.record_date", "timestamp"]
        )

        # 2. Группировка по file_name и извлечение даты
        files_by_date = {}
        for p in points:
            meta = p.get("payload", {}).get("metadata", {})
            fname = meta.get("file_name")
            rdate = meta.get("record_date")
            ts = p.get("payload", {}).get("timestamp")
            if not fname or not ts:
                continue
            files_by_date.setdefault(ts, []).append({
                "file_name": fname,
                "record_date": rdate,
            })

        if not files_by_date:
            raise HTTPException(status_code=404, detail="No data found")

        # 3. Сортировка по timestamp ↓
        sorted_timestamps = sorted(files_by_date.keys(), reverse=True)

        # 4. Логика: если на последней дате >= 2 файлов → берём их. Иначе → берём следующую дату.
        first_ts = sorted_timestamps[0]
        first_files = files_by_date[first_ts]

        if len(first_files) >= 2:
            combined_files = first_files
        else:
            if len(sorted_timestamps) < 2:
                raise HTTPException(status_code=404, detail="Not enough data for comparison")
            second_ts = sorted_timestamps[1]
            combined_files = first_files + files_by_date[second_ts]

        # 🔧 4.1. Удаление дубликатов по file_name
        seen = set()
        selected_files = []
        for f in combined_files:
            if f["file_name"] not in seen:
                selected_files.append(f)
                seen.add(f["file_name"])
        # 5. Получение content из FullDocumentService
        truncate = True if len(selected_files) <= 4 else False
        max_length = MAX_FULL_CHARS if not truncate else None

        result: List[FileResult] = []
        for file in selected_files:
            full_doc = await FullDocumentService.load_full_document(
                collection=collection,
                file_name=file["file_name"],
                truncate=truncate
            )
            if max_length and len(full_doc.content) > max_length:
                full_doc.content = full_doc.content[:max_length] + "\n\n... (текст обрезан)"
            result.append(full_doc)

        return result
