from trips.exceptions import build_throttled_error_payload


def test_build_throttled_error_payload_rounds_wait_time():
    assert build_throttled_error_payload(94.2) == {
        "error": "Too many requests from this device. Please wait a moment and try again.",
        "retry_after_seconds": 95,
    }


def test_build_throttled_error_payload_allows_missing_wait_time():
    assert build_throttled_error_payload(None) == {
        "error": "Too many requests from this device. Please wait a moment and try again.",
        "retry_after_seconds": None,
    }
