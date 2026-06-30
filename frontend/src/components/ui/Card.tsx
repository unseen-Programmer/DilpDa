import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "../../utils/cn";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
};

export function Card({ children, className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] shadow-soft",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
