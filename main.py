from fastapi import FastAPI
from dotenv import load_dotenv
from api import search
from api import document

load_dotenv()

app = FastAPI()
app.include_router(search.router)
app.include_router(document.router)