import type { ReactNode } from "react";
import { motion } from "framer-motion";

import Logo from "../navigation/Logo";

type AuthLayoutProps = {
  title: string;
  subtitle: string;
  children: ReactNode;
};

export function AuthLayout({
  title,
  subtitle,
  children,
}: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-[var(--app-bg)]">
      <div className="grid min-h-screen lg:grid-cols-2">

        {/* Left Side */}

        <motion.div
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="
            hidden
            lg:flex
            flex-col
            justify-center
            px-20
            bg-gradient-to-br
            from-brand-primary
            via-[#8C5A2E]
            to-[#3B2616]
            text-white
          "
        >
          <Logo />

          <div className="mt-16 max-w-xl">
            <h1 className="text-5xl font-bold leading-tight">
              Campus Food,
              <br />
              Smarter Payments.
            </h1>

            <p className="mt-8 text-lg leading-8 text-white/80">
              Order food from your favourite campus restaurants,
              pay instantly or choose DilpDa Pay Later,
              and enjoy a premium food delivery experience.
            </p>

            <div className="mt-12 grid gap-5">

              <div className="rounded-2xl bg-white/10 p-5 backdrop-blur">
                🍔 Order from verified restaurants
              </div>

              <div className="rounded-2xl bg-white/10 p-5 backdrop-blur">
                💳 Buy Now Pay Later
              </div>

              <div className="rounded-2xl bg-white/10 p-5 backdrop-blur">
                🚴 Fast campus delivery
              </div>

            </div>
          </div>
        </motion.div>

        {/* Right Side */}

        <motion.div
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="
            flex
            items-center
            justify-center
            px-6
            py-12
          "
        >
          <div className="w-full max-w-lg">

            <div className="mb-8 text-center">

              <h2 className="text-4xl font-bold text-brand-primary">
                {title}
              </h2>

              <p className="mt-3 text-brand-muted">
                {subtitle}
              </p>

            </div>

            {children}

          </div>
        </motion.div>

      </div>
    </div>
  );
}