import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate approximate distance between two GPS coordinates
    using the Haversine formula.
    """

    earth_radius = 6371  # Kilometers

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c


def predict_eta(distance_km, speed_kmph):
    """
    Predict bus arrival time in minutes.
    """

    if distance_km < 0:
        raise ValueError("Distance cannot be negative.")

    if speed_kmph <= 0:
        return None

    travel_time_hours = distance_km / speed_kmph
    travel_time_minutes = travel_time_hours * 60

    return round(travel_time_minutes, 2)


def get_eta_message(eta_minutes):
    """
    Generate a simple parent-friendly ETA message.
    """

    if eta_minutes is None:
        return "ETA unavailable because the bus is currently stopped."

    if eta_minutes <= 5:
        return "Bus is approaching your stop."

    if eta_minutes <= 15:
        return f"Bus will arrive in approximately {eta_minutes} minutes."

    return f"Bus is approximately {eta_minutes} minutes away."


def predict_bus_arrival(
    current_latitude,
    current_longitude,
    stop_latitude,
    stop_longitude,
    speed_kmph
):
    """
    Complete ETA prediction process.
    """

    distance = calculate_distance(
        current_latitude,
        current_longitude,
        stop_latitude,
        stop_longitude
    )

    eta = predict_eta(distance, speed_kmph)

    return {
        "distance_km": round(distance, 2),
        "speed_kmph": speed_kmph,
        "eta_minutes": eta,
        "message": get_eta_message(eta)
    }


if __name__ == "__main__":

    result = predict_bus_arrival(
        current_latitude=13.0827,
        current_longitude=80.2707,
        stop_latitude=13.0674,
        stop_longitude=80.2376,
        speed_kmph=25
    )

    print("AI ETA Prediction")
    print("-----------------")
    print(f"Distance : {result['distance_km']} km")
    print(f"Speed    : {result['speed_kmph']} km/h")
    print(f"ETA      : {result['eta_minutes']} minutes")
    print(f"Message  : {result['message']}")