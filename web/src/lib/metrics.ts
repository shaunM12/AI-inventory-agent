import type { ChatApiMetrics, SessionMetrics, TurnMetrics } from "./types";
import { EMPTY_SESSION_METRICS } from "./constants";

export function createTurnMetrics(
  metrics: ChatApiMetrics,
  turnId: string,
  timestamp: string,
): TurnMetrics {
  return {
    turnId,
    timestamp,
    model: metrics.model,
    promptTokens: metrics.prompt_tokens,
    completionTokens: metrics.completion_tokens,
    totalTokens: metrics.total_tokens,
    latencyMs: metrics.latency_ms,
    llmRounds: metrics.llm_rounds,
    toolCalls: metrics.tool_calls,
    mutations: metrics.mutations,
  };
}

export function aggregateSessionMetrics(turns: TurnMetrics[]): SessionMetrics {
  if (turns.length === 0) {
    return { ...EMPTY_SESSION_METRICS };
  }

  const totalPromptTokens = turns.reduce((sum, t) => sum + t.promptTokens, 0);
  const totalCompletionTokens = turns.reduce(
    (sum, t) => sum + t.completionTokens,
    0,
  );
  const totalTokens = turns.reduce((sum, t) => sum + t.totalTokens, 0);
  const totalLatencyMs = turns.reduce((sum, t) => sum + t.latencyMs, 0);
  const totalToolCalls = turns.reduce((sum, t) => sum + t.toolCalls, 0);
  const totalMutations = turns.reduce((sum, t) => sum + t.mutations, 0);

  return {
    totalPromptTokens,
    totalCompletionTokens,
    totalTokens,
    totalLatencyMs,
    turnCount: turns.length,
    totalToolCalls,
    totalMutations,
    avgLatencyMs: Math.round(totalLatencyMs / turns.length),
  };
}
