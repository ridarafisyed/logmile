import type { TripSummary } from "../types/trip";
import { formatDurationHours, formatMiles } from "../utils/formatters";

interface MetricSummaryProps {
  summary?: TripSummary;
  loading?: boolean;
  errorMessage?: string | null;
}

interface MetricCardDefinition {
  label: string;
  value: string;
}

export default function MetricSummary({
  summary,
  loading = false,
  errorMessage = null,
}: MetricSummaryProps) {
  const metricCards: MetricCardDefinition[] = summary
    ? [
        {
          label: "Distance",
          value: formatMiles(summary.distance_miles),
        },
        {
          label: "Drive Time",
          value: formatDurationHours(summary.estimated_driving_hours),
        },
        {
          label: "Log Sheets",
          value: String(summary.total_days),
        },
        {
          label: "Cycle Left After Trip",
          value: formatDurationHours(summary.remaining_cycle_hours_after_trip),
        },
      ]
    : [];

  if (!loading && !summary && !errorMessage) {
    return null;
  }

  return (
    <section className="mt-6 grid gap-3">
      {errorMessage && !summary ? (
        <p className="rounded-[1.2rem] border border-amber-300/70 bg-amber-50 px-4 py-3 text-sm font-medium leading-6 text-amber-900">
          Metrics are still unavailable because the latest trip plan did not complete.
          {` ${errorMessage}`}
        </p>
      ) : null}

      {loading ? (
        <div aria-busy="true" className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            "Distance",
            "Drive Time",
            "Log Sheets",
            "Cycle Left After Trip",
          ].map((label) => (
            <article
              key={label}
              className="grid gap-4 rounded-[1.4rem] border border-teal-700/10 bg-white/82 p-5 shadow-[0_16px_34px_rgba(15,23,42,0.08)]"
            >
              <span className="text-[0.78rem] font-bold uppercase tracking-[0.14em] text-teal-700/75">
                {label}
              </span>
              <div className="grid gap-2 animate-pulse">
                <span className="h-4 w-24 rounded-full bg-teal-700/10" />
                <span className="h-9 w-36 rounded-[0.8rem] bg-slate-200/75" />
              </div>
            </article>
          ))}
        </div>
      ) : summary ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metricCards.map((card) => (
            <article
              key={card.label}
              className="grid gap-2 rounded-[1.4rem] border border-teal-700/10 bg-white p-5 shadow-[0_16px_34px_rgba(15,23,42,0.08)]"
            >
              <span className="text-[0.78rem] font-bold uppercase tracking-[0.14em] text-teal-700/75">
                {card.label}
              </span>
              <strong className="text-[1.7rem] font-semibold tracking-[-0.03em] text-ink">
                {card.value}
              </strong>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}
