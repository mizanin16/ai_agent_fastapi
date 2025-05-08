from fastapi import FastAPI
from middleware.request_logger import RequestLoggingMiddleware
from api import search, document, analytics, compare, range, logs, test_response

app = FastAPI()
app.include_router(search.router)
app.include_router(document.router)
app.include_router(analytics.router)
app.include_router(compare.router)
app.include_router(range.router)

app.include_router(logs.router)
app.include_router(test_response.router)

app.add_middleware(RequestLoggingMiddleware)
