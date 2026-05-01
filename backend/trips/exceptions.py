from math import ceil


def build_throttled_error_payload(wait_seconds):
    retry_after_seconds = (
        ceil(wait_seconds) if wait_seconds is not None else None
    )
    return {
        "error": "Too many requests from this device. Please wait a moment and try again.",
        "retry_after_seconds": retry_after_seconds,
    }


def api_exception_handler(exc, context):
    from rest_framework.views import exception_handler

    response = exception_handler(exc, context)
    if response is None:
        return None

    if response.status_code == 429:
        response.data = build_throttled_error_payload(getattr(exc, "wait", None))
        return response

    return response
