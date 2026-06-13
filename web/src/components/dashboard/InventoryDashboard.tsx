"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { fetchAlerts, fetchInventory } from "@/lib/api";
import { groupProductsByStore } from "@/lib/inventory";
import type { AgentConfig, Product } from "@/lib/types";

import { KpiStrip } from "./KpiStrip";
import { StorePanel } from "./StorePanel";
import { ErrorBanner } from "../ui/ErrorBanner";
import { LoadingSpinner } from "../ui/LoadingSpinner";

const DEFAULT_STORE_IDS = ["henderson", "las-vegas"];

interface InventoryDashboardProps {
  config: AgentConfig | null;
  refreshToken: number;
  compact?: boolean;
}

export function InventoryDashboard({
  config,
  refreshToken,
  compact = false,
}: InventoryDashboardProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [alerts, setAlerts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const loadInventory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [inventory, alertRows] = await Promise.all([
        fetchInventory(),
        fetchAlerts(),
      ]);
      setProducts(inventory);
      setAlerts(alertRows);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load inventory");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadInventory();
  }, [loadInventory, refreshToken]);

  const grouped = useMemo(() => groupProductsByStore(products), [products]);
  const storeIds = config?.store_ids ?? DEFAULT_STORE_IDS;
  const threshold = config?.low_stock_threshold ?? 10;

  return (
    <section className="flex h-full min-h-0 flex-col gap-1.5 overflow-hidden px-2 py-2 sm:gap-2 sm:px-3 sm:py-2.5">
      <div className="flex shrink-0 items-center justify-between gap-2">
        <h2 className="text-sm font-semibold text-[var(--text-primary)]">Inventory</h2>
        <button
          type="button"
          onClick={() => void loadInventory()}
          disabled={loading}
          className="rounded-md border border-[var(--border)] px-2.5 py-1 text-xs text-[var(--text-primary)] hover:border-[var(--accent)] disabled:opacity-50"
        >
          Refresh
        </button>
      </div>

      <KpiStrip
        products={products}
        alerts={alerts}
        lowStockThreshold={threshold}
        lastUpdated={lastUpdated}
        loading={loading}
      />

      {error ? <ErrorBanner message={error} title="Inventory load failed" /> : null}

      {loading && products.length === 0 ? (
        <div className="flex flex-1 items-center justify-center">
          <LoadingSpinner label="Loading inventory…" />
        </div>
      ) : (
        <div
          className={`grid min-h-0 flex-1 gap-2 overflow-y-auto sm:gap-2.5 ${
            storeIds.length > 1 ? "grid-cols-1 md:grid-cols-2" : "grid-cols-1"
          }`}
        >
          {storeIds.map((storeId) => (
            <StorePanel
              key={storeId}
              storeId={storeId}
              products={grouped.get(storeId) ?? []}
              lowStockThreshold={threshold}
              dense={compact}
            />
          ))}
        </div>
      )}
    </section>
  );
}
