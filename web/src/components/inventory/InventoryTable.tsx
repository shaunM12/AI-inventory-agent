import { groupProductsByStore, isLowStock, storeLabel } from "@/lib/inventory";
import type { Product } from "@/lib/types";

interface InventoryTableProps {
  products: Product[];
  lowStockThreshold?: number;
  compact?: boolean;
  dense?: boolean;
  title?: string;
  singleStore?: boolean;
}

export function InventoryTable({
  products,
  lowStockThreshold = 10,
  compact = false,
  dense = false,
  title,
  singleStore = false,
}: InventoryTableProps) {
  const grouped = groupProductsByStore(products);
  const storeIds = [...grouped.keys()].sort();
  const cellClass = dense
    ? "px-2 py-0.5"
    : compact
      ? "px-2 py-1"
      : "px-3 py-2";
  const textClass = dense ? "text-[11px]" : compact ? "text-[11px]" : "text-xs";

  if (products.length === 0) {
    return (
      <p className="text-xs text-[var(--text-muted)]">No inventory rows to display.</p>
    );
  }

  const renderTable = (storeId: string, rows: Product[]) => (
    <div className="overflow-x-auto">
      <table className={`w-full text-left ${textClass}`}>
        <thead>
          <tr className="border-b border-[var(--border)] text-[var(--text-muted)]">
            <th className={`${cellClass} font-medium`}>Product</th>
            <th className={`${cellClass} text-right font-medium`}>Qty</th>
            <th className={`${cellClass} font-medium`}>Unit</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((product, index) => {
            const low = isLowStock(product, lowStockThreshold);
            return (
              <tr
                key={product.product_id}
                className={
                  index % 2 === 0 ? "bg-transparent" : "bg-[var(--bg-elevated)]/30"
                }
              >
                <td className={`${cellClass} text-[var(--text-primary)]`}>
                  {product.name}
                  {low ? (
                    <span className="ml-1.5 rounded bg-[var(--danger)]/15 px-1 py-0.5 text-[10px] text-[var(--danger)]">
                      low
                    </span>
                  ) : null}
                </td>
                <td className={`${cellClass} text-right font-mono tabular-nums text-[var(--text-primary)]`}>
                  {product.quantity}
                </td>
                <td className={`${cellClass} text-[var(--text-muted)]`}>{product.unit}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );

  if (singleStore && storeIds.length === 1) {
    return (
      <div>
        {title ? (
          <p className="mb-2 text-xs font-medium text-[var(--text-muted)]">{title}</p>
        ) : null}
        {renderTable(storeIds[0], grouped.get(storeIds[0]) ?? [])}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {title ? (
        <p className="text-xs font-medium text-[var(--text-muted)]">{title}</p>
      ) : null}
      {storeIds.map((storeId) => {
        const rows = grouped.get(storeId) ?? [];
        return (
          <div
            key={storeId}
            className="overflow-hidden rounded-md border border-[var(--border)] bg-[var(--bg-app)]"
          >
            <div className="border-b border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-1.5">
              <p className="text-xs font-medium text-[var(--text-primary)]">
                {storeLabel(storeId)}
              </p>
            </div>
            {renderTable(storeId, rows)}
          </div>
        );
      })}
    </div>
  );
}
