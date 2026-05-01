from trips.maps import service
from trips.maps.errors import MapServiceError
from trips.maps.geometry import haversine_miles


def test_get_route_data_builds_zero_length_leg_for_duplicate_consecutive_waypoints(
    monkeypatch,
):
    captured_coordinates: list[list[float]] = []

    monkeypatch.setattr(service, "get_openrouteservice_api_key", lambda: "test-key")
    monkeypatch.setattr(
        service,
        "search_location_suggestions",
        lambda query_text, api_key, limit: [],
    )
    monkeypatch.setattr(
        service,
        "geocode_location",
        lambda location, api_key: {
            "Chicago, IL": {
                "query": "Chicago, IL",
                "label": "Chicago, IL",
                "coordinates": [-87.6298, 41.8781],
            },
            "Dallas, TX": {
                "query": "Dallas, TX",
                "label": "Dallas, TX",
                "coordinates": [-96.797, 32.7767],
            },
        }[location],
    )

    def fake_request_directions(*, coordinates, api_key):
        captured_coordinates.extend(coordinates)
        return {
            "features": [
                {
                    "geometry": {
                        "coordinates": [
                            [-87.6298, 41.8781],
                            [-96.797, 32.7767],
                        ]
                    },
                    "properties": {
                        "summary": {
                            "distance": 1609344,
                            "duration": 36000,
                        },
                        "segments": [
                            {
                                "distance": 1609344,
                                "duration": 36000,
                            }
                        ],
                        "way_points": [0, 1],
                    },
                }
            ]
        }

    monkeypatch.setattr(service, "request_directions", fake_request_directions)

    route_data = service.get_route_data(
        current_location="Chicago, IL",
        pickup_location="Chicago, IL",
        dropoff_location="Dallas, TX",
    )

    assert captured_coordinates == [
        [-87.6298, 41.8781],
        [-96.797, 32.7767],
    ]
    assert route_data["legs"][0]["kind"] == "to_pickup"
    assert route_data["legs"][0]["distance_miles"] == 0
    assert route_data["legs"][0]["duration_hours"] == 0
    assert route_data["legs"][1]["kind"] == "to_dropoff"
    assert route_data["legs"][1]["distance_miles"] == 1000
    assert route_data["legs"][1]["duration_hours"] == 10


def test_get_route_data_reconstructs_legs_when_segments_are_missing(monkeypatch):
    geometry = [
        [-87.6298, 41.8781],
        [-90.1994, 38.627],
        [-96.797, 32.7767],
    ]
    total_miles = haversine_miles(geometry[0], geometry[1]) + haversine_miles(
        geometry[1], geometry[2]
    )

    monkeypatch.setattr(service, "get_openrouteservice_api_key", lambda: "test-key")
    monkeypatch.setattr(
        service,
        "search_location_suggestions",
        lambda query_text, api_key, limit: [],
    )
    monkeypatch.setattr(
        service,
        "geocode_location",
        lambda location, api_key: {
            "Chicago, IL": {
                "query": "Chicago, IL",
                "label": "Chicago, IL",
                "coordinates": geometry[0],
            },
            "St. Louis, MO": {
                "query": "St. Louis, MO",
                "label": "St. Louis, MO",
                "coordinates": geometry[1],
            },
            "Dallas, TX": {
                "query": "Dallas, TX",
                "label": "Dallas, TX",
                "coordinates": geometry[2],
            },
        }[location],
    )
    monkeypatch.setattr(
        service,
        "request_directions",
        lambda **kwargs: {
            "features": [
                {
                    "geometry": {"coordinates": geometry},
                    "properties": {
                        "summary": {
                            "distance": total_miles * 1609.344,
                            "duration": 21600,
                        },
                        "segments": [],
                        "way_points": [0, 1, 2],
                    },
                }
            ]
        },
    )

    route_data = service.get_route_data(
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
    )

    assert len(route_data["legs"]) == 2
    assert route_data["legs"][0]["kind"] == "to_pickup"
    assert route_data["legs"][1]["kind"] == "to_dropoff"
    assert route_data["legs"][0]["distance_miles"] > 0
    assert route_data["legs"][1]["distance_miles"] > 0
    assert route_data["legs"][0]["duration_hours"] > 0
    assert route_data["legs"][1]["duration_hours"] > 0
    assert round(
        route_data["legs"][0]["duration_hours"] + route_data["legs"][1]["duration_hours"],
        2,
    ) == route_data["duration_hours"]


