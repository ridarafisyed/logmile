import type { LocationFieldValue, LocationOption, TripLocationPayload } from "../types/trip";

export function createLocationFieldValue(text: string): LocationFieldValue {
  return {
    text,
    selection: null,
  };
}

export function toTripLocationPayload(
  value: LocationFieldValue,
): TripLocationPayload {
  const trimmedText = value.text.trim();

  if (value.selection && value.selection.label === trimmedText) {
    return value.selection;
  }

  return trimmedText;
}

export function toLocationFieldValue(
  text: string,
  selection: LocationOption | null = null,
): LocationFieldValue {
  return {
    text,
    selection,
  };
}
