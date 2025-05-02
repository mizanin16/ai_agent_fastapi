from typing import List
from models.schemas import FileMeta
from utils.time import get_year_range
from clients.qdrant import scroll_qdrant


class TopicAnalyzerService:
    @staticmethod
    async def analyze_year(year: int) -> List[FileMeta]:
        start_ts, end_ts = get_year_range(year)

        points = await scroll_qdrant(
            collection="transcriptSummary",
            scroll_filter={
                "must": [{
                    "key": "timestamp",
                    "range": {"gte": start_ts, "lte": end_ts}
                }]
            },
            limit=1000,
            order_by={"key": "timestamp", "direction": "desc"},
            with_payload=["metadata.file_name", "metadata.record_date"]
        )

        seen = set()
        result = []

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
