import { motion } from "framer-motion";

export function Loader() {
  return (
    <motion.div
      animate={{ rotate: 360 }}
      className="h-10 w-10 rounded-full border-4 border-brand-accent/20 border-t-brand-primary"
      transition={{ duration: 0.9, ease: "linear", repeat: Infinity }}
    />
  );
}
