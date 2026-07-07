import {
  FiCoffee,
  FiDribbble,
  FiMoon,
  FiPackage,
  FiSun,
  FiSunrise,
  FiZap,
} from "react-icons/fi";
import type { IconType } from "react-icons";

export type Category = {
  description: string;
  icon: IconType;
  id: string;
  image: string;
  name: string;
};

export const categories: Category[] = [
  {
    id: "breakfast",
    name: "Breakfast",
    description: "Warm starts, crisp bites, and fresh pours.",
    icon: FiSunrise,
    image: "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "lunch",
    name: "Lunch",
    description: "Balanced plates for the long middle of the day.",
    icon: FiSun,
    image: "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "dinner",
    name: "Dinner",
    description: "Slow-cooked comfort with a polished finish.",
    icon: FiMoon,
    image: "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "fast-food",
    name: "Fast Food",
    description: "Bold, quick, and built for cravings.",
    icon: FiZap,
    image: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "beverages",
    name: "Beverages",
    description: "Coolers, shakes, brews, and campus classics.",
    icon: FiCoffee,
    image: "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "snacks",
    name: "Snacks",
    description: "Small plates that keep the table moving.",
    icon: FiPackage,
    image: "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "desserts",
    name: "Desserts",
    description: "Sweet finales with a little ceremony.",
    icon: FiDribbble,
    image: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=900&q=80",
  },
];
