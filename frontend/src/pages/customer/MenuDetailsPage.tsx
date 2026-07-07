import { useMemo, useState } from "react";
import { FiClock, FiMinus, FiPlus, FiShoppingBag, FiStar } from "react-icons/fi";
import { Link, useParams } from "react-router-dom";

import { Badge, Button, Card } from "../../components/ui";
import { menuItems } from "../../data/menu";

export function MenuDetailsPage() {
  const { foodId } = useParams();
  const [quantity, setQuantity] = useState(1);

  const food = useMemo(() => menuItems.find((item) => item.id === foodId), [foodId]);

  if (!food) {
    return (
      <Card className="grid min-h-96 place-items-center bg-white/75 p-8 text-center backdrop-blur dark:bg-white/5">
        <div className="grid justify-items-center gap-4">
          <p className="text-3xl font-black text-[var(--app-text)]">Dish not found</p>
          <p className="max-w-md text-sm leading-6 text-brand-muted">The selected menu item is not available in mock data.</p>
          <Link to="/app/menu">
            <Button>Back to menu</Button>
          </Link>
        </div>
      </Card>
    );
  }

  const totalPrice = food.price * quantity;

  return (
    <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-start">
      <Card className="overflow-hidden bg-white/75 backdrop-blur dark:bg-white/5">
        <img alt={food.name} className="h-[28rem] w-full object-cover" src={food.image} />
      </Card>

      <section className="grid gap-5">
        <Card className="bg-white/75 p-5 backdrop-blur dark:bg-white/5 sm:p-7">
          <div className="grid gap-5">
            <div className="flex flex-wrap items-center gap-3">
              <Badge tone={food.type === "veg" ? "success" : "danger"}>{food.type === "veg" ? "Veg" : "Non Veg"}</Badge>
              <span className="flex items-center gap-1 text-sm font-bold text-brand-muted">
                <FiStar className="text-brand-accent" /> {food.rating} ({food.reviews} reviews)
              </span>
              <span className="flex items-center gap-1 text-sm font-bold text-brand-muted">
                <FiClock className="text-brand-accent" /> {food.prepTime} min
              </span>
            </div>

            <div>
              <h1 className="text-4xl font-black leading-tight text-[var(--app-text)]">{food.name}</h1>
              <p className="mt-3 text-base leading-8 text-brand-muted">{food.description}</p>
            </div>

            <div>
              <p className="text-sm font-black uppercase tracking-[0.18em] text-brand-primary">Ingredients</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {food.ingredients.map((ingredient) => (
                  <span
                    className="rounded-full border border-[var(--app-border)] bg-[var(--app-surface-strong)] px-3 py-1 text-sm font-semibold text-brand-muted"
                    key={ingredient}
                  >
                    {ingredient}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </Card>

        <Card className="bg-white/75 p-5 backdrop-blur dark:bg-white/5 sm:p-7">
          <div className="grid gap-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-bold text-brand-muted">Price</p>
                <p className="text-3xl font-black text-brand-primary">Rs. {totalPrice}</p>
              </div>
              <div className="flex items-center gap-2 rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface-strong)] p-2">
                <Button
                  aria-label="Decrease quantity"
                  className="h-10 w-10 px-0"
                  disabled={quantity === 1}
                  icon={<FiMinus />}
                  onClick={() => setQuantity((value) => Math.max(1, value - 1))}
                  variant="secondary"
                >
                  <span className="sr-only">Decrease</span>
                </Button>
                <span className="grid h-10 w-10 place-items-center text-lg font-black text-[var(--app-text)]">{quantity}</span>
                <Button
                  aria-label="Increase quantity"
                  className="h-10 w-10 px-0"
                  icon={<FiPlus />}
                  onClick={() => setQuantity((value) => value + 1)}
                  variant="secondary"
                >
                  <span className="sr-only">Increase</span>
                </Button>
              </div>
            </div>
            <Button className="w-full" icon={<FiShoppingBag />} size="lg">
              Add to Cart
            </Button>
          </div>
        </Card>
      </section>
    </div>
  );
}
