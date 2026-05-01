from trips.serializers import TripPlanRequestSerializer


def test_trip_plan_request_serializer_accepts_text_locations():
    serializer = TripPlanRequestSerializer(
        data={
            "current_location": "Chicago, IL",
            "pickup_location": "St. Louis, MO",
            "dropoff_location": "Dallas, TX",
            "trip_start_at": "2026-05-01T11:45:00-05:00",
            "current_cycle_used": 20,
            "cycle_rule": "70_8",
        }
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["current_location"] == "Chicago, IL"
    assert serializer.validated_data["trip_start_at"].isoformat() == "2026-05-01T11:45:00-05:00"


def test_trip_plan_request_serializer_accepts_selected_location_objects():
    serializer = TripPlanRequestSerializer(
        data={
            "current_location": {
                "label": "Chicago, IL, USA",
                "query": "Chicago, IL",
                "coordinates": [-87.6298, 41.8781],
            },
            "pickup_location": {
                "label": "St. Louis, MO, USA",
                "coordinates": [-90.1994, 38.627],
            },
            "dropoff_location": {
                "label": "Dallas, TX, USA",
                "coordinates": [-96.797, 32.7767],
            },
            "trip_start_at": "2026-05-01T11:45:00-05:00",
            "current_cycle_used": 20,
            "cycle_rule": "70_8",
        }
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["current_location"]["label"] == "Chicago, IL, USA"
    assert serializer.validated_data["pickup_location"]["query"] == "St. Louis, MO, USA"
