from celery import Celery
from services import tasks 


celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.autodiscover_tasks(['api.tasks']) 

celery_app.conf.beat_schedule = {
    "log-articles-count-daily": {
        "task": "api.tasks.log_articles_count_task",
        "schedule": 86400,  # 24 hours = 86400 seconds
    },
}
celery_app.conf.timezone = "UTC"