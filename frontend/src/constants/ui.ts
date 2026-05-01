import type { DutyStatus, StopType } from "../types/trip";
import type { ToastTone } from "../types/ui";

export const PANEL_SURFACE =
  "rounded-[1.6rem] border border-ink/10 bg-white/80 p-5 shadow-panel backdrop-blur-xl sm:p-6";

export const EYE_BROW =
  "inline-flex items-center rounded-full bg-teal-700/10 px-3 py-1 text-[0.72rem] font-black tracking-[0.14em] text-teal-700";

export const PANEL_TITLE =
  "mt-3 text-[1.5rem] font-semibold leading-tight tracking-[-0.03em] text-ink sm:text-[1.8rem]";

export const BODY_COPY = "text-[0.98rem] leading-7 text-slate-600";

export const FIELD_LABEL = "grid gap-2 text-sm font-semibold text-ink";

export const INPUT_BASE =
  "w-full rounded-[1.05rem] border border-ink/12 bg-[rgba(250,248,244,0.92)] px-4 py-3.5 text-base text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.72)] transition placeholder:text-slate-400 focus:border-teal-700 focus:outline-none focus:ring-4 focus:ring-teal-700/15 disabled:cursor-not-allowed disabled:opacity-60";

export const INPUT_LOCKED =
  "border-teal-700/35 bg-emerald-50/65 ring-1 ring-teal-700/10";

export const INPUT_INVALID =
  "border-red-600 bg-red-50/60 ring-1 ring-red-600/10 focus:border-red-700 focus:ring-red-700/15";

export const PRIMARY_BUTTON =
  "inline-flex w-full items-center justify-center rounded-full bg-gradient-to-r from-teal-700 to-teal-800 px-5 py-4 text-lg font-extrabold text-white shadow-[0_18px_30px_rgba(15,118,110,0.22)] transition hover:-translate-y-0.5 hover:shadow-[0_22px_34px_rgba(15,118,110,0.26)] focus:outline-none focus:ring-4 focus:ring-teal-700/20 disabled:cursor-wait disabled:opacity-60 disabled:hover:translate-y-0";

export const NOTE_SURFACE =
  "rounded-[1.1rem] border border-teal-700/10 bg-teal-700/8 px-4 py-3 text-sm leading-6 text-slate-700";

export const DETAIL_TEXT = "text-sm leading-6 text-slate-500";

export const LIST_TEXT = "grid gap-2 text-sm leading-6 text-slate-600";

export const STOP_PILL_STYLES: Record<StopType, string> = {
  pickup: "bg-teal-700/12 text-teal-700",
  dropoff: "bg-red-700/10 text-red-700",
  fuel: "bg-amber-500/12 text-amber-700",
  break: "bg-blue-600/12 text-blue-700",
  rest: "bg-violet-700/12 text-violet-700",
};

export const DUTY_LINE_STYLES: Record<DutyStatus, string> = {
  off_duty: "stroke-teal-700",
  sleeper_berth: "stroke-violet-700",
  driving: "stroke-red-700",
  on_duty: "stroke-amber-600",
};

export const TOAST_TONE_STYLES: Record<ToastTone, string> = {
  error: "border-red-700/20 bg-red-50/95",
  info: "border-teal-700/15 bg-white/95",
  success: "border-emerald-700/15 bg-emerald-50/95",
};
