import logging

from ..types import Coordinate, RouteDataDict, RouteLegDict, StopDict, WaypointDict
from ..utils import meters_to_miles, round_value, seconds_to_hours
from .client import (
    geocode_location,
    get_openrouteservice_api_key,
    request_directions,
    search_location_suggestions,
)
from .errors import MapServiceError
from .geometry import coordinate_at_distance, coordinates_match, geometry_distance_miles

logger = logging.getLogger("trips.maps")

LOCATION_ROLE_LABELS = {
    "current": "current location",
    "pickup": "pickup location",
    "dropoff": "dropoff location",
}


def build_leg(
    kind: str,
    start_label: str,
    end_label: str,
    segment: dict,
) -> RouteLegDict:
    return build_leg_from_values(
        kind=kind,
        start_label=start_label,
        end_label=end_label,
        distance_miles=meters_to_miles(segment.get("distance", 0)),
        duration_hours=seconds_to_hours(segment.get("duration", 0)),
    )


def build_leg_from_values(
    kind: str,
    start_label: str,
    end_label: str,
    distance_miles: float,
    duration_hours: float,
) -> RouteLegDict:
    return {
        "kind": kind,
        "start": start_label,
        "end": end_label,
        "distance_miles": round_value(distance_miles),
        "duration_hours": round_value(duration_hours),
    }


def build_zero_distance_leg(
    kind: str,
    start_label: str,
    end_label: str,
) -> RouteLegDict:
    return build_leg_from_values(
        kind=kind,
        start_label=start_label,
        end_label=end_label,
        distance_miles=0,
        duration_hours=0,
    )


def resolve_waypoint(
    location_label: str,
    api_key: str,
    location_role: str,
    waypoint: WaypointDict | None = None,
) -> WaypointDict:
    if waypoint is not None:
        return {
            "label": waypoint["label"],
            "query": waypoint["query"],
            "coordinates": waypoint["coordinates"],
        }

    try:
        suggestions = search_location_suggestions(
            query_text=location_label,
            api_key=api_key,
            limit=1,
        )
    except MapServiceError as error:
        logger.warning(
            "ors_location_suggestion_failed role=%s location=%s error=%s",
            location_role,
            location_label,
            error,
        )
        suggestions = []

    if suggestions:
        return suggestions[0]

    try:
        return geocode_location(location_label, api_key)
    except MapServiceError as error:
        role_label = LOCATION_ROLE_LABELS.get(location_role, "location")
        message = str(error)

        if (
            "could not find a location" in message.lower()
            or "failed to geocode" in message.lower()
            or "invalid coordinates" in message.lower()
        ):
            raise MapServiceError(
                f"Could not locate the {role_label} '{location_label}'. "
                "Select a suggestion from the dropdown or enter a fuller place name."
            ) from error

        raise MapServiceError(
            f"Failed to resolve the {role_label} '{location_label}'. {message}"
        ) from error


def dedupe_consecutive_waypoints(
    waypoints: list[WaypointDict],
) -> tuple[list[WaypointDict], list[int]]:
    unique_waypoints: list[WaypointDict] = []
    logical_to_unique_index: list[int] = []

    for waypoint in waypoints:
        if (
            not unique_waypoints
            or not coordinates_match(
                waypoint["coordinates"],
                unique_waypoints[-1]["coordinates"],
            )
        ):
            unique_waypoints.append(waypoint)
        logical_to_unique_index.append(len(unique_waypoints) - 1)

    return unique_waypoints, logical_to_unique_index


def distribute_total(total: float, weights: list[float]) -> list[float]:
    if not weights or total <= 0:
        return [0.0 for _ in weights]

    total_weight = sum(weights)
    if total_weight <= 0:
        even_share = total / len(weights)
        values = [round_value(even_share) for _ in weights[:-1]]
        last_value = round_value(total - sum(values))
        return [*values, last_value]

    distributed_values: list[float] = []
    for weight in weights[:-1]:
        distributed_values.append(round_value(total * (weight / total_weight)))

    distributed_values.append(round_value(total - sum(distributed_values)))
    return distributed_values


