from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .constants import CYCLE_RULE_CHOICES, CYCLE_RULE_MAX_HOURS, DEFAULT_CYCLE_RULE


LOCATION_INPUT_SCHEMA = {
    "oneOf": [
        {"type": "string", "example": "Chicago, IL"},
        {
            "type": "object",
            "properties": {
                "label": {"type": "string", "example": "Chicago, IL, USA"},
                "query": {"type": "string", "example": "Chicago, IL"},
                "coordinates": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2,
                    "example": [-87.6298, 41.8781],
                },
            },
            "required": ["label", "coordinates"],
        },
    ]
}


class CoordinatesField(serializers.ListField):
    child = serializers.FloatField()
    min_length = 2
    max_length = 2


@extend_schema_field(LOCATION_INPUT_SCHEMA)
class LocationInputField(serializers.Field):
    default_error_messages = {
        "invalid": "Location must be a string or an object with label and coordinates.",
        "blank": "Location cannot be blank.",
        "label": "Location label must be a non-empty string.",
        "coordinates": "Location coordinates must contain exactly two numeric values.",
    }

    def to_internal_value(self, data):
        if isinstance(data, str):
            normalized_value = data.strip()
            if not normalized_value:
                self.fail("blank")
            return normalized_value

        if not isinstance(data, dict):
            self.fail("invalid")

        label = data.get("label")
        if not isinstance(label, str) or not label.strip():
            self.fail("label")

        coordinates = data.get("coordinates")
        if not isinstance(coordinates, list) or len(coordinates) != 2:
            self.fail("coordinates")

        try:
            normalized_coordinates = [
                float(coordinates[0]),
                float(coordinates[1]),
            ]
        except (TypeError, ValueError):
            self.fail("coordinates")

        query = data.get("query")
        if not isinstance(query, str) or not query.strip():
            query = label

        return {
            "label": label.strip(),
            "query": query.strip(),
            "coordinates": normalized_coordinates,
        }

    def to_representation(self, value):
        return value


class TripPlanRequestSerializer(serializers.Serializer):
    current_location = LocationInputField()
    pickup_location = LocationInputField()
    dropoff_location = LocationInputField()
    trip_start_at = serializers.CharField(required=False, allow_blank=False)
    current_cycle_used = serializers.FloatField(min_value=0, max_value=70)
    cycle_rule = serializers.ChoiceField(
        choices=CYCLE_RULE_CHOICES,
        default=DEFAULT_CYCLE_RULE,
        required=False,
    )

    def validate(self, attrs):
        cycle_rule = attrs.get("cycle_rule", DEFAULT_CYCLE_RULE)
        current_cycle_used = attrs["current_cycle_used"]
        max_cycle_hours = CYCLE_RULE_MAX_HOURS[cycle_rule]
        trip_start_at_value = self.initial_data.get("trip_start_at")

        if current_cycle_used > max_cycle_hours:
            raise serializers.ValidationError(
                {
                    "current_cycle_used": (
                        f"current_cycle_used cannot be greater than {max_cycle_hours} "
                        f"for cycle rule {cycle_rule}."
                    )
                }
            )

        if trip_start_at_value is not None:
            parsed_trip_start_at = parse_datetime(trip_start_at_value)
            if parsed_trip_start_at is None:
                raise serializers.ValidationError(
                    {
                        "trip_start_at": (
                            "trip_start_at must be an ISO 8601 datetime string."
                        )
                    }
                )
            attrs["trip_start_at"] = parsed_trip_start_at

        return attrs


class WaypointSerializer(serializers.Serializer):
    label = serializers.CharField()
    query = serializers.CharField()
    coordinates = CoordinatesField()


class LocationSearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(min_length=2, max_length=255)
    limit = serializers.IntegerField(min_value=1, max_value=8, default=6, required=False)


class RouteLegSerializer(serializers.Serializer):
    kind = serializers.CharField()
    start = serializers.CharField()
    end = serializers.CharField()
    distance_miles = serializers.FloatField()
    duration_hours = serializers.FloatField()


class RouteLocationsSerializer(serializers.Serializer):
    current = serializers.CharField()
    pickup = serializers.CharField()
    dropoff = serializers.CharField()


class RouteWaypointsSerializer(serializers.Serializer):
    current = WaypointSerializer()
    pickup = WaypointSerializer()
    dropoff = WaypointSerializer()


class RouteSerializer(serializers.Serializer):
    distance_miles = serializers.FloatField()
    duration_hours = serializers.FloatField()
    geometry = serializers.ListField(child=CoordinatesField())
    locations = RouteLocationsSerializer()
    waypoints = RouteWaypointsSerializer()
    legs = RouteLegSerializer(many=True)


class StopSerializer(serializers.Serializer):
    type = serializers.CharField()
    location = serializers.CharField()
    day = serializers.IntegerField()
    hour = serializers.FloatField()
    duration = serializers.FloatField()
    note = serializers.CharField(required=False, allow_blank=True)
    miles_from_route_start = serializers.FloatField(required=False)
    coordinates = CoordinatesField(required=False)


class SegmentSerializer(serializers.Serializer):
    status = serializers.CharField()
    start = serializers.FloatField()
    end = serializers.FloatField()
    duration = serializers.FloatField()
    location = serializers.CharField()
    note = serializers.CharField(required=False, allow_blank=True)


class RemarkSerializer(serializers.Serializer):
    time = serializers.FloatField()
    location = serializers.CharField()
    note = serializers.CharField()


class DailyTotalsSerializer(serializers.Serializer):
    off_duty = serializers.FloatField()
    sleeper_berth = serializers.FloatField()
    driving = serializers.FloatField()
    on_duty = serializers.FloatField()


class DailyLogSerializer(serializers.Serializer):
    day = serializers.IntegerField()
    date = serializers.CharField()
    segments = SegmentSerializer(many=True)
    totals = DailyTotalsSerializer()
    total_hours = serializers.FloatField()
    remarks = RemarkSerializer(many=True)


class SummarySerializer(serializers.Serializer):
    distance_miles = serializers.FloatField()
    estimated_driving_hours = serializers.FloatField()
    current_cycle_used = serializers.FloatField()
    remaining_cycle_hours_after_trip = serializers.FloatField()
    total_days = serializers.IntegerField()
    cycle_rule = serializers.CharField()
    trip_start_at = serializers.DateTimeField(required=False)
    estimated_arrival_at = serializers.DateTimeField(required=False)


class HOSPlanSerializer(serializers.Serializer):
    is_legal = serializers.BooleanField()
    message = serializers.CharField()
    summary = SummarySerializer(required=False)
    daily_logs = DailyLogSerializer(many=True)
    stops = StopSerializer(many=True)


class TripPlanResponseSerializer(serializers.Serializer):
    route = RouteSerializer()
    hos_plan = HOSPlanSerializer()


class LocationSearchResponseSerializer(serializers.Serializer):
    results = WaypointSerializer(many=True)


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.JSONField()
    detail = serializers.JSONField(required=False)
    details = serializers.CharField(required=False)
    retry_after_seconds = serializers.IntegerField(required=False)
