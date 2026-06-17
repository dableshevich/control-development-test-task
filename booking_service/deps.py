from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from booking_service.db import get_session
from booking_service.logic import BookingService
from booking_service.repositories import BookingRepository


def get_booking_repository(
    session: AsyncSession = Depends(get_session),
) -> BookingRepository:
    return BookingRepository(session)


def get_booking_service(
    repo: BookingRepository = Depends(get_booking_repository),
) -> BookingService:
    return BookingService(repo)
