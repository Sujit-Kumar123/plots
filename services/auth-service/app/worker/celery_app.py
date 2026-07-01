from celery import Celery

from app.config import settings

broker_url = settings.redis_url
result_backend = settings.redis_url.rsplit("/", 1)[0] + "/1" if "/" in settings.redis_url else settings.redis_url + "/1"

celery_app = Celery(
    "mvp_worker",
    broker=broker_url,
    backend=result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

celery_app.autodiscover_tasks(["app.worker"])
