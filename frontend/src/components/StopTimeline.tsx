import { BODY_COPY, STOP_PILL_STYLES } from "../constants/ui";
import type { TripStop } from "../types/trip";
import { cn } from "../utils/cn";
import { formatStopMeta } from "../utils/formatters";

interface StopTimelineProps {
  stops: TripStop[];
}

export default function StopTimeline({ stops }: StopTimelineProps) {
  if (stops.length === 0) {
    return (
      <p className={BODY_COPY}>
        No operational stops were generated for this trip yet.
      </p>
    );
  }

  return (
    <ul className="m-0 grid list-none gap-4 p-0">
      {stops.map((stop, index) => (
        <li
          key={`${stop.type}-${stop.day}-${index}`}
          className="flex items-start gap-3 border-b border-ink/8 pb-4 last:border-b-0 last:pb-0"
        >
          <span
            className={cn(
              "inline-flex min-w-[5.3rem] justify-center rounded-full px-3 py-1 text-[0.78rem] font-bold capitalize",
              STOP_PILL_STYLES[stop.type],
            )}
          >
            {stop.type}
          </span>
          <div className="grid gap-1">
            <strong className="text-sm font-semibold text-ink">{stop.location}</strong>
            <p className="text-sm leading-6 text-slate-500">
              {formatStopMeta(stop.day, stop.hour, stop.duration)}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}
