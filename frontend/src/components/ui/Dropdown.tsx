import type { ReactNode } from "react";
import { FiChevronDown } from "react-icons/fi";

import { cn } from "../../utils/cn";

type DropdownOption = {
  label: string;
  value: string;
};

type DropdownProps = {
  className?: string;
  label?: string;
  onChange: (value: string) => void;
  options: DropdownOption[];
  value: string;
  leadingIcon?: ReactNode;
};

export function Dropdown({ className, label, leadingIcon, onChange, options, value }: DropdownProps) {
  return (
    <label className={cn("grid gap-2 text-sm font-medium text-[var(--app-text)]", className)}>
      {label ? <span>{label}</span> : null}
      <span className="relative flex items-center">
        {leadingIcon ? <span className="absolute left-4 text-brand-muted">{leadingIcon}</span> : null}
        <select
          className={cn(
            "h-11 w-full appearance-none rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface-strong)] px-4 pr-10 text-[var(--app-text)] outline-none transition focus:border-brand-accent focus:ring-4 focus:ring-[var(--app-ring)]",
            leadingIcon ? "pl-10" : "",
          )}
          onChange={(event) => onChange(event.target.value)}
          value={value}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <FiChevronDown className="pointer-events-none absolute right-4 text-brand-muted" />
      </span>
    </label>
  );
}
