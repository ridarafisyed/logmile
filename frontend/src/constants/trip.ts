import type { CycleRule, TripFormValues } from "../types/trip";
import { toDateTimeLocalValue } from "../utils/datetime";
import { createLocationFieldValue } from "../utils/location";

export function createDefaultTripFormValues(): TripFormValues {
  return {
    current_location: createLocationFieldValue(""),
    pickup_location: createLocationFieldValue(""),
    dropoff_location: createLocationFieldValue(""),
    trip_start_mode: "now",
    scheduled_trip_start_local: toDateTimeLocalValue(new Date()),
    current_cycle_used: "",
    cycle_rule: "70_8",
  };
}

export const CYCLE_RULE_OPTIONS: Array<{ value: CycleRule; label: string }> = [
  { value: "70_8", label: "70 hours / 8 days" },
  { value: "60_7", label: "60 hours / 7 days" },
];
