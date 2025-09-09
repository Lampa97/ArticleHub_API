from fastapi import FastAPI
from config.db import MongoDBConnector
from api.auth import router as auth_router
from api.articles import router as articles_router




app = FastAPI()
app.include_router(auth_router)
app.include_router(articles_router)

db_connector = MongoDBConnector(app)

app.add_event_handler("startup", db_connector.startup_db_client)
app.add_event_handler("shutdown", db_connector.shutdown_db_client)
