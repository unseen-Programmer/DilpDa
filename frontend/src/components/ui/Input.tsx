import { forwardRef, type InputHTMLAttributes } from "react";

import { cn } from "../../utils/cn";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  error?: string;
  helperText?: string;
  label?: string;
};

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, error, helperText, id, label, ...props },
  ref,
) {
  const inputId = id ?? props.name;

  return (
    <label className="grid gap-2 text-sm font-medium text-[var(--app-text)]" htmlFor={inputId}>
      {label ? <span>{label}</span> : null}
      <input
        className={cn(
          "h-11 rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface-strong)] px-4 text-[var(--app-text)] outline-none transition placeholder:text-brand-muted/70 focus:border-brand-accent focus:ring-4 focus:ring-[var(--app-ring)]",
          error ? "border-brand-danger focus:border-brand-danger" : "",
          className,
        )}
        id={inputId}
        ref={ref}
        {...props}
      />
      {error ? <span className="text-xs font-semibold text-brand-danger">{error}</span> : null}
      {helperText ? <span className="text-xs text-brand-muted">{helperText}</span> : null}
    </label>
  );
});
