export type Offer = {
  badge: string;
  description: string;
  id: string;
  title: string;
};

export const offers: Offer[] = [
  {
    id: "amber-combo",
    badge: "25% OFF",
    title: "Amber Hour Combos",
    description: "Pair any popular main with fries or cold brew and save on the full plate.",
  },
  {
    id: "late-night",
    badge: "FREE DRINK",
    title: "Late Night Ritual",
    description: "Order after 8 PM and get a chilled beverage with selected dinner plates.",
  },
  {
    id: "dessert-finish",
    badge: "BUY 2",
    title: "Sweet Finish",
    description: "Add two desserts to any order and get the lower priced one on the house.",
  },
];
