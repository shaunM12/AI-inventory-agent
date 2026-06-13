import { getApiBaseUrl } from "./constants";
import type {
  AgentConfig,
  ApiError,
  ChatApiResponse,
  Product,
  Store,
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch {
    throw new Error(
      "Cannot reach the inventory API. Start the backend with: .venv/bin/uvicorn api.app:app --reload --host 127.0.0.1 --port 8000",
    );
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as ApiError;
      if (body.detail) {
        detail = body.detail;
      }
    } catch {
      detail = await response.text();
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export async function fetchAgentConfig(): Promise<AgentConfig> {
  return request<AgentConfig>("/agent/config");
}

export async function fetchStores(): Promise<Store[]> {
  return request<Store[]>("/stores");
}

export async function fetchInventory(): Promise<Product[]> {
  return request<Product[]>("/inventory");
}

export async function fetchAlerts(): Promise<Product[]> {
  return request<Product[]>("/inventory/alerts");
}

export async function sendChatMessage(payload: {
  message: string;
  message_history: Record<string, unknown>[];
}): Promise<ChatApiResponse> {
  return request<ChatApiResponse>("/agent/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    await fetchStores();
    return true;
  } catch {
    return false;
  }
}
