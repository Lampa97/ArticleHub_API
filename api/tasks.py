import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from config.settings import DB_URL, DB_NAME, LOGS_DIR
from celery import shared_task
from config.logger import write_log

@shared_task
def send_welcome_email(email, name):
    log_line = f"Welcome email sent to {email} ({name})"
    print(log_line)
    write_log(log_line, log_file=os.path.join(LOGS_DIR, "users.log"))


async def analyze_article_async(article_id):
    client = AsyncIOMotorClient(DB_URL)
    db = client[DB_NAME]
    article = await db.articles.find_one({"_id": ObjectId(article_id)})
    if not article:
        return
    word_count = len(article["content"].split())
    unique_tags = len(set(article.get("tags", [])))
    await db.articles.update_one(
        {"_id": ObjectId(article_id)},
        {"$set": {"analysis": {"word_count": word_count, "unique_tags": unique_tags}}}
    )

@shared_task
def analyze_article(article_id):
    asyncio.run(analyze_article_async(article_id))


async def log_articles_count():
    client = AsyncIOMotorClient(DB_URL)
    db = client[DB_NAME]
    count = await db.articles.count_documents({})
    log_line = f"[Celery Beat] Total articles in DB: {count}"
    print(log_line)
    write_log(log_line, log_file=os.path.join(LOGS_DIR, "articles.log"))

@shared_task
def log_articles_count_task():
    asyncio.run(log_articles_count())