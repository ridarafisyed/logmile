import type { TripFormValues, TripPlanPayload } from "../types/trip";
import { toPlannerPayloadDateTime } from "./datetime";
import { toTripLocationPayload } from "./location";

export function toTripPlanPayload(values: TripFormValues): TripPlanPayload {
  return {
    current_location: toTripLocationPayload(values.current_location),
    pickup_location: toTripLocationPayload(values.pickup_location),
    dropoff_location: toTripLocationPayload(values.dropoff_location),
    trip_start_at: toPlannerPayloadDateTime(
      values.trip_start_mode,
      values.scheduled_trip_start_local,
    ),
    current_cycle_used: Number(values.current_cycle_used),
    cycle_rule: values.cycle_rule,
  };
}
