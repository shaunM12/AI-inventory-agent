export const STORE_LABELS: Record<string, string> = {
  henderson: "Henderson, NV",
  "las-vegas": "Las Vegas, NV",
};

export const STORAGE_KEYS = {
  conversations: "inventory-agent:conversations:v1",
  activeId: "inventory-agent:active-conversation:v1",
} as const;

export const EMPTY_SESSION_METRICS = {
  totalPromptTokens: 0,
  totalCompletionTokens: 0,
  totalTokens: 0,
  totalLatencyMs: 0,
  turnCount: 0,
  totalToolCalls: 0,
  totalMutations: 0,
  avgLatencyMs: 0,
};

/** Same-origin proxy path — works in Codespaces and local dev (see next.config rewrites). */
export const API_PROXY_PREFIX = "/backend";

export function getApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    return API_PROXY_PREFIX;
  }
  return (
    process.env.API_BASE_URL?.replace(/\/$/, "") ||
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8000"
  );
}
