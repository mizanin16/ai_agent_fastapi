import os
import httpx

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_KEY = os.getenv("QDRANT_API_KEY")

HEADERS = {
    "api-key": QDRANT_KEY,
    "Content-Type": "application/json"
}


async def scroll_qdrant(collection: str, scroll_filter: dict, limit: int = 100, order_by: dict = None,
                        with_payload: list = None):
    body = {
        "limit": limit,
        "filter": scroll_filter
    }
    if order_by:
        body["order_by"] = order_by
    if with_payload:
        body["with_payload"] = with_payload

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{QDRANT_HOST}/collections/{collection}/points/scroll",
            headers=HEADERS,
            json=body
        )
        res.raise_for_status()
        return res.json()["result"]["points"]


async def search_qdrant(collection: str, vector: list[float], limit: int = 100) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{QDRANT_HOST}/collections/{collection}/points/search",
            headers=HEADERS,
            json={
                "vector": vector,
                "limit": limit,
                "with_payload": ["metadata.file_name", "metadata.record_date", "content"]
            }
        )
        response.raise_for_status()
        return response.json()["result"]
