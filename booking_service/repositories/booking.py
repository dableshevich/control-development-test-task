from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from booking_service.api.schemas import BookingRequest
from booking_service.db import BookingStatus, Bookings
from booking_service.exceptions import BookingError, BookingNotFoundError


class BookingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: BookingRequest) -> Bookings:
        booking = Bookings(
            name=data.name,
            booking_datetime=data.booking_datetime,
            service_type=data.service_type,
            status=BookingStatus.pending,
        )
        self._session.add(booking)
        try:
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            raise BookingError("Не удалось создать бронь") from e
        await self._session.refresh(booking)
        return booking

    async def get(self, booking_id: int) -> Bookings | None:
        booking = await self._session.get(Bookings, booking_id)
        if booking is None:
            raise BookingNotFoundError(f"Бронь {booking_id} не найдена")
        return booking

    async def list(self) -> Sequence[Bookings]:
        result = await self._session.execute(select(Bookings))
        return result.scalars().all()

    async def destroy(self, booking_id: int) -> bool:
        try:
            booking = await self._session.get(Bookings, booking_id)
            if booking is None:
                raise BookingNotFoundError(f"Бронь {booking_id} не найдена")
            if booking.status != BookingStatus.pending:
                raise BookingError("Бронь не может быть удалена")
            await self._session.delete(booking)
            await self._session.commit()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise BookingError("Не удалось удалить бронь") from e

    async def set_status(
        self, booking_id: int, status: BookingStatus
    ) -> Bookings | None:
        try:
            booking = await self._session.get(Bookings, booking_id)
            if booking is None:
                raise BookingNotFoundError(f"Бронь {booking_id} не найдена")
            booking.status = status
            await self._session.commit()
            await self._session.refresh(booking)
            return booking
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise BookingError("Не удалось обновить статус брони") from e
