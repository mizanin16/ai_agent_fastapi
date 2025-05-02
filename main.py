from fastapi import FastAPI
from api import search, document, metadata, analytics

app = FastAPI()
app.include_router(search.router)
app.include_router(document.router)
app.include_router(metadata.router)
app.include_router(analytics.router)
