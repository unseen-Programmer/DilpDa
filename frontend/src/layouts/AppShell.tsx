import type { ReactNode } from "react";
import { Outlet } from "react-router-dom";

import { Footer, Navbar, Sidebar } from "../components/navigation";

type AppShellProps = {
  children?: ReactNode;
  navItems: Array<{ icon?: ReactNode; label: string; to: string }>;
  title: string;
};

export function AppShell({ children, navItems, title }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[var(--app-bg)] text-[var(--app-text)]">
      <Navbar />
      <div className="mx-auto flex max-w-7xl">
        <Sidebar items={navItems} title={title} />
        <main className="min-h-[calc(100vh-73px)] flex-1 px-4 py-6 sm:px-6 lg:px-8">
          {children ?? <Outlet />}
        </main>
      </div>
      <Footer />
    </div>
  );
}
