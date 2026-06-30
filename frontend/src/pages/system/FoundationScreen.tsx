import { motion } from "framer-motion";
import { FiArrowRight, FiShield } from "react-icons/fi";
import { Link } from "react-router-dom";

import { Badge, Button, Card } from "../../components/ui";
import { ThemeToggle } from "../../components/navigation";

export function FoundationScreen() {
  return (
    <main className="grid min-h-screen place-items-center px-4 py-10">
      <section className="w-full max-w-5xl">
        <div className="mb-8 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="grid h-12 w-12 place-items-center rounded-2xl bg-brand-primary text-xl font-black text-white shadow-soft">
              D
            </span>
            <div>
              <p className="text-xl font-black text-[var(--app-text)]">DilpDa</p>
              <p className="text-sm font-medium text-brand-muted">Frontend foundation</p>
            </div>
          </div>
          <ThemeToggle />
        </div>

        <motion.div
          animate={{ opacity: 1, y: 0 }}
          initial={{ opacity: 0, y: 12 }}
          transition={{ duration: 0.32 }}
        >
          <Card className="overflow-hidden">
            <div className="grid gap-8 p-6 md:grid-cols-[1.1fr_0.9fr] md:p-10">
              <div className="flex flex-col justify-center gap-6">
                <Badge tone="warning">Premium whiskey theme</Badge>
                <div className="grid gap-4">
                  <h1 className="max-w-2xl text-4xl font-black leading-tight text-[var(--app-text)] md:text-6xl">
                    A polished shell for DilpDa’s next chapter.
                  </h1>
                  <p className="max-w-xl text-base leading-7 text-brand-muted">
                    Routing, roles, state, API plumbing, dark mode, motion, and reusable components are ready.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <Link to="/loading">
                    <Button icon={<FiArrowRight />}>Preview loading</Button>
                  </Link>
                  <Link to="/404">
                    <Button icon={<FiShield />} variant="secondary">
                      Preview 404
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="rounded-3xl border border-[var(--app-border)] bg-white/45 p-5 shadow-soft backdrop-blur dark:bg-white/5">
                <div className="grid gap-4">
                  {["React 19", "Redux Toolkit", "React Router", "Tailwind CSS"].map((item) => (
                    <div
                      className="flex items-center justify-between rounded-2xl bg-[var(--app-surface-strong)] px-4 py-3"
                      key={item}
                    >
                      <span className="font-semibold text-[var(--app-text)]">{item}</span>
                      <Badge tone="success">Ready</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </section>
    </main>
  );
}
