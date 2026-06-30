import { AnimatePresence, motion } from "framer-motion";
import type { ReactNode } from "react";
import { FiX } from "react-icons/fi";

import { Button } from "./Button";

type ModalProps = {
  children: ReactNode;
  isOpen: boolean;
  onClose: () => void;
  title: string;
};

export function Modal({ children, isOpen, onClose, title }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen ? (
        <motion.div
          animate={{ opacity: 1 }}
          className="fixed inset-0 z-50 grid place-items-center bg-black/45 p-4 backdrop-blur-sm"
          exit={{ opacity: 0 }}
          initial={{ opacity: 0 }}
        >
          <motion.section
            animate={{ y: 0, scale: 1 }}
            className="w-full max-w-lg rounded-3xl border border-[var(--app-border)] bg-[var(--app-surface)] p-5 shadow-premium"
            exit={{ y: 16, scale: 0.98 }}
            initial={{ y: 16, scale: 0.98 }}
            transition={{ duration: 0.18 }}
          >
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-[var(--app-text)]">{title}</h2>
              <Button aria-label="Close modal" onClick={onClose} size="sm" variant="ghost">
                <FiX />
              </Button>
            </div>
            {children}
          </motion.section>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
