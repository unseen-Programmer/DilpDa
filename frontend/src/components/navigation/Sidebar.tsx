import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { cn } from "../../utils/cn";

type SidebarItem = {
  icon?: ReactNode;
  label: string;
  to: string;
};

type SidebarProps = {
  items: SidebarItem[];
  title: string;
};

export function Sidebar({ items, title }: SidebarProps) {
  return (
    <aside className="hidden min-h-[calc(100vh-73px)] w-72 border-r border-[var(--app-border)] bg-[var(--app-surface)]/80 p-4 backdrop-blur lg:block">
      <p className="px-3 pb-4 text-xs font-bold uppercase tracking-[0.2em] text-brand-muted">{title}</p>
      <nav className="grid gap-1">
        {items.map((item) => (
          <NavLink
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-semibold text-brand-muted transition hover:bg-brand-primary/10 hover:text-[var(--app-text)]",
                isActive ? "bg-brand-primary text-white hover:bg-brand-primary hover:text-white" : "",
              )
            }
            key={item.to}
            to={item.to}
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
