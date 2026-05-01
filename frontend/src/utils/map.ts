import type { LatLngTuple } from "leaflet";

import type { Coordinate } from "../types/trip";

export function toLeafletLatLngs(geometry: Coordinate[]): LatLngTuple[] {
  return geometry.map(([lng, lat]) => [lat, lng]);
}
