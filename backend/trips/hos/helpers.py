from datetime import UTC, datetime, timedelta

from ..types import (
    CycleRule,
    DailyLogDict,
    DailyTotalsDict,
    DutyStatus,
    RemarkDict,
    RouteLegDict,
    SegmentDict,
    StopDict,
    StopType,
)
from ..utils import round_hour, round_miles
from .constants import (
    AVERAGE_SPEED_MPH,
    DROPOFF_DURATION_HOURS,
    FLOAT_EPSILON,
    PICKUP_DURATION_HOURS,
)
from .models import (
    CycleRuleConfig,
    DrivePhase,
    Phase,
    RouteLegInput,
    ServicePhase,
    StopEvent,
    TimelineSegment,
)
from .constants import CYCLE_RULES


def create_segment(
    status: str,
    start: float,
    end: float,
    location: str,
    note: str = "",
) -> SegmentDict:
    return {
        "status": status,
        "start": round_hour(start),
        "end": round_hour(end),
        "duration": round_hour(end - start),
        "location": location,
        "note": note,
    }


def build_daily_log(
    day_number: int,
    date: datetime,
    segments: list[SegmentDict],
) -> DailyLogDict:
    ordered_segments = sorted(segments, key=lambda segment: (segment["start"], segment["end"]))
    normalized_segments: list[SegmentDict] = []
    cursor = 0.0

    for segment in ordered_segments:
        if segment["start"] > cursor + FLOAT_EPSILON:
            normalized_segments.append(
                create_segment(
                    status="off_duty",
                    start=cursor,
                    end=segment["start"],
                    location="Rest location",
                )
            )

        normalized_segments.append(segment)
        cursor = max(cursor, segment["end"])

    if cursor < 24 - FLOAT_EPSILON:
        normalized_segments.append(
            create_segment(
                status="off_duty",
                start=cursor,
                end=24,
                location="Rest location",
            )
        )

    totals: DailyTotalsDict = {
        "off_duty": 0.0,
        "sleeper_berth": 0.0,
        "driving": 0.0,
        "on_duty": 0.0,
    }

    for segment in normalized_segments:
        if segment["status"] in totals:
            totals[segment["status"]] += segment["duration"]

    remarks: list[RemarkDict] = [
        {
            "time": segment["start"],
            "location": segment["location"],
            "note": segment["note"],
        }
        for segment in normalized_segments
        if segment.get("note")
    ]

    return {
        "day": day_number,
        "date": date.strftime("%Y-%m-%d"),
        "segments": normalized_segments,
        "totals": {key: round_hour(value) for key, value in totals.items()},
        "total_hours": 24,
        "remarks": remarks,
    }


def normalize_planning_start(trip_start_at: datetime | None) -> datetime:
    if trip_start_at is None:
        return datetime.now(UTC).replace(second=0, microsecond=0)

    if trip_start_at.tzinfo is None:
        trip_start_at = trip_start_at.replace(tzinfo=UTC)

    return trip_start_at.replace(second=0, microsecond=0)


def hours_to_timedelta(hours: float) -> timedelta:
    return timedelta(seconds=hours * 3600)


def midnight_for(date_time: datetime) -> datetime:
    return date_time.replace(hour=0, minute=0, second=0, microsecond=0)


def decimal_hour_for_datetime(date_time: datetime) -> float:
    return round_hour(
        date_time.hour
        + (date_time.minute / 60)
        + (date_time.second / 3600)
        + (date_time.microsecond / 3_600_000_000)
    )


def decimal_hours_since_day_start(date_time: datetime, day_start: datetime) -> float:
    elapsed_seconds = (date_time - day_start).total_seconds()
    elapsed_hours = elapsed_seconds / 3600
    return round_hour(min(max(elapsed_hours, 0.0), 24.0))


def create_timeline_segment(
    status: DutyStatus,
    start_at: datetime,
    end_at: datetime,
    location: str,
    note: str = "",
) -> TimelineSegment:
    return TimelineSegment(
        status=status,
        start_at=start_at,
        end_at=end_at,
        location=location,
        note=note,
    )


def clip_timeline_segment_to_day(
    segment: TimelineSegment,
    day_start: datetime,
    day_end: datetime,
) -> SegmentDict | None:
    overlap_start = max(segment.start_at, day_start)
    overlap_end = min(segment.end_at, day_end)
    if overlap_start >= overlap_end:
        return None

    return create_segment(
        status=segment.status,
        start=decimal_hours_since_day_start(overlap_start, day_start),
        end=decimal_hours_since_day_start(overlap_end, day_start),
        location=segment.location,
        note=segment.note if overlap_start == segment.start_at else "",
    )


def build_daily_logs(
    trip_start_at: datetime,
    timeline_segments: list[TimelineSegment],
) -> list[DailyLogDict]:
    if not timeline_segments:
        return []

    ordered_segments = sorted(timeline_segments, key=lambda segment: segment.start_at)
    current_day_start = midnight_for(trip_start_at)
    final_day_start = midnight_for(
        max(segment.end_at for segment in ordered_segments)
    )

    daily_logs: list[DailyLogDict] = []
    day_number = 1

    while current_day_start <= final_day_start:
        current_day_end = current_day_start + timedelta(days=1)
        day_segments = [
            clipped_segment
            for segment in ordered_segments
            if (
                clipped_segment := clip_timeline_segment_to_day(
                    segment,
                    current_day_start,
                    current_day_end,
                )
            )
            is not None
        ]
        daily_logs.append(build_daily_log(day_number, current_day_start, day_segments))
        current_day_start = current_day_end
        day_number += 1

    return daily_logs


