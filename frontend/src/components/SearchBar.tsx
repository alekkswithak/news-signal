import { FormEvent, useState } from "react";

interface Props {
  onSearch: (query: string) => void;
  isSearching: boolean;
}

export function SearchBar({ onSearch, isSearching }: Props) {
  const [value, setValue] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = value.trim();
    if (trimmed) onSearch(trimmed);
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Search a topic (e.g. renewable energy)"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        aria-label="Search news"
      />
      <button type="submit" disabled={isSearching || !value.trim()}>
        {isSearching ? "Searching…" : "Search"}
      </button>
    </form>
  );
}
