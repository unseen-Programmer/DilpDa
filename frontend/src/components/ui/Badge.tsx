import type { ReactNode } from "react";

import { cn } from "../../utils/cn";

type BadgeTone = "neutral" | "success" | "warning" | "danger";

type BadgeProps = {
  children: ReactNode;
  tone?: BadgeTone;
};

const toneClasses: Record<BadgeTone, string> = {
  neutral: "bg-brand-primary/10 text-brand-primary",
  success: "bg-brand-success/10 text-brand-success",
  warning: "bg-brand-warning/15 text-amber-700 dark:text-brand-warning",
  danger: "bg-brand-danger/10 text-brand-danger",
};

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return (
    <span className={cn("inline-flex rounded-full px-3 py-1 text-xs font-bold", toneClasses[tone])}>
      {children}
    </span>
  );
}
