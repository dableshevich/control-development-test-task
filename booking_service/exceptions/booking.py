from dataclasses import dataclass


@dataclass(eq=False)
class BookingError(Exception):
    detail: str = "Ошибка бронирования"


@dataclass(eq=False)
class BookingNotFoundError(Exception):
    detail: str = "Бронь не найдена"
