import math

from ..types import Coordinate
from .constants import EARTH_RADIUS_MILES, WAYPOINT_MATCH_TOLERANCE_MILES
from .errors import MapServiceError


def haversine_miles(start: Coordinate, end: Coordinate) -> float:
    start_lng, start_lat = start
    end_lng, end_lat = end

    start_lat_rad = math.radians(start_lat)
    end_lat_rad = math.radians(end_lat)
    delta_lat_rad = math.radians(end_lat - start_lat)
    delta_lng_rad = math.radians(end_lng - start_lng)

    haversine_value = (
        math.sin(delta_lat_rad / 2) ** 2
        + math.cos(start_lat_rad)
        * math.cos(end_lat_rad)
        * math.sin(delta_lng_rad / 2) ** 2
    )
    central_angle = 2 * math.atan2(
        math.sqrt(haversine_value),
        math.sqrt(1 - haversine_value),
    )
    return EARTH_RADIUS_MILES * central_angle


def coordinate_at_distance(
    geometry: list[Coordinate],
    miles_from_start: float,
) -> Coordinate:
    if not geometry:
        raise MapServiceError("Route geometry is empty.")

    if miles_from_start <= 0:
        return geometry[0]

    traversed_miles = 0.0
    for index in range(1, len(geometry)):
        start = geometry[index - 1]
        end = geometry[index]
        segment_miles = haversine_miles(start, end)

        if traversed_miles + segment_miles >= miles_from_start and segment_miles > 0:
            remaining_miles = miles_from_start - traversed_miles
            ratio = remaining_miles / segment_miles
            return [
                round(start[0] + ((end[0] - start[0]) * ratio), 6),
                round(start[1] + ((end[1] - start[1]) * ratio), 6),
            ]

        traversed_miles += segment_miles

    return geometry[-1]


def geometry_distance_miles(geometry: list[Coordinate]) -> float:
    if len(geometry) < 2:
        return 0.0

    return sum(
        haversine_miles(geometry[index - 1], geometry[index])
        for index in range(1, len(geometry))
    )


def coordinates_match(
    start: Coordinate,
    end: Coordinate,
    tolerance_miles: float = WAYPOINT_MATCH_TOLERANCE_MILES,
) -> bool:
    return haversine_miles(start, end) <= tolerance_miles
