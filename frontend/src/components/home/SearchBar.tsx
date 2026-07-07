import { useState } from "react";
import type { FormEvent } from "react";
import { FiSearch } from "react-icons/fi";
import { useNavigate } from "react-router-dom";

import { Button, Input } from "../ui";

type SearchBarProps = {
  className?: string;
  initialValue?: string;
  onSearch?: (query: string) => void;
  placeholder?: string;
};

export function SearchBar({
  className = "",
  initialValue = "",
  onSearch,
  placeholder = "Search biryani, burgers, coffee...",
}: SearchBarProps) {
  const [query, setQuery] = useState(initialValue);
  const navigate = useNavigate();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedQuery = query.trim();

    if (onSearch) {
      onSearch(trimmedQuery);
      return;
    }

    navigate(trimmedQuery ? `/app/search?q=${encodeURIComponent(trimmedQuery)}` : "/app/search");
  };

  return (
    <form
      className={`flex w-full flex-col gap-3 rounded-2xl border border-white/30 bg-white/70 p-2 shadow-soft backdrop-blur dark:border-white/10 dark:bg-white/10 sm:flex-row ${className}`}
      onSubmit={handleSubmit}
    >
      <Input
        aria-label="Search food"
        className="h-12 border-transparent bg-transparent focus:border-brand-accent"
        onChange={(event) => setQuery(event.target.value)}
        placeholder={placeholder}
        value={query}
      />
      <Button className="h-12 shrink-0" icon={<FiSearch />} type="submit">
        Search
      </Button>
    </form>
  );
}
