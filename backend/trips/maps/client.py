import os
from functools import lru_cache

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..types import Coordinate, WaypointDict
from .constants import AUTOCOMPLETE_URL, DIRECTIONS_URL, GEOCODE_URL
from .cache import get_cached_value, set_cached_value
from .errors import MapServiceError


@lru_cache(maxsize=1)
def get_retry_session() -> requests.Session:
    retry = Retry(
        total=settings.ORS_MAX_RETRIES,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset({"GET", "POST"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_openrouteservice_api_key() -> str:
    api_key = os.getenv("OPENROUTESERVICE_API_KEY") or os.getenv("ORS_API_KEY")
    if not api_key:
        raise MapServiceError(
            "OPENROUTESERVICE_API_KEY is not configured. "
            "Set it in your environment before planning a trip."
        )
    return api_key


def raise_ors_api_error(
    response: requests.Response,
    location_text: str | None = None,
    request_name: str = "route directions",
) -> None:
    if response.status_code in {401, 403}:
        raise MapServiceError(
            "OpenRouteService rejected the request. Check the API key and service permissions."
        )
    if response.status_code == 429:
        raise MapServiceError(
            "OpenRouteService rate limit reached. Please retry in a moment."
        )
    if 500 <= response.status_code <= 599:
        raise MapServiceError(
            "OpenRouteService is temporarily unavailable. Please retry shortly."
        )

    if location_text:
        if request_name == "geocoding results":
            raise MapServiceError(
                f"Failed to geocode '{location_text}' with OpenRouteService."
            )
        raise MapServiceError(
            f"Failed to fetch {request_name} for '{location_text}' from OpenRouteService."
        )

    raise MapServiceError(
        f"Failed to fetch {request_name} from OpenRouteService."
    )


def build_waypoint(feature: dict, default_query: str) -> WaypointDict | None:
    coordinates = feature.get("geometry", {}).get("coordinates")
    if not coordinates or len(coordinates) != 2:
        return None

    label = feature.get("properties", {}).get("label", default_query)
    query = feature.get("properties", {}).get("name", label)
    return {
        "query": query,
        "label": label,
        "coordinates": coordinates,
    }


def request_geocode_payload(
    *,
    cache_namespace: str,
    cache_payload: dict,
    endpoint_url: str,
    params: dict,
    request_name: str,
    location_text: str,
) -> dict:
    cached_payload = get_cached_value(cache_namespace, cache_payload)
    if cached_payload is not None:
        return cached_payload

    try:
        response = get_retry_session().get(
            endpoint_url,
            params=params,
            timeout=settings.ORS_REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code >= 400:
            raise_ors_api_error(
                response,
                location_text=location_text,
                request_name=request_name,
            )
    except requests.RequestException as error:
        raise MapServiceError(
            f"Failed to fetch {request_name} from OpenRouteService."
        ) from error

    return set_cached_value(cache_namespace, cache_payload, response.json())


def geocode_location(location_text: str, api_key: str) -> WaypointDict:
    payload = request_geocode_payload(
        cache_namespace="geocode",
        cache_payload={"text": location_text},
        endpoint_url=GEOCODE_URL,
        params={"api_key": api_key, "text": location_text, "size": 1, "boundary.country": "USA"},
        request_name="geocoding results",
        location_text=location_text,
    )
    features = payload.get("features", [])
    if not features:
        raise MapServiceError(
            f"OpenRouteService could not find a location for '{location_text}'."
        )

    waypoint = build_waypoint(features[0], default_query=location_text)
    if waypoint is None:
        raise MapServiceError(
            f"OpenRouteService returned invalid coordinates for '{location_text}'."
        )

    return waypoint


def search_location_suggestions(
    query_text: str,
    api_key: str,
    limit: int = 6,
) -> list[WaypointDict]:
    cache_payload = {"text": query_text, "limit": limit, "country": "USA"}
    cached_results = get_cached_value("autocomplete", cache_payload)
    if cached_results is not None:
        return cached_results

    autocomplete_payload = request_geocode_payload(
        cache_namespace="autocomplete_raw",
        cache_payload=cache_payload,
        endpoint_url=AUTOCOMPLETE_URL,
        params={"api_key": api_key, "text": query_text, "size": limit, "boundary.country": "USA"},
        request_name="location suggestions",
        location_text=query_text,
    )
    features = autocomplete_payload.get("features", [])

    if not features:
        fallback_payload = request_geocode_payload(
            cache_namespace="search_suggestions_raw",
            cache_payload=cache_payload,
            endpoint_url=GEOCODE_URL,
            params={"api_key": api_key, "text": query_text, "size": limit, "boundary.country": "USA"},
            request_name="location suggestions",
            location_text=query_text,
        )
        features = fallback_payload.get("features", [])

    suggestions = [
        waypoint
        for feature in features[:limit]
        if (waypoint := build_waypoint(feature, default_query=query_text)) is not None
    ]
    return set_cached_value("autocomplete", cache_payload, suggestions)


def request_directions(
    coordinates: list[Coordinate],
    api_key: str,
) -> dict:
    cached_directions = get_cached_value("directions", {"coordinates": coordinates})
    if cached_directions is not None:
        return cached_directions

    try:
        response = get_retry_session().post(
            DIRECTIONS_URL,
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json",
            },
            json={"coordinates": coordinates, "instructions": False},
            timeout=settings.ORS_REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code >= 400:
            raise_ors_api_error(response)
    except requests.RequestException as error:
        raise MapServiceError(
            "Failed to fetch route directions from OpenRouteService."
        ) from error

    return set_cached_value(
        "directions",
        {"coordinates": coordinates},
        response.json(),
    )
