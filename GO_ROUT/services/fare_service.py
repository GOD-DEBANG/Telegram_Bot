def calculate_fare(mode, seat_count):
    base = {
        "Bus": 500,
        "Train": 1200,
        "Flight": 4500
    }
    return base[mode] * seat_count
