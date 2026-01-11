import uuid
from services.seat_service import allocate_seats
from services.fare_service import calculate_fare

def create_booking(user, mode, source, destination, operator, seat_count):
    seats = allocate_seats(mode, seat_count)
    fare = calculate_fare(mode, seat_count)

    return {
        "ticket_id": str(uuid.uuid4())[:8],
        "name": user["name"],
        "email": user["email"],
        "mode": mode,
        "from": source,
        "to": destination,
        "operator": operator,
        "seats": seats,
        "fare": fare
    }