def build_legs_from_geometry(
    route_labels: list[tuple[str, str, str]],
    geometry: list[Coordinate],
    waypoint_indices: list[int],
    total_distance_miles: float,
    total_duration_hours: float,
) -> list[RouteLegDict]:
    if len(waypoint_indices) != 3:
        raise MapServiceError(
            "OpenRouteService did not return enough waypoint markers to split the route."
        )

    leg_geometries = []
    raw_leg_distances = []
    for start_index, end_index in zip(waypoint_indices, waypoint_indices[1:]):
        leg_geometry = geometry[start_index : end_index + 1]
        leg_geometries.append(leg_geometry)
        raw_leg_distances.append(geometry_distance_miles(leg_geometry))

    distributed_distances = distribute_total(total_distance_miles, raw_leg_distances)
    distributed_durations = distribute_total(total_duration_hours, raw_leg_distances)

    return [
        build_leg_from_values(
            kind=kind,
            start_label=start_label,
            end_label=end_label,
            distance_miles=distance_miles,
            duration_hours=duration_hours,
        )
        for (kind, start_label, end_label), distance_miles, duration_hours in zip(
            route_labels,
            distributed_distances,
            distributed_durations,
        )
    ]


def build_route_legs(
    current_location: str,
    pickup_location: str,
    dropoff_location: str,
    logical_to_unique_index: list[int],
    geometry: list[Coordinate],
    summary: dict,
    segments: list[dict],
    waypoint_indices: list[int],
) -> list[RouteLegDict]:
    route_labels = [
        ("to_pickup", current_location, pickup_location),
        ("to_dropoff", pickup_location, dropoff_location),
    ]
    total_distance_miles = meters_to_miles(summary.get("distance", 0))
    total_duration_hours = seconds_to_hours(summary.get("duration", 0))
    unique_waypoint_count = len(set(logical_to_unique_index))

    if unique_waypoint_count == 1:
        return [
            build_zero_distance_leg(*route_labels[0]),
            build_zero_distance_leg(*route_labels[1]),
        ]

    if unique_waypoint_count == 2:
        actual_segment = segments[0] if segments else summary
        return [
            build_zero_distance_leg(kind, start_label, end_label)
            if logical_to_unique_index[index] == logical_to_unique_index[index + 1]
            else build_leg_from_values(
                kind=kind,
                start_label=start_label,
                end_label=end_label,
                distance_miles=meters_to_miles(actual_segment.get("distance", 0)),
                duration_hours=seconds_to_hours(actual_segment.get("duration", 0)),
            )
            for index, (kind, start_label, end_label) in enumerate(route_labels)
        ]

    if len(segments) >= 2:
        return [
            build_leg(*route_labels[0], segments[0]),
            build_leg(*route_labels[1], segments[1]),
        ]

    logger.warning(
        "ors_segments_missing logical_waypoints=%s waypoint_indices=%s",
        logical_to_unique_index,
        waypoint_indices,
    )
    return build_legs_from_geometry(
        route_labels=route_labels,
        geometry=geometry,
        waypoint_indices=waypoint_indices,
        total_distance_miles=total_distance_miles,
        total_duration_hours=total_duration_hours,
    )


