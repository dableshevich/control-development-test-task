from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request

from booking_service.api.limiter import limiter
from booking_service.api.schemas import BookingRequest, BookingResponse
from booking_service.deps import get_booking_service
from booking_service.logic import BookingService

booking_router = APIRouter(prefix="/bookings", tags=["bookings"])


@booking_router.get("/", response_model=list[BookingResponse])
async def get_booking_list(
    service: BookingService = Depends(get_booking_service),
):
    return await service.list_bookings()


@booking_router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int, service: BookingService = Depends(get_booking_service)
):
    return await service.get_booking(booking_id)


@booking_router.post("/", response_model=BookingResponse, status_code=201)
@limiter.limit("5/minute")
async def create_booking(
    request: Request,
    request_body: Annotated[BookingRequest, Body()],
    service: BookingService = Depends(get_booking_service),
):
    return await service.create_booking(request_body)


@booking_router.delete("/{booking_id}")
async def destroy_booking(
    booking_id: int, service: BookingService = Depends(get_booking_service)
):
    return await service.cancel_booking(booking_id)
