import type { ReactNode } from "react";

import { EYE_BROW, PANEL_TITLE } from "../../constants/ui";
import { cn } from "../../utils/cn";

interface PanelHeaderProps {
  eyebrow: string;
  title: string;
  aside?: ReactNode;
}

export default function PanelHeader({
  eyebrow,
  title,
  aside,
}: PanelHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-4",
        aside ? "lg:flex-row lg:items-start lg:justify-between" : undefined,
      )}
    >
      <div>
        <span className={EYE_BROW}>{eyebrow}</span>
        <h2 className={PANEL_TITLE}>{title}</h2>
      </div>
      {aside ? <div className="lg:pt-2">{aside}</div> : null}
    </div>
  );
}
