import { BODY_COPY, PANEL_SURFACE } from "../constants/ui";
import { formatApiDateTime } from "../utils/datetime";
import EmptyPanel from "./common/EmptyPanel";
import PanelHeader from "./common/PanelHeader";
import StopTimeline from "./StopTimeline";

import type { HOSPlan } from "../types/trip";

interface TripSummaryPanelProps {
  hosPlan?: HOSPlan;
}

export default function TripSummaryPanel({ hosPlan }: TripSummaryPanelProps) {
  if (!hosPlan) {
    return (
      <EmptyPanel
        description="Once the planner runs, this panel will condense cycle legality, stop timing, and the backend’s dispatch-ready summary into one readable narrative."
        eyebrow="Trip Summary"
        title="Plan a trip to see the backend response summarized here."
        variant="summary"
      />
    );
  }

  const tripStartLabel = formatApiDateTime(hosPlan.summary?.trip_start_at);
  const estimatedArrivalLabel = formatApiDateTime(
    hosPlan.summary?.estimated_arrival_at,
  );

  return (
    <section className={`${PANEL_SURFACE} xl:flex xl:max-h-[42rem] xl:flex-col`}>
      <PanelHeader
        eyebrow="Trip Summary"
        title={
          hosPlan.is_legal
            ? "Trip is legal under the selected cycle rule."
            : "Trip needs a restart or a different plan."
        }
      />
      <p className={`${BODY_COPY} mt-3`}>{hosPlan.message}</p>
      {tripStartLabel || estimatedArrivalLabel ? (
        <div className="mt-5 grid gap-3 rounded-[1.15rem] border border-ink/10 bg-white/60 p-4 sm:grid-cols-2">
          {tripStartLabel ? (
            <div className="grid gap-1">
              <span className="text-[0.78rem] font-bold uppercase tracking-[0.12em] text-slate-500">
                Planned Start
              </span>
              <strong className="text-sm font-semibold text-ink">
                {tripStartLabel}
              </strong>
            </div>
          ) : null}
          {estimatedArrivalLabel ? (
            <div className="grid gap-1">
              <span className="text-[0.78rem] font-bold uppercase tracking-[0.12em] text-slate-500">
                Estimated Arrival
              </span>
              <strong className="text-sm font-semibold text-ink">
                {estimatedArrivalLabel}
              </strong>
            </div>
          ) : null}
        </div>
      ) : null}
      <div className="mt-6 min-h-0 xl:flex-1 xl:overflow-y-auto xl:pr-2">
        <StopTimeline stops={hosPlan.stops} />
      </div>
    </section>
  );
}
