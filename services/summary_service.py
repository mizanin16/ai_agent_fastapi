from typing import List
from models.schemas import FileResult
from clients.qdrant import scroll_qdrant


class ScrollSummaryService:
    @staticmethod
    async def get_by_date_range(start_ts: int, end_ts: int) -> List[FileResult]:
        points = await scroll_qdrant(
            collection="transcriptSummary",
            scroll_filter={
                "must": [{
                    "key": "timestamp",
                    "range": {"gte": start_ts, "lte": end_ts}
                }]
            },
            limit=100,
            order_by={"key": "timestamp", "direction": "desc"},
            with_payload=["metadata.file_name", "metadata.record_date", "content"]
        )

        return [
            FileResult(
                id=p["id"],
                score=1.0,
                file_name=p["payload"]["metadata"]["file_name"],
                record_date=p["payload"]["metadata"]["record_date"],
                content=p["payload"].get("content", "")
            )
            for p in points
        ]
