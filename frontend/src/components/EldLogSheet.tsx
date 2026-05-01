import PanelHeader from "./common/PanelHeader";

import { ELD_LAYOUT, STATUS_ROWS } from "../constants/eld";
import { DUTY_LINE_STYLES, LIST_TEXT, PANEL_SURFACE } from "../constants/ui";
import type { DailyLog } from "../types/trip";
import { cn } from "../utils/cn";
import { createStatusConnectors, xForHour, yForStatus } from "../utils/eld";
import { formatClockHour, formatDurationHours } from "../utils/formatters";

interface EldLogSheetProps {
  log: DailyLog;
}

export default function EldLogSheet({ log }: EldLogSheetProps) {
  const connectors = createStatusConnectors(log);
  const subtleGridClass = "fill-none stroke-slate-900/15 [stroke-width:1]";
  const strongGridClass = "fill-none stroke-slate-900/30 [stroke-width:1]";
  const axisLabelClass = "fill-slate-600 text-[12px] font-bold";

  return (
    <section className={PANEL_SURFACE}>
      <PanelHeader
        eyebrow="ELD Log"
        title={`Day ${log.day} · ${log.date}`}
        aside={
          <div className="flex flex-wrap gap-2 text-xs font-medium text-slate-600">
            <span className="rounded-full border border-ink/10 bg-white/70 px-3 py-1">
              Driving {formatDurationHours(log.totals.driving)}
            </span>
            <span className="rounded-full border border-ink/10 bg-white/70 px-3 py-1">
              On Duty {formatDurationHours(log.totals.on_duty)}
            </span>
            <span className="rounded-full border border-ink/10 bg-white/70 px-3 py-1">
              Off Duty {formatDurationHours(log.totals.off_duty)}
            </span>
          </div>
        }
      />

      <svg
        className="mt-5 h-auto w-full"
        viewBox={`0 0 ${ELD_LAYOUT.svgWidth} ${ELD_LAYOUT.svgHeight}`}
        role="img"
        aria-label={`ELD log for day ${log.day}`}
      >
        <rect
          x={ELD_LAYOUT.leftGutter}
          y={ELD_LAYOUT.topGutter}
          width={ELD_LAYOUT.graphWidth}
          height={ELD_LAYOUT.graphHeight}
          className={subtleGridClass}
        />

        {Array.from({ length: 25 }, (_, hour) => (
          <g key={hour}>
            <line
              x1={xForHour(hour)}
              y1={ELD_LAYOUT.topGutter}
              x2={xForHour(hour)}
              y2={ELD_LAYOUT.topGutter + ELD_LAYOUT.graphHeight}
              className={hour === 24 ? strongGridClass : subtleGridClass}
            />
            {hour < 24 ? (
              <text x={xForHour(hour) + 2} y={22} className={axisLabelClass}>
                {hour}
              </text>
            ) : null}
          </g>
        ))}

        {STATUS_ROWS.map((row, index) => (
          <g key={row.key}>
            <line
              x1={ELD_LAYOUT.leftGutter}
              y1={ELD_LAYOUT.topGutter + index * (ELD_LAYOUT.graphHeight / STATUS_ROWS.length)}
              x2={ELD_LAYOUT.leftGutter + ELD_LAYOUT.graphWidth}
              y2={ELD_LAYOUT.topGutter + index * (ELD_LAYOUT.graphHeight / STATUS_ROWS.length)}
              className={strongGridClass}
            />
            <text
              x={14}
              y={
                ELD_LAYOUT.topGutter +
                index * (ELD_LAYOUT.graphHeight / STATUS_ROWS.length) +
                ELD_LAYOUT.graphHeight / STATUS_ROWS.length / 2 +
                5
              }
              className={axisLabelClass}
            >
              {row.label}
            </text>
          </g>
        ))}

        <line
          x1={ELD_LAYOUT.leftGutter}
          y1={ELD_LAYOUT.topGutter + ELD_LAYOUT.graphHeight}
          x2={ELD_LAYOUT.leftGutter + ELD_LAYOUT.graphWidth}
          y2={ELD_LAYOUT.topGutter + ELD_LAYOUT.graphHeight}
          className={strongGridClass}
        />

        {log.segments.map((segment, index) => (
          <line
            key={`${segment.status}-${segment.start}-${index}`}
            x1={xForHour(segment.start)}
            y1={yForStatus(segment.status)}
            x2={xForHour(segment.end)}
            y2={yForStatus(segment.status)}
            className={cn(
              "fill-none [stroke-linecap:round] [stroke-width:8]",
              DUTY_LINE_STYLES[segment.status],
            )}
          />
        ))}

        {connectors.map((connector, index) => (
          <line
            key={`connector-${index}`}
            x1={connector.x}
            y1={connector.y1}
            x2={connector.x}
            y2={connector.y2}
            className="fill-none stroke-ink [stroke-width:2.5]"
          />
        ))}
      </svg>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-slate-500">
            Remarks
          </h3>
          <ul className={`${LIST_TEXT} m-0 list-none p-0`}>
            {log.remarks.map((remark, index) => (
              <li key={`${remark.time}-${index}`}>
                {formatClockHour(remark.time)} · {remark.location} · {remark.note}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-slate-500">
            Segments
          </h3>
          <ul className={`${LIST_TEXT} m-0 list-none p-0`}>
            {log.segments.map((segment, index) => (
              <li key={`${segment.start}-${segment.end}-${index}`}>
                {formatClockHour(segment.start)}-{formatClockHour(segment.end)} ·{" "}
                {segment.status} · {segment.location}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
