from DEMODATA.demo_data import DESTINATIONS



def get_hotels(destination):
    return DESTINATIONS.get(destination, {}).get("hotels", [])
