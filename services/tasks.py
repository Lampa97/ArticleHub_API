from config.celery import celery_app
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from config.settings import DB_URL, DB_NAME

@celery_app.task
def send_welcome_email(email, name):
    print(f"Welcome email sent to {email} ({name})")


@celery_app.task
def analyze_article(article_id):
    client = AsyncIOMotorClient(DB_URL)
    db = client[DB_NAME]
    article = db.articles.find_one({"_id": ObjectId(article_id)})
    if not article:
        return
    word_count = len(article["content"].split())
    unique_tags = len(set(article.get("tags", [])))
    db.articles.update_one(
        {"_id": ObjectId(article_id)},
        {"$set": {"analysis": {"word_count": word_count, "unique_tags": unique_tags}}}
    )