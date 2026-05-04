import logging

from rest_framework.throttling import SimpleRateThrottle


logger = logging.getLogger("trips.throttles")


class BaseIPRateThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }

    def allow_request(self, request, view):
        try:
            return super().allow_request(request, view)
        except Exception as error:
            logger.warning(
                "throttle_cache_unavailable scope=%s ident=%s error=%s",
                self.scope,
                self.get_ident(request),
                error,
            )
            return True


class TripPlanBurstRateThrottle(BaseIPRateThrottle):
    scope = "trip_plan_burst"


class TripPlanSustainedRateThrottle(BaseIPRateThrottle):
    scope = "trip_plan_sustained"


class LocationSearchRateThrottle(BaseIPRateThrottle):
    scope = "location_search"
