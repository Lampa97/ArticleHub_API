import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from config.settings import DB_URL, DB_NAME, LOGS_DIR
from celery import shared_task
from config.logger import write_log

@shared_task
def send_welcome_email(email, name):
    """
    Celery task to send a welcome email to a new user.

    Args:
        email (str): The user's email address.
        name (str): The user's name.

    Side Effects:
        Writes a log entry to 'users.log' and prints a message to stdout.
    """
    log_line = f"Welcome email sent to {email} ({name})"
    print(log_line)
    write_log(log_line, log_file=os.path.join(LOGS_DIR, "users.log"))


async def analyze_article_async(article_id):
    """
    Asynchronous function to analyze an article.

    Calculates word count and number of unique tags, then updates the article document
    in the database with the analysis results.

    Args:
        article_id (str): The ID of the article to analyze.

    Side Effects:
        Updates the 'analysis' field in the article document in MongoDB.
    """
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
    """
    Celery task to analyze an article.

    Runs the asynchronous analysis function in an event loop.

    Args:
        article_id (str): The ID of the article to analyze.

    Side Effects:
        Updates the article document in MongoDB with analysis results.
    """
    asyncio.run(analyze_article_async(article_id))


async def log_articles_count():
    """
    Asynchronous function to log the total number of articles in the database.

    Counts all articles and writes the result to 'articles.log'.

    Side Effects:
        Writes a log entry to 'articles.log' and prints a message to stdout.
    """
    client = AsyncIOMotorClient(DB_URL)
    db = client[DB_NAME]
    count = await db.articles.count_documents({})
    log_line = f"[Celery Beat] Total articles in DB: {count}"
    print(log_line)
    write_log(log_line, log_file=os.path.join(LOGS_DIR, "articles.log"))

@shared_task
def log_articles_count_task():
    """
    Celery task to periodically log the total number of articles.

    Runs the asynchronous logging function in an event loop.

    Side Effects:
        Writes a log entry to 'articles.log'.
    """
    asyncio.run(log_articles_count())