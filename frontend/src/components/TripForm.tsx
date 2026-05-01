import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

import { CYCLE_RULE_OPTIONS, createDefaultTripFormValues } from "../constants/trip";
import {
  EYE_BROW,
  FIELD_LABEL,
  INPUT_BASE,
  INPUT_INVALID,
  NOTE_SURFACE,
  PANEL_SURFACE,
  PANEL_TITLE,
  PRIMARY_BUTTON,
} from "../constants/ui";
import type {
  LocationFieldMeta,
  LocationFieldMetaMap,
  LocationFieldValue,
  TripFormValues,
  TripStartMode,
} from "../types/trip";
import { toDateTimeLocalValue } from "../utils/datetime";
import {
  createTripFormErrorToastMessage,
  hasTripFormErrors,
  type TripFormErrors,
  validateTripForm,
} from "../utils/tripValidation";
import { cn } from "../utils/cn";
import LocationAutocompleteField from "./LocationAutocompleteField";
import TripStartField from "./TripStartField";
import type { LocationFieldName } from "./LocationAutocompleteField";

interface TripFormProps {
  loading: boolean;
  onValidationError: (message: string) => void;
  onSubmit: (values: TripFormValues) => Promise<void>;
}

const EMPTY_LOCATION_META: LocationFieldMeta = {
  hasSearched: false,
  suggestionCount: 0,
  suggestionError: false,
};

const DEFAULT_LOCATION_META: LocationFieldMetaMap = {
  current_location: EMPTY_LOCATION_META,
  pickup_location: EMPTY_LOCATION_META,
  dropoff_location: EMPTY_LOCATION_META,
};

export default function TripForm({
  loading,
  onValidationError,
  onSubmit,
}: TripFormProps) {
  const [values, setValues] = useState<TripFormValues>(() => createDefaultTripFormValues());
  const [errors, setErrors] = useState<TripFormErrors>({});
  const [locationMeta, setLocationMeta] =
    useState<LocationFieldMetaMap>(DEFAULT_LOCATION_META);

  function clearFieldError(fieldName: keyof TripFormErrors) {
    setErrors((previousErrors) => {
      if (!previousErrors[fieldName]) {
        return previousErrors;
      }

      const nextErrors = { ...previousErrors };
      delete nextErrors[fieldName];
      return nextErrors;
    });
  }

  function updateField(
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) {
    const fieldName = event.target.name as Exclude<
      keyof TripFormValues,
      LocationFieldName
    >;
    const { value } = event.target;

    setValues((previousValues) => ({
      ...previousValues,
      [fieldName]: value,
    }));
    clearFieldError(fieldName as keyof TripFormErrors);
  }

  function updateLocationField(
    fieldName: LocationFieldName,
    fieldValue: LocationFieldValue,
  ) {
    setValues((previousValues) => ({
      ...previousValues,
      [fieldName]: fieldValue,
    }));
    clearFieldError(fieldName);
  }

  function updateLocationMeta(
    fieldName: LocationFieldName,
    meta: LocationFieldMeta,
  ) {
    setLocationMeta((previousMeta) => {
      const currentMeta = previousMeta[fieldName];
      if (
        currentMeta.hasSearched === meta.hasSearched &&
        currentMeta.suggestionCount === meta.suggestionCount &&
        currentMeta.suggestionError === meta.suggestionError
      ) {
        return previousMeta;
      }

      return {
        ...previousMeta,
        [fieldName]: meta,
      };
    });
  }

  function updateTripStartMode(mode: TripStartMode) {
    setValues((previousValues) => ({
      ...previousValues,
      trip_start_mode: mode,
      scheduled_trip_start_local:
        mode === "scheduled" && previousValues.trip_start_mode === "now"
          ? toDateTimeLocalValue(new Date())
          : previousValues.scheduled_trip_start_local,
    }));
    clearFieldError("scheduled_trip_start_local");
  }

  function updateScheduledTripStart(value: string) {
    setValues((previousValues) => ({
      ...previousValues,
      scheduled_trip_start_local: value,
    }));
    clearFieldError("scheduled_trip_start_local");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const validationErrors = validateTripForm(values, locationMeta);
    if (hasTripFormErrors(validationErrors)) {
      setErrors(validationErrors);
      onValidationError(createTripFormErrorToastMessage(validationErrors));
      return;
    }

    setErrors({});
    await onSubmit(values);
  }

  return (
    <form className={`${PANEL_SURFACE} grid gap-4`} onSubmit={handleSubmit}>
      <div>
        <span className={EYE_BROW}>Plan your trip</span>
        <h2 className={PANEL_TITLE}>
          Feed the backend the minimum dispatch context it needs.
        </h2>
      </div>

      <LocationAutocompleteField
        disabled={loading}
        error={errors.current_location}
        label="Current location"
        name="current_location"
        onChange={updateLocationField}
        onMetaChange={updateLocationMeta}
        placeholder="Chicago, IL"
        value={values.current_location}
      />

      <LocationAutocompleteField
        disabled={loading}
        error={errors.pickup_location}
        label="Pickup location"
        name="pickup_location"
        onChange={updateLocationField}
        onMetaChange={updateLocationMeta}
        placeholder="St. Louis, MO"
        value={values.pickup_location}
      />

      <LocationAutocompleteField
        disabled={loading}
        error={errors.dropoff_location}
        label="Dropoff location"
        name="dropoff_location"
        onChange={updateLocationField}
        onMetaChange={updateLocationMeta}
        placeholder="Dallas, TX"
        value={values.dropoff_location}
      />

      <p className={NOTE_SURFACE}>
        Pick a suggestion when possible to lock routing to exact coordinates. Free
        text still works as a fallback.
      </p>

      <TripStartField
        disabled={loading}
        error={errors.scheduled_trip_start_local}
        mode={values.trip_start_mode}
        onModeChange={updateTripStartMode}
        onScheduledValueChange={updateScheduledTripStart}
        scheduledValue={values.scheduled_trip_start_local}
      />

      <div className="grid gap-4 md:grid-cols-2">
        <label className={FIELD_LABEL}>
          <span className="text-[0.94rem]">Current cycle used</span>
          <input
            aria-invalid={Boolean(errors.current_cycle_used)}
            className={cn(
              INPUT_BASE,
              errors.current_cycle_used && INPUT_INVALID,
            )}
            disabled={loading}
            name="current_cycle_used"
            value={values.current_cycle_used}
            onChange={updateField}
            inputMode="decimal"
            min="0"
            max="70"
            step="0.25"
            required
          />
          {errors.current_cycle_used ? (
            <p className="text-sm font-medium leading-6 text-red-700">
              {errors.current_cycle_used}
            </p>
          ) : null}
        </label>

        <label className={FIELD_LABEL}>
          <span className="text-[0.94rem]">Cycle rule</span>
          <select
            className={INPUT_BASE}
            disabled={loading}
            name="cycle_rule"
            value={values.cycle_rule}
            onChange={updateField}
          >
            {CYCLE_RULE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button className={PRIMARY_BUTTON} type="submit" disabled={loading}>
        {loading ? "Planning..." : "Plan Route"}
      </button>
    </form>
  );
}
