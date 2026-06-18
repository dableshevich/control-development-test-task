from booking_service.api.schemas import BookingRequest, BookingStatus
from booking_service.db import Bookings
from booking_service.logging_config import booking_logger as logger
from booking_service.repositories import BookingRepository
from booking_service.worker.tasks import confirm_booking


class BookingService:
    def __init__(self, repo: BookingRepository) -> None:
        self._repo = repo

    async def create_booking(self, data: BookingRequest) -> Bookings:
        booking = await self._repo.create(data)
        await confirm_booking.kiq(booking.id)
        logger.info(
            "Бронь создана и поставлена в очередь",
            extra={"booking_id": booking.id},
        )
        return booking

    async def get_booking(self, booking_id: int) -> Bookings | None:
        return await self._repo.get(booking_id)

    async def list_bookings(self) -> list[Bookings]:
        return list(await self._repo.list())

    async def cancel_booking(self, booking_id: int) -> bool:
        return await self._repo.destroy(booking_id)

    async def confirm_booking(self, booking_id: int) -> Bookings | None:
        return await self._repo.set_status(booking_id, BookingStatus.confirmed)

    async def fail_booking(self, booking_id: int) -> Bookings | None:
        return await self._repo.set_status(booking_id, BookingStatus.failed)
