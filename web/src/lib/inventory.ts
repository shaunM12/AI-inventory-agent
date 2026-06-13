import { STORE_LABELS } from "./constants";
import type { Product } from "./types";

export function storeLabel(storeId: string): string {
  return STORE_LABELS[storeId] ?? storeId;
}

export function groupProductsByStore(products: Product[]): Map<string, Product[]> {
  const grouped = new Map<string, Product[]>();
  for (const product of products) {
    const rows = grouped.get(product.store_id) ?? [];
    rows.push(product);
    grouped.set(product.store_id, rows);
  }

  for (const [storeId, rows] of grouped.entries()) {
    grouped.set(
      storeId,
      [...rows].sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: "base" })),
    );
  }

  return grouped;
}

export function isLowStock(product: Product, threshold: number): boolean {
  return product.quantity < threshold;
}
