from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import DB_URL


class MongoDBConnector:
    def __init__(self, app):
        self.app = app

    async def startup_db_client(self):
        self.app.mongodb_client = AsyncIOMotorClient(
            DB_URL
        )
        self.app.mongodb = self.app.mongodb_client["articlehub"]

    async def shutdown_db_client(self):
        self.app.mongodb_client.close()

