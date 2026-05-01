from datetime import UTC, datetime

from trips.services import trip_planner
from trips.types import TripPlanningInput


def test_build_trip_plan_orchestrates_route_hos_and_stop_hydration(monkeypatch):
    route_data = {
        "distance_miles": 100.0,
        "duration_hours": 2.0,
        "geometry": [[0.0, 0.0], [1.0, 1.0]],
        "locations": {
            "current": "Chicago, IL",
            "pickup": "St. Louis, MO",
            "dropoff": "Dallas, TX",
        },
        "waypoints": {
            "current": {
                "query": "Chicago, IL",
                "label": "Chicago, IL",
                "coordinates": [0.0, 0.0],
            },
            "pickup": {
                "query": "St. Louis, MO",
                "label": "St. Louis, MO",
                "coordinates": [0.5, 0.5],
            },
            "dropoff": {
                "query": "Dallas, TX",
                "label": "Dallas, TX",
                "coordinates": [1.0, 1.0],
            },
        },
        "legs": [
            {
                "kind": "to_pickup",
                "start": "Chicago, IL",
                "end": "St. Louis, MO",
                "distance_miles": 50.0,
                "duration_hours": 1.0,
            },
            {
                "kind": "to_dropoff",
                "start": "St. Louis, MO",
                "end": "Dallas, TX",
                "distance_miles": 50.0,
                "duration_hours": 1.0,
            },
        ],
    }
    hos_plan = {
        "is_legal": True,
        "message": "Trip planned successfully.",
        "daily_logs": [],
        "stops": [
            {
                "type": "pickup",
                "location": "St. Louis, MO",
                "day": 1,
                "hour": 1.0,
                "duration": 1.0,
            }
        ],
    }
    hydrated_stops = [
        {
            "type": "pickup",
            "location": "St. Louis, MO",
            "day": 1,
            "hour": 1.0,
            "duration": 1.0,
            "coordinates": [0.5, 0.5],
        }
    ]

    monkeypatch.setattr(trip_planner, "get_route_data", lambda **_: route_data)
    monkeypatch.setattr(trip_planner, "plan_hos_schedule", lambda **_: hos_plan)
    monkeypatch.setattr(
        trip_planner,
        "attach_stop_coordinates",
        lambda route_data, stops: hydrated_stops,
    )

    trip_input = TripPlanningInput(
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
        current_cycle_used=20.0,
        cycle_rule="70_8",
        trip_start_at=datetime(2026, 5, 1, 0, 0, tzinfo=UTC),
    )

    result = trip_planner.build_trip_plan(trip_input)

    assert result["route"] == route_data
    assert result["hos_plan"]["stops"] == hydrated_stops
