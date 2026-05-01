from trips.maps.geometry import (
    coordinate_at_distance,
    coordinates_match,
    geometry_distance_miles,
    haversine_miles,
)


def test_coordinate_at_distance_returns_start_when_distance_is_zero():
    geometry = [[0.0, 0.0], [1.0, 0.0]]

    coordinate = coordinate_at_distance(geometry=geometry, miles_from_start=0)

    assert coordinate == geometry[0]


def test_coordinate_at_distance_interpolates_between_points():
    geometry = [[0.0, 0.0], [1.0, 0.0]]
    total_miles = haversine_miles(geometry[0], geometry[1])

    coordinate = coordinate_at_distance(
        geometry=geometry,
        miles_from_start=total_miles / 2,
    )

    assert coordinate[0] == 0.5
    assert coordinate[1] == 0.0


def test_geometry_distance_miles_sums_polyline_segments():
    geometry = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]

    total_miles = geometry_distance_miles(geometry)

    assert round(total_miles, 2) == round(
        haversine_miles(geometry[0], geometry[1])
        + haversine_miles(geometry[1], geometry[2]),
        2,
    )


def test_coordinates_match_returns_true_for_near_identical_points():
    assert coordinates_match([0.0, 0.0], [0.0001, 0.0001]) is True
