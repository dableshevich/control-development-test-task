from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from booking_service.api.limiter import limiter
from booking_service.api.routers import booking_router
from booking_service.config import settings
from booking_service.exceptions import BookingError, BookingNotFoundError
from booking_service.logging_config import configure_logging

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
)


app.include_router(booking_router, prefix=settings.API_PREFIX)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(BookingError)
async def booking_error_handler(request: Request, exc: BookingError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.detail},
    )


@app.exception_handler(BookingNotFoundError)
async def booking_not_found_error_handler(
    request: Request, exc: BookingNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.detail},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield
