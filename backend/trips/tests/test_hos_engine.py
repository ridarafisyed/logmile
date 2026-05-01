from datetime import UTC, datetime

from trips.hos_engine import plan_hos_schedule


MIDNIGHT_START = datetime(2026, 5, 1, 0, 0, tzinfo=UTC)


def total_logged_hours(day_log: dict) -> float:
    totals = day_log["totals"]
    return (
        totals["off_duty"]
        + totals["sleeper_berth"]
        + totals["driving"]
        + totals["on_duty"]
    )


def test_rejects_trip_when_cycle_hours_are_already_exhausted():
    plan = plan_hos_schedule(
        distance_miles=100,
        duration_hours=2,
        current_cycle_used=70,
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
        trip_start_at=MIDNIGHT_START,
    )

    assert plan["is_legal"] is False
    assert "restart" in plan["message"].lower()
    assert plan["daily_logs"] == []
    assert plan["stops"] == []


def test_places_pickup_after_arriving_when_route_legs_are_available():
    plan = plan_hos_schedule(
        distance_miles=340,
        duration_hours=6,
        current_cycle_used=20,
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
        trip_start_at=MIDNIGHT_START,
        route_legs=[
            {
                "kind": "to_pickup",
                "start": "Chicago, IL",
                "end": "St. Louis, MO",
                "distance_miles": 120,
                "duration_hours": 2,
            },
            {
                "kind": "to_dropoff",
                "start": "St. Louis, MO",
                "end": "Dallas, TX",
                "distance_miles": 220,
                "duration_hours": 4,
            },
        ],
    )

    assert plan["is_legal"] is True
    assert plan["stops"][0]["type"] == "pickup"
    assert plan["stops"][0]["hour"] == 2
    assert plan["stops"][-1]["type"] == "dropoff"
    assert len(plan["daily_logs"]) == 1
    assert total_logged_hours(plan["daily_logs"][0]) == 24


def test_long_trip_adds_breaks_fuel_and_rest_stops():
    plan = plan_hos_schedule(
        distance_miles=1300,
        duration_hours=23.64,
        current_cycle_used=10,
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
        trip_start_at=MIDNIGHT_START,
        route_legs=[
            {
                "kind": "to_pickup",
                "start": "Chicago, IL",
                "end": "St. Louis, MO",
                "distance_miles": 200,
                "duration_hours": 3.64,
            },
            {
                "kind": "to_dropoff",
                "start": "St. Louis, MO",
                "end": "Dallas, TX",
                "distance_miles": 1100,
                "duration_hours": 20,
            },
        ],
    )

    stop_types = {stop["type"] for stop in plan["stops"]}

    assert plan["is_legal"] is True
    assert {"break", "fuel", "rest", "pickup", "dropoff"} <= stop_types
    assert len(plan["daily_logs"]) >= 2
    assert all(total_logged_hours(day_log) == 24 for day_log in plan["daily_logs"])


def test_60_7_cycle_rule_uses_smaller_cycle_limit():
    plan = plan_hos_schedule(
        distance_miles=100,
        duration_hours=2,
        current_cycle_used=59.5,
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
        cycle_rule="60_7",
        trip_start_at=MIDNIGHT_START,
    )

    assert plan["is_legal"] is False
    assert "cycle hours" in plan["message"].lower() or "restart" in plan["message"].lower()


def test_off_duty_break_does_not_reduce_remaining_cycle_hours():
    plan = plan_hos_schedule(
        distance_miles=550,
        duration_hours=10,
        current_cycle_used=20,
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
        trip_start_at=MIDNIGHT_START,
        route_legs=[
            {
                "kind": "to_pickup",
                "start": "Chicago, IL",
                "end": "St. Louis, MO",
                "distance_miles": 220,
                "duration_hours": 4,
            },
            {
                "kind": "to_dropoff",
                "start": "St. Louis, MO",
                "end": "Dallas, TX",
                "distance_miles": 330,
                "duration_hours": 6,
            },
        ],
    )

    assert plan["is_legal"] is True
    assert any(stop["type"] == "break" for stop in plan["stops"])
    assert plan["summary"]["remaining_cycle_hours_after_trip"] == 38


def test_exact_two_day_trip_keeps_expected_cycle_hours_after_trip():
    plan = plan_hos_schedule(
        distance_miles=969.53,
        duration_hours=16.54,
        current_cycle_used=20,
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
        trip_start_at=MIDNIGHT_START,
        route_legs=[
            {
                "kind": "to_pickup",
                "start": "Chicago, IL",
                "end": "St. Louis, MO",
                "distance_miles": 297.0,
                "duration_hours": 5.4,
            },
            {
                "kind": "to_dropoff",
                "start": "St. Louis, MO",
                "end": "Dallas, TX",
                "distance_miles": 672.53,
                "duration_hours": 11.14,
            },
        ],
    )

    assert plan["is_legal"] is True
    assert plan["summary"]["estimated_driving_hours"] == 16.54
    assert plan["summary"]["remaining_cycle_hours_after_trip"] == 31.46
    assert len(plan["daily_logs"]) == 2


def test_trip_start_time_adds_pre_trip_off_duty_and_uses_real_clock_time():
    plan = plan_hos_schedule(
        distance_miles=969.53,
        duration_hours=16.54,
        current_cycle_used=20,
        current_location="Chicago, IL",
        pickup_location="St. Louis, MO",
        dropoff_location="Dallas, TX",
        trip_start_at=datetime(2026, 5, 1, 11, 45, tzinfo=UTC),
        route_legs=[
            {
                "kind": "to_pickup",
                "start": "Chicago, IL",
                "end": "St. Louis, MO",
                "distance_miles": 297.0,
                "duration_hours": 5.4,
            },
            {
                "kind": "to_dropoff",
                "start": "St. Louis, MO",
                "end": "Dallas, TX",
                "distance_miles": 672.53,
                "duration_hours": 11.14,
            },
        ],
    )

    first_day_segments = plan["daily_logs"][0]["segments"]
    second_day_segments = plan["daily_logs"][1]["segments"]

    assert plan["is_legal"] is True
    assert first_day_segments[0]["status"] == "off_duty"
    assert first_day_segments[0]["start"] == 0
    assert first_day_segments[0]["end"] == 11.75
    assert first_day_segments[1]["status"] == "driving"
    assert first_day_segments[1]["start"] == 11.75
    assert first_day_segments[-1]["status"] == "driving"
    assert first_day_segments[-1]["end"] == 24
    assert second_day_segments[0]["status"] == "driving"
    assert second_day_segments[0]["start"] == 0
    assert second_day_segments[0]["end"] == 0.25
    assert second_day_segments[1]["status"] == "off_duty"
    assert second_day_segments[1]["duration"] == 10


def test_daily_logs_do_not_wrap_segments_backward_across_midnight():
    plan = plan_hos_schedule(
        distance_miles=958.99,
        duration_hours=16.05,
        current_cycle_used=20,
        current_location="Chicago, IL, USA",
        pickup_location="St. Louis, MO, USA",
        dropoff_location="Dallas, TX, USA",
        trip_start_at=datetime(2026, 5, 1, 12, 23, tzinfo=UTC),
        route_legs=[
            {
                "kind": "to_pickup",
                "start": "Chicago, IL, USA",
                "end": "St. Louis, MO, USA",
                "distance_miles": 273.35,
                "duration_hours": 4.97,
            },
            {
                "kind": "to_dropoff",
                "start": "St. Louis, MO, USA",
                "end": "Dallas, TX, USA",
                "distance_miles": 685.64,
                "duration_hours": 11.08,
            },
        ],
    )

    day_one_segments = plan["daily_logs"][0]["segments"]
    day_two_segments = plan["daily_logs"][1]["segments"]

    assert plan["is_legal"] is True
    assert all(segment["end"] > segment["start"] for segment in day_one_segments)
    assert all(segment["end"] > segment["start"] for segment in day_two_segments)
    assert day_one_segments[-1]["status"] == "driving"
    assert day_one_segments[-1]["start"] == 21.88
    assert day_one_segments[-1]["end"] == 24
    assert day_two_segments[0]["status"] == "driving"
    assert day_two_segments[0]["start"] == 0
    assert day_two_segments[0]["end"] == 0.88


def test_same_day_reset_waits_until_next_log_day_before_resuming_work():
    plan = plan_hos_schedule(
        distance_miles=961.03,
        duration_hours=16.43,
        current_cycle_used=20,
        current_location="Chicago, IL, USA",
        pickup_location="St. Louis County, MO, USA",
        dropoff_location="Dallas, TX, USA",
        trip_start_at=datetime(2026, 5, 1, 19, 8, tzinfo=UTC),
        route_legs=[
            {
                "kind": "to_pickup",
                "start": "Chicago, IL, USA",
                "end": "St. Louis County, MO, USA",
                "distance_miles": 284.46,
                "duration_hours": 5.37,
            },
            {
                "kind": "to_dropoff",
                "start": "St. Louis County, MO, USA",
                "end": "Dallas, TX, USA",
                "distance_miles": 676.57,
                "duration_hours": 11.06,
            },
        ],
    )

    day_two_segments = plan["daily_logs"][1]["segments"]
    day_three_segments = plan["daily_logs"][2]["segments"]

    assert plan["is_legal"] is True
    assert plan["summary"]["total_days"] == 3
    assert plan["summary"]["estimated_arrival_at"] == "2026-05-03T06:25:48+00:00"
    assert day_two_segments[-1]["status"] == "off_duty"
    assert day_two_segments[-1]["start"] == 17.63
    assert day_two_segments[-1]["end"] == 24
    assert "next log day" in day_two_segments[-1]["note"].lower()
    assert day_three_segments[0]["status"] == "driving"
    assert day_three_segments[0]["start"] == 0
    assert day_three_segments[0]["end"] == 5.43
    assert any(
        "carried over from the prior log day" in remark["note"].lower()
        for remark in plan["daily_logs"][1]["remarks"]
    )
