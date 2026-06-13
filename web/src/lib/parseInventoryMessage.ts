import type { Product } from "./types";

function isProduct(value: unknown): value is Product {
  if (!value || typeof value !== "object") {
    return false;
  }
  const row = value as Record<string, unknown>;
  return (
    typeof row.product_id === "string" &&
    typeof row.store_id === "string" &&
    typeof row.name === "string" &&
    typeof row.quantity === "number" &&
    typeof row.unit === "string"
  );
}

export function parseProductList(content: string): Product[] | null {
  const trimmed = content.trim();
  if (!trimmed.startsWith("[") && !trimmed.startsWith("{")) {
    return null;
  }

  try {
    const data = JSON.parse(trimmed) as unknown;
    if (Array.isArray(data)) {
      if (data.length === 0) {
        return [];
      }
      return data.every(isProduct) ? data : null;
    }
    if (isProduct(data)) {
      return [data];
    }
    if (data && typeof data === "object") {
      const record = data as Record<string, unknown>;
      const products: Product[] = [];
      if (isProduct(record.source_product)) {
        products.push(record.source_product);
      }
      if (isProduct(record.destination_product)) {
        products.push(record.destination_product);
      }
      if (products.length > 0) {
        return products;
      }
    }
  } catch {
    return null;
  }

  return null;
}

export function parseAsciiInventoryTable(content: string): Product[] | null {
  if (!content.includes("=== store_id:")) {
    return null;
  }

  const products: Product[] = [];
  let currentStore = "";

  for (const line of content.split("\n")) {
    const storeMatch = line.match(/^=== store_id:\s*(\S+)/);
    if (storeMatch) {
      currentStore = storeMatch[1];
      continue;
    }

    if (!currentStore || line.includes("Name") && line.includes("Quantity")) {
      continue;
    }

    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }

    const match = trimmed.match(/^(.+?)\s+(\d+)\s+(\S+)\s*$/);
    if (!match) {
      continue;
    }

    products.push({
      product_id: `${currentStore}-${match[1].trim()}`,
      store_id: currentStore,
      name: match[1].trim(),
      quantity: Number(match[2]),
      unit: match[3],
      created_at: "",
      updated_at: "",
    });
  }

  return products.length > 0 ? products : null;
}

export function extractInventoryProducts(
  content: string,
  toolCall?: string,
): Product[] | null {
  if (toolCall === "list_stores") {
    return null;
  }

  return parseProductList(content) ?? parseAsciiInventoryTable(content);
}

export function parseStoreList(content: string): string[] | null {
  try {
    const data = JSON.parse(content) as unknown;
    if (!Array.isArray(data)) {
      return null;
    }
    const ids = data
      .map((item) =>
        item && typeof item === "object" && "store_id" in item
          ? String((item as { store_id: string }).store_id)
          : null,
      )
      .filter((id): id is string => Boolean(id));
    return ids.length > 0 ? ids : null;
  } catch {
    return null;
  }
}

export function formatToolSummary(toolCall: string, content: string): string | null {
  try {
    const args = JSON.parse(content) as Record<string, unknown>;
    const parts: string[] = [formatToolLabel(toolCall)];

    if (typeof args.store_id === "string") {
      parts.push(args.store_id);
    }
    if (typeof args.name === "string") {
      parts.push(args.name);
    }
    if (typeof args.delta === "number") {
      parts.push(args.delta > 0 ? `+${args.delta}` : String(args.delta));
    }
    if (typeof args.quantity === "number") {
      parts.push(`qty ${args.quantity}`);
    }

    return parts.join(" · ");
  } catch {
    return null;
  }
}

function formatToolLabel(toolName: string): string {
  return toolName.replace(/_/g, " ");
}
