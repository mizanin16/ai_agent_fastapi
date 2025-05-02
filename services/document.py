from models.schemas import FileResult
from services.qdrant import scroll_by_file_name_sorted


async def get_full_document(collection: str, file_name: str) -> FileResult:
    doc = await scroll_by_file_name_sorted(collection, file_name)
    return FileResult(
        id=doc["id"],
        score=1.0,
        file_name=doc["file_name"],
        record_date=doc["record_date"],
        content=doc["content"]
    )
