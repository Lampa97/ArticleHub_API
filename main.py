import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from config.db import MongoDBConnector
from config.settings import LOGS_DIR
from routers.articles import router as articles_router
from routers.auth import router as auth_router

os.makedirs(LOGS_DIR, exist_ok=True)

app = FastAPI()
app.include_router(auth_router)
app.include_router(articles_router)

db_connector = MongoDBConnector(app)

app.add_event_handler("startup", db_connector.startup_db_client)
app.add_event_handler("shutdown", db_connector.shutdown_db_client)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <h2>Welcome to ArticleHub API</h2>
    <ul>
        <li><a href="/docs">Swagger UI</a></li>
        <li><a href="/redoc">ReDoc</a></li>
    </ul>
    """
