from rest_framework.throttling import SimpleRateThrottle


class BaseIPRateThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class TripPlanBurstRateThrottle(BaseIPRateThrottle):
    scope = "trip_plan_burst"


class TripPlanSustainedRateThrottle(BaseIPRateThrottle):
    scope = "trip_plan_sustained"


class LocationSearchRateThrottle(BaseIPRateThrottle):
    scope = "location_search"
