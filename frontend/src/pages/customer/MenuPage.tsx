import { useMemo, useState } from "react";
import { FiFilter, FiSearch } from "react-icons/fi";
import { useSearchParams } from "react-router-dom";

import { FoodGrid } from "../../components/home/FoodGrid";
import { categories } from "../../data/categories";
import { menuItems } from "../../data/menu";
import { Button, Card, Input } from "../../components/ui";
import { cn } from "../../utils/cn";

type FoodFilter = "all" | "veg" | "non-veg";
type SortOption = "popular" | "price-low" | "price-high" | "rating";

export function MenuPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialCategory = searchParams.get("category") ?? "all";
  const [categoryId, setCategoryId] = useState(initialCategory);
  const [query, setQuery] = useState("");
  const [foodFilter, setFoodFilter] = useState<FoodFilter>("all");
  const [sortOption, setSortOption] = useState<SortOption>("popular");

  const filteredFoods = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return menuItems
      .filter((food) => categoryId === "all" || food.categoryId === categoryId)
      .filter((food) => foodFilter === "all" || food.type === foodFilter)
      .filter((food) => {
        if (!normalizedQuery) {
          return true;
        }

        return [food.name, food.description, ...food.ingredients]
          .join(" ")
          .toLowerCase()
          .includes(normalizedQuery);
      })
      .toSorted((firstFood, secondFood) => {
        if (sortOption === "price-low") {
          return firstFood.price - secondFood.price;
        }

        if (sortOption === "price-high") {
          return secondFood.price - firstFood.price;
        }

        if (sortOption === "rating") {
          return secondFood.rating - firstFood.rating;
        }

        return Number(secondFood.isPopular) - Number(firstFood.isPopular) || secondFood.rating - firstFood.rating;
      });
  }, [categoryId, foodFilter, query, sortOption]);

  const selectCategory = (nextCategoryId: string) => {
    setCategoryId(nextCategoryId);
    setSearchParams(nextCategoryId === "all" ? {} : { category: nextCategoryId });
  };

  return (
    <div className="grid gap-6">
      <section className="rounded-[2rem] border border-[var(--app-border)] bg-[linear-gradient(135deg,rgba(45,33,23,0.95),rgba(126,72,31,0.88))] p-6 text-white shadow-premium sm:p-8">
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-brand-accent">DilpDa Menu</p>
        <h1 className="mt-3 text-4xl font-black leading-tight sm:text-5xl">Choose your next plate.</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-white/80">
          Filter by category, dietary preference, and appetite. Everything here is mock data until backend menus are
          connected.
        </p>
      </section>

      <div className="grid gap-5 lg:grid-cols-[18rem_1fr]">
        <Card className="h-fit bg-white/75 p-4 backdrop-blur dark:bg-white/5">
          <div className="mb-4 flex items-center gap-2 text-sm font-black uppercase tracking-[0.18em] text-brand-primary">
            <FiFilter /> Categories
          </div>
          <div className="grid gap-2">
            <button
              className={cn(
                "rounded-2xl px-4 py-3 text-left text-sm font-bold transition",
                categoryId === "all"
                  ? "bg-brand-primary text-white shadow-soft"
                  : "text-brand-muted hover:bg-brand-primary/10 hover:text-[var(--app-text)]",
              )}
              onClick={() => selectCategory("all")}
              type="button"
            >
              All Menu
            </button>
            {categories.map((category) => (
              <button
                className={cn(
                  "rounded-2xl px-4 py-3 text-left text-sm font-bold transition",
                  categoryId === category.id
                    ? "bg-brand-primary text-white shadow-soft"
                    : "text-brand-muted hover:bg-brand-primary/10 hover:text-[var(--app-text)]",
                )}
                key={category.id}
                onClick={() => selectCategory(category.id)}
                type="button"
              >
                {category.name}
              </button>
            ))}
          </div>
        </Card>

        <section className="grid gap-5">
          <Card className="grid gap-4 bg-white/75 p-4 backdrop-blur dark:bg-white/5 xl:grid-cols-[1fr_auto_auto]">
            <Input
              aria-label="Search menu"
              className="bg-[var(--app-surface-strong)]"
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search dishes, ingredients..."
              value={query}
            />
            <div className="flex flex-wrap gap-2">
              {(["all", "veg", "non-veg"] as FoodFilter[]).map((filter) => (
                <Button
                  key={filter}
                  onClick={() => setFoodFilter(filter)}
                  variant={foodFilter === filter ? "primary" : "secondary"}
                >
                  {filter === "all" ? "All" : filter === "veg" ? "Veg" : "Non Veg"}
                </Button>
              ))}
            </div>
            <label className="flex items-center gap-2 rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface-strong)] px-4">
              <FiSearch className="text-brand-primary" />
              <select
                className="h-11 bg-transparent text-sm font-semibold text-[var(--app-text)] outline-none"
                onChange={(event) => setSortOption(event.target.value as SortOption)}
                value={sortOption}
              >
                <option value="popular">Popular</option>
                <option value="rating">Top rated</option>
                <option value="price-low">Price low</option>
                <option value="price-high">Price high</option>
              </select>
            </label>
          </Card>

          {filteredFoods.length > 0 ? (
            <FoodGrid foods={filteredFoods} />
          ) : (
            <Card className="grid min-h-72 place-items-center bg-white/75 p-8 text-center backdrop-blur dark:bg-white/5">
              <div>
                <p className="text-2xl font-black text-[var(--app-text)]">No dishes found</p>
                <p className="mt-2 text-sm text-brand-muted">Try a different category, filter, or search term.</p>
              </div>
            </Card>
          )}
        </section>
      </div>
    </div>
  );
}
