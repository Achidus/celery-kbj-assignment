import os
from celery import Celery
from kombu import Exchange, Queue
from dotenv import load_dotenv

load_dotenv()

BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")

# Exchange topic dipakai untuk mengarahkan task berdasarkan routing key.
jobs_exchange = Exchange("uts_jobs", type="topic", durable=True)

app = Celery(
    "kbj_uts",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["tasks"],
)

app.conf.update(
    task_default_exchange="uts_jobs",
    task_default_exchange_type="topic",
    task_default_routing_key="job.general",
    task_queues=(
        Queue("short_queue", exchange=jobs_exchange, routing_key="job.short"),
        Queue("long_queue", exchange=jobs_exchange, routing_key="job.long"),
        Queue("general_queue", exchange=jobs_exchange, routing_key="job.#"),
    ),
    task_routes={
        "tasks.process_short": {
            "queue": "short_queue",
            "routing_key": "job.short",
        },
        "tasks.process_long": {
            "queue": "long_queue",
            "routing_key": "job.long",
        },
    },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
