import { BODY_COPY, EYE_BROW, PANEL_SURFACE, PANEL_TITLE } from "../../constants/ui";

interface EmptyPanelProps {
  eyebrow: string;
  title: string;
  description: string;
  variant: "map" | "summary" | "logs";
}

function EmptyStateGraphic({
  variant,
}: Pick<EmptyPanelProps, "variant">) {
  const frameClass =
    "fill-[rgba(255,255,255,0.82)] stroke-[rgba(15,23,42,0.08)] [stroke-width:2]";
  const insetFrameClass =
    "fill-[rgba(248,250,252,0.92)] stroke-[rgba(15,23,42,0.05)] [stroke-width:1.6]";
  const gridFrameClass =
    "fill-[rgba(255,255,255,0.78)] stroke-[rgba(15,23,42,0.07)] [stroke-width:2]";
  const gridLineClass = "stroke-[rgba(148,163,184,0.28)] [stroke-width:1.5]";
  const routeLineClass =
    "fill-none stroke-teal-700 [stroke-linecap:round] [stroke-linejoin:round] [stroke-width:6]";
  const accentRouteLineClass =
    "fill-none stroke-amber-600 [stroke-linecap:round] [stroke-linejoin:round] [stroke-width:6]";
  const pointBaseClass = "stroke-white/95 [stroke-width:4]";
  const chipClass = "fill-[rgba(71,85,105,0.18)]";
  const softChipClass = "fill-[rgba(148,163,184,0.22)]";
  const accentChipClass = "fill-[rgba(15,118,110,0.18)]";
  const warmChipClass = "fill-[rgba(217,119,6,0.18)]";
  const dotClass = "fill-[rgba(148,163,184,0.5)]";

  if (variant === "map") {
    return (
      <svg
        aria-hidden="true"
        className="h-auto w-full max-w-sm"
        viewBox="0 0 240 140"
      >
        <rect x="12" y="12" width="216" height="116" rx="20" className={frameClass} />
        <rect x="32" y="26" width="160" height="88" rx="18" className={insetFrameClass} />
        <path
          d="M44 88 C74 34, 110 116, 152 56 S198 42, 208 78"
          className={routeLineClass}
        />
        <circle cx="48" cy="84" r="8" className={`${pointBaseClass} fill-teal-700`} />
        <circle cx="154" cy="56" r="8" className={`${pointBaseClass} fill-blue-700`} />
        <circle cx="208" cy="78" r="8" className={`${pointBaseClass} fill-red-700`} />
        <rect x="54" y="38" width="46" height="10" rx="5" className={accentChipClass} />
        <rect x="136" y="96" width="54" height="10" rx="5" className={softChipClass} />
        <rect x="154" y="28" width="30" height="8" rx="4" className={warmChipClass} />
      </svg>
    );
  }

  if (variant === "summary") {
    return (
      <svg
        aria-hidden="true"
        className="h-auto w-full max-w-sm"
        viewBox="0 0 240 140"
      >
        <rect x="18" y="18" width="92" height="104" rx="18" className={frameClass} />
        <rect x="128" y="18" width="94" height="48" rx="18" className={frameClass} />
        <rect x="128" y="76" width="94" height="46" rx="18" className={frameClass} />
        <rect x="34" y="36" width="44" height="10" rx="5" className={accentChipClass} />
        <rect x="34" y="56" width="58" height="16" rx="8" className={accentChipClass} />
        <rect x="34" y="84" width="54" height="8" rx="4" className={softChipClass} />
        <circle cx="40" cy="96" r="3" className={dotClass} />
        <circle cx="52" cy="96" r="3" className={dotClass} />
        <circle cx="64" cy="96" r="3" className={dotClass} />
        <rect x="142" y="34" width="48" height="10" rx="5" className={warmChipClass} />
        <rect x="142" y="50" width="62" height="8" rx="4" className={softChipClass} />
        <rect x="142" y="92" width="56" height="10" rx="5" className={chipClass} />
        <rect x="142" y="108" width="46" height="8" rx="4" className={softChipClass} />
      </svg>
    );
  }

  return (
    <svg
      aria-hidden="true"
      className="h-auto w-full max-w-sm"
      viewBox="0 0 240 140"
    >
      <rect x="18" y="18" width="204" height="104" rx="18" className={frameClass} />
      <rect x="44" y="38" width="152" height="62" rx="10" className={gridFrameClass} />
      <line x1="82" y1="38" x2="82" y2="100" className={gridLineClass} />
      <line x1="120" y1="38" x2="120" y2="100" className={gridLineClass} />
      <line x1="158" y1="38" x2="158" y2="100" className={gridLineClass} />
      <line x1="44" y1="54" x2="196" y2="54" className={gridLineClass} />
      <line x1="44" y1="70" x2="196" y2="70" className={gridLineClass} />
      <line x1="44" y1="86" x2="196" y2="86" className={gridLineClass} />
      <path d="M54 54 H102 V70 H164 V86 H186" className={accentRouteLineClass} />
      <rect x="52" y="108" width="48" height="10" rx="5" className={accentChipClass} />
      <rect x="112" y="108" width="72" height="10" rx="5" className={softChipClass} />
    </svg>
  );
}

function emptyStateHints(
  variant: EmptyPanelProps["variant"],
): string[] {
  if (variant === "map") {
    return ["Route path", "Stop markers", "Rest points"];
  }

  if (variant === "summary") {
    return ["Legality", "Stops", "ETA notes"];
  }

  return ["24h grid", "Duty lines", "Remarks"];
}

export default function EmptyPanel({
  eyebrow,
  title,
  description,
  variant,
}: EmptyPanelProps) {
  return (
    <section
      className={`${PANEL_SURFACE} grid min-h-[26rem] grid-rows-[auto_1fr] gap-5`}
    >
      <div className="max-w-[34rem]">
        <span className={EYE_BROW}>{eyebrow}</span>
        <h2 className={`${PANEL_TITLE} max-w-[18ch]`}>{title}</h2>
        <p className={`${BODY_COPY} mt-3 max-w-[36rem]`}>{description}</p>
      </div>
      <div className="flex min-h-[14rem] flex-col items-center justify-center gap-4 overflow-hidden rounded-[1.25rem] border border-dashed border-ink/12 bg-[radial-gradient(circle_at_top_left,rgba(15,118,110,0.08),transparent_35%),linear-gradient(180deg,rgba(255,255,255,0.66),rgba(247,245,241,0.92))] px-5 py-6">
        <EmptyStateGraphic variant={variant} />
        <div className="flex flex-wrap items-center justify-center gap-2">
          {emptyStateHints(variant).map((hint) => (
            <span
              key={hint}
              className="inline-flex items-center rounded-full border border-teal-700/10 bg-white/72 px-3 py-1.5 text-[0.78rem] font-semibold text-slate-600"
            >
              {hint}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
