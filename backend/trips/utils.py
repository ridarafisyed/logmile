METERS_PER_MILE = 1609.344
SECONDS_PER_HOUR = 3600


def round_non_negative(value: float, digits: int = 2) -> float:
    return round(max(value, 0), digits)


def round_hour(value: float) -> float:
    return round_non_negative(value)


def round_miles(value: float) -> float:
    return round_non_negative(value)


def round_value(value: float) -> float:
    return round_non_negative(value)


def meters_to_miles(value: float) -> float:
    return value / METERS_PER_MILE


def seconds_to_hours(value: float) -> float:
    return value / SECONDS_PER_HOUR
