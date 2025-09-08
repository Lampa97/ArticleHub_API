from motor.motor_asyncio import AsyncIOMotorClient


class MongoDBConnector:
    def __init__(self, app):
        self.app = app

    async def startup_db_client(self):
        self.app.mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.app.mongodb = self.app.mongodb_client["articlehub"]

    async def shutdown_db_client(self):
        self.app.mongodb_client.close()

