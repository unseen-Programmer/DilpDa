import { motion } from "framer-motion";
import { FiArrowRight } from "react-icons/fi";
import { Link } from "react-router-dom";

import { offers } from "../../data/offers";
import { Button } from "../ui";

export function OfferBanner() {
  return (
    <section className="grid gap-5">
      <div>
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-brand-primary">Featured Offers</p>
        <h2 className="text-3xl font-black text-[var(--app-text)]">Whiskey-glow deals</h2>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {offers.map((offer, index) => (
          <motion.article
            animate={{ opacity: 1, y: 0 }}
            className="relative overflow-hidden rounded-2xl border border-white/20 bg-[linear-gradient(135deg,#2d2117,#7e481f_55%,#e5a94b)] p-5 text-white shadow-premium"
            initial={{ opacity: 0, y: 14 }}
            key={offer.id}
            transition={{ delay: index * 0.08, duration: 0.35 }}
          >
            <div className="absolute -right-8 -top-8 h-28 w-28 rounded-full bg-white/15 blur-2xl" />
            <div className="relative grid min-h-52 content-between gap-6">
              <div className="grid gap-3">
                <span className="w-fit rounded-full bg-white px-3 py-1 text-xs font-black text-brand-primary">
                  {offer.badge}
                </span>
                <div>
                  <h3 className="text-2xl font-black">{offer.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-white/82">{offer.description}</p>
                </div>
              </div>
              <Link to="/app/menu">
                <Button className="bg-white text-brand-primary hover:bg-brand-surface" icon={<FiArrowRight />}>
                  Claim offer
                </Button>
              </Link>
            </div>
          </motion.article>
        ))}
      </div>
    </section>
  );
}
