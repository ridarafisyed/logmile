from collections.abc import Mapping
from datetime import UTC, datetime
import logging
import time
from typing import Any

from ..hos_engine import plan_hos_schedule
from ..map_service import attach_stop_coordinates, get_route_data
from ..types import TripPlanResponseDict, TripPlanningInput, WaypointDict

logger = logging.getLogger("trips.trip_planner")


def normalize_location_input(
    location_value: str | WaypointDict,
) -> tuple[str, WaypointDict | None]:
    if isinstance(location_value, str):
        return location_value, None

    return location_value["label"], location_value


def trip_planning_input_from_validated_data(
    validated_data: Mapping[str, Any],
) -> TripPlanningInput:
    current_location, current_waypoint = normalize_location_input(
        validated_data["current_location"]
    )
    pickup_location, pickup_waypoint = normalize_location_input(
        validated_data["pickup_location"]
    )
    dropoff_location, dropoff_waypoint = normalize_location_input(
        validated_data["dropoff_location"]
    )

    return TripPlanningInput(
        current_location=current_location,
        pickup_location=pickup_location,
        dropoff_location=dropoff_location,
        current_cycle_used=validated_data["current_cycle_used"],
        cycle_rule=validated_data["cycle_rule"],
        trip_start_at=validated_data.get("trip_start_at", datetime.now(UTC)),
        current_waypoint=current_waypoint,
        pickup_waypoint=pickup_waypoint,
        dropoff_waypoint=dropoff_waypoint,
    )


def build_trip_plan(trip_input: TripPlanningInput) -> TripPlanResponseDict:
    started_at = time.perf_counter()

    route_data = get_route_data(
        current_location=trip_input.current_location,
        pickup_location=trip_input.pickup_location,
        dropoff_location=trip_input.dropoff_location,
        current_waypoint=trip_input.current_waypoint,
        pickup_waypoint=trip_input.pickup_waypoint,
        dropoff_waypoint=trip_input.dropoff_waypoint,
    )

    hos_plan = plan_hos_schedule(
        distance_miles=route_data["distance_miles"],
        duration_hours=route_data["duration_hours"],
        current_cycle_used=trip_input.current_cycle_used,
        current_location=trip_input.current_location,
        pickup_location=trip_input.pickup_location,
        dropoff_location=trip_input.dropoff_location,
        cycle_rule=trip_input.cycle_rule,
        trip_start_at=trip_input.trip_start_at,
        route_legs=route_data["legs"],
    )

    hos_plan["stops"] = attach_stop_coordinates(
        route_data=route_data,
        stops=hos_plan["stops"],
    )

    response_payload = {
        "route": route_data,
        "hos_plan": hos_plan,
    }
    logger.info(
        "trip_planned cycle_rule=%s legal=%s distance_miles=%.2f total_days=%s elapsed_ms=%d",
        trip_input.cycle_rule,
        hos_plan["is_legal"],
        route_data["distance_miles"],
        hos_plan.get("summary", {}).get("total_days"),
        int((time.perf_counter() - started_at) * 1000),
    )
    return response_payload
