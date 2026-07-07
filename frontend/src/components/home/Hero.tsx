import { motion } from "framer-motion";
import { FiArrowRight, FiClock, FiStar } from "react-icons/fi";
import { Link } from "react-router-dom";

import heroImage from "../../assets/hero.png";
import { Badge, Button } from "../ui";
import { SearchBar } from "./SearchBar";

export function Hero() {
  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-[var(--app-border)] bg-[var(--app-surface)] shadow-premium">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_20%,rgba(229,169,75,0.26),transparent_28rem),linear-gradient(135deg,rgba(45,33,23,0.94),rgba(126,72,31,0.86)_48%,rgba(255,248,242,0.18))]" />
      <div className="relative grid min-h-[560px] items-center gap-10 px-5 py-10 sm:px-8 lg:grid-cols-[1.05fr_0.95fr] lg:px-12">
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="grid gap-7"
          initial={{ opacity: 0, y: 18 }}
          transition={{ duration: 0.45 }}
        >
          <Badge tone="warning">Premium campus dining</Badge>
          <div className="grid gap-4">
            <h1 className="max-w-3xl text-4xl font-black leading-tight text-white sm:text-5xl lg:text-6xl">
              Food that arrives with a little amber glow.
            </h1>
            <p className="max-w-2xl text-base leading-7 text-brand-surface/85 sm:text-lg">
              Discover chef-picked plates, fast campus favorites, and polished comfort meals from DilpDa.
            </p>
          </div>
          <SearchBar className="max-w-2xl" />
          <div className="flex flex-wrap gap-3">
            <Link to="/app/menu">
              <Button icon={<FiArrowRight />} size="lg">
                Order now
              </Button>
            </Link>
            <div className="flex items-center gap-4 rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-sm font-semibold text-white backdrop-blur">
              <span className="flex items-center gap-2">
                <FiStar className="text-brand-accent" /> 4.8 rated
              </span>
              <span className="h-5 w-px bg-white/25" />
              <span className="flex items-center gap-2">
                <FiClock className="text-brand-accent" /> 20 min avg
              </span>
            </div>
          </div>
        </motion.div>

        <motion.div
          animate={{ opacity: 1, scale: 1 }}
          className="relative min-h-[320px]"
          initial={{ opacity: 0, scale: 0.96 }}
          transition={{ delay: 0.1, duration: 0.5 }}
        >
          <img
            alt="DilpDa premium food spread"
            className="absolute inset-0 h-full w-full rounded-[2rem] object-cover shadow-premium"
            src={heroImage}
          />
          <div className="absolute inset-0 rounded-[2rem] bg-gradient-to-t from-brand-text/35 to-transparent" />
          <div className="absolute bottom-5 left-5 right-5 rounded-2xl border border-white/25 bg-white/15 p-4 text-white shadow-soft backdrop-blur">
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-brand-accent">Tonight's pick</p>
            <p className="mt-1 text-xl font-black">Smoked Chicken Burger + Cold Brew</p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
