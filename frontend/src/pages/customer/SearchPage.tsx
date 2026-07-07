import { useMemo, useState } from "react";
import { FiSearch } from "react-icons/fi";
import { useSearchParams } from "react-router-dom";

import { FoodGrid } from "../../components/home/FoodGrid";
import { categories } from "../../data/categories";
import { menuItems } from "../../data/menu";
import { Button, Card, Input } from "../../components/ui";

export function SearchPage() {
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [activeCategory, setActiveCategory] = useState("all");

  const results = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return menuItems.filter((food) => {
      const matchesCategory = activeCategory === "all" || food.categoryId === activeCategory;
      const matchesQuery =
        !normalizedQuery ||
        [food.name, food.description, food.type, ...food.ingredients].join(" ").toLowerCase().includes(normalizedQuery);

      return matchesCategory && matchesQuery;
    });
  }, [activeCategory, query]);

  return (
    <div className="grid gap-6">
      <Card className="bg-white/75 p-5 shadow-premium backdrop-blur dark:bg-white/5 sm:p-7">
        <div className="grid gap-5">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-brand-primary">Search</p>
            <h1 className="mt-2 text-4xl font-black text-[var(--app-text)]">Find your DilpDa favorite.</h1>
          </div>
          <Input
            aria-label="Live search foods"
            className="h-14 text-base"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Type a dish, ingredient, or preference..."
            value={query}
          />
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => setActiveCategory("all")} variant={activeCategory === "all" ? "primary" : "secondary"}>
              All
            </Button>
            {categories.map((category) => (
              <Button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                variant={activeCategory === category.id ? "primary" : "secondary"}
              >
                {category.name}
              </Button>
            ))}
          </div>
        </div>
      </Card>

      {results.length > 0 ? (
        <FoodGrid foods={results} />
      ) : (
        <Card className="grid min-h-96 place-items-center bg-white/75 p-8 text-center backdrop-blur dark:bg-white/5">
          <div className="grid justify-items-center gap-3">
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-primary/10 text-brand-primary">
              <FiSearch className="h-6 w-6" />
            </div>
            <p className="text-2xl font-black text-[var(--app-text)]">No result found</p>
            <p className="max-w-md text-sm leading-6 text-brand-muted">
              Try another dish name, ingredient, or category filter.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