def test_get_route_data_uses_supplied_waypoints_without_geocoding(monkeypatch):
    requested_locations: list[str] = []

    monkeypatch.setattr(service, "get_openrouteservice_api_key", lambda: "test-key")
    monkeypatch.setattr(
        service,
        "search_location_suggestions",
        lambda query_text, api_key, limit: [],
    )

    def fake_geocode(location, api_key):
        requested_locations.append(location)
        raise AssertionError("geocode_location should not be called when coordinates are supplied")

    monkeypatch.setattr(service, "geocode_location", fake_geocode)
    monkeypatch.setattr(
        service,
        "request_directions",
        lambda **kwargs: {
            "features": [
                {
                    "geometry": {
                        "coordinates": [
                            [-87.6298, 41.8781],
                            [-90.1994, 38.627],
                            [-96.797, 32.7767],
                        ]
                    },
                    "properties": {
                        "summary": {
                            "distance": 2000,
                            "duration": 7200,
                        },
                        "segments": [
                            {"distance": 1000, "duration": 3600},
                            {"distance": 1000, "duration": 3600},
                        ],
                        "way_points": [0, 1, 2],
                    },
                }
            ]
        },
    )

    route_data = service.get_route_data(
        current_location="Chicago, IL, USA",
        pickup_location="St. Louis, MO, USA",
        dropoff_location="Dallas, TX, USA",
        current_waypoint={
            "label": "Chicago, IL, USA",
            "query": "Chicago, IL",
            "coordinates": [-87.6298, 41.8781],
        },
        pickup_waypoint={
            "label": "St. Louis, MO, USA",
            "query": "St. Louis, MO",
            "coordinates": [-90.1994, 38.627],
        },
        dropoff_waypoint={
            "label": "Dallas, TX, USA",
            "query": "Dallas, TX",
            "coordinates": [-96.797, 32.7767],
        },
    )

    assert requested_locations == []
    assert route_data["waypoints"]["current"]["label"] == "Chicago, IL, USA"
    assert route_data["waypoints"]["pickup"]["label"] == "St. Louis, MO, USA"
    assert route_data["waypoints"]["dropoff"]["label"] == "Dallas, TX, USA"


def test_search_locations_falls_back_to_search_when_autocomplete_is_empty(monkeypatch):
    monkeypatch.setattr(service, "get_openrouteservice_api_key", lambda: "test-key")
    monkeypatch.setattr(
        service,
        "search_location_suggestions",
        lambda query_text, api_key, limit: [
            {
                "label": "Chicago, IL, USA",
                "query": "Chicago",
                "coordinates": [-87.6298, 41.8781],
            }
        ],
    )

    results = service.search_locations("Chicago", limit=5)

    assert results == [
        {
            "label": "Chicago, IL, USA",
            "query": "Chicago",
            "coordinates": [-87.6298, 41.8781],
        }
    ]


def test_get_route_data_wraps_geocode_failures_with_location_guidance(monkeypatch):
    monkeypatch.setattr(service, "get_openrouteservice_api_key", lambda: "test-key")
    monkeypatch.setattr(
        service,
        "search_location_suggestions",
        lambda query_text, api_key, limit: [],
    )
    monkeypatch.setattr(
        service,
        "geocode_location",
        lambda location, api_key: (_ for _ in ()).throw(
            MapServiceError(
                f"OpenRouteService could not find a location for '{location}'."
            )
        ),
    )

    try:
        service.get_route_data(
            current_location="Chicago, IL",
            pickup_location="St. Louis, MO",
            dropoff_location="Dallas, TX",
        )
    except MapServiceError as error:
        message = str(error)
    else:
        raise AssertionError("Expected get_route_data to raise MapServiceError")

    assert "current location" in message
    assert "dropdown" in message


