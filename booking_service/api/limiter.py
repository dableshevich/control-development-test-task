from slowapi import Limiter
from slowapi.util import get_remote_address

from booking_service.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
)
