from typing import Any

from celery.result import AsyncResult
from fastapi import FastAPI
from pydantic import BaseModel

from celery_app import celery_app
from tasks import add, echo

app = FastAPI()


class AddTaskRequest(BaseModel):
    left: int
    right: int


class EchoTaskRequest(BaseModel):
    message: str


def serialize_task(task: AsyncResult) -> dict[str, Any]:
    response: dict[str, Any] = {
        "task_id": task.id,
        "status": task.status,
    }

    if not task.ready():
        return response

    if task.successful():
        response["result"] = task.result
    else:
        response["error"] = str(task.result)

    return response


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/tasks/echo")
async def enqueue_echo(payload: EchoTaskRequest):
    task = echo.apply_async(args=[payload.message], queue="default")
    return {"task_id": task.id, "status": task.status, "queue": "default"}


@app.post("/tasks/add")
async def enqueue_add(payload: AddTaskRequest):
    task = add.apply_async(args=[payload.left, payload.right], queue="math")
    return {"task_id": task.id, "status": task.status, "queue": "math"}


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    return serialize_task(AsyncResult(task_id, app=celery_app))
