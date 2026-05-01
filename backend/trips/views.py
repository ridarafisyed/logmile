from rest_framework.decorators import api_view, throttle_classes
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiExample

from .constants import (
    TRIP_PLAN_REQUEST_EXAMPLE,
    TRIP_PLAN_REQUEST_WITH_COORDINATES_EXAMPLE,
)
from .map_service import MapServiceError, search_locations
from .serializers import (
    ErrorResponseSerializer,
    LocationSearchQuerySerializer,
    LocationSearchResponseSerializer,
    TripPlanRequestSerializer,
    TripPlanResponseSerializer,
)
from .services.trip_planner import (
    build_trip_plan,
    trip_planning_input_from_validated_data,
)
from .throttles import (
    LocationSearchRateThrottle,
    TripPlanBurstRateThrottle,
    TripPlanSustainedRateThrottle,
)


@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
            },
        }
    }
)
@api_view(["GET"])
def health_check(request):
    return Response({
        "status": "ok",
        "message": "LogMile backend is running.",
    })


@extend_schema(
    parameters=[LocationSearchQuerySerializer],
    responses={
        200: LocationSearchResponseSerializer,
        400: ErrorResponseSerializer,
        502: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
@api_view(["GET"])
@throttle_classes([LocationSearchRateThrottle])
def location_search(request):
    try:
        query_serializer = LocationSearchQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        results = search_locations(
            query_text=query_serializer.validated_data["q"],
            limit=query_serializer.validated_data["limit"],
        )
        response_serializer = LocationSearchResponseSerializer(
            {"results": results}
        )
        return Response(response_serializer.data)

    except MapServiceError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    except ValidationError as error:
        return Response(
            {"error": error.detail},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as error:
        return Response(
            {
                "error": "Something went wrong while searching locations.",
                "details": str(error),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    request=TripPlanRequestSerializer,
    responses={
        200: TripPlanResponseSerializer,
        400: ErrorResponseSerializer,
        502: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            "Trip planning request with text locations",
            value=TRIP_PLAN_REQUEST_EXAMPLE,
            request_only=True,
        ),
        OpenApiExample(
            "Trip planning request with selected coordinates",
            value=TRIP_PLAN_REQUEST_WITH_COORDINATES_EXAMPLE,
            request_only=True,
        )
    ],
)
@api_view(["POST"])
@throttle_classes([TripPlanBurstRateThrottle, TripPlanSustainedRateThrottle])
def plan_trip(request):
    try:
        request_serializer = TripPlanRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        trip_input = trip_planning_input_from_validated_data(
            request_serializer.validated_data
        )
        response_payload = build_trip_plan(trip_input)
        response_serializer = TripPlanResponseSerializer(response_payload)
        return Response(response_serializer.data)

    except MapServiceError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    except ValidationError as error:
        return Response(
            {"error": error.detail},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as error:
        return Response(
            {
                "error": "Something went wrong while planning the trip.",
                "details": str(error),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
