import type { Product } from "@/lib/types";

interface KpiStripProps {
  products: Product[];
  alerts: Product[];
  lowStockThreshold: number;
  lastUpdated: string | null;
  loading: boolean;
}

export function KpiStrip({
  products,
  alerts,
  lowStockThreshold,
  lastUpdated,
  loading,
}: KpiStripProps) {
  const henderson = products.filter((p) => p.store_id === "henderson").length;
  const lasVegas = products.filter((p) => p.store_id === "las-vegas").length;

  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-2 text-xs text-[var(--text-muted)] sm:gap-x-5 sm:gap-y-1">
      <span>
        <strong className="font-mono text-[var(--text-primary)]">{products.length}</strong>{" "}
        SKUs
      </span>
      <span>
        <strong className="font-mono text-[var(--danger)]">{alerts.length}</strong> low stock
      </span>
      <span>
        Henderson{" "}
        <strong className="font-mono text-[var(--text-primary)]">{henderson}</strong>
      </span>
      <span>
        Las Vegas{" "}
        <strong className="font-mono text-[var(--text-primary)]">{lasVegas}</strong>
      </span>
      <span>
        Alert threshold{" "}
        <strong className="font-mono text-[var(--text-primary)]">&lt; {lowStockThreshold}</strong>
      </span>
      <span className="w-full font-mono sm:ml-auto sm:w-auto">
        {loading ? "Refreshing…" : lastUpdated ? `Updated ${lastUpdated}` : ""}
      </span>
    </div>
  );
}
