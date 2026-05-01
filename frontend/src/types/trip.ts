export type CycleRule = "70_8" | "60_7";
export type TripStartMode = "now" | "scheduled";

export type DutyStatus =
  | "off_duty"
  | "sleeper_berth"
  | "driving"
  | "on_duty";

export type StopType = "pickup" | "dropoff" | "fuel" | "break" | "rest";

export type Coordinate = [lng: number, lat: number];

export interface LocationOption {
  label: string;
  query: string;
  coordinates: Coordinate;
}

export interface LocationFieldValue {
  text: string;
  selection: LocationOption | null;
}

export type LocationFieldKey =
  | "current_location"
  | "pickup_location"
  | "dropoff_location";

export interface LocationFieldMeta {
  hasSearched: boolean;
  suggestionCount: number;
  suggestionError: boolean;
}

export type LocationFieldMetaMap = Record<LocationFieldKey, LocationFieldMeta>;

export type TripLocationPayload = string | LocationOption;

export interface TripFormValues {
  current_location: LocationFieldValue;
  pickup_location: LocationFieldValue;
  dropoff_location: LocationFieldValue;
  trip_start_mode: TripStartMode;
  scheduled_trip_start_local: string;
  current_cycle_used: string;
  cycle_rule: CycleRule;
}

export interface TripPlanPayload {
  current_location: TripLocationPayload;
  pickup_location: TripLocationPayload;
  dropoff_location: TripLocationPayload;
  trip_start_at: string;
  current_cycle_used: number;
  cycle_rule: CycleRule;
}

export interface Waypoint extends LocationOption {}

export interface RouteLeg {
  kind: string;
  start: string;
  end: string;
  distance_miles: number;
  duration_hours: number;
}

export interface RouteData {
  distance_miles: number;
  duration_hours: number;
  geometry: Coordinate[];
  locations: {
    current: string;
    pickup: string;
    dropoff: string;
  };
  waypoints: {
    current: Waypoint;
    pickup: Waypoint;
    dropoff: Waypoint;
  };
  legs: RouteLeg[];
}

export interface TripStop {
  type: StopType;
  location: string;
  day: number;
  hour: number;
  duration: number;
  note?: string;
  miles_from_route_start?: number;
  coordinates?: Coordinate;
}

export interface TripSegment {
  status: DutyStatus;
  start: number;
  end: number;
  duration: number;
  location: string;
  note?: string;
}

export interface TripRemark {
  time: number;
  location: string;
  note: string;
}

export interface DailyLogTotals {
  off_duty: number;
  sleeper_berth: number;
  driving: number;
  on_duty: number;
}

export interface DailyLog {
  day: number;
  date: string;
  segments: TripSegment[];
  totals: DailyLogTotals;
  total_hours: number;
  remarks: TripRemark[];
}

export interface TripSummary {
  distance_miles: number;
  estimated_driving_hours: number;
  current_cycle_used: number;
  remaining_cycle_hours_after_trip: number;
  total_days: number;
  cycle_rule: CycleRule;
  trip_start_at?: string;
  estimated_arrival_at?: string;
}

export interface HOSPlan {
  is_legal: boolean;
  message: string;
  summary?: TripSummary;
  daily_logs: DailyLog[];
  stops: TripStop[];
}

export interface TripPlanResponse {
  route: RouteData;
  hos_plan: HOSPlan;
}

export interface ApiErrorResponse {
  error?: unknown;
  detail?: unknown;
  details?: string;
  retry_after_seconds?: number;
}
