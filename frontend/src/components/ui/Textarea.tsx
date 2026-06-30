import type { TextareaHTMLAttributes } from "react";

import { cn } from "../../utils/cn";

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  error?: string;
  label?: string;
};

export function Textarea({ className, error, id, label, ...props }: TextareaProps) {
  const textareaId = id ?? props.name;

  return (
    <label className="grid gap-2 text-sm font-medium text-[var(--app-text)]" htmlFor={textareaId}>
      {label ? <span>{label}</span> : null}
      <textarea
        className={cn(
          "min-h-28 resize-y rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface-strong)] px-4 py-3 text-[var(--app-text)] outline-none transition placeholder:text-brand-muted/70 focus:border-brand-accent focus:ring-4 focus:ring-[var(--app-ring)]",
          error ? "border-brand-danger focus:border-brand-danger" : "",
          className,
        )}
        id={textareaId}
        {...props}
      />
      {error ? <span className="text-xs font-semibold text-brand-danger">{error}</span> : null}
    </label>
  );
}
