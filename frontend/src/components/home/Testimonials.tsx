import { useMemo, useState } from "react";
import { FiChevronLeft, FiChevronRight, FiStar } from "react-icons/fi";
import { motion } from "framer-motion";

import { Avatar, Button, Card } from "../ui";

const testimonials = [
  {
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80",
    name: "Ananya Rao",
    rating: 5,
    review: "The food feels restaurant-grade but still arrives fast enough between classes. The paneer bowl is my default.",
  },
  {
    avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80",
    name: "Kabir Sen",
    rating: 5,
    review: "Late-night orders are smooth, warm, and reliably packed. DilpDa has become our study group ritual.",
  },
  {
    avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=200&q=80",
    name: "Meera Iyer",
    rating: 4,
    review: "The offers are actually useful and the menu is easy to scan. Desserts are dangerously good.",
  },
];

export function Testimonials() {
  const [activeIndex, setActiveIndex] = useState(0);
  const active = testimonials[activeIndex];
  const stars = useMemo(() => Array.from({ length: active.rating }), [active.rating]);

  const goToPrevious = () => setActiveIndex((index) => (index === 0 ? testimonials.length - 1 : index - 1));
  const goToNext = () => setActiveIndex((index) => (index === testimonials.length - 1 ? 0 : index + 1));

  return (
    <section className="grid gap-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-brand-primary">Testimonials</p>
          <h2 className="text-3xl font-black text-[var(--app-text)]">What customers say</h2>
        </div>
        <div className="flex gap-2">
          <Button aria-label="Previous testimonial" icon={<FiChevronLeft />} onClick={goToPrevious} variant="secondary">
            Prev
          </Button>
          <Button aria-label="Next testimonial" icon={<FiChevronRight />} onClick={goToNext} variant="secondary">
            Next
          </Button>
        </div>
      </div>
      <Card className="overflow-hidden bg-white/75 p-5 backdrop-blur dark:bg-white/5 sm:p-7">
        <motion.div
          animate={{ opacity: 1, x: 0 }}
          className="grid gap-5"
          initial={{ opacity: 0, x: 18 }}
          key={active.name}
          transition={{ duration: 0.25 }}
        >
          <div className="flex items-center gap-4">
            <Avatar alt={active.name} src={active.avatar} />
            <div>
              <p className="font-black text-[var(--app-text)]">{active.name}</p>
              <div className="mt-1 flex text-brand-accent">
                {stars.map((_, index) => (
                  <FiStar fill="currentColor" key={index} />
                ))}
              </div>
            </div>
          </div>
          <p className="text-xl font-semibold leading-9 text-[var(--app-text)]">"{active.review}"</p>
          <div className="flex gap-2">
            {testimonials.map((testimonial, index) => (
              <button
                aria-label={`Show ${testimonial.name} testimonial`}
                className={`h-2 rounded-full transition-all ${
                  index === activeIndex ? "w-8 bg-brand-primary" : "w-2 bg-brand-primary/25"
                }`}
                key={testimonial.name}
                onClick={() => setActiveIndex(index)}
                type="button"
              />
            ))}
          </div>
        </motion.div>
      </Card>
    </section>
  );
}