def get_route_data(
    current_location: str,
    pickup_location: str,
    dropoff_location: str,
    current_waypoint: WaypointDict | None = None,
    pickup_waypoint: WaypointDict | None = None,
    dropoff_waypoint: WaypointDict | None = None,
) -> RouteDataDict:
    api_key = get_openrouteservice_api_key()

    current_waypoint = resolve_waypoint(
        location_label=current_location,
        api_key=api_key,
        location_role="current",
        waypoint=current_waypoint,
    )
    pickup_waypoint = resolve_waypoint(
        location_label=pickup_location,
        api_key=api_key,
        location_role="pickup",
        waypoint=pickup_waypoint,
    )
    dropoff_waypoint = resolve_waypoint(
        location_label=dropoff_location,
        api_key=api_key,
        location_role="dropoff",
        waypoint=dropoff_waypoint,
    )
    logical_waypoints = [current_waypoint, pickup_waypoint, dropoff_waypoint]
    unique_waypoints, logical_to_unique_index = dedupe_consecutive_waypoints(
        logical_waypoints
    )

    if len(unique_waypoints) == 1:
        geometry = [unique_waypoints[0]["coordinates"]]
        summary = {"distance": 0, "duration": 0}
        segments: list[dict] = []
        waypoint_indices = [0, 0, 0]
    else:
        try:
            directions_payload = request_directions(
                coordinates=[waypoint["coordinates"] for waypoint in unique_waypoints],
                api_key=api_key,
            )
        except MapServiceError as error:
            message = str(error)
            if (
                "temporarily unavailable" in message.lower()
                or "rate limit" in message.lower()
                or "rejected the request" in message.lower()
            ):
                raise

            raise MapServiceError(
                "Failed to calculate a drivable route between the selected current, pickup, and dropoff locations. "
                "Select the suggested locations or use fuller place names, then try again."
            ) from error

        features = directions_payload.get("features", [])
        if not features:
            raise MapServiceError("OpenRouteService did not return any route features.")

        feature = features[0]
        geometry = feature.get("geometry", {}).get("coordinates", [])
        properties = feature.get("properties", {})
        summary = properties.get("summary", {})
        segments = properties.get("segments", [])
        waypoint_indices = properties.get("way_points", [])

    legs = build_route_legs(
        current_location=current_location,
        pickup_location=pickup_location,
        dropoff_location=dropoff_location,
        logical_to_unique_index=logical_to_unique_index,
        geometry=geometry,
        summary=summary,
        segments=segments,
        waypoint_indices=waypoint_indices,
    )

    return {
        "distance_miles": round_value(meters_to_miles(summary.get("distance", 0))),
        "duration_hours": round_value(seconds_to_hours(summary.get("duration", 0))),
        "geometry": geometry,
        "locations": {
            "current": current_location,
            "pickup": pickup_location,
            "dropoff": dropoff_location,
        },
        "waypoints": {
            "current": current_waypoint,
            "pickup": pickup_waypoint,
            "dropoff": dropoff_waypoint,
        },
        "legs": legs,
    }


def search_locations(query_text: str, limit: int = 6) -> list[WaypointDict]:
    api_key = get_openrouteservice_api_key()
    return search_location_suggestions(
        query_text=query_text,
        api_key=api_key,
        limit=limit,
    )


def resolve_stop_coordinates(
    stop: StopDict,
    geometry: list[Coordinate],
    waypoints: dict,
) -> Coordinate:
    if stop["type"] == "pickup":
        return waypoints["pickup"]["coordinates"]
    if stop["type"] == "dropoff":
        return waypoints["dropoff"]["coordinates"]
    if stop["type"] == "rest" and stop.get("miles_from_route_start") is None:
        return waypoints["current"]["coordinates"]
    return coordinate_at_distance(
        geometry=geometry,
        miles_from_start=float(stop.get("miles_from_route_start", 0)),
    )


def attach_stop_coordinates(
    route_data: RouteDataDict,
    stops: list[StopDict],
) -> list[StopDict]:
    geometry = route_data["geometry"]
    waypoints = route_data["waypoints"]
    hydrated_stops = []

    for stop in stops:
        stop_with_coordinates = dict(stop)
        stop_with_coordinates["coordinates"] = resolve_stop_coordinates(
            stop=stop,
            geometry=geometry,
            waypoints=waypoints,
        )
        hydrated_stops.append(stop_with_coordinates)

    return hydrated_stops
