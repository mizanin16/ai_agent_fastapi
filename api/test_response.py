from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/test-response-size")
async def test_response_size(size: int = Query(..., ge=1, le=500000)):
    """
    Возвращает JSON-объект с полем `payload`, содержащим строку заданной длины.
    Используется для тестирования ограничений на размер ответа.
    """
    content = "х" * size
    return JSONResponse(content={"length": len(content), "payload": content})
