from clients.qdrant import scroll_qdrant
from models.schemas import FileMeta

class TimeRangeService:
    @staticmethod
    async def get_summaries_by_range(from_ts: int, to_ts: int) -> list[FileMeta]:
        points = await scroll_qdrant(
            collection="transcriptSummary",
            scroll_filter={
                "must": [{
                    "key": "timestamp",
                    "range": {
                        "gte": from_ts,
                        "lte": to_ts
                    }
                }]
            },
            limit=100,
            with_payload=["metadata.file_name", "metadata.record_date"]
        )

        seen = set()
        result = []

        for p in points:
            meta = p.get("payload", {}).get("metadata", {})
            fname = meta.get("file_name")
            if fname and fname not in seen:
                seen.add(fname)
                result.append(FileMeta(
                    file_name=fname,
                    record_date=meta.get("record_date", "")
                ))

        return result
