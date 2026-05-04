from trips.throttles import LocationSearchRateThrottle
import trips.views as trip_views


class ExplodingCache:
    def get(self, *args, **kwargs):
        raise RuntimeError("cache unavailable")

    def set(self, *args, **kwargs):
        raise RuntimeError("cache unavailable")


def test_root_path_responds_for_render_probe(client):
    response = client.head("/")

    assert response.status_code == 200


def test_location_search_ignores_throttle_cache_failures(client, monkeypatch):
    monkeypatch.setattr(LocationSearchRateThrottle, "cache", ExplodingCache())
    monkeypatch.setattr(
        trip_views,
        "search_locations",
        lambda query_text, limit: [
            {
                "label": "Chicago, IL, USA",
                "query": query_text,
                "coordinates": [-87.6298, 41.8781],
            }
        ],
    )

    response = client.get("/api/locations/search/", {"q": "Chicago", "limit": 1})

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "label": "Chicago, IL, USA",
                "query": "Chicago",
                "coordinates": [-87.6298, 41.8781],
            }
        ]
    }
