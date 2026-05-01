import type { TripStartMode } from "../types/trip";

const previewFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
});

const detailedFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  hour: "numeric",
  minute: "2-digit",
});

function padNumber(value: number): string {
  return String(value).padStart(2, "0");
}

export function toDateTimeLocalValue(date: Date): string {
  return [
    date.getFullYear(),
    padNumber(date.getMonth() + 1),
    padNumber(date.getDate()),
  ].join("-") +
    `T${padNumber(date.getHours())}:${padNumber(date.getMinutes())}`;
}

export function parseDateTimeLocalValue(localValue: string): Date {
  const [datePart = "", timePart = ""] = localValue.split("T");
  const [year, month, day] = datePart.split("-").map(Number);
  const [hour, minute] = timePart.split(":").map(Number);

  return new Date(year, (month || 1) - 1, day || 1, hour || 0, minute || 0, 0, 0);
}

export function toOffsetDateTimeString(date: Date): string {
  const offsetMinutes = -date.getTimezoneOffset();
  const sign = offsetMinutes >= 0 ? "+" : "-";
  const absoluteOffsetMinutes = Math.abs(offsetMinutes);
  const offsetHours = Math.floor(absoluteOffsetMinutes / 60);
  const offsetRemainderMinutes = absoluteOffsetMinutes % 60;

  return (
    `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}` +
    `T${padNumber(date.getHours())}:${padNumber(date.getMinutes())}:00` +
    `${sign}${padNumber(offsetHours)}:${padNumber(offsetRemainderMinutes)}`
  );
}

export function toPlannerPayloadDateTime(
  mode: TripStartMode,
  scheduledLocalValue: string,
): string {
  const effectiveDate =
    mode === "now" ? new Date() : parseDateTimeLocalValue(scheduledLocalValue);

  return toOffsetDateTimeString(effectiveDate);
}

export function formatPlannerPreview(date: Date): string {
  return previewFormatter.format(date);
}

export function formatApiDateTime(dateTimeValue?: string): string | null {
  if (!dateTimeValue) {
    return null;
  }

  const parsedDate = new Date(dateTimeValue);
  if (Number.isNaN(parsedDate.getTime())) {
    return null;
  }

  return detailedFormatter.format(parsedDate);
}