def resolve_cycle_rule(cycle_rule: CycleRule) -> CycleRuleConfig:
    rule = CYCLE_RULES.get(cycle_rule)
    if rule is None:
        raise ValueError(f"Unsupported cycle rule '{cycle_rule}'.")
    return CycleRuleConfig(max_hours=rule["max_hours"], days=rule["days"])


def normalize_route_legs(
    distance_miles: float,
    duration_hours: float | None,
    current_location: str,
    dropoff_location: str,
    route_legs: list[RouteLegDict] | None,
) -> list[RouteLegInput]:
    if route_legs:
        normalized_legs = []
        for leg in route_legs:
            leg_distance_miles = float(leg["distance_miles"])
            leg_duration_hours = leg["duration_hours"]
            if leg_duration_hours <= 0:
                leg_duration_hours = leg_distance_miles / AVERAGE_SPEED_MPH

            normalized_legs.append(
                RouteLegInput(
                    kind=leg["kind"],
                    start=leg["start"],
                    end=leg["end"],
                    distance_miles=leg_distance_miles,
                    duration_hours=float(leg_duration_hours),
                )
            )
        return normalized_legs

    effective_duration_hours = duration_hours
    if effective_duration_hours is None or effective_duration_hours <= 0:
        effective_duration_hours = distance_miles / AVERAGE_SPEED_MPH

    return [
        RouteLegInput(
            kind="full_route",
            start=current_location,
            end=dropoff_location,
            distance_miles=float(distance_miles),
            duration_hours=float(effective_duration_hours),
        )
    ]


def create_phases(
    distance_miles: float,
    duration_hours: float | None,
    current_location: str,
    pickup_location: str,
    dropoff_location: str,
    route_legs: list[RouteLegDict] | None,
) -> tuple[list[Phase], float]:
    normalized_legs = normalize_route_legs(
        distance_miles=distance_miles,
        duration_hours=duration_hours,
        current_location=current_location,
        dropoff_location=dropoff_location,
        route_legs=route_legs,
    )

    if len(normalized_legs) == 1:
        drive_leg = normalized_legs[0]
        return (
            [
                ServicePhase(
                    service_type="pickup",
                    location=pickup_location,
                    duration_hours=PICKUP_DURATION_HOURS,
                    note="Pickup - loading/check-in",
                ),
                DrivePhase(
                    phase_name="linehaul",
                    start=drive_leg.start,
                    end=drive_leg.end,
                    location="On route",
                    note="Driving",
                    remaining_miles=drive_leg.distance_miles,
                    remaining_hours=drive_leg.duration_hours,
                ),
                ServicePhase(
                    service_type="dropoff",
                    location=dropoff_location,
                    duration_hours=DROPOFF_DURATION_HOURS,
                    note="Dropoff - unloading/check-out",
                ),
            ],
            drive_leg.duration_hours,
        )

    phases: list[Phase] = []
    for leg in normalized_legs:
        phases.append(
            DrivePhase(
                phase_name=leg.kind,
                start=leg.start,
                end=leg.end,
                location=f"On route to {leg.end}",
                note="Driving to pickup" if leg.kind == "to_pickup" else "Driving",
                remaining_miles=leg.distance_miles,
                remaining_hours=leg.duration_hours,
            )
        )
        if leg.kind == "to_pickup":
            phases.append(
                ServicePhase(
                    service_type="pickup",
                    location=pickup_location,
                    duration_hours=PICKUP_DURATION_HOURS,
                    note="Pickup - loading/check-in",
                )
            )

    phases.append(
        ServicePhase(
            service_type="dropoff",
            location=dropoff_location,
            duration_hours=DROPOFF_DURATION_HOURS,
            note="Dropoff - unloading/check-out",
        )
    )

    return phases, sum(leg.duration_hours for leg in normalized_legs)


def drive_phase_completed(phase: DrivePhase) -> bool:
    return (
        phase.remaining_hours <= FLOAT_EPSILON
        or phase.remaining_miles <= FLOAT_EPSILON
    )


def has_remaining_driving(phases: list[Phase], current_phase_index: int) -> bool:
    current_phase = phases[current_phase_index]
    if isinstance(current_phase, DrivePhase) and not drive_phase_completed(current_phase):
        return True

    return any(
        isinstance(phase, DrivePhase) and not drive_phase_completed(phase)
        for phase in phases[current_phase_index + 1 :]
    )


def create_stop_event(
    stop_type: StopType,
    location: str,
    start_at: datetime,
    duration_hours: float,
    miles_from_route_start: float,
    note: str = "",
) -> StopEvent:
    return StopEvent(
        stop_type=stop_type,
        location=location,
        start_at=start_at,
        duration_hours=duration_hours,
        miles_from_route_start=miles_from_route_start,
        note=note,
    )


def serialize_stop_events(
    trip_start_at: datetime,
    stop_events: list[StopEvent],
) -> list[StopDict]:
    serialized_stops: list[StopDict] = []

    for stop_event in sorted(stop_events, key=lambda stop: stop.start_at):
        stop_date_offset = (stop_event.start_at.date() - trip_start_at.date()).days
        stop: StopDict = {
            "type": stop_event.stop_type,
            "location": stop_event.location,
            "day": stop_date_offset + 1,
            "hour": decimal_hour_for_datetime(stop_event.start_at),
            "duration": round_hour(stop_event.duration_hours),
            "miles_from_route_start": round_miles(stop_event.miles_from_route_start),
        }

        if stop_event.note:
            stop["note"] = stop_event.note

        serialized_stops.append(stop)

    return serialized_stops
