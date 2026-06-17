async def test_create_booking_happy_path(client):
    resp = await client.post(
        "/api/bookings",
        json={
            "name": "Иван",
            "booking_datetime": "2026-06-20T14:00:00+03:00",
            "service_type": "demo",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert isinstance(body["id"], int)


async def test_get_booking_returns_created(client):
    created = await client.post(
        "/api/bookings",
        json={
            "name": "Иван",
            "booking_datetime": "2026-06-20T14:00:00+03:00",
            "service_type": "demo",
        },
    )
    booking_id = created.json()["id"]
    resp = await client.get(f"/api/bookings/{booking_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == booking_id


async def test_get_missing_returns_404(client):
    resp = await client.get("/api/bookings/9999")
    assert resp.status_code == 404


async def test_invalid_service_type_returns_422(client):
    resp = await client.post(
        "/api/bookings",
        json={
            "name": "Иван",
            "booking_datetime": "2026-06-20T14:00:00+03:00",
            "service_type": "not_a_real_type",
        },
    )
    assert resp.status_code == 422


async def test_missing_field_returns_422(client):
    resp = await client.post(
        "/api/bookings",
        json={
            "name": "Иван",
        },
    )
    assert resp.status_code == 422
