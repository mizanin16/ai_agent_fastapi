from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/test-response-size")
async def test_response_size(size: int = Query(1024, ge=1, le=500000)):
    content = "к" * size
    return JSONResponse(content={"id": "test", "content": content})

@router.get("/test-response-size-query")
async def test_response_size(size: int = Query(1024, ge=1, le=500000)):
    content = "a" * size
    return JSONResponse(content={"id": "test", "content": content})
