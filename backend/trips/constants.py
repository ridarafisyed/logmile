from .types import CycleRule


DEFAULT_CYCLE_RULE: CycleRule = "70_8"
CYCLE_RULE_CHOICES = (
    ("70_8", "70_8"),
    ("60_7", "60_7"),
)
CYCLE_RULE_MAX_HOURS = {
    "70_8": 70,
    "60_7": 60,
}
TRIP_PLAN_REQUEST_EXAMPLE = {
    "current_location": "Chicago, IL",
    "pickup_location": "St. Louis, MO",
    "dropoff_location": "Dallas, TX",
    "trip_start_at": "2026-05-01T11:45:00-05:00",
    "current_cycle_used": 20,
    "cycle_rule": DEFAULT_CYCLE_RULE,
}
TRIP_PLAN_REQUEST_WITH_COORDINATES_EXAMPLE = {
    "current_location": {
        "label": "Chicago, IL, USA",
        "query": "Chicago, IL",
        "coordinates": [-87.6298, 41.8781],
    },
    "pickup_location": {
        "label": "St. Louis, MO, USA",
        "query": "St. Louis, MO",
        "coordinates": [-90.1994, 38.627],
    },
    "dropoff_location": {
        "label": "Dallas, TX, USA",
        "query": "Dallas, TX",
        "coordinates": [-96.797, 32.7767],
    },
    "trip_start_at": "2026-05-01T11:45:00-05:00",
    "current_cycle_used": 20,
    "cycle_rule": DEFAULT_CYCLE_RULE,
}