def test_get_route_data_wraps_direction_failures_with_route_guidance(monkeypatch):
    monkeypatch.setattr(service, "get_openrouteservice_api_key", lambda: "test-key")
    monkeypatch.setattr(
        service,
        "search_location_suggestions",
        lambda query_text, api_key, limit: [
            {
                "query": location,
                "label": location,
                "coordinates": coordinates,
            }
            for location, coordinates in {
                "Chicago, IL": [-87.6298, 41.8781],
                "St. Louis, MO": [-90.1994, 38.627],
                "Dallas, TX": [-96.797, 32.7767],
            }.items()
            if location == query_text
        ],
    )
    monkeypatch.setattr(
        service,
        "geocode_location",
        lambda location, api_key: {
            "Chicago, IL": {
                "query": "Chicago, IL",
                "label": "Chicago, IL",
                "coordinates": [-87.6298, 41.8781],
            },
            "St. Louis, MO": {
                "query": "St. Louis, MO",
                "label": "St. Louis, MO",
                "coordinates": [-90.1994, 38.627],
            },
            "Dallas, TX": {
                "query": "Dallas, TX",
                "label": "Dallas, TX",
                "coordinates": [-96.797, 32.7767],
            },
        }[location],
    )
    monkeypatch.setattr(
        service,
        "request_directions",
        lambda **kwargs: (_ for _ in ()).throw(
            MapServiceError("Failed to fetch route directions from OpenRouteService.")
        ),
    )

    try:
        service.get_route_data(
            current_location="Chicago, IL",
            pickup_location="St. Louis, MO",
            dropoff_location="Dallas, TX",
        )
    except MapServiceError as error:
        message = str(error)
    else:
        raise AssertionError("Expected get_route_data to raise MapServiceError")

    assert "drivable route" in message
    assert "suggested locations" in message


def test_get_route_data_prefers_search_suggestions_for_free_text_locations(monkeypatch):
    requested_locations: list[str] = []
    requested_coordinates: list[list[list[float]]] = []

    monkeypatch.setattr(service, "get_openrouteservice_api_key", lambda: "test-key")
    monkeypatch.setattr(
        service,
        "search_location_suggestions",
        lambda query_text, api_key, limit: [
            {
                "label": {
                    "Chicago, IL": "City of Chicago, IL, USA",
                    "St. Louis, MO": "St. Louis, Missouri, USA",
                    "Dallas, TX": "Dallas, Texas, USA",
                }[query_text],
                "query": query_text,
                "coordinates": {
                    "Chicago, IL": [-87.6298, 41.8781],
                    "St. Louis, MO": [-90.1994, 38.627],
                    "Dallas, TX": [-96.797, 32.7767],
                }[query_text],
            }
        ],
    )

    def fake_geocode(location, api_key):
        requested_locations.append(location)
        raise AssertionError(
            "geocode_location should not be called when a search suggestion exists"
        )

    def fake_request_directions(*, coordinates, api_key):
        requested_coordinates.append(coordinates)
        return {
            "features": [
                {
                    "geometry": {"coordinates": coordinates},
                    "properties": {
                        "summary": {
                            "distance": 2000,
                            "duration": 7200,
                        },
                        "segments": [
                            {"distance": 1000, "duration": 3600},
                            {"distance": 1000, "duration": 3600},
                        ],
                        "way_points": [0, 1, 2],
                    },
                }
            ]
        }

    monkeypatch.setattr(service, "geocode_location", fake_geocode)
    monkeypatch.setattr(service, "request_directions", fake_request_directions)

    route_data = service.get_route_data(
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
    )

    assert requested_locations == []
    assert requested_coordinates == [
        [
            [-87.6298, 41.8781],
            [-90.1994, 38.627],
            [-96.797, 32.7767],
        ]
    ]
    assert route_data["waypoints"]["current"]["label"] == "City of Chicago, IL, USA"
