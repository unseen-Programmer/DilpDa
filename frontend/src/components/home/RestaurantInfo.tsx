import { FiAward, FiShoppingBag, FiUsers } from "react-icons/fi";

import { Card } from "../ui";

const stats = [
  { icon: FiUsers, label: "Customers served", value: "18K+" },
  { icon: FiShoppingBag, label: "Orders completed", value: "72K+" },
  { icon: FiAward, label: "Years serving", value: "6" },
];

export function RestaurantInfo() {
  return (
    <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
      <div className="grid gap-4">
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-brand-primary">About DilpDa</p>
        <h2 className="text-3xl font-black leading-tight text-[var(--app-text)] sm:text-4xl">
          Campus comfort with a premium pour of hospitality.
        </h2>
        <p className="text-base leading-8 text-brand-muted">
          DilpDa began as a small campus counter and grew into a polished food ordering experience for busy students,
          faculty, and late-night project crews. The kitchen still moves with the same care: generous portions, warm
          service, and flavors that feel familiar without feeling ordinary.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        {stats.map((stat) => {
          const Icon = stat.icon;

          return (
            <Card className="bg-white/75 p-5 backdrop-blur dark:bg-white/5" key={stat.label}>
              <div className="grid gap-4">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-brand-primary text-white shadow-soft">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-3xl font-black text-[var(--app-text)]">{stat.value}</p>
                  <p className="mt-1 text-sm font-semibold text-brand-muted">{stat.label}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
