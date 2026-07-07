import { categories } from "../../data/categories";
import { CategoryCard } from "./CategoryCard";

export function CategoryGrid() {
  return (
    <section className="grid gap-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-brand-primary">Categories</p>
          <h2 className="text-3xl font-black text-[var(--app-text)]">Browse by craving</h2>
        </div>
        <p className="max-w-xl text-sm leading-6 text-brand-muted">
          Breakfast through dessert, curated for fast campus ordering.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {categories.map((category) => (
          <CategoryCard category={category} key={category.id} />
        ))}
      </div>
    </section>
  );
}
