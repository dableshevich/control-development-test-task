from datetime import UTC, datetime

import pytest

from booking_service.api.schemas import BookingRequest
from booking_service.db import BookingStatus, ServiceType
from booking_service.repositories import BookingRepository
from booking_service.worker import tasks
from booking_service.worker.tasks.booking import (
    ExternalServiceError,
    _confirm_booking,
)


async def _make_pending(session):
    repo = BookingRepository(session)
    return await repo.create(
        BookingRequest(
            name="Иван",
            booking_datetime=datetime(2026, 6, 20, 14, tzinfo=UTC),
            service_type=ServiceType.demo,
        )
    )


async def test_worker_confirms_on_success(session, monkeypatch):
    monkeypatch.setattr(tasks.booking.random, "random", lambda: 0.9)
    booking = await _make_pending(session)
    await _confirm_booking(session, booking.id)
    assert (
        await BookingRepository(session).get(booking.id)
    ).status == BookingStatus.confirmed


async def test_worker_raises_on_external_failure(session, monkeypatch):
    monkeypatch.setattr(tasks.booking.random, "random", lambda: 0.01)
    booking = await _make_pending(session)
    with pytest.raises(ExternalServiceError):
        await _confirm_booking(session, booking.id)


async def test_worker_idempotent_on_confirmed(session, monkeypatch):
    monkeypatch.setattr(tasks.booking.random, "random", lambda: 0.01)
    booking = await _make_pending(session)
    await BookingRepository(session).set_status(
        booking.id, BookingStatus.confirmed
    )
    await _confirm_booking(session, booking.id)
    assert (
        await BookingRepository(session).get(booking.id)
    ).status == BookingStatus.confirmed
