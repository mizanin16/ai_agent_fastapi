from typing import List, Optional
from models.schemas import FileMeta
from clients.qdrant import scroll_qdrant


class TopicAnalyzerService:
    @staticmethod
    async def analyze(
            start_ts: Optional[int] = None,
            end_ts: Optional[int] = None,
            file_names: Optional[List[str]] = None
    ) -> List[FileMeta]:

        if not file_names and (start_ts is None or end_ts is None):
            raise ValueError("Either file_names or both start_ts and end_ts must be provided")

        if file_names:
            must_conditions = [{
                "key": "metadata.file_name",
                "match": {"any": file_names}
            }]
        else:
            must_conditions = [{
                "key": "timestamp",
                "range": {
                    "gte": start_ts,
                    "lte": end_ts
                }
            }]

        points = await scroll_qdrant(
            collection="transcriptSummary",
            scroll_filter={"must": must_conditions},
            limit=5000,
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
