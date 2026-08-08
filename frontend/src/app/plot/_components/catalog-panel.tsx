"use client";

import { memo, use, useCallback, useMemo, useState, useTransition } from "react";
import { Suspense } from "react";
import type { CatalogItem } from "@/lib/services/plot-catalog";

interface CatalogItemCardProps {
  item: CatalogItem;
  selected: boolean;
  onSelect: (item: CatalogItem) => void;
}

const CatalogItemCard = memo(function CatalogItemCard({ item, selected, onSelect }: CatalogItemCardProps) {
  const handleClick = useCallback(() => onSelect(item), [item, onSelect]);
  return (
    <button
      onClick={handleClick}
      className={[
        "w-full flex items-center gap-2 px-2 py-1.5 text-left rounded-md border cursor-pointer transition-colors",
        selected
          ? "bg-primary text-primary-foreground border-primary"
          : "bg-secondary text-secondary-foreground border-border hover:bg-accent hover:text-accent-foreground",
      ].join(" ")}
    >
      <span className="w-3 h-3 rounded-sm shrink-0 border border-black/10" style={{ backgroundColor: item.default_color }} />
      <span className="flex-1 min-w-0">
        <span className="block text-xs font-medium truncate">{item.name}</span>
        <span className="block text-[10px] opacity-70 truncate">
          {item.width}×{item.height}×{item.depth} · {item.category}
        </span>
      </span>
    </button>
  );
});

function CatalogPanelSkeleton() {
  return (
    <div className="flex flex-col gap-1.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="h-9 rounded-md bg-muted animate-pulse" />
      ))}
    </div>
  );
}

interface CatalogListProps {
  promise: Promise<CatalogItem[]>;
  selectedId?: string;
  onSelect: (item: CatalogItem) => void;
}

function CatalogList({ promise, selectedId, onSelect }: CatalogListProps) {
  const items = use(promise);
  const [query, setQuery] = useState("");
  const [isPending, startTransition] = useTransition();

  const handleQueryChange = useCallback((v: string) => {
    startTransition(() => setQuery(v));
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter(i => i.name.toLowerCase().includes(q) || i.category.toLowerCase().includes(q));
  }, [items, query]);

  return (
    <div className="flex flex-col gap-2">
      <input
        defaultValue={query}
        onChange={(e) => handleQueryChange(e.target.value)}
        placeholder="Search furniture…"
        className="w-full px-2 py-1 text-xs bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
      />
      <div className={["flex flex-col gap-1.5 overflow-y-auto max-h-64 transition-opacity", isPending ? "opacity-60" : ""].join(" ")}>
        {filtered.length === 0 && (
          <span className="text-[11px] text-muted-foreground text-center py-2">No items found</span>
        )}
        {filtered.map(item => (
          <CatalogItemCard key={item.id} item={item} selected={item.id === selectedId} onSelect={onSelect} />
        ))}
      </div>
    </div>
  );
}

interface CatalogPanelProps {
  catalogPromise: Promise<CatalogItem[]>;
  selectedId?: string;
  onSelect: (item: CatalogItem) => void;
}

export function CatalogPanel({ catalogPromise, selectedId, onSelect }: CatalogPanelProps) {
  return (
    <div className="absolute top-3 right-3 z-10 bg-card rounded-xl shadow-lg p-3.5 w-56 flex flex-col gap-2 border border-border">
      <h3 className="text-xs font-semibold text-card-foreground">🛋️ Furniture Catalog</h3>
      <Suspense fallback={<CatalogPanelSkeleton />}>
        <CatalogList promise={catalogPromise} selectedId={selectedId} onSelect={onSelect} />
      </Suspense>
    </div>
  );
}
