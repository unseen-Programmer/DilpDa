import type { FoodItem } from "../../data/menu";
import { FoodCard } from "./FoodCard";

type FoodGridProps = {
  foods: FoodItem[];
};

export function FoodGrid({ foods }: FoodGridProps) {
  return (
    <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
      {foods.map((food) => (
        <FoodCard food={food} key={food.id} />
      ))}
    </div>
  );
}
