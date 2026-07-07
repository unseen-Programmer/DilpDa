import { motion } from "framer-motion";
import { Link } from "react-router-dom";

import type { Category } from "../../data/categories";
import { Card } from "../ui";

type CategoryCardProps = {
  category: Category;
};

export function CategoryCard({ category }: CategoryCardProps) {
  const Icon = category.icon;

  return (
    <motion.div whileHover={{ y: -6 }} transition={{ duration: 0.2 }}>
      <Link to={`/app/menu?category=${category.id}`}>
        <Card className="group overflow-hidden bg-white/70 backdrop-blur dark:bg-white/5">
          <div className="relative h-36 overflow-hidden">
            <img
              alt={category.name}
              className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
              src={category.image}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-brand-text/75 to-transparent" />
            <div className="absolute bottom-4 left-4 grid h-12 w-12 place-items-center rounded-2xl bg-brand-accent text-brand-text shadow-soft">
              <Icon className="h-5 w-5" />
            </div>
          </div>
          <div className="grid gap-2 p-4">
            <h3 className="text-lg font-black text-[var(--app-text)]">{category.name}</h3>
            <p className="text-sm leading-6 text-brand-muted">{category.description}</p>
          </div>
        </Card>
      </Link>
    </motion.div>
  );
}
