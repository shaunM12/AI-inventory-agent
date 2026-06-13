import { InventoryTable } from "@/components/inventory/InventoryTable";
import { storeLabel } from "@/lib/inventory";
import type { Product } from "@/lib/types";

interface StorePanelProps {
  storeId: string;
  products: Product[];
  lowStockThreshold: number;
  dense?: boolean;
}

export function StorePanel({
  storeId,
  products,
  lowStockThreshold,
  dense = false,
}: StorePanelProps) {
  return (
    <div className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--bg-panel)]">
      <div
        className={`flex shrink-0 items-center justify-between border-b border-[var(--border)] ${
          dense ? "px-2.5 py-1.5" : "px-3 py-2"
        }`}
      >
        <div>
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            {storeLabel(storeId)}
          </h3>
          <p className="text-[11px] text-[var(--text-muted)]">
            {products.length} products
          </p>
        </div>
      </div>
      <div className={`min-h-0 overflow-x-auto ${dense ? "p-1.5" : "p-2 sm:p-2.5"}`}>
        <InventoryTable
          products={products}
          lowStockThreshold={lowStockThreshold}
          singleStore
          dense={dense}
        />
      </div>
    </div>
  );
}
