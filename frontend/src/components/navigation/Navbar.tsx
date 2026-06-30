import { FiBell, FiShoppingBag } from "react-icons/fi";
import { Link } from "react-router-dom";

import { env } from "../../config/env";
import { useAppSelector } from "../../store/hooks";
import { Avatar, Badge, Button } from "../ui";
import { ThemeToggle } from "./ThemeToggle";

export function Navbar() {
  const cartItems = useAppSelector((state) => state.cart.itemCount);
  const unreadCount = useAppSelector((state) => state.notification.unreadCount);
  const profile = useAppSelector((state) => state.user.profile);

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--app-border)] bg-[var(--app-surface)]/85 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link className="flex items-center gap-3" to="/">
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-brand-primary text-lg font-black text-white shadow-soft">
            D
          </span>
          <span className="text-lg font-black tracking-wide text-[var(--app-text)]">{env.appName}</span>
        </Link>
        <div className="flex items-center gap-2">
          <Button icon={<FiShoppingBag />} size="sm" variant="ghost">
            Cart
          </Button>
          {cartItems > 0 ? <Badge>{cartItems}</Badge> : null}
          <Button icon={<FiBell />} size="sm" variant="ghost">
            Alerts
          </Button>
          {unreadCount > 0 ? <Badge tone="warning">{unreadCount}</Badge> : null}
          <ThemeToggle />
          <Avatar initials={profile?.email?.slice(0, 1).toUpperCase() ?? "D"} />
        </div>
      </div>
    </header>
  );
}
