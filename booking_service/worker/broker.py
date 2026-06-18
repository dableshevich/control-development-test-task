from taskiq import SmartRetryMiddleware, TaskiqEvents
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from booking_service.config import settings
from booking_service.logging_config import configure_logging

broker = (
    ListQueueBroker(settings.REDIS_URL)
    .with_result_backend(RedisAsyncResultBackend(settings.REDIS_URL))
    .with_middlewares(
        SmartRetryMiddleware(
            default_retry_count=3,
            default_delay=1,
            use_delay_exponent=True,
            max_delay_exponent=60,
            use_jitter=False,
        )
    )
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def _setup_logging(state):
    configure_logging()


from booking_service.worker.tasks import *  # noqa
