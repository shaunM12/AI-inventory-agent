export const INVENTORY_DISPLAY_TOOLS = new Set([
  "list_inventory",
  "get_store_inventory",
  "get_low_stock_alerts",
]);

export const INVENTORY_MUTATION_TOOLS = new Set([
  "create_product",
  "update_stock",
  "delete_product",
  "transfer_stock",
]);

/** Tool results hidden in chat — inventory lives in the dashboard. */
export const INVENTORY_CHAT_TOOLS = new Set([
  ...INVENTORY_DISPLAY_TOOLS,
  ...INVENTORY_MUTATION_TOOLS,
]);

export function formatToolLabel(toolName: string): string {
  return toolName.replace(/_/g, " ");
}
