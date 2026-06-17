import asyncio
import logging
import random

from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession

from booking_service.db import BookingStatus
from booking_service.db.session import async_session
from booking_service.repositories.booking import BookingRepository
from booking_service.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

FAILURE_RATE = 0.15


class ExternalServiceError(Exception):
    """Имитация недоступности сервиса."""


class ConfirmTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        booking_id = args[0]
        asyncio.run(_set_status(booking_id, BookingStatus.failed))
        logger.warning("Бронь %s переведена в failed после ретраев", booking_id)


@celery_app.task(
    bind=True,
    base=ConfirmTask,
    autoretry_for=(ExternalServiceError,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=False,
    max_retries=3,
)
def confirm_booking(self, booking_id: int) -> None:
    asyncio.run(_run(booking_id))


async def _run(booking_id: int) -> None:
    async with async_session() as session:
        await _confirm_booking(session, booking_id)


async def _confirm_booking(session: AsyncSession, booking_id: int) -> None:
    repo = BookingRepository(session)
    booking = await repo.get(booking_id)

    if booking is None:
        logger.warning("Бронь %s не найдена, задача пропущена", booking_id)
        return

    if booking.status == BookingStatus.confirmed:
        logger.info("Бронь %s уже confirmed, пропуск", booking_id)
        return

    if random.random() < FAILURE_RATE:
        raise ExternalServiceError("notification service unavailable")

    await repo.set_status(booking_id, BookingStatus.confirmed)
    logger.info("MOCK: уведомление отправлено по брони %s", booking_id)


async def _set_status(booking_id: int, status: BookingStatus) -> None:
    async with async_session() as session:
        repo = BookingRepository(session)
        await repo.set_status(booking_id, status)
        logger.info(
            "MOCK: статус изменён",
            extra={"booking_id": booking_id, "event": "status_changed"},
        )
