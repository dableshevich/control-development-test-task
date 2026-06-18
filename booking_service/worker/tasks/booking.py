import random

from taskiq import Context, TaskiqDepends

from booking_service.db import BookingStatus
from booking_service.db.session import async_session
from booking_service.logging_config import booking_logger as logger
from booking_service.repositories import BookingRepository
from booking_service.worker.broker import broker

FAILURE_RATE = 0.15
MAX_RETRIES = 3


class ExternalServiceError(Exception):
    """Имитация сбоя внешнего сервиса уведомлений."""


async def _confirm_booking(session, booking_id: int, retries: int = 0) -> None:
    repo = BookingRepository(session)
    booking = await repo.get(booking_id)

    if booking is None:
        logger.warning("Бронь не найдена", extra={"booking_id": booking_id})
        return
    if booking.status == BookingStatus.confirmed:
        logger.info(
            "Бронь уже подтверждена, пропуск",
            extra={"booking_id": booking_id, "event": "skip_idempotent"},
        )
        return

    if random.random() < FAILURE_RATE:
        if retries >= MAX_RETRIES - 1:
            await repo.set_status(booking_id, BookingStatus.failed)
            logger.warning(
                "Бронь переведена в failed после ретраев",
                extra={"booking_id": booking_id, "event": "failed"},
            )
            return
        logger.info(
            "Сбой внешнего сервиса, уйдёт в retry",
            extra={"booking_id": booking_id, "retry": retries},
        )
        raise ExternalServiceError("notification service unavailable")

    await repo.set_status(booking_id, BookingStatus.confirmed)
    logger.info(
        "MOCK: бронь подтверждена",
        extra={"booking_id": booking_id, "event": "notification_sent"},
    )


@broker.task(retry_on_error=True)
async def confirm_booking(
    booking_id: int,
    context: Context = TaskiqDepends(),
) -> None:
    retries = context.message.labels.get("_retries", 0)
    async with async_session() as session:
        await _confirm_booking(session, booking_id, retries)
