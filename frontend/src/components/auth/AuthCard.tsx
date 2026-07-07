import type { ReactNode } from "react";

type AuthCardProps = {
  title: string;
  subtitle?: string;
  children: ReactNode;
};

export function AuthCard({
  title,
  subtitle,
  children,
}: AuthCardProps) {
  return (
    <div
      className="
        w-full
        max-w-lg
        rounded-3xl
        border
        border-[var(--app-border)]
        bg-[var(--app-surface)]/90
        p-8
        shadow-[var(--shadow-premium)]
        backdrop-blur-xl
      "
    >
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-brand-primary">
          {title}
        </h2>

        {subtitle && (
          <p className="mt-2 text-sm text-[var(--app-muted)]">
            {subtitle}
          </p>
        )}
      </div>

      {children}
    </div>
  );
}