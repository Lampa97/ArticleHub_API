import os
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from routers.articles import router as articles_router
from routers.auth import router as auth_router
from config.settings import LOGS_DIR
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env.test"))

class TestMongoDBConnector:
    def __init__(self, app):
        self.app = app

    async def startup_db_client(self):
        self.app.mongodb_client = AsyncIOMotorClient(os.getenv("TEST_DB_URL"))
        self.app.mongodb = self.app.mongodb_client[os.getenv("TEST_DB_NAME")]

    async def shutdown_db_client(self):
        self.app.mongodb_client.close()

os.makedirs(LOGS_DIR, exist_ok=True)

app = FastAPI()
app.include_router(auth_router)
app.include_router(articles_router)

db_connector = TestMongoDBConnector(app)
app.add_event_handler("startup", db_connector.startup_db_client)
app.add_event_handler("shutdown", db_connector.shutdown_db_client)
