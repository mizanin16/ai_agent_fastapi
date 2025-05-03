from clients.qdrant import scroll_qdrant
from models.schemas import FileResult
from collections import defaultdict


class CompareMeetingsService:

    @staticmethod
    async def compare_last_meetings(collection: str = "transcriptSummary") -> list[FileResult]:
        # Шаг 1: получить все timestamps
        points = await scroll_qdrant(
            collection=collection,
            scroll_filter={},
            limit=200,
            with_payload=["metadata.file_name", "metadata.record_date", "timestamp", "content"]
        )

        timestamps = defaultdict(list)
        for point in points:
            payload = point.get("payload", {})
            ts = payload.get("timestamp")
            if ts is not None:
                timestamps[ts].append(point)

        # Шаг 2: отсортировать timestamps по убыванию
        sorted_ts = sorted(timestamps.items(), key=lambda x: x[0], reverse=True)

        # Шаг 3: анализ последней даты
        latest_ts, latest_points = sorted_ts[0]
        if len(latest_points) >= 2:
            return CompareMeetingsService._to_file_results(latest_points)

        # Шаг 4: получить второй по времени `timestamp`
        if len(sorted_ts) > 1:
            second_ts, second_points = sorted_ts[1]
            return CompareMeetingsService._to_file_results(latest_points + second_points)

        return CompareMeetingsService._to_file_results(latest_points)

    @staticmethod
    def _to_file_results(points: list[dict]) -> list[FileResult]:
        results = []
        for p in points:
            payload = p.get("payload", {})
            meta = payload.get("metadata", {})
            results.append(FileResult(
                id=p.get("id", ""),
                score=1.0,
                file_name=meta.get("file_name", ""),
                record_date=meta.get("record_date", ""),
                content=payload.get("content", ""),
                collection_used=""  # optional
            ))
        return results
