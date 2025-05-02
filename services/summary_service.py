from typing import List
from clients.qdrant import scroll_qdrant
from models.schemas import FileMeta, FileResult
from utils.time import get_year_range


class ScrollSummaryService:
    @staticmethod
    async def get_by_date_range(start_ts: int, end_ts: int) -> List[FileMeta]:
        points = await scroll_qdrant(
            collection="transcriptSummary",
            scroll_filter={
                "must": [
                    {
                        "key": "timestamp",
                        "range": {
                            "gte": start_ts,
                            "lte": end_ts
                        }
                    }
                ]
            },
            limit=1000,
            order_by={"key": "timestamp", "direction": "desc"},
            with_payload=["metadata.file_name", "metadata.record_date"]
        )

        seen = set()
        unique_files = []
        for point in points:
            meta = point.get("payload", {}).get("metadata", {})
            fname = meta.get("file_name")
            if not fname or fname in seen:
                continue
            seen.add(fname)
            unique_files.append(FileMeta(
                file_name=fname,
                record_date=meta.get("record_date")
            ))

        return unique_files

    @staticmethod
    async def get_latest_n(count: int = 2) -> List[FileResult]:
        points = await scroll_qdrant(
            collection="transcriptSummary",
            scroll_filter={"must": []},
            limit=count,
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

    @staticmethod
    async def get_by_year(year: int) -> List[FileMeta]:
        start_ts, end_ts = get_year_range(year)

        points = await scroll_qdrant(
            collection="transcriptSummary",
            scroll_filter={
                "must": [
                    {
                        "key": "timestamp",
                        "range": {
                            "gte": start_ts,
                            "lte": end_ts
                        }
                    }
                ]
            },
            limit=2000,
            order_by={"key": "timestamp", "direction": "desc"},
            with_payload=["metadata.file_name", "metadata.record_date"]
        )

        seen = set()
        results = []
        for p in points:
            meta = p.get("payload", {}).get("metadata", {})
            fname = meta.get("file_name")
            if fname and fname not in seen:
                seen.add(fname)
                results.append(FileMeta(
                    file_name=fname,
                    record_date=meta.get("record_date")
                ))
        return results

