import { formatToolLabel } from "./inventoryTools";

export type TaskStatus = "completed" | "failed";

export function isToolFailure(content: string): boolean {
  const trimmed = content.trim();
  if (!trimmed) {
    return true;
  }

  const lower = trimmed.toLowerCase();
  if (
    lower.startsWith("error:") ||
    lower.includes(" failed") ||
    lower.includes("not found") ||
    lower.includes("invalid ")
  ) {
    return true;
  }

  try {
    const data = JSON.parse(trimmed) as unknown;
    if (data && typeof data === "object" && !Array.isArray(data)) {
      const record = data as Record<string, unknown>;
      if ("detail" in record || "error" in record) {
        return true;
      }
    }
  } catch {
    // Plain-text tool results are treated as success.
  }

  return false;
}

export function getToolTaskSummary(
  content: string,
  toolCall?: string,
): { status: TaskStatus; summary: string } {
  const label = toolCall ? formatToolLabel(toolCall) : "Task";
  const failed = isToolFailure(content);

  return {
    status: failed ? "failed" : "completed",
    summary: failed ? `${label} failed` : `${label} completed`,
  };
}
