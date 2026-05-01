import { API_BASE_URL } from "../constants/api";
import type { ApiErrorResponse, LocationOption } from "../types/trip";
import { formatApiError } from "../utils/errors";
import { readJsonResponse, toRequestError } from "../utils/http";

interface LocationSearchResponse {
  results: LocationOption[];
}

export async function searchLocations(
  query: string,
  signal?: AbortSignal,
): Promise<LocationOption[]> {
  try {
    const params = new URLSearchParams({ q: query });
    const response = await fetch(
      `${API_BASE_URL}/api/locations/search/?${params.toString()}`,
      { signal },
    );
    const data = await readJsonResponse<LocationSearchResponse | ApiErrorResponse>(
      response,
    );

    if (!response.ok) {
      const errorResponse = data as ApiErrorResponse | null;
      const retryAfterSeconds = errorResponse?.retry_after_seconds;
      const message =
        formatApiError(errorResponse?.error) ||
        formatApiError(errorResponse?.detail) ||
        errorResponse?.details ||
        (response.status === 429
          ? retryAfterSeconds
            ? `Location search is temporarily rate-limited. Please wait about ${Math.max(1, Math.ceil(retryAfterSeconds / 60))} minute${Math.ceil(retryAfterSeconds / 60) === 1 ? "" : "s"} and try again.`
            : "Location search is temporarily rate-limited. Please wait a moment and try again."
          : null) ||
        `Failed to load location suggestions with status ${response.status}.`;

      throw new Error(message);
    }

    if (!data) {
      throw new Error(
        "Location search succeeded but the backend returned an unreadable response.",
      );
    }

    return (data as LocationSearchResponse).results;
  } catch (error) {
    throw toRequestError(error, "Failed to load location suggestions.");
  }
}
