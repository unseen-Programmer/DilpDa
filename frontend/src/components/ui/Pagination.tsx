import { FiChevronLeft, FiChevronRight } from "react-icons/fi";

import { Button } from "./Button";

type PaginationProps = {
  currentPage: number;
  onPageChange: (page: number) => void;
  totalPages: number;
};

export function Pagination({ currentPage, onPageChange, totalPages }: PaginationProps) {
  return (
    <nav className="flex items-center justify-between gap-3" aria-label="Pagination">
      <Button
        disabled={currentPage <= 1}
        icon={<FiChevronLeft />}
        onClick={() => onPageChange(currentPage - 1)}
        variant="secondary"
      >
        Previous
      </Button>
      <span className="text-sm font-semibold text-brand-muted">
        Page {currentPage} of {Math.max(totalPages, 1)}
      </span>
      <Button
        disabled={currentPage >= totalPages}
        icon={<FiChevronRight />}
        onClick={() => onPageChange(currentPage + 1)}
        variant="secondary"
      >
        Next
      </Button>
    </nav>
  );
}
