from datetime import datetime
from dataclasses import dataclass
from typing import Literal, TypeAlias

from ..types import DutyStatus, StopType


@dataclass(frozen=True, slots=True)
class CycleRuleConfig:
    max_hours: int
    days: int


@dataclass(frozen=True, slots=True)
class RouteLegInput:
    kind: str
    start: str
    end: str
    distance_miles: float
    duration_hours: float


@dataclass(slots=True)
class DrivePhase:
    kind: Literal["drive"] = "drive"
    phase_name: str = ""
    start: str = ""
    end: str = ""
    location: str = ""
    note: str = ""
    remaining_miles: float = 0.0
    remaining_hours: float = 0.0


@dataclass(frozen=True, slots=True)
class ServicePhase:
    kind: Literal["service"] = "service"
    service_type: str = ""
    location: str = ""
    duration_hours: float = 0.0
    note: str = ""


@dataclass(frozen=True, slots=True)
class TimelineSegment:
    status: DutyStatus
    start_at: datetime
    end_at: datetime
    location: str
    note: str = ""


@dataclass(frozen=True, slots=True)
class StopEvent:
    stop_type: StopType
    location: str
    start_at: datetime
    duration_hours: float
    miles_from_route_start: float
    note: str = ""


Phase: TypeAlias = DrivePhase | ServicePhase
