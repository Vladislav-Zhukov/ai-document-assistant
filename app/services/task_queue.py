from redis import Redis
from rq import Queue

from app.core.config import settings


redis_conn = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)

document_queue = Queue(
    settings.RQ_QUEUE_NAME,
    connection=redis_conn,
)