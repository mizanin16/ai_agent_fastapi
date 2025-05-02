import os
import httpx
from typing import List

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_KEY = os.getenv("QDRANT_API_KEY")

HEADERS = {
    "api-key": QDRANT_KEY,
    "Content-Type": "application/json"
}

async def search_qdrant(collection: str, vector: List[float], limit: int) -> List[dict]:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{QDRANT_HOST}/collections/{collection}/points/search",
            headers=HEADERS,
            json={
                "vector": vector,
                "limit": limit,
                "with_payload": ["metadata.file_name", "metadata.record_date", "content"]
            }
        )
        res.raise_for_status()
        return res.json()["result"]

async def scroll_by_file_name_sorted(collection: str, file_name: str, limit: int = 100) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{QDRANT_HOST}/collections/{collection}/points/scroll",
            headers={
                "api-key": QDRANT_KEY,
                "Content-Type": "application/json"
            },
            json={
                "limit": limit,
                "filter": {
                    "must": [
                        {
                            "key": "metadata.file_name",
                            "match": {"value": file_name}
                        }
                    ]
                },
                "with_payload": True
            }
        )
        res.raise_for_status()
        points = res.json()["result"]["points"]

        # сортировка по loc.lines.from
        sorted_points = sorted(
            points,
            key=lambda p: p["payload"]
                .get("loc", {})
                .get("lines", {})
                .get("from", 0)
        )

        return {
            "id": sorted_points[0]["id"],
            "file_name": file_name,
            "record_date": sorted_points[0]["payload"]
                .get("metadata", {})
                .get("record_date", ""),
            "content": "\n".join([
                p["payload"].get("content", "") for p in sorted_points
            ])
        }
