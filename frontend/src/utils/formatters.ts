const numberFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
});

export function formatNumber(value: number): string {
  return numberFormatter.format(value);
}

export function formatMiles(value: number): string {
  return `${formatNumber(value)} mi`;
}

function toWholeMinutes(value: number): number {
  return Math.max(0, Math.round(value * 60));
}

function formatMinutesAsHours(totalMinutes: number): string {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours === 0) {
    return `${minutes}m`;
  }

  if (minutes === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${minutes}m`;
}

export function formatDurationHours(value: number): string {
  return formatMinutesAsHours(toWholeMinutes(value));
}

export function formatClockHour(value: number): string {
  return formatMinutesAsHours(toWholeMinutes(value));
}

export function formatHours(value: number): string {
  return formatDurationHours(value);
}

export function formatStopMeta(day: number, hour: number, duration: number): string {
  return `Day ${day} · ${formatClockHour(hour)} · ${formatDurationHours(duration)}`;
}
