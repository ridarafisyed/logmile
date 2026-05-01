import type { LatLngTuple } from "leaflet";
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer } from "react-leaflet";

import { BODY_COPY, PANEL_SURFACE } from "../constants/ui";
import EmptyPanel from "./common/EmptyPanel";
import PanelHeader from "./common/PanelHeader";

import { MARKER_COLORS, ROUTE_LINE_COLOR, ROUTE_LINE_WEIGHT } from "../constants/map";
import type { Coordinate, RouteData, StopType, TripStop } from "../types/trip";
import { formatStopMeta } from "../utils/formatters";
import { toLeafletLatLngs } from "../utils/map";

interface RouteMapProps {
  route?: RouteData;
  stops: TripStop[];
}

interface MapMarker {
  type: StopType | "current";
  label: string;
  meta: string;
  coordinates: Coordinate;
}

function createMarker(
  type: StopType | "current",
  label: string,
  coordinates: Coordinate,
  meta: string,
): MapMarker {
  return {
    type,
    label,
    meta,
    coordinates,
  };
}

function toMarkerCenter(coordinates: Coordinate): LatLngTuple {
  return [coordinates[1], coordinates[0]];
}

export default function RouteMap({ route, stops }: RouteMapProps) {
  if (!route?.geometry.length) {
    return (
      <EmptyPanel
        description="The planned corridor, major waypoints, and required fuel, break, and rest markers will land here after dispatch input is complete."
        eyebrow="Route Map"
        title="Map data appears here after a trip is planned."
        variant="map"
      />
    );
  }

  const line = toLeafletLatLngs(route.geometry);
  const legendItems = [
    { label: "Fuel", swatch: "bg-amber-500" },
    { label: "Break", swatch: "bg-blue-600" },
    { label: "Rest", swatch: "bg-violet-700" },
  ] as const;

  const markers: MapMarker[] = [
    createMarker(
      "current",
      route.waypoints.current.label,
      route.waypoints.current.coordinates,
      "Trip origin",
    ),
    createMarker(
      "pickup",
      route.waypoints.pickup.label,
      route.waypoints.pickup.coordinates,
      "Pickup location",
    ),
    createMarker(
      "dropoff",
      route.waypoints.dropoff.label,
      route.waypoints.dropoff.coordinates,
      "Dropoff location",
    ),
    ...stops
      .filter((stop) => ["fuel", "break", "rest"].includes(stop.type))
      .filter((stop): stop is TripStop & { coordinates: Coordinate } => Boolean(stop.coordinates))
      .map((stop) =>
        createMarker(
          stop.type,
          stop.location,
          stop.coordinates,
          `${formatStopMeta(stop.day, stop.hour, stop.duration)} · ${stop.note || stop.type}`,
        ),
      ),
  ];

  return (
    <section className={PANEL_SURFACE}>
      <PanelHeader
        eyebrow="Route Map"
        title="Waypoints and legally-required stops on the planned route."
        aside={
          <div className="flex flex-wrap gap-2 text-xs font-medium text-slate-600">
            {legendItems.map((item) => (
              <span
                key={item.label}
                className="inline-flex items-center gap-2 rounded-full border border-ink/10 bg-white/75 px-3 py-1"
              >
                <span className={`h-2.5 w-2.5 rounded-full ${item.swatch}`} />
                {item.label}
              </span>
            ))}
          </div>
        }
      />

      <p className={`${BODY_COPY} mt-3 max-w-[40rem]`}>
        Follow the corridor from current location to pickup to dropoff, with
        operational markers layered on top where the HOS engine inserts non-driving
        time.
      </p>

      <div className="mt-6 h-[22rem] overflow-hidden rounded-[1.25rem] border border-ink/10 sm:h-[26rem]">
        <MapContainer bounds={line} scrollWheelZoom={false} className="h-full w-full">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Polyline
            positions={line}
            pathOptions={{
              color: ROUTE_LINE_COLOR,
              weight: ROUTE_LINE_WEIGHT,
            }}
          />
          {markers.map((marker, index) => (
            <CircleMarker
              key={`${marker.type}-${index}`}
              center={toMarkerCenter(marker.coordinates)}
              radius={7}
              pathOptions={{
                color: MARKER_COLORS[marker.type],
                fillColor: MARKER_COLORS[marker.type],
                fillOpacity: 0.9,
                weight: 2,
              }}
            >
              <Popup>
                <strong>{marker.label}</strong>
                <div>{marker.meta}</div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </section>
  );
}
