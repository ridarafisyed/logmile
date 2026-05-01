import type { DutyStatus } from "../types/trip";

export const STATUS_ROWS: Array<{ key: DutyStatus; label: string }> = [
  { key: "off_duty", label: "Off Duty" },
  { key: "sleeper_berth", label: "Sleeper" },
  { key: "driving", label: "Driving" },
  { key: "on_duty", label: "On Duty" },
];

export const ELD_LAYOUT = {
  svgWidth: 1120,
  svgHeight: 300,
  leftGutter: 130,
  topGutter: 36,
  graphWidth: 920,
  graphHeight: 180,
} as const;
