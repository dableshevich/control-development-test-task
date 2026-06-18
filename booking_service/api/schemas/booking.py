from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ServiceType(StrEnum):
    consultation = "consultation"
    demo = "demo"
    interview = "interview"
    online_call = "online_call"


class BookingStatus(StrEnum):
    pending = "pending"
    failed = "failed"
    confirmed = "confirmed"


class BookingRequest(BaseModel):
    name: str
    booking_datetime: datetime
    service_type: ServiceType


class BookingResponse(BaseModel):
    id: int
    name: str
    booking_datetime: datetime
    service_type: ServiceType
    status: BookingStatus
