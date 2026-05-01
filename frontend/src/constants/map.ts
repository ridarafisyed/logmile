import type { StopType } from "../types/trip";

export const ROUTE_LINE_COLOR = "#0f766e";
export const ROUTE_LINE_WEIGHT = 5;

export const MARKER_COLORS: Record<StopType | "current", string> = {
  current: "#0f172a",
  pickup: "#0f766e",
  dropoff: "#b91c1c",
  fuel: "#d97706",
  break: "#2563eb",
  rest: "#6d28d9",
};
