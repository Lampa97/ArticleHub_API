import time
import pytest
from bson import ObjectId
from config.settings import LOGS_DIR, DB_URL, DB_NAME
from services.tasks import send_welcome_email, analyze_article
from pymongo import MongoClient


def test_send_welcome_email_integration():
    """
    Integration test for Celery send_welcome_email task.
    Checks that log entry is written to the logs collection in MongoDB.
    """
    email = "celerytest@example.com"
    name = "Celery Test"

    # Запустить задачу
    send_welcome_email.delay(email, name).get(timeout=10)
    time.sleep(2)  # Дать немного времени на запись

    # Проверить наличие лога в базе
    mongo = MongoClient(DB_URL)
    db = mongo[DB_NAME]
    log = db.logs.find_one({"type": "user", "message": f"Welcome email sent to {email} ({name})"})
    assert log is not None



def test_analyze_article_integration():
    """
    Integration test for Celery analyze_article task.
    Checks that analysis field is added to article in MongoDB after task execution.
    """
    mongo = MongoClient(DB_URL)
    db = mongo[DB_NAME]
    db.articles.delete_many({})
    # db.users.delete_many({})

    # Создать статью напрямую в базе
    article_data = {
        "title": "Celery Article",
        "content": "Celery integration test content.",
        "tags": ["celery", "integration"]
    }
    article_id = db.articles.insert_one(article_data).inserted_id
    time.sleep(2)  # Дать немного времени на запись

    # Запустить задачу анализа
    analyze_article.delay(str(article_id)).get(timeout=10)
    time.sleep(5)  # Дать немного времени на обновление

    # Проверить наличие анализа
    article = db.articles.find_one({"_id": ObjectId(article_id)})
    assert article is not None
    assert "analysis" in article
    assert "word_count" in article["analysis"]
    assert "unique_tags" in article["analysis"]