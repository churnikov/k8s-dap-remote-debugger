import os

from celery import Celery


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/1")

celery_app = Celery(
    "k8s_remote_debugger",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks"],
)

celery_app.conf.update(
    result_expires=3600,
    task_default_queue="default",
    task_routes={
        "tasks.echo": {"queue": "default"},
        "tasks.add": {"queue": "math"},
    },
    task_track_started=True,
)
