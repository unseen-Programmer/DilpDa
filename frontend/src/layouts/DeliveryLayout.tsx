import { deliveryNavItems } from "../config/navigation";
import { AppShell } from "./AppShell";

export function DeliveryLayout() {
  return <AppShell navItems={deliveryNavItems} title="Delivery" />;
}
