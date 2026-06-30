import { restaurantOwnerNavItems } from "../config/navigation";
import { AppShell } from "./AppShell";

export function RestaurantOwnerLayout() {
  return <AppShell navItems={restaurantOwnerNavItems} title="Restaurant" />;
}
