from datetime import datetime
from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict, TypeAlias


CycleRule: TypeAlias = Literal["70_8", "60_7"]
DutyStatus: TypeAlias = Literal["off_duty", "sleeper_berth", "driving", "on_duty"]
StopType: TypeAlias = Literal["pickup", "dropoff", "fuel", "break", "rest"]
Coordinate: TypeAlias = list[float]


class RouteLocationsDict(TypedDict):
    current: str
    pickup: str
    dropoff: str


class WaypointDict(TypedDict):
    label: str
    query: str
    coordinates: Coordinate


class RouteWaypointsDict(TypedDict):
    current: WaypointDict
    pickup: WaypointDict
    dropoff: WaypointDict


class RouteLegDict(TypedDict):
    kind: str
    start: str
    end: str
    distance_miles: float
    duration_hours: float


class RouteDataDict(TypedDict):
    distance_miles: float
    duration_hours: float
    geometry: list[Coordinate]
    locations: RouteLocationsDict
    waypoints: RouteWaypointsDict
    legs: list[RouteLegDict]


class SegmentDict(TypedDict):
    status: DutyStatus
    start: float
    end: float
    duration: float
    location: str
    note: str


class RemarkDict(TypedDict):
    time: float
    location: str
    note: str


class DailyTotalsDict(TypedDict):
    off_duty: float
    sleeper_berth: float
    driving: float
    on_duty: float


class DailyLogDict(TypedDict):
    day: int
    date: str
    segments: list[SegmentDict]
    totals: DailyTotalsDict
    total_hours: float
    remarks: list[RemarkDict]


class StopDict(TypedDict):
    type: StopType
    location: str
    day: int
    hour: float
    duration: float
    note: NotRequired[str]
    miles_from_route_start: NotRequired[float]
    coordinates: NotRequired[Coordinate]


class SummaryDict(TypedDict):
    distance_miles: float
    estimated_driving_hours: float
    current_cycle_used: float
    remaining_cycle_hours_after_trip: float
    total_days: int
    cycle_rule: CycleRule
    trip_start_at: NotRequired[str]
    estimated_arrival_at: NotRequired[str]


class HOSPlanDict(TypedDict):
    is_legal: bool
    message: str
    daily_logs: list[DailyLogDict]
    stops: list[StopDict]
    summary: NotRequired[SummaryDict]


class TripPlanResponseDict(TypedDict):
    route: RouteDataDict
    hos_plan: HOSPlanDict


class LocationSearchResponseDict(TypedDict):
    results: list[WaypointDict]


@dataclass(frozen=True, slots=True)
class TripPlanningInput:
    current_location: str
    pickup_location: str
    dropoff_location: str
    current_cycle_used: float
    cycle_rule: CycleRule
    trip_start_at: datetime
    current_waypoint: WaypointDict | None = None
    pickup_waypoint: WaypointDict | None = None
    dropoff_waypoint: WaypointDict | None = None
