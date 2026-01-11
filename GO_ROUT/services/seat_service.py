import random

def get_available_seats(mode):
    if mode == "Flight":
        return [f"{row}{seat}" for row in range(1, 31) for seat in ["A", "B", "C", "D"]]
    elif mode == "Train":
        return [f"S{n}" for n in range(1, 73)]
    else:
        return [f"A{n}" for n in range(1, 41)]

def allocate_seats(mode, count=2):
    seats = get_available_seats(mode)
    return random.sample(seats, count)
