from datetime import datetime, timezone
import socket

from celery_app import celery_app


@celery_app.task(name="tasks.echo")
def echo(message: str) -> dict[str, str]:
    return {
        "message": message,
        "handled_by": socket.gethostname(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


@celery_app.task(name="tasks.add")
def add(left: int, right: int) -> dict[str, int | str]:
    return {
        "left": left,
        "right": right,
        "result": left + right,
        "handled_by": socket.gethostname(),
    }
