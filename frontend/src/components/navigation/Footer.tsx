import { env } from "../../config/env";

export function Footer() {
  return (
    <footer className="border-t border-[var(--app-border)] px-4 py-6 text-sm text-brand-muted sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <span>{env.appName}</span>
        <span>Premium food ordering, built with care.</span>
      </div>
    </footer>
  );
}

export default Footer;