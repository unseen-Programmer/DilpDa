import { adminNavItems } from "../config/navigation";
import { AppShell } from "./AppShell";

export function AdminLayout() {
  return <AppShell navItems={adminNavItems} title="Admin" />;
}
