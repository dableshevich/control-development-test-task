from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ServiceType(StrEnum):
    consultation = "consultation"
    demo = "demo"
    interview = "interview"
    online_call = "online_call"


class BookingStatus(StrEnum):
    pending = "pending"
    failed = "failed"
    confirmed = "confirmed"


class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    booking_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    service_type: Mapped[ServiceType] = mapped_column(nullable=False)
    status: Mapped[BookingStatus] = mapped_column(nullable=False)
