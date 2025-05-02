from collections import Counter
import re
from utils.time import get_year_range
from clients.qdrant import scroll_qdrant


class TopicAnalyzerService:
    @staticmethod
    async def analyze_year(year: int) -> list[str]:
        start_ts, end_ts = get_year_range(year)
        points = await scroll_qdrant(
            collection="transcriptSummary",
            scroll_filter={
                "must": [{
                    "key": "timestamp",
                    "range": {"gte": start_ts, "lte": end_ts}
                }]
            },
            limit=100,
            with_payload=["content"]
        )

        text = " ".join(p["payload"].get("content", "") for p in points)
        words = re.findall(r"\b[\wа-яА-Я]{4,}\b", text.lower())
        counter = Counter(words)
        return [word for word, _ in counter.most_common(10)]
