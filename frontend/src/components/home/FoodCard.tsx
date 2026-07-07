import { motion } from "framer-motion";
import { FiClock, FiPlus, FiStar } from "react-icons/fi";
import { Link } from "react-router-dom";

import type { FoodItem } from "../../data/menu";
import { Badge, Button, Card } from "../ui";

type FoodCardProps = {
  food: FoodItem;
};

export function FoodCard({ food }: FoodCardProps) {
  return (
    <motion.div whileHover={{ y: -6 }} transition={{ duration: 0.2 }}>
      <Card className="group h-full overflow-hidden bg-white/75 backdrop-blur dark:bg-white/5">
        <Link to={`/app/menu/${food.id}`}>
          <div className="relative h-48 overflow-hidden">
            <img
              alt={food.name}
              className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
              src={food.image}
            />
            <div className="absolute left-4 top-4">
              <Badge tone={food.type === "veg" ? "success" : "danger"}>{food.type === "veg" ? "Veg" : "Non Veg"}</Badge>
            </div>
          </div>
        </Link>
        <div className="grid gap-4 p-4">
          <div className="grid gap-2">
            <div className="flex items-start justify-between gap-3">
              <Link className="min-w-0" to={`/app/menu/${food.id}`}>
                <h3 className="line-clamp-2 text-lg font-black text-[var(--app-text)]">{food.name}</h3>
              </Link>
              <p className="shrink-0 text-lg font-black text-brand-primary">Rs. {food.price}</p>
            </div>
            <p className="line-clamp-2 text-sm leading-6 text-brand-muted">{food.description}</p>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3 text-sm font-semibold text-brand-muted">
            <span className="flex items-center gap-1">
              <FiStar className="text-brand-accent" /> {food.rating}
            </span>
            <span className="flex items-center gap-1">
              <FiClock className="text-brand-accent" /> {food.prepTime} min
            </span>
            <Button className="h-10 px-3" icon={<FiPlus />} size="sm">
              Add
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
