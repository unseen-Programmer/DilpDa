import { customerNavItems } from "../config/navigation";
import { AppShell } from "./AppShell";

export function CustomerLayout() {
  return <AppShell navItems={customerNavItems} title="Customer" />;
}
