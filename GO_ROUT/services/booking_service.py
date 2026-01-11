import uuid
import random
from datetime import datetime, timedelta
from services.seat_service import allocate_seats
from services.fare_service import calculate_fare

def generate_city_code(city_name):
    """Generate 3-letter airport/station code from city name"""
    # Common city codes
    city_codes = {
        "delhi": "DEL",
        "new delhi": "DEL",
        "mumbai": "BOM",
        "bangalore": "BLR",
        "bengaluru": "BLR",
        "chennai": "MAA",
        "kolkata": "CCU",
        "hyderabad": "HYD",
        "pune": "PNQ",
        "ahmedabad": "AMD",
        "jaipur": "JAI",
        "lucknow": "LKO",
        "goa": "GOI",
        "kochi": "COK",
        "cochin": "COK",
        "chandigarh": "IXC",
        "indore": "IDR",
        "nagpur": "NAG",
        "varanasi": "VNS",
        "amritsar": "ATQ",
        "srinagar": "SXR",
        "patna": "PAT",
        "bhopal": "BHO",
        "coimbatore": "CJB",
        "thiruvananthapuram": "TRV",
        "trivandrum": "TRV",
        "vizag": "VTZ",
        "visakhapatnam": "VTZ",
        "agra": "AGR",
        "udaipur": "UDR",
        "mangalore": "IXE",
        "ranchi": "IXR"
    }
    
    city_lower = city_name.lower().strip()
    if city_lower in city_codes:
        return city_codes[city_lower]
    
    # Fallback: use first 3 letters
    return city_name[:3].upper()

def generate_travel_times(mode):
    """Generate realistic departure and arrival times based on mode"""
    # Start from current time + 2-8 hours (booking in advance)
    hours_ahead = random.randint(2, 8)
    departure = datetime.now() + timedelta(hours=hours_ahead)
    
    # Round to nearest 15 minutes
    departure = departure.replace(minute=(departure.minute // 15) * 15, second=0, microsecond=0)
    
    # Travel duration based on mode
    if mode == "Flight":
        duration = timedelta(hours=random.randint(1, 3), minutes=random.choice([0, 15, 30, 45]))
    elif mode == "Train":
        duration = timedelta(hours=random.randint(3, 8), minutes=random.choice([0, 15, 30, 45]))
    else:  # Bus
        duration = timedelta(hours=random.randint(4, 10), minutes=random.choice([0, 15, 30, 45]))
    
    arrival = departure + duration
    
    # Boarding time (30 mins before for flight, 15 mins for others)
    boarding_offset = timedelta(minutes=30 if mode == "Flight" else 15)
    boarding = departure - boarding_offset
    
    return {
        "departure_time": departure.strftime("%H:%M"),
        "arrival_time": arrival.strftime("%H:%M"),
        "boarding_time": boarding.strftime("%H:%M")
    }

def generate_gate(mode):
    """Generate realistic gate/platform number"""
    if mode == "Flight":
        # Airport gates: A1-A20, B1-B15, C1-C10
        terminal = random.choice(['A', 'B', 'C'])
        number = random.randint(1, 20 if terminal == 'A' else 15)
        return f"{terminal}{number}"
    elif mode == "Train":
        # Railway platforms: 1-12
        return f"Platform {random.randint(1, 12)}"
    else:  # Bus
        # Bus bays: 1-25
        return f"Bay {random.randint(1, 25)}"

def create_booking(user, mode, source, destination, operator, seat_count, specific_seats=None):
    if specific_seats:
        seats = specific_seats
    else:
        seats = allocate_seats(mode, seat_count)
    fare = calculate_fare(mode, seat_count)
    
    # Generate travel times
    times = generate_travel_times(mode)
    
    return {
        "ticket_id": str(uuid.uuid4())[:8].upper(),
        "name": user["name"],
        "email": user["email"],
        "mode": mode,
        "from": source,
        "to": destination,
        "from_code": generate_city_code(source),
        "to_code": generate_city_code(destination),
        "operator": operator,
        "seats": seats,
        "fare": fare,
        "departure_time": times["departure_time"],
        "arrival_time": times["arrival_time"],
        "boarding_time": times["boarding_time"],
        "gate": generate_gate(mode)
    }

def search_transport(source, destination, mode):
    """Generate mock transport options"""
    options = []
    
    # Operators based on mode
    if mode == "Flight":
        operators = ["IndiGo", "Air India", "Vistara", "SpiceJet", "Akasa Air"]
        base_price = 3000
    elif mode == "Train":
        operators = ["Rajdhani Exp", "Shatabdi Exp", "Vande Bharat", "Duronto Exp", "Intercity Exp"]
        base_price = 800
    else:  # Bus
        operators = ["ZingBus", "IntrCity SmartBus", "NueGo", "Orange Travels", "VRL Travels"]
        base_price = 500

    # Generate 5 random options
    for i in range(5):
        operator = random.choice(operators)
        
        # Random times
        hour = random.randint(6, 22)
        minute = random.choice([0, 15, 30, 45])
        dept_time = f"{hour:02d}:{minute:02d}"
        
        # Calculate arrival
        if mode == "Flight":
            duration_mins = random.randint(60, 180)
        elif mode == "Train":
            duration_mins = random.randint(180, 600)
        else:
            duration_mins = random.randint(240, 720)
            
        arrival_dt = datetime.strptime(dept_time, "%H:%M") + timedelta(minutes=duration_mins)
        arrival_time = arrival_dt.strftime("%H:%M")
        
        # Price variation
        price = base_price + random.randint(0, 2000)
        
        options.append({
            "id": f"{mode[:1].upper()}{random.randint(100, 999)}",
            "operator": operator,
            "departure": dept_time,
            "arrival": arrival_time,
            "price": price,
            "duration": f"{duration_mins//60}h {duration_mins%60}m"
        })
        
    return sorted(options, key=lambda x: x['price'])