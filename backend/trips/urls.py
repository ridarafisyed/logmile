from django.urls import path
from .views import health_check, location_search, plan_trip

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("locations/search/", location_search, name="location-search"),
    path("trip/plan/", plan_trip, name="plan-trip"),
]
