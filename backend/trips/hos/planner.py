from datetime import datetime

from ..types import CycleRule, HOSPlanDict, RouteLegDict
from .constants import (
    BREAK_AFTER_DRIVING_HOURS,
    BREAK_DURATION_HOURS,
    FLOAT_EPSILON,
    FUEL_STOP_DURATION_HOURS,
    FUEL_STOP_EVERY_MILES,
    MAX_DRIVING_HOURS_PER_DAY,
    MAX_DUTY_WINDOW_HOURS,
    MAX_PLANNING_DAYS,
    REQUIRED_REST_HOURS,
)
from .helpers import (
    build_daily_logs,
    create_phases,
    create_stop_event,
    create_timeline_segment,
    drive_phase_completed,
    has_remaining_driving,
    hours_to_timedelta,
    midnight_for,
    next_midnight_after,
    normalize_planning_start,
    resolve_cycle_rule,
    serialize_stop_events,
)
from .models import ServicePhase, StopEvent, TimelineSegment
from ..utils import round_hour, round_miles


def cycle_exhausted_response(message: str) -> HOSPlanDict:
    return {
        "is_legal": False,
        "message": message,
        "daily_logs": [],
        "stops": [],
    }


def plan_hos_schedule(
    distance_miles: float,
    current_cycle_used: float,
    current_location: str,
    pickup_location: str,
    dropoff_location: str,
    duration_hours: float | None = None,
    cycle_rule: CycleRule = "70_8",
    trip_start_at: datetime | None = None,
    route_legs: list[RouteLegDict] | None = None,
) -> HOSPlanDict:
    cycle_config = resolve_cycle_rule(cycle_rule)
    remaining_cycle_hours = cycle_config.max_hours - current_cycle_used

    if remaining_cycle_hours <= 0:
        return cycle_exhausted_response(
            "Driver has no remaining cycle hours. A 34-hour restart is required."
        )

    phases, total_driving_hours_needed = create_phases(
        distance_miles=distance_miles,
        duration_hours=duration_hours,
        current_location=current_location,
        pickup_location=pickup_location,
        dropoff_location=dropoff_location,
        route_legs=route_legs,
    )

    planning_start_at = normalize_planning_start(trip_start_at)
    current_time = planning_start_at
    phase_index = 0
    miles_since_fuel = 0.0
    miles_from_route_start = 0.0
    duty_window_used = 0.0
    driving_in_shift = 0.0
    driving_since_break = 0.0
    break_counter_reset_at = planning_start_at
    shift_has_progress = False
    timeline_segments: list[TimelineSegment] = []
    stop_events: list[StopEvent] = []

    if planning_start_at > midnight_for(planning_start_at):
        timeline_segments.append(
            create_timeline_segment(
                status="off_duty",
                start_at=midnight_for(planning_start_at),
                end_at=planning_start_at,
                location=current_location,
                note="Off duty before planned trip start",
            )
        )

    def build_response(message: str, is_legal: bool) -> HOSPlanDict:
        daily_logs = build_daily_logs(planning_start_at, timeline_segments)
        response: HOSPlanDict = {
            "is_legal": is_legal,
            "message": message,
            "daily_logs": daily_logs,
            "stops": serialize_stop_events(planning_start_at, stop_events),
        }

        if is_legal:
            response["summary"] = {
                "distance_miles": round_miles(distance_miles),
                "estimated_driving_hours": round_hour(total_driving_hours_needed),
                "current_cycle_used": round_hour(current_cycle_used),
                "remaining_cycle_hours_after_trip": round_hour(remaining_cycle_hours),
                "total_days": len(daily_logs),
                "cycle_rule": cycle_rule,
                "trip_start_at": planning_start_at.isoformat(),
                "estimated_arrival_at": current_time.isoformat(),
            }

        return response

    def add_rest_reset() -> bool:
        nonlocal current_time, duty_window_used, driving_in_shift, driving_since_break, break_counter_reset_at, shift_has_progress

        if not shift_has_progress:
            return False

        rest_start = current_time
        rest_end = rest_start + hours_to_timedelta(REQUIRED_REST_HOURS)
        timeline_segments.append(
            create_timeline_segment(
                status="off_duty",
                start_at=rest_start,
                end_at=rest_end,
                location="Rest location",
                note="10-hour off-duty reset",
            )
        )
        stop_events.append(
            create_stop_event(
                stop_type="rest",
                location="Rest location",
                start_at=rest_start,
                duration_hours=REQUIRED_REST_HOURS,
                miles_from_route_start=miles_from_route_start,
                note="10-hour off-duty reset",
            )
        )

        current_time = rest_end
        if midnight_for(rest_end) == midnight_for(rest_start):
            next_log_day_start = next_midnight_after(rest_end)
            timeline_segments.append(
                create_timeline_segment(
                    status="off_duty",
                    start_at=rest_end,
                    end_at=next_log_day_start,
                    location="Rest location",
                    note="Off duty after reset before next log day",
                )
            )
            current_time = next_log_day_start

        duty_window_used = 0.0
        driving_in_shift = 0.0
        driving_since_break = 0.0
        break_counter_reset_at = current_time
        shift_has_progress = False
        return True

    while phase_index < len(phases):
        if (current_time.date() - planning_start_at.date()).days + 1 > MAX_PLANNING_DAYS:
            return build_response("Trip is too long for the MVP planner.", False)

        if remaining_cycle_hours <= 0:
            return build_response(
                "Trip exceeds the available cycle hours. A 34-hour restart is required.",
                False,
            )

        phase = phases[phase_index]

        if isinstance(phase, ServicePhase):
            if phase.duration_hours > remaining_cycle_hours:
                return build_response(
                    "Trip exceeds the available cycle hours. A 34-hour restart is required.",
                    False,
                )

            if duty_window_used + phase.duration_hours > MAX_DUTY_WINDOW_HOURS + FLOAT_EPSILON:
                if add_rest_reset():
                    continue

                return build_response(
                    "Planner could not fit the next trip action into a legal duty window.",
                    False,
                )

            service_start = current_time
            service_end = service_start + hours_to_timedelta(phase.duration_hours)
            timeline_segments.append(
                create_timeline_segment(
                    status="on_duty",
                    start_at=service_start,
                    end_at=service_end,
                    location=phase.location,
                    note=phase.note,
                )
            )
            stop_events.append(
                create_stop_event(
                    stop_type=phase.service_type,
                    location=phase.location,
                    start_at=service_start,
                    duration_hours=phase.duration_hours,
                    miles_from_route_start=miles_from_route_start,
                    note=phase.note,
                )
            )

            current_time = service_end
            duty_window_used += phase.duration_hours
            remaining_cycle_hours -= phase.duration_hours
            shift_has_progress = True
            phase_index += 1
            continue

        if drive_phase_completed(phase):
            phase_index += 1
            continue

        if (
            driving_in_shift >= MAX_DRIVING_HOURS_PER_DAY - FLOAT_EPSILON
            or duty_window_used >= MAX_DUTY_WINDOW_HOURS - FLOAT_EPSILON
        ):
            if add_rest_reset():
                continue

            return build_response(
                "Planner could not fit the next trip action into a legal duty window.",
                False,
            )

        future_driving_exists = has_remaining_driving(phases, phase_index)

        if (
            future_driving_exists
            and miles_since_fuel >= FUEL_STOP_EVERY_MILES - FLOAT_EPSILON
        ):
            if (
                duty_window_used + FUEL_STOP_DURATION_HOURS
                > MAX_DUTY_WINDOW_HOURS + FLOAT_EPSILON
                or remaining_cycle_hours < FUEL_STOP_DURATION_HOURS - FLOAT_EPSILON
            ):
                if add_rest_reset():
                    continue

                return build_response(
                    "Planner could not fit the next trip action into a legal duty window.",
                    False,
                )

            fuel_start = current_time
            fuel_end = fuel_start + hours_to_timedelta(FUEL_STOP_DURATION_HOURS)
            timeline_segments.append(
                create_timeline_segment(
                    status="on_duty",
                    start_at=fuel_start,
                    end_at=fuel_end,
                    location="Fuel stop",
                    note="Fueling",
                )
            )
            stop_events.append(
                create_stop_event(
                    stop_type="fuel",
                    location="Fuel stop",
                    start_at=fuel_start,
                    duration_hours=FUEL_STOP_DURATION_HOURS,
                    miles_from_route_start=miles_from_route_start,
                    note="Fueling",
                )
            )

            current_time = fuel_end
            duty_window_used += FUEL_STOP_DURATION_HOURS
            remaining_cycle_hours -= FUEL_STOP_DURATION_HOURS
            miles_since_fuel = 0.0
            driving_since_break = 0.0
            break_counter_reset_at = current_time
            shift_has_progress = True
            continue

        if driving_since_break >= BREAK_AFTER_DRIVING_HOURS - FLOAT_EPSILON:
            if duty_window_used + BREAK_DURATION_HOURS > MAX_DUTY_WINDOW_HOURS + FLOAT_EPSILON:
                if add_rest_reset():
                    continue

                return build_response(
                    "Planner could not fit the next trip action into a legal duty window.",
                    False,
                )

            break_start = current_time
            break_end = break_start + hours_to_timedelta(BREAK_DURATION_HOURS)
            break_note = "30-minute break after 8 cumulative driving hours"
            if midnight_for(break_start) > midnight_for(break_counter_reset_at):
                break_note = (
                    "30-minute break after 8 cumulative driving hours carried over from the prior log day"
                )
            timeline_segments.append(
                create_timeline_segment(
                    status="off_duty",
                    start_at=break_start,
                    end_at=break_end,
                    location="Break stop",
                    note=break_note,
                )
            )
            stop_events.append(
                create_stop_event(
                    stop_type="break",
                    location="Break stop",
                    start_at=break_start,
                    duration_hours=BREAK_DURATION_HOURS,
                    miles_from_route_start=miles_from_route_start,
                    note=break_note,
                )
            )

            current_time = break_end
            duty_window_used += BREAK_DURATION_HOURS
            driving_since_break = 0.0
            break_counter_reset_at = current_time
            shift_has_progress = True
            continue

        phase_speed_mph = phase.remaining_miles / phase.remaining_hours
        available_drive_hours = min(
            MAX_DRIVING_HOURS_PER_DAY - driving_in_shift,
            MAX_DUTY_WINDOW_HOURS - duty_window_used,
            BREAK_AFTER_DRIVING_HOURS - driving_since_break,
            phase.remaining_hours,
            remaining_cycle_hours,
        )

        hours_until_fuel = (FUEL_STOP_EVERY_MILES - miles_since_fuel) / phase_speed_mph
        should_fuel_after_drive = False

        if future_driving_exists and hours_until_fuel < available_drive_hours - FLOAT_EPSILON:
            available_drive_hours = hours_until_fuel
            should_fuel_after_drive = True

        if available_drive_hours <= FLOAT_EPSILON:
            if add_rest_reset():
                continue

            return build_response(
                "Planner could not fit the next trip action into a legal duty window.",
                False,
            )

        drive_start = current_time
        drive_end = drive_start + hours_to_timedelta(available_drive_hours)
        driven_miles = min(
            phase.remaining_miles,
            phase_speed_mph * available_drive_hours,
        )
        timeline_segments.append(
            create_timeline_segment(
                status="driving",
                start_at=drive_start,
                end_at=drive_end,
                location=phase.location,
                note=phase.note,
            )
        )

        current_time = drive_end
        duty_window_used += available_drive_hours
        driving_in_shift += available_drive_hours
        driving_since_break += available_drive_hours
        remaining_cycle_hours -= available_drive_hours
        phase.remaining_hours = max(phase.remaining_hours - available_drive_hours, 0.0)
        phase.remaining_miles = max(phase.remaining_miles - driven_miles, 0.0)
        miles_from_route_start += driven_miles
        miles_since_fuel += driven_miles
        shift_has_progress = True

        if drive_phase_completed(phase):
            phase_index += 1

        future_driving_exists = (
            has_remaining_driving(phases, phase_index)
            if phase_index < len(phases)
            else False
        )
        should_fuel_after_drive = should_fuel_after_drive or (
            future_driving_exists
            and miles_since_fuel >= FUEL_STOP_EVERY_MILES - FLOAT_EPSILON
        )

        if should_fuel_after_drive:
            if (
                duty_window_used + FUEL_STOP_DURATION_HOURS
                > MAX_DUTY_WINDOW_HOURS + FLOAT_EPSILON
                or remaining_cycle_hours < FUEL_STOP_DURATION_HOURS - FLOAT_EPSILON
            ):
                if add_rest_reset():
                    continue

                return build_response(
                    "Planner could not fit the next trip action into a legal duty window.",
                    False,
                )

            fuel_start = current_time
            fuel_end = fuel_start + hours_to_timedelta(FUEL_STOP_DURATION_HOURS)
            timeline_segments.append(
                create_timeline_segment(
                    status="on_duty",
                    start_at=fuel_start,
                    end_at=fuel_end,
                    location="Fuel stop",
                    note="Fueling",
                )
            )
            stop_events.append(
                create_stop_event(
                    stop_type="fuel",
                    location="Fuel stop",
                    start_at=fuel_start,
                    duration_hours=FUEL_STOP_DURATION_HOURS,
                    miles_from_route_start=miles_from_route_start,
                    note="Fueling",
                )
            )

            current_time = fuel_end
            duty_window_used += FUEL_STOP_DURATION_HOURS
            remaining_cycle_hours -= FUEL_STOP_DURATION_HOURS
            miles_since_fuel = 0.0
            driving_since_break = 0.0
            shift_has_progress = True

    return build_response("Trip planned successfully.", True)
