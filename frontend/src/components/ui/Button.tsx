import type { ButtonHTMLAttributes, ReactNode } from "react";
import { FiLoader } from "react-icons/fi";

import { cn } from "../../utils/cn";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  icon?: ReactNode;
  isLoading?: boolean;
  variant?: ButtonVariant;
  size?: ButtonSize;
};

const variantClasses: Record<ButtonVariant, string> = {
  primary: "bg-brand-primary text-white shadow-soft hover:bg-brand-secondary",
  secondary: "bg-brand-surface text-brand-text ring-1 ring-[var(--app-border)] hover:bg-white",
  ghost: "bg-transparent text-[var(--app-text)] hover:bg-brand-primary/10",
  danger: "bg-brand-danger text-white shadow-soft hover:bg-red-700",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-11 px-4 text-sm",
  lg: "h-12 px-5 text-base",
};

export function Button({
  children,
  className,
  disabled,
  icon,
  isLoading = false,
  size = "md",
  type = "button",
  variant = "primary",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-2xl font-semibold transition duration-200 focus:outline-none focus:ring-4 focus:ring-[var(--app-ring)] disabled:cursor-not-allowed disabled:opacity-60",
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
      disabled={disabled || isLoading}
      type={type}
      {...props}
    >
      {isLoading ? <FiLoader className="h-4 w-4 animate-spin" /> : icon}
      <span>{children}</span>
    </button>
  );
}
