import type {
  LocationFieldMetaMap,
  LocationFieldValue,
  TripFormValues,
} from "../types/trip";
import { parseDateTimeLocalValue } from "./datetime";

export type TripFormErrorField =
  | "current_location"
  | "pickup_location"
  | "dropoff_location"
  | "current_cycle_used"
  | "scheduled_trip_start_local";

export type TripFormErrors = Partial<Record<TripFormErrorField, string>>;

const cycleMaxHoursByRule = {
  "70_8": 70,
  "60_7": 60,
} as const;

function looksLikeFullPlaceName(value: string): boolean {
  const normalizedValue = value.trim();
  if (!normalizedValue) {
    return false;
  }

  if (normalizedValue.includes(",")) {
    return true;
  }

  const alphaTokens = normalizedValue
    .split(/\s+/)
    .filter((token) => /[A-Za-z]/.test(token));
  return alphaTokens.length >= 2;
}

function validateLocation(
  value: LocationFieldValue,
  label: string,
  meta?: {
    hasSearched: boolean;
    suggestionCount: number;
    suggestionError: boolean;
  },
): string | undefined {
  if (!value.text.trim()) {
    return `${label} is required.`;
  }

  if (
    value.selection === null &&
    !looksLikeFullPlaceName(value.text)
  ) {
    return `${label} needs a fuller place name or a confirmed suggestion.`;
  }

  if (
    value.selection === null &&
    meta?.hasSearched &&
    meta.suggestionCount > 0 &&
    !meta.suggestionError
  ) {
    return `${label} needs a confirmed suggestion. Pick one from the dropdown or enter a fuller place name.`;
  }

  return undefined;
}

export function validateTripForm(
  values: TripFormValues,
  locationMeta?: Partial<LocationFieldMetaMap>,
): TripFormErrors {
  const errors: TripFormErrors = {};

  errors.current_location = validateLocation(
    values.current_location,
    "Current location",
    locationMeta?.current_location,
  );
  errors.pickup_location = validateLocation(
    values.pickup_location,
    "Pickup location",
    locationMeta?.pickup_location,
  );
  errors.dropoff_location = validateLocation(
    values.dropoff_location,
    "Dropoff location",
    locationMeta?.dropoff_location,
  );

  const cycleValue = values.current_cycle_used.trim();
  const cycleMax = cycleMaxHoursByRule[values.cycle_rule];

  if (!cycleValue) {
    errors.current_cycle_used = "Current cycle used is required.";
  } else {
    const parsedCycleValue = Number(cycleValue);
    if (Number.isNaN(parsedCycleValue)) {
      errors.current_cycle_used = "Current cycle used must be a number.";
    } else if (parsedCycleValue < 0 || parsedCycleValue > cycleMax) {
      errors.current_cycle_used = `Current cycle used must be between 0 and ${cycleMax} hours.`;
    }
  }

  if (values.trip_start_mode === "scheduled") {
    const scheduledValue = values.scheduled_trip_start_local.trim();
    if (!scheduledValue) {
      errors.scheduled_trip_start_local = "Scheduled trip start is required.";
    } else if (Number.isNaN(parseDateTimeLocalValue(scheduledValue).getTime())) {
      errors.scheduled_trip_start_local =
        "Scheduled trip start must be a valid date and time.";
    }
  }

  return Object.fromEntries(
    Object.entries(errors).filter(([, errorMessage]) => Boolean(errorMessage)),
  ) as TripFormErrors;
}

export function hasTripFormErrors(errors: TripFormErrors): boolean {
  return Object.keys(errors).length > 0;
}

export function createTripFormErrorToastMessage(errors: TripFormErrors): string {
  const errorMessages = Object.values(errors).filter(Boolean);

  if (errorMessages.length === 0) {
    return "Please correct the highlighted fields before planning the route.";
  }

  if (errorMessages.length === 1) {
    return errorMessages[0]!;
  }

  return `Please correct the highlighted fields. ${errorMessages[0]}`;
}
