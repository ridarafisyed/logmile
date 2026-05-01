import { ELD_LAYOUT, STATUS_ROWS } from "../constants/eld";
import type { DailyLog, DutyStatus } from "../types/trip";

const rowHeight = ELD_LAYOUT.graphHeight / STATUS_ROWS.length;

export function xForHour(hour: number): number {
  return ELD_LAYOUT.leftGutter + (hour / 24) * ELD_LAYOUT.graphWidth;
}

export function yForStatus(status: DutyStatus): number {
  const rowIndex = STATUS_ROWS.findIndex((row) => row.key === status);
  return ELD_LAYOUT.topGutter + rowIndex * rowHeight + rowHeight / 2;
}

export function createStatusConnectors(log: DailyLog) {
  return log.segments.slice(0, -1).flatMap((segment, index) => {
    const nextSegment = log.segments[index + 1];

    if (segment.status === nextSegment.status) {
      return [];
    }

    return [
      {
        x: xForHour(segment.end),
        y1: yForStatus(segment.status),
        y2: yForStatus(nextSegment.status),
      },
    ];
  });
}
