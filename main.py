from fastapi import FastAPI
from api import search, document, analytics, compare, range

app = FastAPI()
app.include_router(search.router)
app.include_router(document.router)
app.include_router(analytics.router)
app.include_router(compare.router)
app.include_router(range.router)
