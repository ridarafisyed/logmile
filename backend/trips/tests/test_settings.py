from django.conf import settings


def test_default_cache_uses_locmem_backend():
    assert settings.CACHES["default"]["BACKEND"] == "django.core.cache.backends.locmem.LocMemCache"
