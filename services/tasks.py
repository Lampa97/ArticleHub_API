from bson import ObjectId
from celery import shared_task
from pymongo import MongoClient

from config.settings import DB_NAME, DB_URL
from models.log import Log


@shared_task
def send_welcome_email(email: str, name: str):
    """
    Celery task to send a welcome email to a new user.
    Writes a log entry to the 'logs' collection in MongoDB.
    """
    log_line = f"Welcome email sent to {email} ({name})"
    client = MongoClient(DB_URL)
    db = client[DB_NAME]
    db.logs.insert_one({"type": "user", "message": log_line})


@shared_task
def analyze_article(article_id: str):
    """
    Celery task to analyze an article.
    Calculates word count and number of unique tags, then updates the article document
    in the database with the analysis results.
    """
    client = MongoClient(DB_URL)
    db = client[DB_NAME]
    article = db.articles.find_one({"_id": ObjectId(article_id)})
    if not article:
        return
    word_count = len(article["content"].split())
    unique_tags = len(set(article.get("tags", [])))
    db.articles.update_one(
        {"_id": ObjectId(article_id)}, {"$set": {"analysis": {"word_count": word_count, "unique_tags": unique_tags}}}
    )


@shared_task
def log_articles_count_task():
    """
    Celery task to periodically log the total number of articles.
    Writes a log entry to the 'logs' collection in MongoDB.
    """
    client = MongoClient(DB_URL)
    db = client[DB_NAME]
    count = db.articles.count_documents({})
    log_line = f"[Celery Beat] Total articles in DB: {count}"
    log = Log(type="article", message=log_line)
    db.logs.insert_one(log.model_dump())
