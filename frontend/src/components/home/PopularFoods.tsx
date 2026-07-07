import { Link } from "react-router-dom";

import { menuItems } from "../../data/menu";
import { Button } from "../ui";
import { FoodGrid } from "./FoodGrid";

export function PopularFoods() {
  const popularFoods = menuItems.filter((food) => food.isPopular).slice(0, 6);

  return (
    <section className="grid gap-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-brand-primary">Popular Foods</p>
          <h2 className="text-3xl font-black text-[var(--app-text)]">Campus favorites</h2>
        </div>
        <Link to="/app/menu">
          <Button variant="secondary">View menu</Button>
        </Link>
      </div>
      <FoodGrid foods={popularFoods} />
    </section>
  );
}
