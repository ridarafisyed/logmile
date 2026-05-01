import { API_BASE_URL } from "../constants/api";
import type { ApiErrorResponse, TripPlanPayload, TripPlanResponse } from "../types/trip";
import { formatApiError } from "../utils/errors";
import { readJsonResponse, toRequestError } from "../utils/http";

export async function planTrip(payload: TripPlanPayload): Promise<TripPlanResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/trip/plan/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await readJsonResponse<TripPlanResponse | ApiErrorResponse>(response);

    if (!response.ok) {
      const errorResponse = data as ApiErrorResponse | null;
      const retryAfterSeconds = errorResponse?.retry_after_seconds;
      const message =
        formatApiError(errorResponse?.error) ||
        formatApiError(errorResponse?.detail) ||
        errorResponse?.details ||
        (response.status === 429
          ? retryAfterSeconds
            ? `Too many trip planning requests. Please wait about ${Math.max(1, Math.ceil(retryAfterSeconds / 60))} minute${Math.ceil(retryAfterSeconds / 60) === 1 ? "" : "s"} and try again.`
            : "Too many trip planning requests. Please wait a moment and try again."
          : null) ||
        (response.status === 502
          ? "The backend could not complete route planning. Check the location inputs or retry in a moment."
          : `Trip planning failed with status ${response.status}.`);

      throw new Error(message);
    }

    if (!data) {
      throw new Error("Trip planning succeeded but the backend returned an unreadable response.");
    }

    return data as TripPlanResponse;
  } catch (error) {
    throw toRequestError(error, "Failed to plan trip.");
  }
}
