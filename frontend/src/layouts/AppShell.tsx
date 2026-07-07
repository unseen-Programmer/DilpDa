import type { ReactNode } from "react";
import { Outlet, useLocation } from "react-router-dom";

import { Footer, Navbar, Sidebar } from "../components/navigation";

type AppShellProps = {
  children?: ReactNode;
  navItems: Array<{ icon?: ReactNode; label: string; to: string }>;
  title: string;
};

export function AppShell({ children, navItems, title }: AppShellProps) {
  const location = useLocation();

  // Hide sidebar on public customer pages
  const hideSidebar =
    location.pathname === "/" ||
    location.pathname === "/menu" ||
    location.pathname === "/search" ||
    location.pathname.startsWith("/menu/");

  return (
    <div className="min-h-screen bg-[var(--app-bg)] text-[var(--app-text)]">
      <Navbar />

      <div
        className={
          hideSidebar
            ? "pt-24"
            : "mx-auto flex max-w-7xl pt-24"
        }
      >
        {!hideSidebar && (
          <Sidebar items={navItems} title={title} />
        )}

        <main
          className={
            hideSidebar
              ? "w-full"
              : "min-h-[calc(100vh-96px)] flex-1 px-4 pb-8 sm:px-6 lg:px-8"
          }
        >
          {children ?? <Outlet />}
        </main>
      </div>

      <Footer />
    </div>
  );
}