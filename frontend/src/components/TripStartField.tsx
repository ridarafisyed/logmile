import { useEffect, useState } from "react";
import type { ChangeEvent } from "react";

import { INPUT_BASE, INPUT_INVALID, NOTE_SURFACE } from "../constants/ui";
import type { TripStartMode } from "../types/trip";
import { cn } from "../utils/cn";
import { formatPlannerPreview } from "../utils/datetime";

interface TripStartFieldProps {
  disabled?: boolean;
  mode: TripStartMode;
  scheduledValue: string;
  error?: string;
  onModeChange: (mode: TripStartMode) => void;
  onScheduledValueChange: (value: string) => void;
}

export default function TripStartField({
  disabled = false,
  mode,
  scheduledValue,
  error,
  onModeChange,
  onScheduledValueChange,
}: TripStartFieldProps) {
  const [currentTime, setCurrentTime] = useState(() => new Date());

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setCurrentTime(new Date());
    }, 60_000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, []);

  function handleScheduledChange(event: ChangeEvent<HTMLInputElement>) {
    onScheduledValueChange(event.target.value);
  }

  const toggleBaseClass =
    "rounded-full px-4 py-2 text-sm font-semibold transition focus:outline-none focus:ring-4 focus:ring-teal-700/15";

  return (
    <div className="grid gap-2">
      <span className="text-[0.94rem] font-semibold text-ink">Trip start</span>
      <div className="grid gap-3 rounded-[1.15rem] border border-ink/10 bg-white/60 p-3">
        <div className="inline-flex w-fit rounded-full bg-ink/5 p-1">
          <button
            className={cn(
              toggleBaseClass,
              mode === "now"
                ? "bg-white text-ink shadow-sm"
                : "text-slate-600 hover:text-ink",
            )}
            disabled={disabled}
            onClick={() => onModeChange("now")}
            type="button"
          >
            Now
          </button>
          <button
            className={cn(
              toggleBaseClass,
              mode === "scheduled"
                ? "bg-white text-ink shadow-sm"
                : "text-slate-600 hover:text-ink",
            )}
            disabled={disabled}
            onClick={() => onModeChange("scheduled")}
            type="button"
          >
            Select date &amp; time
          </button>
        </div>

        {mode === "now" ? (
          <p className={NOTE_SURFACE}>
            Uses your local time when you submit:{" "}
            <span className="font-semibold text-ink">
              {formatPlannerPreview(currentTime)}
            </span>
          </p>
        ) : (
          <label className="grid gap-2 text-sm font-semibold text-ink">
            <span className="text-[0.82rem] uppercase tracking-[0.12em] text-slate-500">
              Scheduled local time
            </span>
            <input
              aria-invalid={Boolean(error)}
              className={cn(INPUT_BASE, error && INPUT_INVALID)}
              disabled={disabled}
              onChange={handleScheduledChange}
              required={mode === "scheduled"}
              type="datetime-local"
              value={scheduledValue}
            />
          </label>
        )}
      </div>
      {error ? (
        <p className="text-sm font-medium leading-6 text-red-700">{error}</p>
      ) : null}
    </div>
  );
}
