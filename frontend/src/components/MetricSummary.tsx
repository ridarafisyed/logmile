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
          label: "Total Days",
          value: String(summary.total_days),
        },
        {
          label: "Cycle Left After Trip",
          value: formatDurationHours(summary.remaining_cycle_hours_after_trip),
        },
      ]
    : loading
      ? [
          { label: "Distance", value: "Planning..." },
          { label: "Drive Time", value: "Planning..." },
          { label: "Total Days", value: "Planning..." },
          { label: "Cycle Left After Trip", value: "Planning..." },
        ]
      : errorMessage
        ? [
            { label: "Distance", value: "Unavailable" },
            { label: "Drive Time", value: "Unavailable" },
            { label: "Total Days", value: "Unavailable" },
            { label: "Cycle Left After Trip", value: "Unavailable" },
          ]
    : [
        { label: "Distance", value: "Pending" },
        { label: "Drive Time", value: "Pending" },
        { label: "Total Days", value: "Pending" },
        { label: "Cycle Left After Trip", value: "Pending" },
      ];

  return (
    <section className="mt-6 grid gap-3">
      {errorMessage && !summary ? (
        <p className="rounded-[1.2rem] border border-amber-300/70 bg-amber-50 px-4 py-3 text-sm font-medium leading-6 text-amber-900">
          Metrics are still unavailable because the latest trip plan did not complete.
          {` ${errorMessage}`}
        </p>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metricCards.map((card) => (
          <article
            key={card.label}
            className="grid gap-2 rounded-[1.4rem] bg-ink p-5 text-emerald-50 shadow-[0_18px_34px_rgba(16,34,27,0.18)]"
          >
            <span className="text-[0.78rem] font-bold uppercase tracking-[0.14em] text-teal-200">
              {card.label}
            </span>
            <strong className="text-[1.7rem] font-semibold tracking-[-0.03em]">
              {card.value}
            </strong>
          </article>
        ))}
      </div>
    </section>
  );
}
