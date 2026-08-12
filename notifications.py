from models import create_notification


def bus_started_notification(parent_id):
    return create_notification(
        parent_id,
        "Your school bus has started the trip.",
        "BUS_STARTED"
    )


def bus_approaching_notification(parent_id, eta_minutes):
    return create_notification(
        parent_id,
        f"Your bus is approaching your stop. Estimated arrival: {eta_minutes} minutes.",
        "BUS_APPROACHING"
    )


def bus_delay_notification(parent_id, delay_minutes):
    return create_notification(
        parent_id,
        f"Your school bus is delayed by approximately {delay_minutes} minutes.",
        "BUS_DELAY"
    )


def emergency_notification(parent_id, message):
    return create_notification(
        parent_id,
        f"Emergency Alert: {message}",
        "EMERGENCY"
    )


def create_custom_notification(parent_id, message):
    return create_notification(
        parent_id,
        message,
        "GENERAL"
    )