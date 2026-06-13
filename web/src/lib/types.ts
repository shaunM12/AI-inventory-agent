export interface Product {
  product_id: string;
  store_id: string;
  name: string;
  quantity: number;
  unit: string;
  created_at: string;
  updated_at: string;
}

export interface Store {
  store_id: string;
}

export interface AgentConfig {
  model: string;
  api_base_url: string;
  low_stock_threshold: number;
  store_ids: string[];
  openai_base_url: string;
  llm_configured: boolean;
}

export interface TurnMetrics {
  turnId: string;
  timestamp: string;
  model: string;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  latencyMs: number;
  llmRounds: number;
  toolCalls: number;
  mutations: number;
}

export interface SessionMetrics {
  totalPromptTokens: number;
  totalCompletionTokens: number;
  totalTokens: number;
  totalLatencyMs: number;
  turnCount: number;
  totalToolCalls: number;
  totalMutations: number;
  avgLatencyMs: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "agent" | "tool" | "error";
  content: string;
  toolCall?: string;
  timestamp: string;
  taskStatus?: "completed" | "failed";
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
  messageHistory: Record<string, unknown>[];
  sessionMetrics: SessionMetrics;
  turnMetrics: TurnMetrics[];
}

export interface ConversationEvent {
  actor: string;
  message: string;
  tool_call: string;
  timestamp: string;
}

export interface ChatApiMetrics {
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  latency_ms: number;
  llm_rounds: number;
  tool_calls: number;
  mutations: number;
}

export interface ChatApiResponse {
  reply: string;
  show_reply: boolean;
  events: ConversationEvent[];
  message_history: Record<string, unknown>[];
  metrics: ChatApiMetrics;
  inventory_products: Product[] | null;
  config: AgentConfig;
}

export interface ApiError {
  detail: string;
}
